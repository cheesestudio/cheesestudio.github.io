from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import queue
import sys
import threading
import time
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
        root.title("魅魔社 · VIP 名单管理 v1.5 · 12款爱心头衔")
        root.geometry("1120x760")
        root.minsize(980, 650)
        root.configure(bg="#15111e")
        root.protocol("WM_DELETE_WINDOW", self.close)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure(".", font=("Microsoft YaHei UI", 9), background="#201929", foreground="#f3eaf8")
        style.configure("TFrame", background="#15111e")
        style.configure("Card.TFrame", background="#201929")
        style.configure("TLabel", background="#15111e", foreground="#d1bfdc")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 20, "bold"), foreground="#f7e9fa")
        style.configure("Subtitle.TLabel", font=("Microsoft YaHei UI", 9), foreground="#a58db2")
        style.configure("Section.TLabel", font=("Microsoft YaHei UI", 12, "bold"), foreground="#f1d8fc")
        style.configure("TButton", padding=(9, 5), background="#382745", borderwidth=0)
        style.map("TButton", background=[("active", "#60406d"), ("disabled", "#2b2333")],
                  foreground=[("disabled", "#8d7c98")])
        style.configure("Accent.TButton", background="#9a4ab5", foreground="white")
        style.map("Accent.TButton", background=[("active", "#b75ad5"), ("disabled", "#503459")])
        style.configure("TEntry", fieldbackground="#2c2338", foreground="#fff2ff", insertcolor="white", padding=7)
        style.configure("TCombobox", fieldbackground="#2c2338", foreground="#fff2ff", padding=6)
        style.map("TCombobox", fieldbackground=[("readonly", "#2c2338")], foreground=[("readonly", "#fff2ff")])
        style.configure("Treeview", background="#201929", fieldbackground="#201929", foreground="#eadff0", rowheight=32, borderwidth=0)
        style.configure("Treeview.Heading", background="#342540", foreground="#ddcbe8", padding=8)
        style.map("Treeview", background=[("selected", "#674078")], foreground=[("selected", "white")])
        root.option_add("*TCombobox*Listbox.background", "#2c2338")
        root.option_add("*TCombobox*Listbox.foreground", "#fff2ff")
        outer = ttk.Frame(root, padding=(18, 14, 18, 12))
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(5, weight=1)
        ttk.Label(outer, text="SUCCUBUS CLUB  /  MEMBER ROSTER", foreground="#ba8bcd", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        title_row = ttk.Frame(outer)
        title_row.grid(row=1, column=0, sticky="ew", pady=(2, 5))
        title_row.columnconfigure(0, weight=1)
        title_block = ttk.Frame(title_row)
        title_block.grid(row=0, column=0, sticky="w")
        ttk.Label(title_block, text="魅魔社 · 名单管理", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_block, text="维护 VRChat 显示昵称、头衔样式与有效期", style="Subtitle.TLabel").pack(anchor="w", pady=(1, 0))
        self.publish_button = self.button(title_row, "一键保存并提交 GitHub", self.publish, "Accent.TButton")
        self.publish_button.grid(row=0, column=1, sticky="e", padx=(12, 0))
        path_row = ttk.Frame(outer)
        path_row.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        path_row.columnconfigure(0, weight=1)
        self.path_label = ttk.Label(path_row, text=str(self.path), foreground="#9d8ba9")
        self.path_label.grid(row=0, column=0, sticky="w")
        path_actions = ttk.Frame(path_row)
        path_actions.grid(row=0, column=1, sticky="e")
        self.button(path_actions, "读取本地", self.reload_local).pack(side="left")
        self.button(path_actions, "读取 GitHub", self.load_remote).pack(side="left", padx=7)
        self.button(path_actions, "选择名单文件", self.choose_file).pack(side="left")
        cards = ttk.Frame(outer, style="Card.TFrame", padding=(9, 6))
        cards.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        for column in range(6):
            cards.columnconfigure(column, weight=1, uniform="badges")
        self.badge_var = tk.IntVar(value=1)
        for badge, name, filename in BADGES:
            with Image.open(ASSET_DIR / filename) as image:
                displayed = image.convert("RGBA")
                displayed.thumbnail((120, 44), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(displayed, master=root)
            self.preview_images.append(photo)
            card = tk.Radiobutton(cards, text=f"{badge}  {name}", image=photo, compound="top",
                                  variable=self.badge_var, value=badge, command=self.badge_changed,
                                  indicatoron=False, bg="#201929", fg="#dfcbe8", selectcolor="#50305f",
                                  activebackground="#3c2749", activeforeground="white", relief="flat",
                                  font=("Microsoft YaHei UI", 9), padx=7, pady=5, cursor="hand2")
            card.grid(row=(badge-1)//6, column=(badge-1)%6, sticky="ew", padx=3, pady=2)
        toolbar = ttk.Frame(outer)
        toolbar.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        toolbar.columnconfigure(1, weight=1)
        self.search_var = tk.StringVar()
        ttk.Label(toolbar, text="玩家名单", style="Section.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 14))
        search = ttk.Entry(toolbar, textvariable=self.search_var, width=24)
        search.grid(row=0, column=1, sticky="ew")
        ttk.Label(toolbar, text="搜索昵称", style="Subtitle.TLabel").grid(row=0, column=2, sticky="e", padx=(8, 0))
        self.button(toolbar, "增加玩家", self.start_new_player, "Accent.TButton").grid(row=0, column=3, sticky="e", padx=(12, 0))
        self.search_var.trace_add("write", lambda *_: self.refresh_table())
        body = ttk.Frame(outer)
        body.grid(row=5, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        table_frame = ttk.Frame(body)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.tree = ttk.Treeview(table_frame, columns=("name", "badge", "expiry"), show="headings", selectmode="browse")
        self.tree.heading("name", text="VRChat 显示昵称")
        self.tree.heading("badge", text="头顶徽章类别")
        self.tree.heading("expiry", text="有效期")
        self.tree.column("name", width=280, minwidth=180)
        self.tree.column("badge", width=145, minwidth=120)
        self.tree.column("expiry", width=125, minwidth=110)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        editor_panel = ttk.Frame(body, width=300, style="Card.TFrame", padding=10)
        editor_panel.grid(row=0, column=1, sticky="nsew")
        editor_panel.grid_propagate(False)
        editor_panel.columnconfigure(0, weight=1)
        editor_panel.rowconfigure(0, weight=1)
        body.columnconfigure(1, weight=0, minsize=300)
        self.editor_canvas = tk.Canvas(editor_panel, background="#201929", highlightthickness=0, width=264, height=100)
        self.editor_canvas.grid(row=0, column=0, sticky="nsew")
        editor_scrollbar = ttk.Scrollbar(editor_panel, orient="vertical", command=self.editor_canvas.yview)
        editor_scrollbar.grid(row=0, column=1, sticky="ns")
        self.editor_canvas.configure(yscrollcommand=editor_scrollbar.set)
        editor = ttk.Frame(self.editor_canvas, style="Card.TFrame", padding=(4, 0, 4, 8))
        editor_window = self.editor_canvas.create_window((0, 0), window=editor, anchor="nw")
        editor.bind("<Configure>", lambda _: self.editor_canvas.configure(scrollregion=self.editor_canvas.bbox("all")))
        self.editor_canvas.bind("<Configure>", lambda event: self.editor_canvas.itemconfigure(editor_window, width=event.width))
        root.bind("<MouseWheel>", self.scroll_editor, add="+")
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
        ttk.Label(editor, text="有效期").pack(anchor="w")
        self.duration_var = tk.StringVar(value="永久")
        self.duration_combo = ttk.Combobox(editor, textvariable=self.duration_var,
                                           values=["永久", "1个月", "3个月", "6个月", "12个月", "自定义到期日期"],
                                           state="readonly")
        self.duration_combo.pack(fill="x", pady=(5, 4))
        self.duration_combo.bind("<<ComboboxSelected>>", lambda _: self.duration_changed())
        self.expiry_date_var = tk.StringVar()
        self.expiry_date_entry = ttk.Entry(editor, textvariable=self.expiry_date_var)
        self.expiry_date_entry.pack(fill="x", pady=(0, 8))
        self.apply_button = self.button(editor_panel, "保存新增 / 更新玩家", self.apply_player, "Accent.TButton")
        self.apply_button.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Label(editor, text="自定义日期格式：YYYY-MM-DD；永久不会过期。", foreground="#a58db2", wraplength=268).pack(anchor="w", pady=(0, 4))
        self.button(editor, "清空选择，新增另一位", self.clear_selection).pack(fill="x", pady=4)
        self.button(editor, "删除所选玩家", self.remove_player).pack(fill="x", pady=4)
        self.button(editor, "仅保存本地 TXT", self.save_local).pack(fill="x", pady=(8, 4))
        ttk.Label(editor, text="上方图片可切换类别。\n到期后地图自动隐藏头衔。\n提交只更新 SuccubusList.txt。", wraplength=268, foreground="#a58db2", justify="left").pack(anchor="w", pady=(8, 0))
        self.summary_var = tk.StringVar()
        ttk.Label(outer, textvariable=self.summary_var, foreground="#c897dc").grid(row=6, column=0, sticky="w", pady=(8, 3))
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(outer, textvariable=self.status_var, wraplength=1020).grid(row=7, column=0, sticky="w")
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

    def scroll_editor(self, event):
        widget = event.widget
        while widget is not None:
            if widget == self.editor_canvas:
                self.editor_canvas.yview_scroll(-int(event.delta / 120), "units")
                return "break"
            widget = getattr(widget, "master", None)

    def duration_changed(self):
        custom = self.duration_var.get() == "自定义到期日期"
        self.expiry_date_entry.configure(state="normal" if custom else "disabled")

    @staticmethod
    def expiry_text(expires_at):
        if expires_at == 0:
            return "永久"
        suffix = "（已过期）" if expires_at <= int(time.time()) else ""
        return datetime.fromtimestamp(expires_at).strftime("%Y-%m-%d") + suffix

    def expiry_from_editor(self):
        choice = self.duration_var.get()
        if choice == "永久":
            return 0
        if choice == "自定义到期日期":
            try:
                value = datetime.strptime(self.expiry_date_var.get().strip(), "%Y-%m-%d")
            except ValueError as exc:
                raise RosterError("自定义到期日期必须是 YYYY-MM-DD，例如 2026-10-07。") from exc
            return int((value + timedelta(days=1)).timestamp()) - 1
        days = {"1个月": 30, "3个月": 90, "6个月": 180, "12个月": 365}
        if choice not in days:
            raise RosterError("请选择有效期，或选择永久。")
        return int((datetime.now() + timedelta(days=days[choice])).timestamp())

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
            self.tree.insert("", "end", iid=str(index), values=(player.display_name, f"{player.badge} · {BADGES[player.badge-1][1]}", self.expiry_text(player.expires_at)))
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
        if hasattr(self, "apply_button"):
            self.apply_button.configure(text="保存更新玩家")
        player = self.players[index]
        self.name_var.set(player.display_name)
        self.badge_var.set(player.badge)
        self.badge_changed()
        if player.expires_at == 0:
            self.duration_var.set("永久")
            self.expiry_date_var.set("")
        else:
            self.duration_var.set("自定义到期日期")
            self.expiry_date_var.set(datetime.fromtimestamp(player.expires_at).strftime("%Y-%m-%d"))
        self.duration_changed()

    def clear_selection(self):
        self.selected = None
        if hasattr(self, "apply_button"):
            self.apply_button.configure(text="保存新增玩家")
        if hasattr(self, "tree"):
            self.tree.selection_remove(*self.tree.selection())
        self.name_var.set("")
        self.duration_var.set("永久")
        self.expiry_date_var.set("")
        self.duration_changed()

    def start_new_player(self):
        if self.busy:
            return
        self.clear_selection()
        self.name_entry.focus_set()
        self.editor_canvas.yview_moveto(0)
        self.status_var.set("请输入昵称、选择头衔和有效期，然后点击“保存新增 / 更新玩家”。")

    def apply_player(self):
        if self.busy:
            return
        try:
            expires_at = self.expiry_from_editor()
        except RosterError as exc:
            messagebox.showerror("有效期不正确", str(exc), parent=self.root)
            return
        player = Player(self.name_var.get(), self.badge_var.get(), expires_at)
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
        assert len(app.preview_images) == len(BADGES) == 12
        assert app.badge_combo["values"][11].startswith("12")
        root.destroy()
        print("GUI_SMOKE_OK: 12 artworks, scrollable editor, fixed save button, and table initialized")
        return
    root.mainloop()


if __name__ == "__main__":
    main()
