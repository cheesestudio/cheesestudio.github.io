# Bullet Hell Boss Rush

赛博朋克风格弹幕射击游戏，HTML5 Canvas 单文件实现。

[![Play Now](https://img.shields.io/badge/Play%20Now-Launch-brightgreen?style=flat&logo=gamepad)](https://cheesestudio.github.io/bullet-hell-game/)

> 💡 点击上方按钮直接在浏览器玩！或访问 https://cheesestudio.github.io/bullet-hell-game/

## 游戏特色

- **3 BOSS × 3 形态 = 9 关卡**：VOID / PULSE / CORE 三大BOSS
- **13 种弹幕模式**：laser / ring / spiral / wave / wall / scatter / beam / homing / rain / corridor / pincer / predict / helix_spread
- **BOSS 技能系统**：瞬移 / 召唤 / 护盾 / 冲锋 / 克隆 / 传送门 / 黑洞 / 白洞 / 激光 / 幻影
- **60FPS 流畅运行**：帧时间限制、定时器清理、子弹数量上限优化
- **本地积分存储**：localStorage 记录最高分
- **霓虹赛博朋克视觉**：深色网格背景 + 流星 + 粒子特效 + 屏幕震动 + 闪光

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

## 运行方式

### 方法一：直接打开（推荐）
直接在浏览器中打开 `bullet-hell.html` 文件

### 方法二：GitHub Pages 在线玩
访问 https://cheesestudio.github.io/bullet-hell-game/

### 方法三：本地服务器
```bash
python -m http.server 8000
# 访问 http://localhost:8000
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

## License

MIT