from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from roster_core import (BADGES, ROSTER_FILE, GitPublisher, Player, Roster, RosterError,
                         digest, parse_roster, revised_roster, save_atomic,
                         serialize_roster, validate_players)

APP_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
DEFAULT_PATH = APP_DIR / ROSTER_FILE if (APP_DIR / ROSTER_FILE).exists() else Path(r"D:\Code\Git\cheesestudio.github.io\SuccubusList.txt")
STATE_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "MeiMoSheVIPManager"
ASSET_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "art"
if not ASSET_DIR.exists():
    ASSET_DIR = APP_DIR / "SuccubusVIPArt"


class RosterApp:
    def __init__(self, root: tk.Tk, smoke=False):
        self.root = root
        self.smoke = smoke
        self.events = queue.Queue()
        self.busy = False
        self.players = []
        self.loaded = Roster(0, ())
        self.local_digest = digest(b"")
        self.remote_blob = None
        self.remote_ready = False
        self.remote_revision = -1
        self.dirty = False
        self.selected = None
        self.buttons = []
        self.preview_images = []
        self.path = DEFAULT_PATH
        if not smoke:
            try:
                settings = json.loads((STATE_DIR / "settings.json").read_text(encoding="utf-8"))
                self.path = Path(settings["roster_path"])
            except (OSError, ValueError, KeyError):
                pass
        root.title("魅魔社 · VIP 名单管理")
        root.geometry("1000x680")
        root.minsize(920, 620)
        root.configure(bg="#15111e")
        root.protocol("WM_DELETE_WINDOW", self.close)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure(".", font=("Microsoft YaHei UI", 9), background="#201929", foreground="#f3eaf8")
        style.configure("TFrame", background="#15111e")
        style.configure("Card.TFrame", background="#201929")
        style.configure("TLabel", background="#15111e", foreground="#d1bfdc")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 20, "bold"), foreground="#f7e9fa")
        style.configure("TButton", padding=(10, 5), background="#382745", borderwidth=0)
        style.map("TButton", background=[("active", "#60406d"), ("disabled", "#2b2333")],
                  foreground=[("disabled", "#8d7c98")])
        style.configure("Accent.TButton", background="#9a4ab5", foreground="white")
        style.map("Accent.TButton", background=[("active", "#b75ad5"), ("disabled", "#503459")])
        style.configure("TEntry", fieldbackground="#2c2338", foreground="#fff2ff", insertcolor="white", padding=7)
        style.configure("TCombobox", fieldbackground="#2c2338", foreground="#fff2ff", padding=6)
        style.map("TCombobox", fieldbackground=[("readonly", "#2c2338")], foreground=[("readonly", "#fff2ff")])
        style.configure("Treeview", background="#201929", fieldbackground="#201929", foreground="#eadff0", rowheight=34, borderwidth=0)
        style.configure("Treeview.Heading", background="#342540", foreground="#ddcbe8", padding=8)
        style.map("Treeview", background=[("selected", "#674078")], foreground=[("selected", "white")])
        root.option_add("*TCombobox*Listbox.background", "#2c2338")
        root.option_add("*TCombobox*Listbox.foreground", "#fff2ff")
        outer = ttk.Frame(root, padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="SUCCUBUS CLUB  /  MEMBERSHIP", foreground="#ba8bcd", font=("Segoe UI", 9)).pack(anchor="w")
        title_row = ttk.Frame(outer)
        title_row.pack(fill="x", pady=(4, 4))
        ttk.Label(title_row, text="魅魔社 · 名单管理", style="Title.TLabel").pack(side="left")
        self.publish_button = self.button(title_row, "一键保存并提交 GitHub", self.publish, "Accent.TButton")
        self.publish_button.pack(side="right")
        self.path_label = ttk.Label(outer, text=str(self.path), foreground="#9d8ba9")
        self.path_label.pack(anchor="w", pady=(2, 8))
        cards = ttk.Frame(outer)
        cards.pack(fill="x")
        self.badge_var = tk.IntVar(value=1)
        for badge, name, filename in BADGES:
            with Image.open(ASSET_DIR / filename) as image:
                displayed = image.convert("RGBA")
                displayed.thumbnail((70, 64), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(displayed, master=root)
            self.preview_images.append(photo)
            card = tk.Radiobutton(cards, text=f"{badge}  {name}", image=photo, compound="top",
                                  variable=self.badge_var, value=badge, command=self.badge_changed,
                                  indicatoron=False, bg="#201929", fg="#dfcbe8", selectcolor="#50305f",
                                  activebackground="#3c2749", activeforeground="white", relief="flat",
                                  font=("Microsoft YaHei UI", 9), padx=7, pady=5, cursor="hand2")
            card.grid(row=0, column=badge-1, sticky="nsew", padx=(0, 7 if badge < 6 else 0))
            cards.columnconfigure(badge-1, weight=1)
        toolbar = ttk.Frame(outer)
        toolbar.pack(fill="x", pady=(10, 8))
        self.search_var = tk.StringVar()
        ttk.Label(toolbar, text="搜索昵称").pack(side="left", padx=(0, 8))
        search = ttk.Entry(toolbar, textvariable=self.search_var, width=24)
        search.pack(side="left")
        self.search_var.trace_add("write", lambda *_: self.refresh_table())
        self.button(toolbar, "选择名单文件", self.choose_file).pack(side="right")
        self.button(toolbar, "读取 GitHub", self.load_remote).pack(side="right", padx=8)
        self.button(toolbar, "读取本地", self.reload_local).pack(side="right")
        body = ttk.Frame(outer)
        body.pack(fill="both", expand=True)
        table_frame = ttk.Frame(body)
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        self.tree = ttk.Treeview(table_frame, columns=("name", "badge"), show="headings", selectmode="browse")
        self.tree.heading("name", text="VRChat 显示昵称")
        self.tree.heading("badge", text="头顶徽章类别")
        self.tree.column("name", width=350, minwidth=200)
        self.tree.column("badge", width=180, minwidth=130)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        editor = ttk.Frame(body, width=270)
        editor.pack(side="right", fill="y")
        editor.pack_propagate(False)
        ttk.Label(editor, text="编辑玩家", font=("Microsoft YaHei UI", 14, "bold"), foreground="#f1d8fc").pack(anchor="w", pady=(2, 8))
        ttk.Label(editor, text="显示昵称（与游戏内完全一致）").pack(anchor="w")
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(editor, textvariable=self.name_var)
        self.name_entry.pack(fill="x", pady=(5, 8))
        self.name_entry.bind("<Return>", lambda _: self.apply_player())
        ttk.Label(editor, text="徽章类别").pack(anchor="w")
        self.badge_combo = ttk.Combobox(editor, values=[f"{i} · {name}" for i, name, _ in BADGES], state="readonly")
        self.badge_combo.current(0)
        self.badge_combo.pack(fill="x", pady=(5, 8))
        self.badge_combo.bind("<<ComboboxSelected>>", lambda _: self.badge_var.set(self.badge_combo.current()+1))
        self.button(editor, "新增 / 更新所选玩家", self.apply_player, "Accent.TButton").pack(fill="x", pady=4)
        self.button(editor, "清空选择，新增另一位", self.clear_selection).pack(fill="x", pady=4)
        self.button(editor, "删除所选玩家", self.remove_player).pack(fill="x", pady=4)
        self.button(editor, "仅保存本地 TXT", self.save_local).pack(fill="x", pady=(8, 4))
        ttk.Label(editor, text="上方图片可切换类别。\n删除并发布后会撤下对应标识。\n提交只更新 SuccubusList.txt。", wraplength=268, foreground="#a58db2", justify="left").pack(anchor="w", pady=(8, 0))
        self.summary_var = tk.StringVar()
        ttk.Label(outer, textvariable=self.summary_var, foreground="#c897dc").pack(anchor="w", pady=(12, 6))
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(outer, textvariable=self.status_var, wraplength=900).pack(anchor="w")
        self.load_local_initial()
        if not smoke:
            root.after(100, self.poll_events)
            root.after(300, self.check_remote)

    def button(self, parent, text, command, style="TButton"):
        button = ttk.Button(parent, text=text, command=command, style=style)
        self.buttons.append(button)
        return button

    def badge_changed(self):
        self.badge_combo.current(self.badge_var.get()-1)

    def accept_raw(self, raw, local=True):
        self.loaded = parse_roster(raw)
        self.players = list(self.loaded.players)
        if local:
            self.local_digest = digest(raw)
        self.dirty = not local
        self.clear_selection()
        self.refresh_table()

    def load_local_initial(self):
        try:
            self.accept_raw(self.path.read_bytes() if self.path.exists() else b"")
            self.status_var.set("已读取本地名单。正在准备远程版本检查…" if not self.smoke else "界面自检")
        except (OSError, RosterError) as exc:
            self.status_var.set(f"读取失败：{exc}")
            self.local_digest = None
        self.publish_button.configure(state="disabled")

    def refresh_table(self):
        if not hasattr(self, "tree"):
            return
        old_selection = self.selected
        self.tree.delete(*self.tree.get_children())
        query = self.search_var.get().casefold()
        for index, player in enumerate(self.players):
            if query and query not in player.display_name.casefold():
                continue
            self.tree.insert("", "end", iid=str(index), values=(player.display_name, f"{player.badge} · {BADGES[player.badge-1][1]}"))
        if old_selection is not None and self.tree.exists(str(old_selection)):
            self.tree.selection_set(str(old_selection))
        self.summary_var.set(f"{len(self.players)} / 512 位玩家    ·    版本 {self.loaded.revision}" + ("    ·    有未保存改动" if self.dirty else ""))

    def on_select(self, _=None):
        selection = self.tree.selection()
        if not selection:
            return
        index = int(selection[0])
        if index >= len(self.players):
            return
        self.selected = index
        player = self.players[index]
        self.name_var.set(player.display_name)
        self.badge_var.set(player.badge)
        self.badge_changed()

    def clear_selection(self):
        self.selected = None
        if hasattr(self, "tree"):
            self.tree.selection_remove(*self.tree.selection())
        self.name_var.set("")

    def apply_player(self):
        if self.busy:
            return
        player = Player(self.name_var.get(), self.badge_var.get())
        proposed = list(self.players)
        if self.selected is None:
            proposed.append(player)
        else:
            proposed[self.selected] = player
        try:
            validate_players(tuple(proposed))
            serialize_roster(Roster(self.loaded.revision, tuple(proposed)))
        except RosterError as exc:
            messagebox.showerror("不能保存此玩家", str(exc), parent=self.root)
            return
        self.players = proposed
        self.selected = len(proposed)-1 if self.selected is None else self.selected
        self.dirty = tuple(self.players) != self.loaded.players
        self.refresh_table()
        self.status_var.set("已更新表格；点击一键提交后才会发布到地图。")

    def remove_player(self):
        if self.busy or self.selected is None:
            return
        name = self.players[self.selected].display_name
        if not messagebox.askyesno("删除玩家", f"从名单移除 {name}？\n发布后，此玩家的头顶标识也会撤下。", parent=self.root):
            return
        del self.players[self.selected]
        self.clear_selection()
        self.dirty = tuple(self.players) != self.loaded.players
        self.refresh_table()

    def discard_ok(self):
        return not self.dirty or messagebox.askyesno("未保存修改", "放弃表格里尚未保存的修改？", parent=self.root)

    def choose_file(self):
        if self.busy or not self.discard_ok():
            return
        path = filedialog.askopenfilename(title="选择 SuccubusList.txt", initialdir=self.path.parent,
                                         filetypes=[("VIP 名单", "SuccubusList.txt")], parent=self.root)
        if not path:
            return
        chosen = Path(path)
        if chosen.name != ROSTER_FILE:
            messagebox.showerror("文件名不符", "请选择名为 SuccubusList.txt 的名单。", parent=self.root)
            return
        self.path = chosen
        self.path_label.configure(text=str(self.path))
        self.remote_ready = False
        self.load_local_initial()
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        (STATE_DIR / "settings.json").write_text(json.dumps({"roster_path": str(self.path)}, ensure_ascii=False), encoding="utf-8")
        self.check_remote()

    def reload_local(self):
        if self.busy or not self.discard_ok():
            return
        self.load_local_initial()
        self.check_remote()

    def save_local(self):
        if self.busy:
            return False
        try:
            if self.local_digest is None:
                raise RosterError("请先修正并重新读取原名单，不能覆盖未能解析的文件。")
            changed = tuple(self.players) != self.loaded.players or self.loaded.revision <= self.remote_revision or self.loaded.revision == 0
            floor = max(self.loaded.revision, self.remote_revision)
            roster = revised_roster(Roster(floor, self.loaded.players), tuple(self.players)) if changed else self.loaded
            raw = serialize_roster(roster)
            self.local_digest = save_atomic(self.path, raw, self.local_digest, STATE_DIR / "backups")
            self.loaded = roster
            self.dirty = False
            self.refresh_table()
            self.status_var.set("已保存本地 TXT；尚未发布的修改需要点击一键提交。")
            return True
        except (OSError, RosterError) as exc:
            messagebox.showerror("保存失败", str(exc), parent=self.root)
            return False

    def start_worker(self, function, complete):
        if self.busy:
            return
        self.busy = True
        for button in self.buttons:
            button.configure(state="disabled")
        self.name_entry.configure(state="disabled")
        self.badge_combo.configure(state="disabled")
        def work():
            try:
                self.events.put(("done", complete, function()))
            except Exception as exc:
                self.events.put(("error", str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def poll_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "status":
                    self.status_var.set(event[1])
                    continue
                self.busy = False
                for button in self.buttons:
                    button.configure(state="normal")
                self.name_entry.configure(state="normal")
                self.badge_combo.configure(state="readonly")
                if event[0] == "error":
                    self.status_var.set("操作失败：" + event[1])
                    messagebox.showerror("操作未完成", event[1], parent=self.root)
                else:
                    event[1](event[2])
                self.publish_button.configure(state="normal" if self.remote_ready else "disabled")
        except queue.Empty:
            pass
        self.root.after(100, self.poll_events)

    def check_remote(self):
        self.status_var.set("正在读取 GitHub 版本；可使用本机现有 Git 登录凭据…")
        def complete(result):
            raw, blob = result
            remote = parse_roster(raw)
            self.remote_blob = blob
            self.remote_revision = remote.revision
            self.remote_ready = True
            if remote.players != self.loaded.players and remote.revision >= self.loaded.revision:
                self.remote_ready = False
                self.status_var.set("GitHub 与本地内容不同。请先点击“读取 GitHub”载入最新名单，再编辑提交。")
            else:
                self.status_var.set("GitHub 已连接。一键提交只更新名单，网站及其他工作区改动会保留。")
        self.start_worker(lambda: GitPublisher(self.path.parent).remote_roster(), complete)

    def load_remote(self):
        if self.busy or not self.discard_ok():
            return
        def complete(result):
            raw, blob = result
            self.accept_raw(raw, local=False)
            self.remote_blob = blob
            self.remote_revision = self.loaded.revision
            self.remote_ready = True
            # Preserve the local file until an explicit save, and detect external edits.
            self.local_digest = digest(self.path.read_bytes() if self.path.exists() else b"")
            self.status_var.set("已将 GitHub 最新名单载入表格，未覆盖本地文件。")
        self.status_var.set("正在读取 GitHub 最新名单…")
        self.start_worker(lambda: GitPublisher(self.path.parent).remote_roster(), complete)

    def publish(self):
        if self.busy or not self.remote_ready or not self.save_local():
            return
        raw = serialize_roster(self.loaded)
        baseline = self.remote_blob
        def complete(result):
            commit, blob = result
            self.remote_blob = blob
            self.remote_revision = self.loaded.revision
            self.status_var.set(f"已发布到 GitHub · 提交 {commit[:8]} · 新下载成功后，房间内会更新标识。")
        self.start_worker(lambda: GitPublisher(self.path.parent).publish(
            raw, baseline, lambda message: self.events.put(("status", message))), complete)

    def close(self):
        if self.busy:
            messagebox.showinfo("请稍候", "正在执行 Git 操作，请等待操作结束后关闭。", parent=self.root)
            return
        if self.discard_ok():
            self.root.destroy()


def main():
    smoke = "--smoke-test" in sys.argv
    root = tk.Tk()
    if smoke:
        root.withdraw()
    app = RosterApp(root, smoke=smoke)
    if smoke:
        root.update_idletasks()
        assert len(app.preview_images) == 6
        assert app.badge_combo["values"][5].startswith("6")
        root.destroy()
        print("GUI_SMOKE_OK: six artworks, editor fields, and table initialized")
        return
    root.mainloop()


if __name__ == "__main__":
    main()
