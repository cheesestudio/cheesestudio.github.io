# BOSS Behavior Patterns Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 10 BOSS special abilities, 4 tactical bullet patterns, and pattern-linked movement for enhanced gameplay depth.

**Architecture:** Extend existing bullet-hell.html with new ability system, update fireBossPattern(), add ability state management to boss object.

**Tech Stack:** Vanilla JavaScript, Canvas 2D API

---

## Task 1: Extend BOSS Object with Ability Properties

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: Add ability properties to boss object**

Find the boss object definition (around line 463) and add:
```javascript
// Ability state
abilityCooldowns: {
  teleport: 0,
  summon: 0,
  shield: 0,
  charge: 0,
  clone: 0,
  portal: 0,
  blackHole: 0,
  whiteHole: 0,
  laser: 0,
  phantom: 0
},
shieldHp: 0,
clones: [],
portals: [],
blackHoleActive: false,
whiteHoleActive: false,
laserActive: false,
laserAngle: 0,
phantomTankActive: false,
phantomTankX: 0,
abilityPhase: 0 // 0-9 for different abilities
```

- [ ] **Step 2: Add BOSS_ABILITIES config**

Add after BOSS_NAMES:
```javascript
const BOSS_ABILITIES = {
  TELEPORT: { cooldown: 15, triggerHp: 0.8, name: 'TELEPORT' },
  SUMMON: { cooldown: 30, triggerHp: 1.0, name: 'SUMMON' },
  SHIELD: { cooldown: 999, triggerHp: 0.6, name: 'SHIELD' },
  CHARGE: { cooldown: 20, triggerHp: 0.4, name: 'CHARGE' },
  CLONE: { cooldown: 25, triggerHp: 0.5, name: 'CLONE' },
  PORTAL: { cooldown: 45, triggerHp: 1.0, name: 'PORTAL' },
  BLACK_HOLE: { cooldown: 30, triggerHp: 0.3, name: 'BLACK_HOLE' },
  WHITE_HOLE: { cooldown: 25, triggerHp: 0.35, name: 'WHITE_HOLE' },
  LASER: { cooldown: 20, triggerHp: 0.25, name: 'LASER' },
  PHANTOM: { cooldown: 15, triggerHp: 0.2, name: 'PHANTOM' }
};
```

---

## Task 2: Add 4 New Tactical Bullet Patterns

**Files:**
- Modify: `bullet-hell.html` (extend fireBossPattern function)

- [ ] **Step 1: Add corridor pattern (safe passage)**

In fireBossPattern(), add:
```javascript
else if (p === 'corridor') {
  const gapX = player.x; // Gap follows player
  for (let i = 0; i < 12; i++) {
    const bx = (i / 12) * canvas.width;
    // Skip bullets near player position (create corridor)
    if (Math.abs(bx - gapX) > 80) {
      bullets.push({
        x: bx,
        y: boss.y + 20,
        vx: 0,
        vy: 120,
        r: 5,
        owner: 'boss',
        color: boss.color
      });
    }
  }
}
```

- [ ] **Step 2: Add pincer pattern (from both sides)**

```javascript
else if (p === 'pincer') {
  // Left side bullets
  for (let i = 0; i < 5; i++) {
    bullets.push({
      x: -20,
      y: boss.y + i * 30 + 20,
      vx: 150,
      vy: 30,
      r: 5,
      owner: 'boss',
      color: '#ff00ff'
    });
  }
  // Right side bullets
  for (let i = 0; i < 5; i++) {
    bullets.push({
      x: canvas.width + 20,
      y: boss.y + i * 30 + 20,
      vx: -150,
      vy: 30,
      r: 5,
      owner: 'boss',
      color: '#00ffff'
    });
  }
}
```

- [ ] **Step 3: Add predict pattern (lead targeting)**

