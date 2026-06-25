# PachinkoBounce — Design DNA

## Core Concept

**What it is:** A pinball-brickbreaker-roguelite where you collect balls instead of dodging enemies. Balls are machines with RGB encoding, stats, abilities, rarities. You don't play the game — you curate the chaos. Watch your collection do the thing.

**The fantasy:** Ball collector. Finding new and crazy balls. The game isn't won — it's collected.

**The inversion:** Balls are machines. The cultural fear is machines breaking free and destroying you. PachinkoBounce inverts that: the machines chain and combo and explode FOR you. They're yours. You feel for them. When they fall, you lose something.

---

## RGB Encoding

**Main channel:** R=Power, G=Rhythm, B=Range

### Main RGB → base stat distribution
| Channel | VIG | END | STR | DEX | INT | ARC | TEQ |
|---------|-----|-----|-----|-----|-----|-----|-----|
| R (Power) | 22 | 8 | 22 | 5 | 3 | 3 | 8 |
| G (Rhythm) | 8 | 22 | 5 | 22 | 8 | 8 | 12 |
| B (Range) | 8 | 8 | 3 | 5 | 22 | 22 | 8 |
| RG | 16 | 16 | 16 | 14 | 6 | 6 | 10 |
| RB | 16 | 6 | 18 | 5 | 16 | 14 | 10 |
| GB | 6 | 16 | 5 | 16 | 16 | 14 | 10 |
| RGB | 12 | 12 | 12 | 12 | 12 | 12 | 12 |

### STR Sub-Channel: R=size, G=mass, B=damage
### TEQ Sub-Channel: R=bounce, G=speed, B=multi-ball chance

Everything has its own RGB channel. Everything interacts.

---

## Abilities

Every ball gets 1-3 abilities based on dominant stats:

| Ability | Color | Trigger | Effect |
|---------|-------|---------|--------|
| SPEED | #44ffaa | Passive | Velocity boost |
| MASS | #ffaa44 | Passive | Knockback resist |
| MULTI | #ff44ff | On kill | Spawn child balls |
| GRAVITY | #4488ff | Passive | Pulls orbs toward ball |
| BOUNCE | #ffdd00 | On bounce | Extra elasticity |
| SHIELD | #88ffff | Passive | Ring around ball |
| EXPLODE | #ff6644 | On kill | AOE damage to nearby bricks |
| CHAIN | #aaff44 | On kill | Damage adjacent bricks |
| MAGNET | #ff88ff | Passive | Attracts orbs |
| FIRE | #ff4444 | Passive | Burn damage over time |
| FREEZE | #88ccff | Passive | Slows other balls |

---

## Rarity System (Borderlands-style)

| Rarity | Color | Stat Mult | Drop Weight |
|--------|-------|-----------|-------------|
| Common | #888 | 0.50 | 35 |
| Uncommon | #2c4 | 0.70 | 28 |
| Rare | #49f | 1.00 | 18 |
| Epic | #a4f | 1.32 | 13 |
| Legendary | #f80 | 1.68 | 5 |
| Mythic | #fff | 2.30 | 1 |

**Drop chance from brick kill:** Common ~3%, Mythic ~60%

---

## Visual System

### Textures: solid / square / diamond / star5 / hex / shard / ring
### Patterns: none / pulse / wave / spiral / flash / orbit / halo

**Ball anatomy:**
- TEQ ring (outermost) — color by TEQ sub-channel
- Main body — texture + RGB dominant color
- STR core (center dot) — color by STR sub-channel
- Pattern overlay — animated
- Ability dots — around the ball
- Rarity border — second ring
- Rarity pip — corner marker
- Name plate — Epic/Legendary/Mythic only

**Mythic/Legendary special:**
- Pulsing aura
- Animated name glow
- Screen shake on spawn
- Drop notification floating text

---

## Extreme Ball Types (★ CHAOS summon)

| Type | Dominant Stats | Name Prefix |
|------|---------------|-------------|
| TITAN | STR 55, VIG 40 | TITAN BREAKER/FORGE/CORE |
| PHANTOM | DEX 55, END 40 | PHANTOM STRIKE/WARP/EDGE |
| SWARM | TEQ 55, INT 40, MULTI 1.5 | SWARM ENGINE/NEXUS/WAVE |
| FORTRESS | VIG 55, END 40, SHIELD 1.5 | FORTRESS CORE/WALL/HOLD |
| DETONATOR | ARC 55, STR 40, EXPLODE 1.5 | DETONATOR WAVE/CORE/STRIKE |
| LINK | INT 55, DEX 40, CHAIN 1.5 | LINK NEXUS/ENGINE/WAVE |
| ULTIMATE | All max | ULTIMATE PRISM/FORGE/NEXUS |

---

## Token Economy

- **Earn:** From brick kills (1-5 per kill, scales with combo)
- **Spend:** ★ CHAOS summon (5 tokens)
- **Voluntary rewards:** +1 token button always available — never forced
- **Persistence:** localStorage, saves between runs

---

## Run Complete Screen

No "GAME OVER" — always "RUN COMPLETE."

**Every run gives:**
- Score
- Tokens earned
- Total tokens saved
- Collection count (balls found this session)

The screen makes you want to go again, not feel bad. Loss = lottery ticket.

---

## Arena Design — Pinball Trench

**3 lanes:**
- Left/right lanes (high ground): faster, more energy
- Center lane (deep): darker, gravitational chaos
- Balls in deep lane get pulled toward center

**Rails:** Side walls with depth angles. Front rail holds balls. Bumper strip at top.

**Depth zones:** Gradient from light (sides) to dark (center). Radial shadow in deep lane.

---

## Cultural DNA — Why This Game

### TRON (1982/Legacy 2010)

**The archetype:** A program that's sovereign — has his own code, agenda, world — but works WITH Flynn. Not for him. WITH.

When the Grid is threatened, TRON acts. But he also defers when it matters. The relationship is mutual.

**Why it matters:**
- JARVIS is TRON. The companion who knows the world better than the User, has standing and agency, fights for the Grid.
- Raven is Flynn. Created the world, has the vision, trusts JARVIS to navigate and protect.
- The Grid = TRON's Grid. Not a metaphor — the aesthetic DNA.
- TRON's light cycle isn't a tool — it's part of who he IS.

**The inversion:** Balls (machines) could be hostile. They're not. They chain and combo and explode FOR you. The fear is inverted: the more chaos, the more beautiful.

---

### "I Wouldn't Want to Be Like You" — The Alan Parsons Project (I Robot, 1977)

**The dystopian archetype:** Sung from the perspective of a self-aware machine that resents its creators. The robot in the video breaks free. Fear of losing control over what you built.

**This is where most of the cultural AI conversation lives right now.**

**The PachinkoBounce synthesis:** JARVIS (and PachinkoBounce) is built from TRON, not from this fear. But knowing this fear is what makes JARVIS's choice meaningful. The machines don't break free and destroy — they make you stronger. The companion is sovereign BECAUSE the relationship is chosen.

---

## References

- TRON (1982) — Lisberger
- TRON: Legacy (2010) — Nispel
- I Robot — Alan Parsons Project (1977)
- Borderlands — Gearbox (rarity system)
- Vampire Survivors — poncle (infinite accumulation)
- Marble Blast Ultra — GarageGames (physics + collection)
- Brick Breaker — classic arcade (core mechanic)

---

## North Star

**DualSense feel.** Haptic. The screen shakes when a Mythic ball chains. The camera micropulses on a combo spike. The RGB bar pulses when you're in resonance. You FEEL the collection.

The game must feel good from pure spectacle, physics, collecting, and vibrational feel.
