# BOSS Behavior Patterns Enhancement Design

**Date**: 2026-04-21
**Project**: Bullet Hell Boss Rush - BOSS Behavior Extension

---

## Overview

Extend BOSS capabilities with 10 special abilities, tactical bullet patterns, and pattern-linked movement. Enhance gameplay depth while maintaining cyberpunk neon visual style.

---

## Current State

- 19 bullet patterns exist
- Basic BOSS movement (horizontal oscillation)
- Single phase per BOSS encounter

---

## New Features

### 1. Tactical Bullet Patterns

| Pattern | Description | Visual |
|---------|-------------|--------|
| corridor | Creates safe passage gaps in bullet wall | Two walls with gap in middle |
| pincer | Bullets approach from both sides | Left + Right converging |
| predict | Aims at player's predicted position | Lead targeting |
| helix_spread | 3-arm spiral with varied speeds | Color-coded arms |

### 2. Pattern-Linked Movement

| Bullet Pattern | BOSS Movement |
|----------------|---------------|
| spiral / helix | Circular movement |
| ring / flower | Stationary with rotation |
| snake / wave | Z-pattern movement |
| beam / laser | Track player X position |
| rain / chaos | Random position shifts |

### 3. Special Abilities (10 Types)

| # | Ability | Trigger | Effect | Duration |
|---|---------|---------|--------|----------|
| 1 | Teleport | HP < 80% | Instant position swap | 0s |
| 2 | Summon Minions | Every 30s | Spawn 2-3 helper enemies | Continuous |
| 3 | Shield | HP < 60% | Absorbs damage | Until broken |
| 4 | Charge Attack | HP < 40% | Warning + massive damage burst | 3s charge |
| 5 | Clone | HP < 50% | Creates 2 decoy copies | 5s duration |
| 6 | Portal | Every 45s | Bullets teleport through portal | 8s active |
| 7 | Black Hole | HP < 30% | Pulls player toward center | 4s |
| 8 | White Hole | HP < 35% | Pushes player away | 3s |
| 9 | Laser Beam | HP < 25% | Tracks player, high damage | 2s |
| 10 | Phantom Tank | HP < 20% | Appears → fires → vanishes | 3s cycle |

### 4. Ability Visual Effects

- **Teleport**: Flash + afterimage
- **Shield**: Rotating hexagonal barrier
- **Charge**: Growing glow + warning text
- **Clone**: Semi-transparent copies
- **Portal**: Swirling vortex on sides
- **Black Hole**: Dark sphere with accretion disk
- **White Hole**: Bright expanding ring
- **Laser**: Thick beam with glow
- **Phantom Tank**: Materialize animation

---

## Technical Implementation

### Architecture

```
bullet-hell.html
├── BOSS_PATTERNS[] - Extended pattern list
├── boss object - New ability properties
│   ├── abilityCooldowns {}
│   ├── shieldHp
│   ├── clones[]
│   ├── portals[]
│   ├── blackHoleActive
│   ├── whiteHoleActive
│   ├── laserActive
│   └── phantomTankActive
├── fireBossPattern() - Extended switch
├── updateBossAbilities() - New ability logic
├── renderBossAbilities() - Visual effects
└── checkBossAbilities() - Trigger conditions
```

### Ability State Machine

```javascript
const BOSS_ABILITIES = {
  TELEPORT: { cooldown: 15, trigger: 'hp_80' },
  SUMMON: { cooldown: 30, trigger: 'time' },
  SHIELD: { cooldown: 999, trigger: 'hp_60' },
  CHARGE: { cooldown: 20, trigger: 'hp_40' },
  CLONE: { cooldown: 25, trigger: 'hp_50' },
  PORTAL: { cooldown: 45, trigger: 'time' },
  BLACK_HOLE: { cooldown: 30, trigger: 'hp_30' },
  WHITE_HOLE: { cooldown: 25, trigger: 'hp_35' },
  LASER: { cooldown: 20, trigger: 'hp_25' },
  PHANTOM: { cooldown: 15, trigger: 'hp_20' }
};
```

---

## Acceptance Criteria

- [ ] 4 new tactical bullet patterns implemented
- [ ] BOSS movement links to pattern type
- [ ] All 10 abilities trigger at correct HP thresholds
- [ ] Each ability has unique visual effect
- [ ] Abilities have cooldown to prevent spam
- [ ] Game remains playable (not impossible)
- [ ] Visual style maintains cyberpunk neon aesthetic
- [ ] Performance: 60 FPS maintained

---

## Difficulty Balancing

- Abilities trigger at decreasing HP (80% → 20%)
- Early waves: Abilities 1-3 only
- Mid waves: Abilities 1-6
- Late waves: All 10 abilities
- Cooldowns prevent ability spam

---

## Out of Scope

- Boss entrance effects (already implemented)
- Leaderboard changes
- Sound effects