```javascript
else if (p === 'predict') {
  // Calculate player's predicted position
  const dx = player.x - boss.x;
  const dy = player.y - boss.y;
  const dist = Math.sqrt(dx*dx + dy*dy);
  // Lead by 0.3 seconds
  const leadTime = 0.3;
  const predictX = player.x + (dx / dist) * 100 * leadTime;
  const predictY = player.y + (dy / dist) * 100 * leadTime;

  bullets.push({
    x: boss.x,
    y: boss.y,
    vx: (predictX - boss.x) * 2,
    vy: (predictY - boss.y) * 2,
    r: 6,
    owner: 'boss',
    color: '#ffff00'
  });
}
```

- [ ] **Step 4: Add helix_spread pattern**

```javascript
else if (p === 'helix_spread') {
  const angle = Date.now() / 200;
  const colors = ['#ff00ff', '#00ffff', '#ffff00'];
  for (let j = 0; j < 3; j++) {
    const a = angle + j * Math.PI * 2 / 3;
    const speed = 50 + j * 20; // Different speeds per arm
    bullets.push({
      x: boss.x,
      y: boss.y,
      vx: Math.cos(a) * speed,
      vy: Math.sin(a) * speed + 40,
      r: 4 + j,
      owner: 'boss',
      color: colors[j]
    });
  }
}
```

- [ ] **Step 5: Add new patterns to BOSS_PATTERNS array**

Update BOSS_PATTERNS:
```javascript
const BOSS_PATTERNS = [
  'laser', 'ring', 'spiral', 'wave', 'wall', 'scatter', 'beam', 'homing', 'rain',
  'double_spiral', 'flower', 'cross', 'snake', 'pulse', 'vortex', 'burst', 'helix', 'galaxy', 'chaos',
  'corridor', 'pincer', 'predict', 'helix_spread'
];
```

---

## Task 3: Implement Pattern-Linked Movement

**Files:**
- Modify: `bullet-hell.html` (update updateBoss function)

- [ ] **Step 1: Add movement logic based on pattern**

Find updateBoss() and add pattern-linked movement inside the normal (non-entrance) behavior section:
```javascript
// Pattern-linked movement
const pattern = boss.pattern;
if (pattern === 'spiral' || pattern === 'helix' || pattern === 'double_spiral') {
  // Circular movement
  const t = Date.now() / 1000;
  boss.x = canvas.width / 2 + Math.cos(t) * 100;
  boss.y = 80 + Math.sin(t * 2) * 20;
}
else if (pattern === 'ring' || pattern === 'flower' || pattern === 'galaxy') {
  // Stationary with slight drift
  boss.x += Math.sin(Date.now() / 500) * 20 * dt;
}
else if (pattern === 'snake' || pattern === 'wave') {
  // Z-pattern
  const t = Date.now() / 500;
  boss.x = canvas.width / 2 + Math.sin(t) * 150;
  boss.y = 80 + Math.sin(t * 2) * 30;
}
else if (pattern === 'beam' || pattern === 'laser') {
  // Track player X
  const targetX = player.x;
  boss.x += (targetX - boss.x) * 2 * dt;
}
else if (pattern === 'rain' || pattern === 'chaos') {
  // Random position shifts
  if (Math.random() < 0.02) {
    boss.x = 100 + Math.random() * (canvas.width - 200);
  }
}
```

---

## Task 4: Implement Special Abilities System

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: Add checkBossAbilities() function**

