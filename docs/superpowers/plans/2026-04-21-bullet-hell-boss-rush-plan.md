# Bullet Hell Boss Rush Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 赛博朋克风格BOSS Rush弹幕游戏，单HTML文件，支持3个多形态BOSS，localStorage积分

**Architecture:** 单Canvas游戏循环，实体-组件系统，玩家/BOSS/子弹/粒子分离，高效碰撞检测

**Tech Stack:** HTML5 Canvas + Vanilla JavaScript，无框架依赖

---

## File Structure

```
OMO/
└── bullet-hell.html    # 整个游戏（单文件）
```

---

## Task 1: 游戏骨架与循环

**Files:**
- Create: `bullet-hell.html`

- [ ] **Step 1: 基础HTML结构 + Canvas**

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bullet Hell Boss Rush</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #0a0a1a;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      overflow: hidden;
      font-family: 'Courier New', monospace;
    }
    canvas {
      border: 2px solid #1a1a3a;
      box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
    }
  </style>
</head>
<body>
  <canvas id="game" width="480" height="640"></canvas>
  <script>
    const canvas = document.getElementById('game');
    const ctx = canvas.getContext('2d');
  </script>
</body>
</html>
```

- [ ] **Step 2: 游戏循环 + 状态机**

```javascript
// Game states
const STATE = { MENU: 0, PLAYING: 1, TRANSITION: 2, GAMEOVER: 3 };
let gameState = STATE.MENU;
let lastTime = 0;

function gameLoop(timestamp) {
  const dt = (timestamp - lastTime) / 1000;
  lastTime = timestamp;

  // Update
  switch(gameState) {
    case STATE.PLAYING: update(dt); break;
    case STATE.MENU: updateMenu(dt); break;
    case STATE.GAMEOVER: updateGameOver(dt); break;
  }

  // Render
  render();

  requestAnimationFrame(gameLoop);
}

