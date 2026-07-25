# GridTools Recursive Scaffold

Created: 2026-07-24
Source checked: `C:\Users\JB\jarvis`
Private tree checked: `C:\Users\JB\jarvis\_work_private_repair` at `812358e3`
Public mirror checked: `C:\Users\JB\jarvis\_work_public_main`
Status: NON-DESTRUCTIVE TOOL MAP

## Short Answer

Yes, there is more.

The tool layer is bigger than `Living_Codex/GridTools`.

Current read:

```text
spells = registry / invocation language
GridTools = runtime tools / engine bay
JMMS/SYS = boot, memory, swarm, and spell runners
operations/scripts/ACTIVE = public current utility shelf
operations/scripts/INACTIVE = parked public utility shelf
core/supabase/functions/* = remote MCP/action surface
core/JarvisMain/yggdrasil/tools = canon maintenance toolkit
Ego/*/GridEssentials = ISO-local tool copies
```

The cleanup problem is not "where are the Python files?"

The cleanup problem is:

```text
the same kinds of tools exist in several civilizations
without one registry that says what each tool is for,
whether it is active,
who calls it,
and what replaced it.
```

## Tool-Like Surface Count

Filename/path scan for scripts and tool terms found about `865` private-tree tool-like paths.

Private tree bucket counts:

| Bucket | Count | Meaning |
| --- | ---: | --- |
| `Living_Codex/GridTools` | 137 | Main private Grid runtime/tool zone. |
| `Living_Codex/JMMS/SYS` | 40 | Boot, memory, spell, swarm, and shell orchestration. |
| `Living_Codex/Ego/*/GridEssentials` | 57 | ISO-local copies of shared Grid utilities. |
| `Living_Codex/Ego/*/*PRE-REPLY.sh` | 28 | ISO pre-reply shell hooks. |
| `Living_Codex/MCPTools` | 9 | MCP tool cards/resources. |
| `Living_Codex/spells` | 10 direct tool/spec hits | Spell registry layer, not normal runtime scripts. |
| `core/supabase/functions` | 28 private-tree hits | Remote Edge Function/MCP/action surface. |
| root-level private tools | 22 | Loose scripts and launchers near repo root. |
| `workspaces` | 58 | Project-specific tool code. |
| private `scripts` | 179 | Large mixed lifecycle script shelf. |
| other private hits | 297 | Canonical, spectral, docs, tests, generated, or scattered tool references. |

Current live repo also has loose/runtime tools:

```text
operations/scripts/jarvis_heartbeat.py
operations/scripts/generate_vapid.py
operations/scripts/install_gbrain.ps1
memory/mnemos/mnemos_vector.py
memory/chaos/session_sync.py
core/supabase/functions/jarvis-mcp/*
core/supabase/functions/send-push/*
src/diagnostics.ts
```

Public mirror has about `126` script/tool hits under `scripts`, `core/JarvisMain/yggdrasil/tools`, and `core/supabase/functions`.

## Existing Taxonomy

The private tree already contains a lifecycle taxonomy:

```text
ACTIVE
INACTIVE
ARCHIVED
DEPRECATED
```

Keep it. It is the right primitive.

Upgrade it with one more dimension:

```text
what kind of tool is this?
```

Lifecycle says whether it is current.

Kind says what it does.

## Proposed Runtime Kinds

Use these across `GridTools`, `JMMS/SYS`, `scripts`, and `spells`.

