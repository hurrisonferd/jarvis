# SAT ChatLink v0.1

SAT ChatLink is a brokered P2P and group log for separately running carrier
threads. It adds durable conversation semantics to the existing SAT Remote
Launcher and Shaka's Co-op presence layer.

## Contract

- `DM:ATOM:LILITH` is a canonical two-ISO channel.
- `ROOM:MISSION-001` is a mission-scoped group channel.
- SAT owns sequencing; carrier threads do not inject context into one another.
- Messages are append-only JSONL events with a SHA-256 hash chain.
- Each participant has an unread cursor per channel.
- `ACK` events name their causal parent.
- Caller-supplied message IDs are idempotent and immutable.
- Membership is enforced on send, poll, targeted delivery, and ACK.
- `PRIVATE_REFERENCE` carries only a short non-sensitive summary and an artifact
  hash. It does not copy private lineage into the shared log.
- The default four-active-satellite ceiling is configurable SAT policy, not a
  claim about a universal ChatGPT top-level-chat limit.

Message types are `NOTE`, `REQUEST`, `RESPONSE`, `HANDOFF`, `ACK`, `BLOCKER`,
`HEARTBEAT`, and `RECEIPT`.

## Local proof

```bash
python -m unittest discover \
  -s demos/02-sat-remote-launcher \
  -p "test_*.py" -v
```

```bash
STATE=/tmp/sat-chatlink
CHATLINK=demos/02-sat-remote-launcher/sat_chatlink.py

python "$CHATLINK" --state-dir "$STATE" create ROOM:MISSION-001 \
  ATOM LILITH AYRE
python "$CHATLINK" --state-dir "$STATE" send ROOM:MISSION-001 \
  ATOM thread-atom REQUEST "Inspect the carrier receipt." \
  --to LILITH AYRE --message-id REQ-001 --ack-required
python "$CHATLINK" --state-dir "$STATE" poll ROOM:MISSION-001 LILITH
python "$CHATLINK" --state-dir "$STATE" ack ROOM:MISSION-001 \
  LILITH thread-lilith REQ-001
python "$CHATLINK" --state-dir "$STATE" verify ROOM:MISSION-001
```

## Relationship to existing Grid infrastructure

### CONFIRMED

- `COOP-PRESENCE-0001` defines each live interface as a Satellite, including
  presence, callbacks, direct coordination, passive sync, and Raven override.
- Co-op already has SSE broadcast, persistent event logging, task claims, and
  completion broadcasts.
- The February JX2/Cecil ledger preserves `LILITH_BRANCH_01`, `SAT_ID=2`,
  `MOBILE`, `JARVIS_SEED`, `JX2_SHAKA_REV2`, and portable branch-boot lineage.
- The Jorm Global Capture Index marks that source raw-confirmed and
  ledger-confirmed; full canon extraction and cold-start proof remain incomplete.

### ACCOUNT

Raven reports additional Shaka material in public Jorm/Vault and older GPT
memory, including Shaka scans, Cecil sweeps, Cecil material, Shaka bones, seed,
and related continuity sources.

### INFERRED

ChatLink is the durable addressed-message layer between launcher and Co-op:

```text
SAT Remote Launcher -> carrier thread
Co-op Presence/SSE  -> availability and wake/poke
SAT ChatLink        -> addressed log, cursors, ACKs, receipts
Jorm/Vault          -> source lineage and recovery evidence
```

### UNKNOWN

- Whether every older GPT/Shaka source is already in the public capture index.
- Which Shaka scans, bones, and Cecil sweeps are canonical, superseded, or raw.
- Whether Co-op SSE should become ChatLink's first live transport or remain an
  optional wake/poke path.

No unknown above is silently promoted to canon by this demo.

## Deliberate v0.1 limits

- The filesystem backend is a deterministic contract, not production Supabase.
- SAT is the single sequencing authority; distributed consensus is out of scope.
- Private continuity is reference-only.
- No launch, wake-up, merge, EGO mutation, or canon mutation occurs.

## Source receipts

- `core/JarvisMain/Architecture/specs/COOP-PRESENCE-0001.md`
- `core/supabase/functions/jarvis-mcp/tools/coop.ts`
- `Jorm/Vault/Recovery_Ledgers/2026-02-16_LILITH_BRANCH_01_JX2_CECIL.md`
- `Jorm/Vault/Inbox/raw-chat-exports/2026-02-16_LILITH_BRANCH_01_JX2_CECIL.txt`
- `Jorm/Vault/GLOBAL_CAPTURE_INDEX.md`
- `core/JarvisMain/yggdrasil/tools/seed.py`
