# Better UI Effects Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现4个UI特效 - BOSS死亡爆炸+屏幕震动、动态血条、得分上浮、Combo系统

**Architecture:** 在现有bullet-hell.html基础上添加新功能模块

**Tech Stack:** Vanilla JavaScript, Canvas 2D API

---

## Task 1: 屏幕震动系统

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加震动状态变量**

```javascript
// Screen shake
let screenShake = { x: 0, y: 0, intensity: 0, time: 0 };

function triggerScreenShake(intensity = 3, duration = 0.1) {
  screenShake.intensity = intensity;
  screenShake.time = duration;
}
```

- [ ] **Step 2: 更新震动逻辑**

```javascript
function updateScreenShake(dt) {
  if (screenShake.time > 0) {
    screenShake.time -= dt;
    screenShake.x = (Math.random() - 0.5) * screenShake.intensity * 2;
    screenShake.y = (Math.random() - 0.5) * screenShake.intensity * 2;
  } else {
    screenShake.x = 0;
    screenShake.y = 0;
  }
}
```

- [ ] **Step 3: 应用震动到渲染**

在render()开头添加：
```javascript
ctx.save();
ctx.translate(screenShake.x, screenShake.y);
// ... render game ...
ctx.restore();
```

- [ ] **Step 4: 在update()中调用updateScreenShake(dt)**

---

## Task 2: BOSS死亡爆炸粒子

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加爆炸粒子数组**

```javascript
const explosionParticles = [];

function spawnExplosion(x, y, color, count = 30) {
  for (let i = 0; i < count; i++) {
    const angle = (Math.PI * 2 / count) * i + Math.random() * 0.5;
    const speed = 100 + Math.random() * 200;
    explosionParticles.push({
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      r: 3 + Math.random() * 4,
      life: 0.5 + Math.random() * 0.5,
      color
    });
  }
}
```

- [ ] **Step 2: 更新爆炸粒子**

```javascript
function updateExplosionParticles(dt) {
  for (let i = explosionParticles.length - 1; i >= 0; i--) {
    const p = explosionParticles[i];
    p.x += p.vx * dt;
    p.y += p.vy * dt;
    p.life -= dt;
    p.r *= 0.98;
    if (p.life <= 0) explosionParticles.splice(i, 1);
  }
}
```

- [ ] **Step 3: 渲染爆炸粒子**

```javascript
function renderExplosionParticles() {
  for (const p of explosionParticles) {
    ctx.save();
    ctx.globalAlpha = p.life;
    ctx.shadowBlur = 15;
    ctx.shadowColor = p.color;
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}
```

- [ ] **Step 4: BOSS死亡时触发**

在checkBossHit()中，当boss.hp <= 0时：
```javascript
spawnExplosion(boss.x, boss.y, boss.color, 40);
triggerScreenShake(5, 0.15);
```

---

## Task 3: 动态血条

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加显示血量变量**

```javascript
let displayHp = 100;
```

- [ ] **Step 2: 更新显示血量插值**

```javascript
function updateDisplayHp(dt) {
  const diff = boss.hp - displayHp;
  if (Math.abs(diff) > 0.5) {
    displayHp += diff * 10 * dt;
  } else {
    displayHp = boss.hp;
  }
}
```

- [ ] **Step 3: 修改血条渲染**

```javascript
// Boss health bar with animation
if (boss.active) {
  ctx.fillStyle = '#222';
  ctx.fillRect(canvas.width - 170, 10, 160, 20);
  const hpPercent = Math.max(0, displayHp / boss.maxHp);
  ctx.fillStyle = boss.color;
  ctx.fillRect(canvas.width - 170, 10, 160 * hpPercent, 20);
  ctx.strokeStyle = boss.color;
  ctx.lineWidth = 2;
  ctx.strokeRect(canvas.width - 170, 10, 160, 20);
}
```

- [ ] **Step 4: 在update()中调用updateDisplayHp(dt)，渲染时用displayHp**

