from pathlib import Path
import subprocess

import pytest

from roster_core import (GitPublisher, Player, PublishError, Roster, RosterError, digest,
                         parse_roster, revised_roster, save_atomic, serialize_roster)


def test_unicode_roundtrip_and_revision():
    initial = Roster(9000000000000, (Player('奶酪 🦇 "VIP"', 6), Player("Name With Space", 1)))
    assert parse_roster(serialize_roster(initial)) == initial
    changed = revised_roster(initial, (Player("新玩家", 2),))
    assert changed.revision > initial.revision


def test_empty_and_revocation():
    assert parse_roster(b"\xef\xbb\xbf\r\n") == Roster(0, ())
    assert parse_roster(serialize_roster(Roster(12, ()))).players == ()


@pytest.mark.parametrize("raw", [
    b"<html>404</html>", b'{"schemaVersion":2,"revision":1,"players":[]}',
    b'{"schemaVersion":1,"revision":true,"players":[]}',
    b'{"schemaVersion":1,"revision":1,"revision":2,"players":[]}',
    b'{"schemaVersion":1,"revision":1,"players":[{"displayName":"A","badge":7}]}',
    b'{"schemaVersion":1,"revision":1,"players":[{"displayName":"A","badge":1},{"displayName":"A","badge":2}]}',
    b'{"schemaVersion":1,"revision":1,"players":[{"displayName":" A","badge":1}]}',
    b'{"schemaVersion":1,"revision":1,"players":[{"displayName":"A\\nB","badge":1}]}',
    b'{"schemaVersion":1,"revision":1,"players":[{"displayName":"A","badge":true}]}',
    b'{"schemaVersion":1,"revision":1,"players":[{"displayName":"\\ud800","badge":1}]}',
])
def test_reject_invalid_rosters(raw):
    with pytest.raises(RosterError):
        parse_roster(raw)


def test_atomic_save_preserves_external_changes(tmp_path):
    path = tmp_path / "SuccubusList.txt"
    path.write_bytes(b"")
    raw = serialize_roster(Roster(1, (Player("A", 2),)))
    save_atomic(path, raw, digest(b""), tmp_path / "backups")
    assert path.read_bytes() == raw
    assert next((tmp_path / "backups").iterdir()).read_bytes() == b""
    path.write_bytes(b"external")
    with pytest.raises(RosterError, match="其他程序"):
        save_atomic(path, raw, digest(raw), tmp_path / "backups")
    assert path.read_bytes() == b"external"


def git(path, *args, input=None):
    result = subprocess.run(["git", "-C", str(path), *args], input=input, capture_output=True,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    return result.stdout


@pytest.fixture
def repositories(tmp_path):
    remote = tmp_path / "remote.git"
    remote.mkdir()
    git(remote, "init", "--bare", "--initial-branch=main")
    site = tmp_path / "site"
    site.mkdir()
    git(site, "init", "--initial-branch=main")
    git(site, "config", "user.email", "test@example.invalid")
    git(site, "config", "user.name", "Test")
    (site / "index.html").write_text("KEEP WEBSITE", encoding="utf-8")
    (site / "SuccubusList.txt").write_bytes(b"")
    git(site, "add", ".")
    git(site, "commit", "-m", "initial website")
    git(site, "remote", "add", "origin", str(remote))
    git(site, "push", "origin", "main")
    local = tmp_path / "local"
    local.mkdir()
    git(local, "init", "--initial-branch=main")
    git(local, "config", "user.email", "test@example.invalid")
    git(local, "config", "user.name", "Test")
    (local / "old-history.txt").write_text("different history", encoding="utf-8")
    (local / "SuccubusList.txt").write_bytes(b"")
    git(local, "add", ".")
    git(local, "commit", "-m", "unrelated local history")
    git(local, "remote", "add", "origin", str(remote))
    return remote, site, local, GitPublisher(local, expected_origin=str(remote))


def test_publish_preserves_unrelated_history_index_dirty_files_and_website(repositories):
    remote, site, local, publisher = repositories
    (local / "staged.txt").write_text("DO NOT PUBLISH", encoding="utf-8")
    git(local, "add", "staged.txt")
    (local / "old-history.txt").write_text("unsaved edit", encoding="utf-8")
    before_head = git(local, "rev-parse", "HEAD")
    before_status = git(local, "status", "--porcelain")
    _, baseline = publisher.remote_roster()
    raw = serialize_roster(Roster(123, (Player("奶酪", 5),)))
    commit, blob = publisher.publish(raw, baseline)
    assert git(remote, "show", "main:SuccubusList.txt") == raw
    assert git(remote, "show", "main:index.html") == b"KEEP WEBSITE"
    assert git(local, "rev-parse", "HEAD") == before_head
    assert git(local, "status", "--porcelain") == before_status
    assert git(local, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).strip() == b"SuccubusList.txt"
    assert publisher.blob_at(publisher.head()) == blob
    assert publisher.publish(raw, blob)[0] == commit


def test_remote_roster_conflict_is_not_overwritten(repositories):
    remote, site, local, publisher = repositories
    _, baseline = publisher.remote_roster()
    other = serialize_roster(Roster(4, (Player("Other", 1),)))
    (site / "SuccubusList.txt").write_bytes(other)
    git(site, "add", "SuccubusList.txt")
    git(site, "commit", "-m", "other person updated roster")
    git(site, "push", "origin", "main")
    with pytest.raises(PublishError, match="其他人修改"):
        publisher.publish(serialize_roster(Roster(5, (Player("My edit", 2),))), baseline)
    assert git(remote, "show", "main:SuccubusList.txt") == other


def test_concurrent_website_change_is_preserved(repositories):
    remote, site, local, publisher = repositories
    _, baseline = publisher.remote_roster()
    (site / "index.html").write_text("NEW WEBSITE", encoding="utf-8")
    git(site, "add", "index.html")
    git(site, "commit", "-m", "website changed independently")
    git(site, "push", "origin", "main")
    raw = serialize_roster(Roster(7, (Player("A", 3),)))
    publisher.publish(raw, baseline)
    assert git(remote, "show", "main:index.html") == b"NEW WEBSITE"
    assert git(remote, "show", "main:SuccubusList.txt") == raw


def test_reject_lower_revision(repositories):
    _, _, _, publisher = repositories
    _, baseline = publisher.remote_roster()
    _, blob = publisher.publish(serialize_roster(Roster(20, (Player("A", 1),))), baseline)
    with pytest.raises(PublishError, match="版本号"):
        publisher.publish(serialize_roster(Roster(20, ())), blob)
