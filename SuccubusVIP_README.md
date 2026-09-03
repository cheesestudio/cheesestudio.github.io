# 魅魔社 VIP 名单编辑器

双击 `StartSuccubusVIP.cmd`，或运行 `python SuccubusVIPManager.py`。源码与 `SuccubusList.txt` 放在同一个 Git 仓库目录，图片放在 `SuccubusVIPArt/`。

首次使用需要 Python 3.11 或更新版、Git 和 Pillow：

```powershell
py -3 -m pip install -r requirements-succubus.txt
```

Git 需要已登录有此仓库写权限的 GitHub 账号。使用现有 Git 凭据，不需要在软件中填写令牌。免 Python 版本可使用单独提供的 Windows EXE 文件夹。

1. 软件启动时检查远程名单；有其他人的新改动时，先点击“读取 GitHub”。
2. 输入 VRChat **显示昵称**，包括原有大小写、空格和特殊符号；选择 1–6 类图片。
3. 点击“新增 / 更新”把表单内容写入表格；选中表格行可修改或删除。
4. 点击“一键提交”保存 TXT、生成新版本并推送到 GitHub `main`。只更新 `SuccubusList.txt`。

类别：1 粉樱初契、2 月魅银辉、3 绯红誓约、4 鎏金契约、5 幻晶星冕、6 永夜魔冠。

## 更新规则

TXT 内使用 UTF-8 JSON，示例结构如下（昵称仅为格式示例）：

```json
{
  "schemaVersion": 1,
  "revision": 1788426000000,
  "players": [{"displayName": "Example Player", "badge": 6}]
}
```

软件每次提交自动提高 `revision`，地图只接受更高版本，以免旧客户端或 GitHub 缓存把名单回退。手动编辑 TXT 时也必须提高版本号。删除全部玩家请保留 JSON 结构、提高版本号并设置 `players: []`，不要清空文件。

最多 512 名玩家、UTF-8 文件最多 48000 字节、昵称最多 64 个 UTF-16 单元。相同昵称不能重复，类别只能为 1–6。昵称匹配不是账号 ID 验证，改名后需要更新名单。

地图会在玩家加入时以及约每 180 秒尝试下载。任何客户端成功下载更高版本后，通过 Udon 手动同步转发；其他玩家即使不能访问 GitHub，也能接收房间同步。新增、更换类别和删除都会重新匹配当前玩家。下载失败或内容错误时保留最后有效名单。GitHub 缓存和 VRChat 下载队列可能延迟更新。

当前地图使用 raw.githubusercontent.com。至少一位负责下载的玩家需要允许该世界的 **Allow Untrusted URLs**。本地显示/隐藏按钮只控制当前玩家视角，不更改 VIP 资格。

## 文件与 Git 保护

保存前检查 TXT 是否被其他程序修改；旧文件自动备份到 `%LOCALAPPDATA%\MeiMoSheVIPManager\backups`。软件设置也保存在此目录。

发布以远程 `main` 为父提交，使用临时 Git index，只改名单，不切换本地分支、不重置工作区、不包含已暂存的其他文件、不强推。这样可兼容此仓库本地和远程历史不一致的情况。成功发布后，本地 Git 状态仍可能显示 TXT 已修改，这是保留本地分支的正常结果。

远程名单同时被别人修改时会停止发布；请先读取 GitHub 再重新编辑。并发的网站改动会被保留。发布源码和图片需要普通 Git 操作，编辑器的一键提交只管理名单。

测试：`python -m pytest test_succubus_roster_core.py`（需要 pytest）；`python SuccubusVIPManager.py --smoke-test` 检查窗口组件与六张图片能否载入。
