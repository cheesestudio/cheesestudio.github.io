# Bullet Hell Boss Rush

赛博朋克风格弹幕射击游戏，HTML5 Canvas 单文件实现。

[![Play Now](https://img.shields.io/badge/Play%20Now-Launch-brightgreen?style=flat&logo=gamepad)](https://cheesestudio.github.io/)

> ✅ **官方部署地址**: https://cheesestudio.github.io
> 🎮 现在支持 DG-LAB 郊狼脉冲主机联机反馈！

## 游戏特色

- **3 BOSS × 3 形态 = 9 关卡**：VOID / PULSE / CORE 三大BOSS
- **13 种弹幕模式**：laser / ring / spiral / wave / wall / scatter / beam / homing / rain / corridor / pincer / predict / helix_spread
- **BOSS 技能系统**：瞬移 / 召唤 / 护盾 / 冲锋 / 克隆 / 传送门 / 黑洞 / 白洞 / 激光 / 幻影
- **60FPS 流畅运行**：帧时间限制、定时器清理、子弹数量上限优化
- **本地积分存储**：localStorage 记录最高分
- **霓虹赛博朋克视觉**：深色网格背景 + 流星 + 粒子特效 + 屏幕震动 + 闪光
- ✅ **郊狼脉冲主机支持**：游戏事件实时反馈
- ✅ **多人联机支持**：通过 WebSocket 中继多人同步游戏

## 操作方式

| 按键 | 功能 |
|------|------|
| `W` / `↑` | 向上移动 |
| `S` / `↓` | 向下移动 |
| `A` / `←` | 向左移动 |
| `D` / `→` | 向右移动 |
| `Space` / `Enter` | 开始游戏 / 重新开始 |
| `Escape` | 暂停/继续 |
| `K` | 开发者模式：无敌开关 |

---

## 🐺 DG-LAB 郊狼使用说明

✅ **游戏现已完整支持 郊狼3.0 脉冲主机 SOCKET 协议**

### 使用步骤：

1.  打开 DG-LAB APP → 进入「SOCKET 控制」功能
2.  在游戏主页点击「郊狼连接」按钮
3.  用 APP 扫描游戏中显示的二维码完成配对
4.  开始游戏，游戏事件会自动触发脉冲反馈

### 映射的游戏事件：

| 游戏事件 | 脉冲效果 |
|---|---|
| 玩家中弹 | 强冲击脉冲 |
| 吃到道具 | 轻柔双脉冲 |
| Boss 放大招 | 递增警告脉冲 |
| 游戏结束 | 长渐变脉冲 |

> ⚠️ **安全提示**：请从最低强度开始测试，永远不要超过你能承受的范围。内置 30ms 脉冲间隔保护。

---

## 👥 多人联机说明

通过 `relay.js` 中继服务器支持多人联机同步游戏：

### 搭建中继服务器：

```bash
node relay.js
```

默认监听端口 `9999`，支持多客户端连接和消息转发。

### 联机步骤：

1.  主机启动中继服务器
2.  所有玩家在游戏中输入服务器地址
3.  任意玩家开始游戏会同步到所有连接的客户端
4.  游戏状态、得分、BOSS 血量会实时同步

---

## 运行方式

### 方法一：直接在线玩（推荐）
访问 https://cheesestudio.github.io

### 方法二：本地运行
直接在浏览器中打开 `bullet-hell.html` 文件

### 方法三：本地服务器
```bash
python -m http.server 8000
# 访问 http://localhost:8000
```

### 方法四：运行带中继服务
```bash
npm install ws
node relay.js
```

## 游戏系统

- **Power 系统**：收集红色 P 道具提升火力（最高4级）
- **擦弹系统**：子弹擦身而过可获得额外分数
- **连击系统**：连续击中BOSS获得分数加成
- **道具类型**：
  - 🔴 P - 提升火力
  - 🟡 S - 500 分数
  - 🟢 B - 获得额外生命

## 修复日志

✅ **2026-04-22 郊狼集成**
- ✅ 添加 DG-LAB SOCKET v2 协议完整支持
- ✅ 游戏事件脉冲映射
- ✅ 30ms 安全冷却保护
- ✅ 连接状态指示
- ✅ 添加 WebSocket 多人中继服务器

✅ **2026-04-21 代码审计修复**
- 🔧 限制最大帧时间 0.05s，避免后台卡顿导致子弹瞬移
- 🔧 添加安全定时器追踪，游戏重启时清理所有超时回调
- 🔧 限制最大子弹数量 200 颗，防止后期帧率崩溃
- 🔧 修复 4 处悬挂内存泄漏
- 🔧 修复 Escape 暂停键状态重置 bug

## 技术栈

- HTML5 Canvas
- Vanilla JavaScript
- 无框架依赖
- 100% 客户端运行
- 原生 WebSocket 协议

## License

MIT
