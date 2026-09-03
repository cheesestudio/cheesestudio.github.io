"""Roster contract and exact-file Git publishing; no GUI dependencies."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Callable

SCHEMA_VERSION = 1
MAX_PLAYERS = 512
MAX_BYTES = 48000
ROSTER_FILE = "SuccubusList.txt"
ORIGIN_URL = "https://github.com/cheesestudio/cheesestudio.github.io.git"
BADGES = ((1, "粉樱初契", "VIP_01_Rosebud.png"),
          (2, "月魅银辉", "VIP_02_MoonCharm.png"),
          (3, "绯红誓约", "VIP_03_CrimsonPact.png"),
          (4, "鎏金契约", "VIP_04_GildedPact.png"),
          (5, "幻晶星冕", "VIP_05_AstralCrown.png"),
          (6, "永夜魔冠", "VIP_06_EternalNight.png"))


class RosterError(ValueError):
    pass


class PublishError(RuntimeError):
    pass


@dataclass(frozen=True)
class Player:
    display_name: str
    badge: int


@dataclass(frozen=True)
class Roster:
    revision: int
    players: tuple[Player, ...]


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate_players(players: tuple[Player, ...]) -> None:
    if len(players) > MAX_PLAYERS:
        raise RosterError(f"最多支持 {MAX_PLAYERS} 名玩家。")
    names = set()
    for row, player in enumerate(players, 1):
        name = player.display_name
        if not isinstance(name, str) or not name or name != name.strip():
            raise RosterError(f"第 {row} 行：昵称不能为空，也不能带首尾空格。")
        try:
            units = len(name.encode("utf-16-le")) // 2
        except UnicodeEncodeError as exc:
            raise RosterError(f"第 {row} 行：昵称包含无效 Unicode 字符。") from exc
        if units > 64 or any(ord(c) < 32 or ord(c) == 127 for c in name):
            raise RosterError(f"第 {row} 行：昵称超过 64 个字符单位或包含控制字符。")
        if name in names:
            raise RosterError(f"昵称重复：{name}")
        names.add(name)
        if type(player.badge) is not int or not 1 <= player.badge <= 6:
            raise RosterError(f"第 {row} 行：徽章类别必须为 1–6。")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RosterError(f"JSON 字段重复：{key}")
        result[key] = value
    return result


def parse_roster(raw: bytes) -> Roster:
    if len(raw) > MAX_BYTES:
        raise RosterError(f"名单不能超过 {MAX_BYTES} 字节。")
    try:
        text = raw.decode("utf-8-sig")
        if not text.strip():
            return Roster(0, ())
        document = json.loads(text, object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RosterError("名单必须是 UTF-8 JSON，或尚未填写的空文件。") from exc
    if not isinstance(document, dict) or set(document) != {"schemaVersion", "revision", "players"}:
        raise RosterError("名单需要 schemaVersion、revision、players 三个字段。")
    if type(document["schemaVersion"]) is not int or document["schemaVersion"] != SCHEMA_VERSION:
        raise RosterError("不支持的名单格式版本。")
    revision = document["revision"]
    if type(revision) is not int or not 0 <= revision <= 9007199254740991:
        raise RosterError("revision 必须是有效的非负整数版本号。")
    rows = document["players"]
    if not isinstance(rows, list) or len(rows) > MAX_PLAYERS:
        raise RosterError(f"players 必须是最多 {MAX_PLAYERS} 项的数组。")
    players = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"displayName", "badge"}:
            raise RosterError("每名玩家必须包含 displayName 和 badge 两个字段。")
        players.append(Player(row["displayName"], row["badge"]))
    result = Roster(revision, tuple(players))
    validate_players(result.players)
    return result


def serialize_roster(roster: Roster) -> bytes:
    validate_players(roster.players)
    data = {"schemaVersion": SCHEMA_VERSION, "revision": roster.revision,
            "players": [{"displayName": p.display_name, "badge": p.badge} for p in roster.players]}
    raw = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    parse_roster(raw)
    return raw


def revised_roster(previous: Roster, players: tuple[Player, ...]) -> Roster:
    validate_players(players)
    revision = max(int(time.time() * 1000), previous.revision + 1)
    return Roster(revision, players)


def save_atomic(path: Path, raw: bytes, expected_digest: str | None, backup_dir: Path) -> str:
    parse_roster(raw)
    old = path.read_bytes() if path.exists() else b""
    if expected_digest is not None and digest(old) != expected_digest:
        raise RosterError("TXT 已被其他程序修改，请先重新读取，避免覆盖。")
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)
    if path.exists() and old != raw:
        backup = backup_dir / f"SuccubusList-{time.time_ns()}.txt"
        backup.write_bytes(old)
    fd, temporary = tempfile.mkstemp(prefix=".succubus-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        # Recheck after preparing the file, before the atomic replacement.
        latest = path.read_bytes() if path.exists() else b""
        if digest(latest) != digest(old):
            raise RosterError("保存期间 TXT 又发生变化，已保留外部修改。")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return digest(raw)


class GitPublisher:
    def __init__(self, repo: Path, expected_origin: str = ORIGIN_URL):
        self.repo = Path(repo)
        self.expected_origin = expected_origin
        self.git = shutil.which("git")
        if not self.git:
            raise PublishError("没有找到 Git，请先安装 Git for Windows。")

    def run(self, *args: str, input: bytes | None = None, env: dict | None = None,
            check: bool = True) -> subprocess.CompletedProcess:
        environment = os.environ.copy()
        # Do not inherit unrelated alternate-index/repository settings.
        for key in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE"):
            environment.pop(key, None)
        environment["GIT_TERMINAL_PROMPT"] = "0"
        # Desktop launches do not inherit the proxy environment of a terminal.
        # Apply Windows' existing system proxy only to this Git subprocess.
        if os.name == "nt" and not any(environment.get(k) for k in ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy")):
            from urllib.request import getproxies_registry
            proxies = getproxies_registry()
            proxy = proxies.get("https") or proxies.get("http")
            if proxy:
                environment["HTTPS_PROXY"] = proxy
        if env:
            environment.update(env)
        network = bool(args) and args[0] in ("fetch", "push")
        for attempt in range(2 if network else 1):
            try:
                result = subprocess.run([self.git, "-C", str(self.repo), *args], input=input,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        timeout=60 if network else 90, env=environment,
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            except subprocess.TimeoutExpired as exc:
                if network and attempt == 0:
                    continue
                raise PublishError("Git 连接超时，本地修改仍保留。请检查代理是否开启，再点击读取 GitHub 或重试提交。") from exc
            except OSError as exc:
                raise PublishError(f"Git 无法启动：{exc}") from exc
            error = result.stderr.decode("utf-8", errors="replace").lower()
            transient = any(word in error for word in ("could not connect", "failed to connect", "could not resolve", "timed out", "connection reset", "connection was reset"))
            if not (network and attempt == 0 and result.returncode and transient):
                break
        if check and result.returncode:
            message = result.stderr.decode("utf-8", errors="replace").strip()
            if network and transient:
                message = "无法连接 GitHub（已重试）。本地修改仍保留。\n软件会使用 Windows 系统代理，请确认代理软件正在运行。\n\n" + message
            raise PublishError(message or "Git 命令失败。")
        return result

    def verify_origin(self):
        actual = self.run("remote", "get-url", "origin").stdout.decode().strip()
        if actual != self.expected_origin:
            raise PublishError("origin 与配置的名单仓库不同，已停止提交。")

    def fetch(self):
        self.verify_origin()
        self.run("fetch", "origin", "refs/heads/main:refs/remotes/origin/main")

    def head(self) -> str:
        return self.run("rev-parse", "refs/remotes/origin/main").stdout.decode().strip()

    def blob_at(self, commit: str) -> str | None:
        listing = self.run("ls-tree", commit, "--", ROSTER_FILE).stdout.decode().strip()
        if not listing:
            return None
        fields = listing.split()
        if fields[0] != "100644" or fields[1] != "blob":
            raise PublishError("远程名单不是普通文件，已停止。")
        return fields[2]

    def remote_roster(self, refresh=True) -> tuple[bytes, str | None]:
        if refresh:
            self.fetch()
        blob = self.blob_at(self.head())
        raw = self.run("cat-file", "blob", blob).stdout if blob else b""
        parse_roster(raw)
        return raw, blob

    def publish(self, raw: bytes, expected_blob: str | None,
                progress: Callable[[str], None] = lambda message: None) -> tuple[str, str]:
        incoming = parse_roster(raw)
        self.verify_origin()
        progress("正在检查 GitHub 最新名单…")
        self.fetch()
        for attempt in range(2):
            parent = self.head()
            actual_blob = self.blob_at(parent)
            new_blob = self.run("hash-object", "-w", "--stdin", input=raw).stdout.decode().strip()
            if actual_blob == new_blob:
                return parent, new_blob
            if actual_blob != expected_blob:
                raise PublishError("GitHub 名单已被其他人修改。请先读取远程名单，再合并你的修改；没有覆盖远程。")
            remote_raw = self.run("cat-file", "blob", actual_blob).stdout if actual_blob else b""
            remote = parse_roster(remote_raw)
            if incoming.revision <= remote.revision:
                raise PublishError("本地版本号没有高于远程。请重新保存，生成新版本后再提交。")
            with tempfile.TemporaryDirectory(prefix="succubus-git-") as temporary:
                index_env = {"GIT_INDEX_FILE": str(Path(temporary) / "index")}
                self.run("read-tree", parent, env=index_env)
                self.run("update-index", "--add", "--cacheinfo",
                         f"100644,{new_blob},{ROSTER_FILE}", env=index_env)
                tree = self.run("write-tree", env=index_env).stdout.decode().strip()
                message = (f"Update Succubus VIP roster ({len(incoming.players)} players)\n\n"
                           "Constraint: Change only SuccubusList.txt.\n"
                           "Confidence: high\nScope-risk: narrow\n")
                commit = self.run("commit-tree", tree, "-p", parent,
                                  input=message.encode("utf-8")).stdout.decode().strip()
            changed = self.run("diff-tree", "--no-commit-id", "--name-only", "-r", commit).stdout.decode().splitlines()
            if changed != [ROSTER_FILE]:
                raise PublishError("提交范围验证失败，未推送。")
            progress("正在提交名单到 GitHub…")
            result = self.run("push", "origin", f"{commit}:refs/heads/main", check=False)
            if result.returncode == 0:
                self.fetch()
                remote_head = self.head()
                # Another legitimate commit may have arrived immediately after our push.
                included = self.run("merge-base", "--is-ancestor", commit, remote_head, check=False)
                if included.returncode:
                    raise PublishError("推送返回成功，但无法确认远程包含此提交，请检查 GitHub。")
                return commit, new_blob
            self.fetch()
            if self.blob_at(self.head()) == new_blob:
                return self.head(), new_blob
            if attempt == 1 or self.head() == parent:
                raise PublishError(result.stderr.decode("utf-8", errors="replace").strip() or "推送失败。")
            progress("网站有并发更新，正在保留网站改动并重新提交名单…")
        raise PublishError("推送未完成。")