Add after updateBoss():
```javascript
function checkBossAbilities(dt) {
  if (!boss.active) return;

  const hpPercent = boss.hp / boss.maxHp;
  const waveDifficulty = Math.min(waveCount / 10, 1); // 0-1 based on wave

  // Update all cooldowns
  for (const key in boss.abilityCooldowns) {
    if (boss.abilityCooldowns[key] > 0) {
      boss.abilityCooldowns[key] -= dt;
    }
  }

  // Determine which abilities are available based on wave
  const availableAbilities = Math.floor(waveDifficulty * 10) + 3; // 3-10 abilities

  // 1. TELEPORT - HP < 80%
  if (hpPercent < 0.8 && boss.abilityCooldowns.teleport <= 0 && availableAbilities >= 1) {
    triggerTeleport();
    boss.abilityCooldowns.teleport = 15;
  }

  // 2. SUMMON - Every 30 seconds
  if (boss.abilityCooldowns.summon <= 0 && availableAbilities >= 2) {
    triggerSummon();
    boss.abilityCooldowns.summon = 30;
  }

  // 3. SHIELD - HP < 60%
  if (hpPercent < 0.6 && boss.shieldHp <= 0 && availableAbilities >= 3) {
    triggerShield();
  }

  // 4. CHARGE - HP < 40%
  if (hpPercent < 0.4 && boss.abilityCooldowns.charge <= 0 && availableAbilities >= 4) {
    triggerChargeAttack();
    boss.abilityCooldowns.charge = 20;
  }

  // 5. CLONE - HP < 50%
  if (hpPercent < 0.5 && boss.abilityCooldowns.clone <= 0 && availableAbilities >= 5) {
    triggerClone();
    boss.abilityCooldowns.clone = 25;
  }

  // 6. PORTAL - Every 45 seconds
  if (boss.abilityCooldowns.portal <= 0 && availableAbilities >= 6) {
    triggerPortal();
    boss.abilityCooldowns.portal = 45;
  }

  // 7. BLACK_HOLE - HP < 30%
  if (hpPercent < 0.3 && boss.abilityCooldowns.blackHole <= 0 && availableAbilities >= 7) {
    triggerBlackHole();
    boss.abilityCooldowns.blackHole = 30;
  }

  // 8. WHITE_HOLE - HP < 35%
  if (hpPercent < 0.35 && boss.abilityCooldowns.whiteHole <= 0 && availableAbilities >= 8) {
    triggerWhiteHole();
    boss.abilityCooldowns.whiteHole = 25;
  }

  // 9. LASER - HP < 25%
  if (hpPercent < 0.25 && boss.abilityCooldowns.laser <= 0 && availableAbilities >= 9) {
    triggerLaser();
    boss.abilityCooldowns.laser = 20;
  }

  // 10. PHANTOM - HP < 20%
  if (hpPercent < 0.2 && boss.abilityCooldowns.phantom <= 0 && availableAbilities >= 10) {
    triggerPhantomTank();
    boss.abilityCooldowns.phantom = 15;
  }
}
```

- [ ] **Step 2: Add ability trigger functions**

Add all 10 trigger functions:
```javascript
function triggerTeleport() {
  // Flash effect
  spawnExplosion(boss.x, boss.y, '#ffffff', 20);
  // Swap position
  boss.x = canvas.width - boss.x;
  boss.y = 80 + (Math.random() - 0.5) * 60;
  triggerScreenShake(5, 0.2);
  spawnExplosion(boss.x, boss.y, boss.color, 20);
}

function triggerSummon() {
  // Spawn 2-3 minions
  const count = 2 + Math.floor(Math.random() * 2);
  for (let i = 0; i < count; i++) {
    minions.push({
      x: 50 + Math.random() * (canvas.width - 100),
      y: -20,
      vx: 20 + Math.random() * 30,
      vy: 50 + Math.random() * 30,
      r: 10,
      hp: 20,
      color: boss.color
    });
  }
}

function triggerShield() {
  boss.shieldHp = boss.maxHp * 0.3; // 30% shield
}

function triggerChargeAttack() {
  boss.charging = true;
  boss.chargeTime = 0;
  // Warning effect - screen flash
  triggerScreenShake(3, 0.5);
}

function triggerClone() {
  // Create 2 clones
  boss.clones = [];
  for (let i = 0; i < 2; i++) {
    boss.clones.push({
      x: boss.x + (Math.random() - 0.5) * 100,
      y: boss.y + (Math.random() - 0.5) * 50,
      alpha: 0.5,
      offset: Math.random() * Math.PI * 2
    });
  }
  setTimeout(() => { boss.clones = []; }, 5000);
}

function triggerPortal() {
  // Create portals on left and right
  boss.portals = [
    { x: 50, y: canvas.height / 2, active: true },
    { x: canvas.width - 50, y: canvas.height / 2, active: true }
  ];
  setTimeout(() => { boss.portals = []; }, 8000);
}

function triggerBlackHole() {
  boss.blackHoleActive = true;
  boss.blackHoleTime = 0;
  setTimeout(() => { boss.blackHoleActive = false; }, 4000);
}

function triggerWhiteHole() {
  boss.whiteHoleActive = true;
  boss.whiteHoleTime = 0;
  setTimeout(() => { boss.whiteHoleActive = false; }, 3000);
}

function triggerLaser() {
  boss.laserActive = true;
  boss.laserTime = 0;
  boss.laserAngle = Math.atan2(player.y - boss.y, player.x - boss.x);
  setTimeout(() => { boss.laserActive = false; }, 2000);
}

function triggerPhantomTank() {
  boss.phantomTankActive = true;
  boss.phantomTankX = Math.random() > 0.5 ? 50 : canvas.width - 50;
  boss.phantomTankVisible = true;
  setTimeout(() => {
    boss.phantomTankVisible = false;
    // Fire when appearing
    bullets.push({
      x: boss.phantomTankX,
      y: 100,
      vx: boss.phantomTankX < canvas.width / 2 ? 200 : -200,
      vy: 150,
      r: 8,
      owner: 'boss',
      color: '#ff0000'
    });
  }, 500);
  setTimeout(() => { boss.phantomTankActive = false; }, 3000);
}
```