function update(dt) { /* placeholder */ }
function render() {
  ctx.fillStyle = '#0a0a1a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

requestAnimationFrame(gameLoop);
```

- [ ] **Step 3: 测试运行**

Open: `bullet-hell.html` in browser
Expected: 深色背景Canvas，无报错

---

## Task 2: 输入系统 + 玩家

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 输入处理**

```javascript
// Input
const keys = {};
window.addEventListener('keydown', e => keys[e.key] = true);
window.addEventListener('keyup', e => keys[e.key] = false);

function isDown(key) {
  return keys[key] || keys[key.toLowerCase()];
}
```

- [ ] **Step 2: 玩家类**

```javascript
// Player
const player = {
  x: canvas.width / 2,
  y: canvas.height - 80,
  w: 24,
  h: 32,
  speed: 200,
  shootCooldown: 0,
  shootRate: 0.2,
  invincible: 0,
  lives: 3,
  score: 0
};

function updatePlayer(dt) {
  // Movement
  if (isDown('ArrowLeft') || isDown('a')) player.x -= player.speed * dt;
  if (isDown('ArrowRight') || isDown('d')) player.x += player.speed * dt;
  if (isDown('ArrowUp') || isDown('w')) player.y -= player.speed * dt;
  if (isDown('ArrowDown') || isDown('s')) player.y += player.speed * dt;

  // Clamp to bounds
  player.x = Math.max(player.w/2, Math.min(canvas.width - player.w/2, player.x));
  player.y = Math.max(player.h/2, Math.min(canvas.height - player.h/2, player.y));

  // Auto-fire
  player.shootCooldown -= dt;
  if (player.shootCooldown <= 0) {
    shootBullet(player.x, player.y - 16, -400, 'player');
    player.shootCooldown = player.shootRate;
  }

  // Invincibility frame
  if (player.invincible > 0) player.invincible -= dt;
}
```

- [ ] **Step 3: 渲染玩家**

```javascript
function renderPlayer() {
  if (player.invincible > 0 && Math.floor(player.invincible * 10) % 2 === 0) return;

  ctx.save();
  ctx.translate(player.x, player.y);

  // Glow
  ctx.shadowBlur = 15;
  ctx.shadowColor = '#00ffff';

  // Triangle
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.moveTo(0, -player.h/2);
  ctx.lineTo(-player.w/2, player.h/2);
  ctx.lineTo(player.w/2, player.h/2);
  ctx.closePath();
  ctx.fill();

  // Tail flame
  ctx.fillStyle = '#00ffff';
  ctx.beginPath();
  ctx.moveTo(-4, player.h/2);
  ctx.lineTo(4, player.h/2);
  ctx.lineTo(0, player.h/2 + 8 + Math.random() * 4);
  ctx.closePath();
  ctx.fill();

  ctx.restore();
}
```

- [ ] **Step 4: 测试运行**

Expected: 白色三角形，可键盘控制移动，尾部火焰效果

---

## Task 3: 子弹系统

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 子弹数组 + 生成**

```javascript
const bullets = [];
const ENEMY_BULLETS = [];

function shootBullet(x, y, vy, owner, type = 'normal') {
  bullets.push({
    x, y,
    vx: 0,
    vy,
    r: 4,
    owner,
    type,
    color: owner === 'player' ? '#00ffff' : '#ff4444'
  });
}
```

- [ ] **Step 2: 更新子弹 + 清理**

```javascript
function updateBullets(dt) {
  for (let i = bullets.length - 1; i >= 0; i--) {
    const b = bullets[i];
    b.x += b.vx * dt;
    b.y += b.vy * dt;

    // Off-screen cleanup
    if (b.y < -20 || b.y > canvas.height + 20 ||
        b.x < -20 || b.x > canvas.width + 20) {
      bullets.splice(i, 1);
    }
  }
}
```

- [ ] **Step 3: 渲染子弹（带Glow）**

```javascript
function renderBullets() {
  for (const b of bullets) {
    ctx.save();
    ctx.shadowBlur = 10;
    ctx.shadowColor = b.color;
    ctx.fillStyle = b.color;
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}
```

- [ ] **Step 4: 测试运行**

Expected: 青色子弹从玩家射出，带发光效果

---

## Task 4: 碰撞检测

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 圆形碰撞**

```javascript
function circleCollision(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  const dist = Math.sqrt(dx*dx + dy*dy);
  return dist < (a.r + b.r);
}
```

- [ ] **Step 2: 玩家击中检测**

```javascript
function checkPlayerHit() {
  if (player.invincible > 0) return;

  for (const b of bullets) {
    if (b.owner !== 'player' && circleCollision(player, b)) {
      // Remove bullet
      const idx = bullets.indexOf(b);
      if (idx > -1) bullets.splice(idx, 1);

      // Damage
      lives--;
      player.invincible = 2;

      if (lives <= 0) {
        gameState = STATE.GAMEOVER;
      }
      return;
    }
  }
}
```

- [ ] **Step 3: BOSS击中检测**

```后期Task 6中添加BOSS后再调用**

---

## Task 5: BOSS基础框架

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: BOSS类结构**

```javascript
const boss = {
  x: canvas.width / 2,
  y: 100,
  r: 30,
  hp: 100,
  maxHp: 100,
  phase: 0,
  cooldown: 0,
  pattern: 0,
  active: false
};

const BOSS_PHASES = [
  // VOID - Phase 1
  { name: 'VOID', hp: 100, color: '#ff00ff', pattern: 'laser' },
  { name: 'VOID', hp: 100, color: '#ff00ff', pattern: 'ring' },
  { name: 'VOID', hp: 100, color: '#ff00ff', pattern: 'spiral' },
  // PULSE - Phase 2
  { name: 'PULSE', hp: 120, color: '#00ff00', pattern: 'wave' },
  { name: 'PULSE', hp: 120, color: '#00ff00', pattern: 'wall' },
  { name: 'PULSE', hp: 120, color: '#00ff00', pattern: 'scatter' },
  // CORE - Phase 3
  { name: 'CORE', hp: 150, color: '#ff8800', pattern: 'beam' },
  { name: 'CORE', hp: 150, color: '#ff8800', pattern: 'homing' },
  { name: 'CORE', hp: 150, color: '#ff8800', pattern: 'rain' }
];

let bossIndex = 0;

function startBoss() {
  const config = BOSS_PHASES[bossIndex];
  boss.hp = boss.maxHp = config.hp;
  boss.phase = bossIndex % 3;
  boss.pattern = config.pattern;
  boss.color = config.color;
  boss.active = true;
  boss.x = canvas.width / 2;
  boss.y = 100;
}
```

- [ ] **Step 2: BOSS移动 + 渲染**

```javascript
function updateBoss(dt) {
  if (!boss.active) return;

  // Simple horizontal movement
  boss.x += Math.sin(Date.now() / 1000) * 50 * dt;

  boss.cooldown -= dt;
  if (boss.cooldown <= 0) {
    fireBossPattern();
    boss.cooldown = 0.5;
  }
}

function renderBoss() {
  if (!boss.active) return;

  ctx.save();
  ctx.translate(boss.x, boss.y);
  ctx.shadowBlur = 20;
  ctx.shadowColor = boss.color;

  // Shape based on phase
  ctx.fillStyle = boss.color;
  ctx.beginPath();
  const sides = 3 + boss.phase;
  for (let i = 0; i < sides; i++) {
    const angle = (i / sides) * Math.PI * 2 - Math.PI / 2;
    const px = Math.cos(angle) * boss.r;
    const py = Math.sin(angle) * boss.r;
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}
```

- [ ] **Step 3: BOSS血条UI**

```javascript
function renderUI() {
  // Lives
  ctx.fillStyle = '#ff4444';
  ctx.font = '20px monospace';
  for (let i = 0; i < lives; i++) {
    ctx.fillText('❤', 10 + i * 24, 30);
  }

  // Boss health bar
  if (boss.active) {
    ctx.fillStyle = '#333';
    ctx.fillRect(canvas.width - 160, 10, 150, 15);
    ctx.fillStyle = boss.color;
    ctx.fillRect(canvas.width - 160, 10, 150 * (boss.hp / boss.maxHp), 15);
    ctx.strokeStyle = '#666';
    ctx.strokeRect(canvas.width - 160, 10, 150, 15);
  }

  // Score
  ctx.fillStyle = '#fff';
  ctx.textAlign = 'right';
  ctx.fillText(`SCORE: ${score}`, canvas.width - 10, canvas.height - 10);
  ctx.textAlign = 'left';
}
```

- [ ] **Step 4: 测试运行**

Expected: BOSS显示，血条显示，UI元素

---

## Task 6: BOSS弹幕模式

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 弹幕模式函数**

```javascript
function fireBossPattern() {
  const p = boss.pattern;

  if (p === 'laser') {
    // Laser array
    for (let i = -2; i <= 2; i++) {
      bullets.push({
        x: boss.x + i * 30,
        y: boss.y + 20,
        vx: i * 20,
        vy: 150,
        r: 6,
        owner: 'boss',
        color: '#ff00ff'
      });
    }
  }
  else if (p === 'ring') {
    // Expanding ring
    for (let i = 0; i < 16; i++) {
      const angle = (i / 16) * Math.PI * 2;
      bullets.push({
        x: boss.x,
        y: boss.y,
        vx: Math.cos(angle) * 120,
        vy: Math.sin(angle) * 120,
        r: 5,
        owner: 'boss',
        color: '#ff00ff'
      });
    }
  }
  else if (p === 'spiral') {
    // Spiral
    const angle = Date.now() / 200;
    bullets.push({
      x: boss.x,
      y: boss.y,
      vx: Math.cos(angle) * 100,
      vy: Math.sin(angle) * 100,
      r: 4,
      owner: 'boss',
      color: '#ff00ff'
    });
    bullets.push({
      x: boss.x,
      y: boss.y,
      vx: Math.cos(angle + Math.PI) * 100,
      vy: Math.sin(angle + Math.PI) * 100,
      r: 4,
      owner: 'boss',
      color: '#ff00ff'
    });
  }
  else if (p === 'wave') {
    // Concentric waves
    const t = Date.now() / 1000;
    for (let i = 0; i < 8; i++) {
      const r = 30 + (t * 50 % 100);
      const angle = (i / 8) * Math.PI * 2;
      bullets.push({
        x: boss.x + Math.cos(angle) * r,
        y: boss.y + Math.sin(angle) * r,
        vx: Math.cos(angle) * 80,
        vy: Math.sin(angle) * 80 + 50,
        r: 5,
        owner: 'boss',
        color: '#00ff00'
      });
    }
  }
  else if (p === 'wall') {
    // Wall
    for (let i = 0; i < 8; i++) {
      bullets.push({
        x: boss.x - 60 + i * 20,
        y: boss.y + 20,
        vx: 0,
        vy: 100,
        r: 5,
        owner: 'boss',
        color: '#00ff00'
      });
    }
  }
  else if (p === 'scatter') {
    // Random scatter
    for (let i = 0; i < 5; i++) {
      bullets.push({
        x: boss.x + (Math.random() - 0.5) * 100,
        y: boss.y + 20,
        vx: (Math.random() - 0.5) * 150,
        vy: 80 + Math.random() * 50,
        r: 4,
        owner: 'boss',
        color: '#00ff00'
      });
    }
  }
  else if (p === 'beam') {
    // Aim at player
    const dx = player.x - boss.x;
    const dy = player.y - boss.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    bullets.push({
      x: boss.x,
      y: boss.y,
      vx: (dx/dist) * 200,
      vy: (dy/dist) * 200,
      r: 6,
      owner: 'boss',
      color: '#ff8800'
    });
  }
  else if (p === 'homing') {
    // Slightly homing
    const dx = player.x - boss.x;
    const dy = player.y - boss.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    bullets.push({
      x: boss.x,
      y: boss.y,
      vx: (dx/dist) * 100 + (Math.random() - 0.5) * 50,
      vy: (dx/dist) * 100 + (Math.random() - 0.5) * 50,
      r: 5,
      owner: 'boss',
      color: '#ff8800'
    });
  }
  else if (p === 'rain') {
    // Full screen rain
    for (let i = 0; i < 5; i++) {
      bullets.push({
        x: Math.random() * canvas.width,
        y: -10,
        vx: (Math.random() - 0.5) * 30,
        vy: 100 + Math.random() * 50,
        r: 4,
        owner: 'boss',
        color: '#ff8800'
      });
    }
  }
}
```

- [ ] **Step 2: BOSS受伤 + 阶段转换**

```javascript
function checkBossHit() {
  if (!boss.active) return;

  for (let i = bullets.length - 1; i >= 0; i--) {
    const b = bullets[i];
    if (b.owner === 'player' && circleCollision(b, boss)) {
      bullets.splice(i, 1);
      boss.hp -= 10;
      score += 10;

      if (boss.hp <= 0) {
        // Phase transition
        bossIndex++;
        if (bossIndex >= BOSS_PHASES.length) {
          // Victory!
          boss.active = false;
        } else {
          // Next phase
          startBoss();
        }
      }
    }
  }
}
```

- [ ] **Step 3: 测试运行**

Expected: 各种弹幕模式正常工作，阶段转换正常

---

## Task 7: 粒子效果 + 背景

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 粒子系统**

```javascript
const particles = [];

function spawnParticle(x, y, color) {
  for (let i = 0; i < 5; i++) {
    particles.push({
      x, y,
      vx: (Math.random() - 0.5) * 100,
      vy: (Math.random() - 0.5) * 100,
      life: 0.5,
      color
    });
  }
}

function updateParticles(dt) {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.x += p.vx * dt;
    p.y += p.vy * dt;
    p.life -= dt;
    if (p.life <= 0) particles.splice(i, 1);
  }
}

function renderParticles() {
  for (const p of particles) {
    ctx.globalAlpha = p.life * 2;
    ctx.fillStyle = p.color;
    ctx.fillRect(p.x, p.y, 3, 3);
  }
  ctx.globalAlpha = 1;
}
```

- [ ] **Step 2: 背景网格 + 星尘**

```javascript
const stars = [];
for (let i = 0; i < 50; i++) {
  stars.push({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    s: Math.random() * 2 + 1,
    s: Math.random() * 20 + 10
  });
}

function renderBackground() {
  // Grid
  ctx.strokeStyle = '#1a1a3a';
  ctx.lineWidth = 1;
  for (let x = 0; x < canvas.width; x += 40) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }
  for (let y = 0; y < canvas.height; y += 40) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }

  // Stars
  for (const s of stars) {
    s.y += s.speed * 0.016;
    if (s.y > canvas.height) s.y = 0;
    ctx.fillStyle = `rgba(255,255,255,${0.3 + s.s/5})`;
    ctx.fillRect(s.x, s.y, s.s, s.s);
  }
}
```

- [ ] **Step 3: 更新render函数**

```javascript
function render() {
  ctx.fillStyle = '#0a0a1a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  renderBackground();
  renderParticles();
  renderBullets();
  if (boss.active) renderBoss();
  renderPlayer();
  renderUI();
}
```

- [ ] **Step 4: 测试运行**

Expected: 网格背景下落，粒子效果

---

## Task 8: 游戏状态 + 积分

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 开始/结束画面**

```javascript
let score = 0;
let highScore = localStorage.getItem('bulletHellHigh') || 0;

function updateMenu(dt) {
  if (isDown(' ') || isDown('Enter')) {
    startGame();
  }
}

function updateGameOver(dt) {
  if (isDown(' ') || isDown('Enter')) {
    startGame();
  }
}

function startGame() {
  score = 0;
  lives = 3;
  bossIndex = 0;
  startBoss();
  gameState = STATE.PLAYING;
}

function renderMenu() {
  ctx.fillStyle = '#fff';
  ctx.textAlign = 'center';
  ctx.font = '30px monospace';
  ctx.fillText('BULLET HELL', canvas.width/2, canvas.height/2 - 40);
  ctx.font = '16px monospace';
  ctx.fillText('BOSS RUSH', canvas.width/2, canvas.height/2 - 10);
  ctx.fillStyle = '#00ffff';
  ctx.fillText('PRESS SPACE TO START', canvas.width/2, canvas.height/2 + 40);
  ctx.fillStyle = '#888';
  ctx.font = '12px monospace';
  ctx.fillText(`HIGH SCORE: ${highScore}`, canvas.width/2, canvas.height/2 + 80);
  ctx.textAlign = 'left';
}

function renderGameOver() {
  ctx.fillStyle = 'rgba(0,0,0,0.7)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#ff4444';
  ctx.textAlign = 'center';
  ctx.font = '30px monospace';
  ctx.fillText('GAME OVER', canvas.width/2, canvas.height/2 - 20);
  ctx.fillStyle = '#fff';
  ctx.font = '20px monospace';
  ctx.fillText(`SCORE: ${score}`, canvas.width/2, canvas.height/2 + 20);
  if (score > highScore) {
    localStorage.setItem('bulletHellHigh', score);
    highScore = score;
    ctx.fillStyle = '#00ffff';
    ctx.fillText('NEW HIGH SCORE!', canvas.width/2, canvas.height/2 + 50);
  }
  ctx.fillStyle = '#888';
  ctx.font = '14px monospace';
  ctx.fillText('PRESS SPACE TO RESTART', canvas.width/2, canvas.height/2 + 90);
  ctx.textAlign = 'left';
}
```

- [ ] **Step 2: 修改render + update**

```javascript
function render() {
  ctx.fillStyle = '#0a0a1a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  renderBackground();

  switch(gameState) {
    case STATE.MENU:
      renderMenu();
      break;
    case STATE.PLAYING:
      renderParticles();
      renderBullets();
      if (boss.active) renderBoss();
      renderPlayer();
      renderUI();
      break;
    case STATE.GAMEOVER:
      renderParticles();
      renderBullets();
      renderGameOver();
      break;
  }
}

function update(dt) {
  switch(gameState) {
    case STATE.MENU:
      updateMenu(dt);
      break;
    case STATE.PLAYING:
      updatePlayer(dt);
      updateBullets(dt);
      updateBoss(dt);
      updateParticles(dt);
      checkPlayerHit();
      checkBossHit();
      break;
    case STATE.GAMEOVER:
      updateGameOver(dt);
      break;
  }
}
```

- [ ] **Step 3: 测试运行**

Expected: 开始菜单，SPACE开始，游戏进行，Game Over，high score保存

---

## Task 9: 音���（可选）

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: Web Audio合成**

```javascript
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playSound(type) {
  if (audioCtx.state === 'suspended') audioCtx.resume();

  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.connect(gain);
  gain.connect(audioCtx.destination);

  if (type === 'shoot') {
    osc.frequency.value = 880;
    osc.type = 'square';
    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.1);
  }
  else if (type === 'hit') {
    osc.frequency.value = 220;
    osc.type = 'sawtooth';
    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.2);
  }
}
```

- [ ] **Step 2: 在事件触发处调用**

```javascript
// In shootBullet: playSound('shoot');
// In player hit: playSound('hit');
// In boss hit: playSound('hit');
```

---

## Task 10: 最终测试

**Files:**
- Modify: `bullet-hell.html`

- [ ] **验证清单**

1. [ ] 单HTML文件在浏览器打开
2. [ ] 玩家移动 + 自动射击
3. [ ] 3个BOSS x 3形态 = 9关卡
4. [ ] 每形态独特弹幕模式
5. [ ] 血条递减
6. [ ] 形态转换
7. [ ] 分数累计
8. [ ] 3条命系统
9. [ ] Game Over画面 + 重开
10. [ ] high score存localStorage
11. [ ] 赛博朋克霓虹视觉
12. [ ] 60FPS流畅运行

---