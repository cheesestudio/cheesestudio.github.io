# Bullet Hell Boss Rush

赛博朋克风格弹幕射击游戏，HTML5 Canvas 单文件实现。

## 游戏特色

- **3 BOSS × 3 形态 = 9 关卡**：VOID / PULSE / CORE 三大BOSS
- **9 种弹幕模式**：laser / ring / spiral / wave / wall / scatter / beam / homing / rain
- **60FPS 流畅运行**：requestAnimationFrame 游戏循环
- **本地积分存储**：localStorage 记录最高分
- **霓虹赛博朋克视觉**：深色网格背景 + 粒子特效

## 操作方式

| 按键 | 功能 |
|------|------|
| `W` / `↑` | 向上移动 |
| `S` / `↓` | 向下移动 |
| `A` / `←` | 向左移动 |
| `D` / `→` | 向右移动 |
| `Space` / `Enter` | 开始/重开 |

## 运行方式

直接在浏览器打开 `bullet-hell.html`，或：

```bash
# 本地服务
python -m http.server 8000
# 访问 http://localhost:8000
```

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