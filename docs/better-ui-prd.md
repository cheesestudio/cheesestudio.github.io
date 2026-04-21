# Product Requirements Document: Better UI Effects

**Version**: 1.0
**Date**: 2026-04-21
**Author**: Sarah (Product Owner)
**Quality Score**: 92/100

---

## Executive Summary

为Bullet Hell Boss Rush游戏增强视觉UI特效，提升打击反馈感和沉浸感。包括BOSS死亡爆炸特效与屏幕震动、动态血条动画、得分上浮显示、连杀Combo系统。保持赛博朋克霓虹风格，增强玩家成就感。

---

## Problem Statement

**Current Situation**: 当前游戏UI较基础，缺少视觉反馈，打击感不足

**Proposed Solution**: 增加爆炸特效、屏幕震动、动态血条、得分动画、Combo系统

**Business Impact**: 提升游戏体验，增加玩家留存率和成就感

---

## Success Metrics

**Primary KPIs:**
- BOSS死亡时触发爆炸粒子效果
- 击中BOSS时屏幕轻微震动
- 血条有平滑过渡动画
- 得分时显示上浮数字
- Combo系统正确计时和显示

**Validation**: 人工测试各特效触发时机

---

## User Stories & Acceptance Criteria

### Story 1: BOSS死亡爆炸特效

**As a** 玩家
**I want to** 看到BOSS死亡时的炫酷爆炸特效
**So that** 有成就感和满足感

**Acceptance Criteria:**
- [ ] BOSS血量归零时触发爆炸粒子
- [ ] 爆炸粒子向外扩散
- [ ] 屏幕快速小幅度震动
- [ ] BOSS消失并进入下一形态

### Story 2: 动态血条动画

**As a** 玩家
**I want to** 看到平滑的血条变化
**So that** 了解BOSS受损程度更直观

**Acceptance Criteria:**
- [ ] BOSS血条有平滑过渡效果
- [ ] 血条减少时有动画过渡
- [ ] 保持霓虹发光风格

### Story 3: 得分上浮动画

**As a** 玩家
**I want to** 看到得分数字上浮
**So that** 了解得分来源

**Acceptance Criteria:**
- [ ] 击中BOSS时显示+分数
- [ ] 数字上浮并淡出消失
- [ ] 分数累加动画

### Story 4: Combo连杀系统

**As a** 玩家
**I want to** 看到连杀计数
**So that** 挑战更高Combo

**Acceptance Criteria:**
- [ ] 2秒内连续击中BOSS累加Combo
- [ ] Combo数字会放大显示
- [ ] Combo归零时有冷却计时

---

## Functional Requirements

### Feature 1: BOSS死亡爆炸 + 屏幕震动
- Description: BOSS血量归零时触发爆裂粒子效果
- User flow: BOSS被击败 → 爆炸粒子生成 → 屏幕震动 → BOSS消失
- Screen shake: 快速小幅度震动（震动时长100ms，位移±3px）

### Feature 2: 动态血条
- Description: 血条平滑过渡动画
- Current health显示用插值平滑过渡到actual health

### Feature 3: 得分上浮动画
- Description: 击中时在位置显示+分数
- 数字上移并淡出，持续0.5秒

### Feature 4: Combo系统
- Description: 2秒内连续击中累加
- Combo显示在屏幕中央偏上
- Combo≥2时数字放大

### Out of Scope
- 音效配合（可选后续添加）
- 多语言支持

---

## Technical Constraints

### Performance
- 60 FPS
- 粒子数量限制（max 200）

### Technology
- Canvas 2D API
- Vanilla JavaScript

---

## MVP Scope & Phasing

### Phase 1: MVP
- BOSS死亡爆炸 + 屏幕震动
- 动态血条动画
- 得分上浮动画
- Combo系统基础

### Phase 2: Enhancements
- 更多粒子效果
- 音效配合

---

*This PRD was created through interactive requirements gathering with quality scoring.*