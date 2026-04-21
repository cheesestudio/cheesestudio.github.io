# Bullet Hell Boss Rush

赛博朋克风格弹幕射击游戏，HTML5 Canvas 单文件实现。

## 游戏特色

- **3 BOSS × 3 形态 = 9 关卡**：VOID / PULSE / CORE 三大BOSS
- **9 种弹幕模式**：laser / ring / spiral / wave / wall / scatter / beam / homing / rain
- **60FPS 流畅运行**：requestAnimationFrame 游戏循环
- **本地积分存储**：localStorage 记录最高分
- **霓虹赛博朋克视觉**：深色网格背景 + 流星 + 粒子特效

## 操作方式

| 按键 | 功能 |
|------|------|
| `W` / `↑` | 向上移动 |
| `S` / `↓` | 向下移动 |
| `A` / `←` | 向左移动 |
| `D` / `→` | 向右移动 |
| `Space` / `Enter` | 开始游戏 / 重新开始 |
| `Escape` | 暂停/继续 |

## 运行方式

### 方法一：直接打开
直接在浏览器中打开 `bullet-hell.html` 文件

### 方法二：本地服务器
```bash
# Python 3
python -m http.server 8000

# 访问 http://localhost:8000
```

### 方法三：VS Code Live Server
1. 安装 VS Code 扩展 "Live Server"
2. 右键点击 `bullet-hell.html` → "Open with Live Server"

## 游戏系统

- **Power 系统**：收集红色 P 道具提升火力（最高4级）
- **擦弹系统**：子弹擦身而过可获得额外分数
- **道具类型**：
  - 🔴 P - 提升火力
  - 🟡 S - 500 分数
  - 🟢 B - 获得额外生命

## 游戏截图

```
BULLET HELL
BOSS RUSH
PRESS SPACE TO START
```

## 技术栈

- HTML5 Canvas
- Vanilla JavaScript (无框架依赖)
- Web Audio API (可选音效)

## License

MIT
