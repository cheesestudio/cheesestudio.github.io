# Bullet Hell Boss Rush - Game Design Spec

## Project Overview

- **Project Name:** Bullet Hell Boss Rush
- **Type:** 2D Shooter / BOSS Rush Browser Game
- **Summary:** 赛博朋克风格的BOSS Rush弹幕游戏，玩家控制飞机击败3个多形态BOSS
- **Platform:** Single HTML file, browser-based, localStorage score

---

## Gameplay

### Core Loop
- Player aircraft moves in bottom 1/4 of screen
- Auto-fire main weapon every 0.2s
- Defeat BOSS phases to progress
- 3 phases per BOSS = BOSS defeated
- 3 lives = Game Over

### Difficulty Levels
- 3 BOSSes × 3 phases = 9 stages total
- 3 difficulty stars per BOSS (easy/medium/hard)

### Controls
- Arrow keys / WASD: Move
- Auto-fire (no manual fire key needed)

---

## Visual Design

### Color Palette
- Background: `#0a0a1a` (deep navy black)
- Grid lines: `#1a1a3a` (subtle)
- Player: White triangle `#ffffff` + cyan tail flame `#00ffff`
- Bullets: Glow effect with colors (blue=normal, red=warning)
- BOSS geometric shapes with shift glow colors per phase

### UI Elements
- Top-left: BOSS health bar
- Top-right: Lives (❤❤❤)
- Bottom: Score display
- Game Over screen with final score + restart option

### Visual Effects
- Grid background with moving lines
- Slow-falling star dust particles
- Bullet glow (canvas shadowBlur)
- Player tail flame particles
- Explosion particles on BOSS hit
- Screen flash on BOSS phase transition

---

## BOSS Design

### BOSS 1: VOID
| Phase | Shape | Bullet Pattern |
|-------|-------|--------------|
| 1 | Triangle | Laser array |
| 2 | Diamond | Expanding ring |
| 3 | Hexagon | Spiral |

### BOSS 2: PULSE
| Phase | Shape | Bullet Pattern |
|-------|-------|--------------|
| 1 | Circle | Concentric waves |
| 2 | Ring | Reflection wall |
| 3 | Polygon | Random scatter |

### BOSS 3: CORE
| Phase | Shape | Bullet Pattern |
|-------|-------|--------------|
| 1 | Square | Laser beam |
| 2 | Diamond | Homing bullets |
| 3 | Star | Full-screen rain |

---

## Technical Implementation

### Technology
- Single HTML file
- Native Canvas 2D API
- Vanilla JavaScript (no frameworks)
- localStorage for high score

### Architecture
- Game loop with requestAnimationFrame
- Entity-component system:
  - Player class
  - BOSS base class + phase variants
  - Bullet class (player & enemy)
  - Particle system
  - Collision detection (circle-circle)

### Performance Targets
- 60 FPS
- Max 500 bullets on screen
- Efficient bullet cleanup (off-screen culling)

---

## Audio (Optional)

- Background: 8-bit electronic (CDN or Web Audio API synthesis)
- SFX: Shoot, hit, explode (Web Audio API beeps)

---

## Acceptance Criteria

1. ✅ Single HTML file opens in browser
2. ✅ Player moves and auto-shoots
3. ✅ 3 BOSSes with 3 phases each
4. ✅ Each phase has unique bullet pattern
5. ✅ Health bar decreases on hit
6. ✅ Phase transition when health = 0
7. ✅ Score accumulates
8. ✅ Lives system (3 lives)
9. ✅ Game Over screen with restart
10. ✅ High score persisted in localStorage
11. ✅ Cyberpunk/neon visual style
12. ✅ Smooth 60 FPS gameplay