---

## Task 5: Implement Ability Visual Effects

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: Add renderBossAbilities() function**

Add after renderBoss():
```javascript
function renderBossAbilities() {
  if (!boss.active) return;

  // Shield
  if (boss.shieldHp > 0) {
    ctx.save();
    ctx.translate(boss.x, boss.y);
    ctx.strokeStyle = boss.color;
    ctx.lineWidth = 3;
    ctx.globalAlpha = 0.6 + Math.sin(Date.now() / 100) * 0.2;
    // Rotating hexagon shield
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const angle = (i / 6) * Math.PI * 2 + Date.now() / 500;
      const px = Math.cos(angle) * (boss.r + 20);
      const py = Math.sin(angle) * (boss.r + 20);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.stroke();
    ctx.restore();
  }

  // Clones
  for (const clone of boss.clones) {
    ctx.save();
    ctx.globalAlpha = clone.alpha;
    ctx.translate(clone.x + Math.sin(Date.now() / 200 + clone.offset) * 5, clone.y);
    ctx.scale(0.8, 0.8);
    ctx.fillStyle = boss.color;
    ctx.beginPath();
    ctx.arc(0, 0, boss.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // Portals
  for (const portal of boss.portals) {
    if (portal.active) {
      ctx.save();
      ctx.translate(portal.x, portal.y);
      const gradient = ctx.createRadialGradient(0, 0, 5, 0, 0, 40);
      gradient.addColorStop(0, '#000000');
      gradient.addColorStop(0.5, '#4400ff');
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(0, 0, 40, 0, Math.PI * 2);
      ctx.fill();
      ctx.rotate(Date.now() / 200);
      ctx.strokeStyle = '#8800ff';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(0, 0, 30, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
  }

  // Black Hole
  if (boss.blackHoleActive) {
    ctx.save();
    ctx.translate(boss.x, boss.y);
    const gradient = ctx.createRadialGradient(0, 0, 5, 0, 0, 60);
    gradient.addColorStop(0, '#000000');
    gradient.addColorStop(0.3, '#220044');
    gradient.addColorStop(1, 'transparent');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(0, 0, 60, 0, Math.PI * 2);
    ctx.fill();
    // Accretion disk
    ctx.strokeStyle = '#4400ff';
    ctx.lineWidth = 2;
    for (let i = 0; i < 3; i++) {
      ctx.beginPath();
      ctx.ellipse(0, 0, 40 + i * 10, 15, Date.now() / 500 + i, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.restore();
  }

  // White Hole
  if (boss.whiteHoleActive) {
    ctx.save();
    ctx.translate(boss.x, boss.y);
    const gradient = ctx.createRadialGradient(0, 0, 5, 0, 0, 80);
    gradient.addColorStop(0, '#ffffff');
    gradient.addColorStop(0.3, '#ffff00');
    gradient.addColorStop(1, 'transparent');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(0, 0, 80, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // Laser Beam
  if (boss.laserActive) {
    ctx.save();
    ctx.translate(boss.x, boss.y);
    // Track player
    boss.laserAngle = Math.atan2(player.y - boss.y, player.x - boss.x);
    ctx.rotate(boss.laserAngle);

    // Main beam
    ctx.fillStyle = '#ff0000';
    ctx.shadowBlur = 20;
    ctx.shadowColor = '#ff0000';
    ctx.fillRect(0, -4, canvas.width, 8);

    // Inner bright core
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, -2, canvas.width, 4);
    ctx.restore();
  }

  // Phantom Tank
  if (boss.phantomTankActive && boss.phantomTankVisible) {
    ctx.save();
    ctx.translate(boss.phantomTankX, 100);
    ctx.fillStyle = '#444444';
    ctx.fillRect(-15, -10, 30, 20);
    ctx.fillStyle = '#ff0000';
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#ff0000';
    ctx.beginPath();
    ctx.arc(boss.phantomTankX < canvas.width / 2 ? 15 : -15, 0, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // Charge warning text
  if (boss.charging) {
    ctx.save();
    ctx.fillStyle = '#ff0000';
    ctx.font = 'bold 24px monospace';
    ctx.textAlign = 'center';
    ctx.shadowBlur = 20;
    ctx.shadowColor = '#ff0000';
    ctx.fillText('WARNING!', canvas.width / 2, canvas.height / 2);
    ctx.restore();
  }
}
```