---

## Task 4: 得分上浮动画

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加分数弹出数组**

```javascript
const scorePopups = [];

function spawnScorePopup(x, y, value) {
  scorePopups.push({
    x, y,
    value,
    vy: -80,
    life: 0.6,
    scale: 1
  });
}
```

- [ ] **Step 2: 更新分数弹出**

```javascript
function updateScorePopups(dt) {
  for (let i = scorePopups.length - 1; i >= 0; i--) {
    const p = scorePopups[i];
    p.y += p.vy * dt;
    p.life -= dt;
    p.scale = 1 + (0.6 - p.life) * 0.5;
    if (p.life <= 0) scorePopups.splice(i, 1);
  }
}
```

- [ ] **Step 3: 渲染分数弹出**

```javascript
function renderScorePopups() {
  for (const p of scorePopups) {
    ctx.save();
    ctx.globalAlpha = Math.min(1, p.life * 2);
    ctx.fillStyle = '#ffff00';
    ctx.font = `bold ${16 * p.scale}px monospace`;
    ctx.textAlign = 'center';
    ctx.fillText(`+${p.value}`, p.x, p.y);
    ctx.restore();
  }
}
```

- [ ] **Step 4: 击中BOSS时触发**

在checkBossHit()中，score += 10后添加：
```javascript
spawnScorePopup(boss.x, boss.y - 30, 10);
```

- [ ] **Step 5: 添加到update和render**

---

## Task 5: Combo系统

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: 添加Combo变量**

```javascript
let combo = 0;
let comboTimer = 0;
const COMBO_TIME = 2.0;
```

- [ ] **Step 2: 更新Combo逻辑**

```javascript
function updateCombo(dt) {
  if (comboTimer > 0) {
    comboTimer -= dt;
    if (comboTimer <= 0) {
      combo = 0;
    }
  }
}

function addCombo() {
  combo++;
  comboTimer = COMBO_TIME;
}
```

- [ ] **Step 3: 渲染Combo显示**

```javascript
function renderCombo() {
  if (combo >= 2) {
    ctx.save();
    const scale = 1 + Math.min(combo * 0.1, 0.5);
    ctx.fillStyle = '#ff6600';
    ctx.font = `bold ${24 * scale}px monospace`;
    ctx.textAlign = 'center';
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#ff6600';
    ctx.fillText(`${combo}x COMBO!`, canvas.width / 2, 60);
    ctx.restore();
  }
}
```

- [ ] **Step 4: 击中时触发Combo**

在checkBossHit()中添加addCombo()

- [ ] **Step 5: 添加到update和render**

---

## Task 6: 整合所有更新

**Files:**
- Modify: `bullet-hell.html`

- [ ] **更新update()函数**

```javascript
function update(dt) {
  updateScreenShake(dt);
  updatePlayer(dt);
  updateBullets(dt);
  updateBoss(dt);
  updateParticles(dt);
  updateExplosionParticles(dt);
  updateDisplayHp(dt);
  updateScorePopups(dt);
  updateCombo(dt);
  checkPlayerHit();
  checkBossHit();
}
```

- [ ] **更新render()函数**

```javascript
function render() {
  ctx.save();
  ctx.translate(screenShake.x, screenShake.y);
  
  ctx.fillStyle = '#0a0a1a';
  ctx.fillRect(-10, -10, canvas.width + 20, canvas.height + 20);
  renderBackground();

  switch(gameState) {
    case STATE.MENU:
      renderMenu();
      break;
    case STATE.PLAYING:
      renderExplosionParticles();
      renderScorePopups();
      renderParticles();
      renderBullets();
      if (boss.active) renderBoss();
      renderPlayer();
      renderUI();
      renderCombo();
      break;
    case STATE.GAMEOVER:
      renderParticles();
      renderBullets();
      renderGameOver();
      break;
  }
  
  ctx.restore();
}
```

- [ ] **测试运行**

---