# 魅魔社 VIP 名单编辑器（v1.5）

Windows 免安装版可直接下载仓库根目录的 `MeiMoSheVIPManager-Windows-v1.5.zip`。完整解压后运行 `MeiMoSheVIPManager.exe`，不要单独复制 EXE。

双击 `StartSuccubusVIP.cmd`，或运行 `python SuccubusVIPManager.py`。源码与 `SuccubusList.txt` 放在同一个 Git 仓库目录，图片放在 `SuccubusVIPArt/`。

首次使用需要 Python 3.11 或更新版、Git 和 Pillow：

```powershell
py -3 -m pip install -r requirements-succubus.txt
```

Git 需要已登录有此仓库写权限的 GitHub 账号。使用现有 Git 凭据，不需要在软件中填写令牌。免 Python 版本可使用单独提供的 Windows EXE 文件夹。

1. 软件启动时检查远程名单；有其他人的新改动时，先点击“读取 GitHub”。
2. 输入 VRChat **显示昵称**，包括原有大小写、空格和特殊符号；选择 1–12 类图片和有效期。选择“永久”不会过期，也可以选择月份或自定义 `YYYY-MM-DD` 到期日期。
3. 点击“新增 / 更新”把表单内容写入表格；选中表格行可修改或删除。
4. 点击“一键提交”保存 TXT、生成新版本并推送到 GitHub `main`。只更新 `SuccubusList.txt`。

类别：1 粉桃眨眼、2 月紫好梦、3 薄荷欢笑、4 晴蓝害羞、5 蜜桃心意、6 莓红调皮、7 丁香蝴蝶结、8 奶油可可、9 珊瑚吐舌、10 青瓷慵懒、11 蓝紫星眸、12 樱雪微笑。

旧名单保留原编号，1–6 对应新系列前六款；7–12 为新增款式。新增 7–12 类玩家前，请先使用已更新的地图。

## 更新规则

TXT 内使用 UTF-8 JSON，示例结构如下（昵称仅为格式示例）：

```json
{
  "schemaVersion": 2,
  "revision": 1788426000000,
  "players": [{"displayName": "Example Player", "badge": 6, "expiresAt": 0}]
}
```

软件每次提交自动提高 `revision`，地图只接受更高版本，以免旧客户端或 GitHub 缓存把名单回退。每名玩家的 `expiresAt` 是 Unix 秒数，到期后地图自动隐藏头衔；填 `0` 表示永久有效。软件可选择永久、1/3/6/12 个月或自定义到期日期。手动编辑 TXT 时也必须提高版本号。删除全部玩家请保留 JSON 结构、提高版本号并设置 `players: []`，不要清空文件。

最多 512 名玩家、UTF-8 文件最多 48000 字节、昵称最多 64 个 UTF-16 单元。相同昵称不能重复，类别只能为 1–12。昵称匹配不是账号 ID 验证，改名后需要更新名单。

地图会在玩家加入时以及约每 180 秒尝试下载。任何客户端成功下载更高版本后，通过 Udon 手动同步转发；其他玩家即使不能访问 GitHub，也能接收房间同步。新增、更换类别和删除都会重新匹配当前玩家。下载失败或内容错误时保留最后有效名单。GitHub 缓存和 VRChat 下载队列可能延迟更新。

当前地图使用 raw.githubusercontent.com。至少一位负责下载的玩家需要允许该世界的 **Allow Untrusted URLs**。本地显示/隐藏按钮只控制当前玩家视角，不更改 VIP 资格。

## 文件与 Git 保护

保存前检查 TXT 是否被其他程序修改；旧文件自动备份到 `%LOCALAPPDATA%\MeiMoSheVIPManager\backups`。软件设置也保存在此目录。

发布以远程 `main` 为父提交，使用临时 Git index，只改名单，不切换本地分支、不重置工作区、不包含已暂存的其他文件、不强推。这样可兼容此仓库本地和远程历史不一致的情况。成功发布后，本地 Git 状态仍可能显示 TXT 已修改，这是保留本地分支的正常结果。

远程名单同时被别人修改时会停止发布；请先读取 GitHub 再重新编辑。并发的网站改动会被保留。发布源码和图片需要普通 Git 操作，编辑器的一键提交只管理名单。

测试：`python -m pytest test_succubus_roster_core.py`（需要 pytest）；`python SuccubusVIPManager.py --smoke-test` 检查窗口组件与十二张图片能否载入。