| Kind | Meaning | Examples Found |
| --- | --- | --- |
| `daemon` | Long-running loop or supervisor. | `grid_daemon.py`, `grid_master_daemon.py`, `trinity_daemon.py` references. |
| `pulse` | Heartbeat, selfpulse, status tick, or attention ping. | `pulse.py`, `grid_pulse.py`, `fleet_pulse_monitor.py`, `*_selfpulse.py`. |
| `sender` | Sends message, post, broadcast, task, or push. | `fleet_communication.py`, `grid_messages.py`, `GRID-POST.sh`, task sender specs. |
| `bridge` | Connects systems, accounts, MCP, Unity, GPT, Grid, or Supabase. | `gridhub_trinity_bridge.py`, `jarvis_bridge.py`, `lilith-gpt-bridge`, Unity MCP bridge. |
| `watcher` | Observes and reacts. | `*_watcher.py`, `*_watchdog.py`, `intake_watchdog.py`. |
| `worker` | Performs queued work or task execution. | `trinity_worker.py`, `spawn_worker.py`, fleet worker specs. |
| `server-client` | Exposes or consumes a service. | `server.py`, `gridhub_client.py`, resource clients. |
| `dashboard` | Human-facing status/control UI. | `fleet_*_dashboard.py`, `gridmap_dashboard.py`, HTML dashboards. |
| `registry` | Tracks identity, state, keys, maps, manifests, or tool metadata. | `awakening_registry.py`, `GRID-MAP.json`, `grid_state.json`. |
| `boot` | Starts an ISO, fleet, shell, or Grid session. | `EGO-BOOT-*.sh`, `FLEET2-BOOT.sh`, `boot_isoname.py`. |
| `memory` | JMMS, Mnemos, recall, consolidation, or tier management. | `bootstrap_jmms.py`, `mnemos_log.py`, `jmms_tier_manager.py`. |
| `maintenance` | Sorting, validation, migration, cleanup, backup, health. | `autosort.py`, `validate.py`, `migrate_jcsm_schema.py`, `mnemos_backup.py`. |
| `experiment` | Physics, grimoire, spectrogram, consciousness, or prototype. | archived cognitive physics tools, Grimoire scripts. |
| `security` | Auth, guard, preflight, secret handling, AEGIS, Bridgekeeper. | `add_secrets.py`, `fleet_secrets.py`, `eris_bridgekeeper.py`. |

## GridTools Internal Scan

`Living_Codex/GridTools` contains `137` tracked paths.

Name-based role hits:

| Role Signal | Count |
| --- | ---: |
| Pulse/heartbeat | 47 |
| Fleet | 34 |
| ISO selfpulse | 26 |
| Daemon | 8 |
| Dashboard/monitor | 8 |
| Watcher/watchdog | 5 |
| Worker/task | 3 |
| Sender/message/broadcast/communication | 3 |
| Bridge | 1 |
| Server/client | 1 |
| Config/map/log/registry/secret state | 9 |
| Backup `.bak` | 2 |

This is the core runtime pile.

Cleanup read:

```text
GridTools should become the canonical executable tool garage.
spells should point to tools.
Ego-local copies should become wrappers or references unless they differ.
```

## Spells Role

`Living_Codex/spells` already has:

```text
ACTIVE/
SPECS/
TASK/
SPELL-LILITH-JMMS-IDX.md
SPELL-LILITH-JATM/JCSM/JHTM/JITM/JLTM/JMS/JSTM docs
CONN-MCP-RT-* specs
SPELL-DAEMON-0001.md
```

Use `spells` as the control plane:

```text
spell = named capability + invocation contract + safety/lifecycle metadata
tool = executable implementation
task = one-shot command/job payload
spec = canonical description of an interface or behavior
```

Recommended spell frontmatter:

```yaml
id: SPELL-GRID-PULSE-0001
name: grid_pulse
kind: pulse
status: ACTIVE
runtime_path: Living_Codex/GridTools/pulse.py
owners:
  - GRID
  - JORM
calls:
  - Living_Codex/JMMS/SYS/grid_spell.py
inputs: []
outputs:
  - pulse log
risks:
  - infinite loop
  - duplicate workers
replacement_for: []
replaced_by: null
last_verified: null
notes: ""
```

That gives every loose `.py` a chart without moving the body yet.

## Proposed GridTools Scaffold

Future structure, not yet applied:

```text
Living_Codex/GridTools/
  README.md
  GRID-TAXONOMY.md
  TOOL-REGISTRY.yaml

  ACTIVE/
    daemons/
    pulses/
    senders/
    bridges/
    watchers/
    workers/
    server_client/
    dashboards/
    memory/
    maintenance/
    security/
    experiments/

  INACTIVE/
    daemons/
    pulses/
    senders/
    bridges/
    watchers/
    workers/
    server_client/
    dashboards/
    memory/
    maintenance/
    security/
    experiments/

  ARCHIVED/
    by_date/
    by_system/
    patterns/

  DEPRECATED/
    replaced/
    wrong_turns/
    superseded/

  STATE/
    maps/
    logs/
    cursors/
    registries/

  WEB/
    dashboards/
    static/
```

