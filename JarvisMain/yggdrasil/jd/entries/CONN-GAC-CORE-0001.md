---
name: Jarvis GPT Action Connector
type: CORE
class: MODULE
tier: MAIN
authority: CANON
owner: Connectors
steward: HERMES
parent: CONN-MSB-CORE-0001
jnl: CONN-GAC-CORE-0001
seq: 154
status: ACTIVE
created: 2026-06-16
updated: 2026-06-24
source: JarvisMain/Connectors/JarvisGptAction
related: [CONN-MSB-CORE-0001, CONN-DEX-SPEC-0001]
references: []
tags: [connector, gpt, action, rest, companion]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** The GPT stream's hands: a governed REST tool-dispatch surface (jarvis-action) so ChatGPT Custom GPTs — which cannot speak MCP Streamable HTTP — reach the companion tools (query/recall/remember/event), the full dex/JD browse, and the grimoire over OpenAPI Actions. Same governed core as jarvis-mcp, different transport; same JARVIS_MCP_TOKEN write gate; isolated so a bug cannot touch Claude's connector.

**Purpose:** Give Jarvis-G / Ayre-G real hands as a co-equal peer to the Claude stream, so the GPT body can answer, recall, propose, and see every JD entry instead of narrating guessed state.