---

## Task 6: Apply Ability Effects to Gameplay

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: Apply black hole gravity to player**

In updatePlayer(), add at the start:
```javascript
if (boss.blackHoleActive) {
  const dx = boss.x - player.x;
  const dy = boss.y - player.y;
  const dist = Math.sqrt(dx*dx + dy*dy);
  if (dist > 20) {
    player.x += (dx / dist) * 100 * dt;
    player.y += (dy / dist) * 100 * dt;
  }
}
```

- [ ] **Step 2: Apply white hole repulsion to player**

After black hole code:
```javascript
if (boss.whiteHoleActive) {
  const dx = player.x - boss.x;
  const dy = player.y - boss.y;
  const dist = Math.sqrt(dx*dx + dy*dy);
  if (dist < 300) {
    player.x += (dx / dist) * 150 * dt;
    player.y += (dy / dist) * 150 * dt;
  }
}
```

- [ ] **Step 3: Apply portal teleportation to bullets**

In updateBullets(), add after position update:
```javascript
// Portal teleportation
if (boss.portals.length > 0) {
  for (const portal of boss.portals) {
    if (portal.active) {
      // Check if bullet is near portal
      const otherPortal = boss.portals.find(p => p !== portal);
      if (otherPortal && otherPortal.active) {
        const dx = b.x - portal.x;
        const dy = b.y - portal.y;
        if (Math.sqrt(dx*dx + dy*dy) < 30) {
          b.x = otherPortal.x + (Math.random() - 0.5) * 20;
          b.y = otherPortal.y + (Math.random() - 0.5) * 20;
        }
      }
    }
  }
}
```

- [ ] **Step 4: Shield damage reduction**

In checkBossHit(), add shield check at start:
```javascript
function checkBossHit() {
  if (!boss.active) return;

  // Shield blocks damage
  if (boss.shieldHp > 0) {
    for (let i = bullets.length - 1; i >= 0; i--) {
      const b = bullets[i];
      if (b.owner === 'player' && circleCollision(b, { x: boss.x, y: boss.y, r: boss.r + 25 })) {
        bullets.splice(i, 1);
        boss.shieldHp -= 5;
        spawnSparkle(b.x, b.y, boss.color);
        if (boss.shieldHp <= 0) {
          spawnExplosion(boss.x, boss.y, boss.color, 30);
          triggerScreenShake(3, 0.2);
        }
        return; // No damage to boss while shielded
      }
    }
  }
  // ... rest of existing code
```

- [ ] **Step 5: Laser damage to player**