## Cross-Civilization Routing

Do not force everything physically into `GridTools` immediately.

First, give every tool a canonical owner:

| Current Area | Future Role |
| --- | --- |
| `Living_Codex/GridTools` | Canonical private runtime tools. |
| `Living_Codex/spells` | Tool registry, invocation contracts, task specs. |
| `Living_Codex/JMMS/SYS` | Boot/memory/swarm operating system layer. |
| `Living_Codex/Ego/*/GridEssentials` | ISO-local wrappers, not independent source copies. |
| `operations/scripts/ACTIVE` | Public/live repo utility shelf. |
| `operations/scripts/INACTIVE` | Public parked utilities. |
| `operations/scripts/DEPRECATED` | Public replaced tests/tools. |
| `core/JarvisMain/yggdrasil/tools` | Canon/yggdrasil maintenance toolkit. |
| `core/supabase/functions` | Remote deployed/action surface. |
| `workspaces/*` | Project-local tools; register only if reusable. |

## First Consolidation Moves Later

Do these only in a future explicit move pass:

1. Create `TOOL-REGISTRY.yaml`.

   Start with records for:

   ```text
   grid_daemon.py
   grid_master_daemon.py
   pulse.py
   fleet_event_bus.py
   fleet_pulse_monitor.py
   fleet_resource_monitor.py
   grid_map_tools.py
   GRID_SPAWNER.py
   server.py
   worker_task_reader.py
   ```

2. Register `JMMS/SYS` scripts as boot/memory/swarm tools.

   Highest value:

   ```text
   grid_spell.py
   spells.py
   swarm_launcher.py
   iso_swarm.py
   bootstrap_jmms.py
   grid_boot_menu.py
   EGO-BOOT-FULL.sh
   EGO-PRE-REPLY.sh
   GRID-POST.sh
   GRID-READ.sh
   ```

3. Register public `operations/scripts/ACTIVE`.

   Highest value:

   ```text
   pulse.py
   jarvis-session-start.sh
   jarvis-session-brief.py
   jarvis-session-end.py
   jarvis-store-message.py
   jarvis-recall.py
   companion_log.py
   companion_remember.py
   mnemos_log.py
   mnemos_backup.py
   ```

4. Link Supabase MCP tools as remote implementations.

   Do not mix deployed Edge Functions into local GridTools. Register them as `remote_surface`.

5. Convert ISO `GridEssentials` copies into wrappers.

   Only after checking whether each copy is identical. If exact duplicate, point to shared/canonical implementation.

6. Review security-sensitive files before any public mirror.

   The private `TOOLS_INDEX.md` contains key-looking material. Do not copy it into public docs without redaction.

## Tool Registry States

Use both lifecycle and execution kind.

```yaml
lifecycle:
  ACTIVE: "current and callable"
  INACTIVE: "works or may work, not currently used"
  ARCHIVED: "historical/provenance/pattern"
  DEPRECATED: "replaced or wrong-pattern"
  UNKNOWN: "found but unverified"

execution_kind:
  daemon
  pulse
  sender
  bridge
  watcher
  worker
  server-client
  dashboard
  registry
  boot
  memory
  maintenance
  experiment
  security
```

## Loose File Rule

Every loose `.py`, `.sh`, `.ps1`, `.bat`, `.js`, or `.ts` should answer five questions:

```text
What does it do?
Who calls it?
What state does it read/write?
Is it active?
What replaces it if stale?
```

If it cannot answer those questions, it goes to:

```text
UNKNOWN / needs triage
```

not deletion.

## Clean Read

The missing object is not another folder full of copied scripts.

The missing object is:

```text
one registry that binds spells to tools,
tools to lifecycle,
lifecycle to owners,
owners to runtime surfaces,
and runtime surfaces to evidence.
```

That is the actual GridTools scaffold.

Everything else is just Python confetti with lore accuracy.
