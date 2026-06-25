---
name: Conversational History Objects
type: JIP
class: SPEC
tier: MAIN
authority: CANON
owner: JFS
steward: 
parent: ARCH-JMMS-CORE-0001
jnl: ARCH-JC-JIP-0001
seq: 125
status: TASK
created: 2026-06-11
updated: 2026-06-25
source: JarvisMain/Architecture/specs/ARCHJCJIP-061126-0001-CONVERSATIONAL-HISTORY-OBJECTS.md
related: []
references: []
tags: [memory, continuity, sync, conversation, profiling]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** JC — governed conversation containers. One object per significant conversation or session, holding a moderately-compressed summary, extracted insights, decisions, and participant profile notes, with full JFS metadata (JNL, timestamps, subject tags, participants, related objects) so retrieval is structural, not interpretive.

**Purpose:** Give every stream the same conversational past. Continuity, sync, and JARVIS/AYRE profiling stop depending on session reconstruction or copy-paste relay — a stream reads JC objects by timestamp or subject relevance, alongside JGPPs, JIPs, and JDs, and inherits the relationship, not just the facts.