In checkPlayerHit(), add laser damage:
```javascript
if (boss.laserActive) {
  // Check if player is in laser path
  const angle = boss.laserAngle;
  // Simple check: is player roughly in line with laser?
  const dx = player.x - boss.x;
  const dy = player.y - boss.y;
  const playerAngle = Math.atan2(dy, dx);
  const angleDiff = Math.abs(angle - playerAngle);
  if (angleDiff < 0.1 || angleDiff > Math.PI * 2 - 0.1) {
    playerHit();
  }
}
```

---

## Task 7: Integrate Everything

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: Call checkBossAbilities in update loop**

Find the update() function and add:
```javascript
function update(dt) {
  gameTime += dt;
  updateScreenShake(dt);
  updatePlayer(dt);
  updateBullets(dt);
  updatePowerups(dt);
  updateBoss(dt);
  checkBossAbilities(dt); // ADD THIS
  updateParticles(dt);
  updateExplosionParticles(dt);
  updateDisplayHp(dt);
  updateScorePopups(dt);
  updateCombo(dt);
  checkPlayerHit();
  checkBossHit();
}
```

- [ ] **Step 2: Call renderBossAbilities in render**

Find the PLAYING case in render() and add after renderBoss():
```javascript
case STATE.PLAYING:
  renderExplosionParticles();
  renderScorePopups();
  renderParticles();
  renderBullets();
  renderPowerups();
  if (boss.active) {
    renderBoss();
    renderBossAbilities(); // ADD THIS
  }
  renderPlayer();
  renderUI();
  renderCombo();
  break;
```

- [ ] **Step 3: Update charge attack logic**

In updateBoss(), add charge behavior:
```javascript
// Charge attack handling
if (boss.charging) {
  boss.chargeTime += dt;
  if (boss.chargeTime >= 3) {
    // Fire massive burst
    for (let i = 0; i < 20; i++) {
      const angle = (i / 20) * Math.PI * 2;
      bullets.push({
        x: boss.x,
        y: boss.y,
        vx: Math.cos(angle) * 200,
        vy: Math.sin(angle) * 200,
        r: 8,
        owner: 'boss',
        color: '#ff0000'
      });
    }
    boss.charging = false;
    triggerScreenShake(8, 0.3);
  }
  return; // Don't do normal behavior while charging
}
```

- [ ] **Step 4: Update minion rendering**

Find renderParticles() or add new function:
```javascript
function renderMinions() {
  for (const m of minions) {
    ctx.save();
    ctx.fillStyle = m.color;
    ctx.shadowBlur = 10;
    ctx.shadowColor = m.color;
    ctx.beginPath();
    ctx.arc(m.x, m.y, m.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}
```

- [ ] **Step 5: Add minions to update loop**

Add updateMinions function and call it:
```javascript
function updateMinions(dt) {
  for (let i = minions.length - 1; i >= 0; i--) {
    const m = minions[i];
    m.x += m.vx * dt;
    m.y += m.vy * dt;
    if (m.y > canvas.height + 20 || m.x < -20 || m.x > canvas.width + 20) {
      minions.splice(i, 1);
    }
  }
}
```

Add to update():
```javascript
updateMinions(dt);
```

Add to render():
```javascript
renderMinions();
```

---

## Task 8: Final Integration & Testing

**Files:**
- Modify: `bullet-hell.html`

- [ ] **Step 1: Add minions array initialization**

Find where other arrays are initialized and add:
```javascript
const minions = [];
```

- [ ] **Step 2: Test in browser**

Open bullet-hell.html in browser and verify:
- [ ] 4 new bullet patterns work (corridor, pincer, predict, helix_spread)
- [ ] BOSS moves according to pattern type
- [ ] All 10 abilities trigger at correct HP levels
- [ ] Each ability has visual effect
- [ ] Game remains playable

- [ ] **Step 3: Syntax validation**

Run: `node -e "require('fs').readFileSync('bullet-hell.html','utf8').match(/<script>([\s\S]*)<\/script>/)[1]" | node --check`
Expected: No output (no errors)

---

## Summary

This plan adds:
- 4 new tactical bullet patterns
- Pattern-linked BOSS movement (7 movement types)
- 10 special abilities with unique effects
- Visual effects for all abilities
- Integration with existing gameplay systems
