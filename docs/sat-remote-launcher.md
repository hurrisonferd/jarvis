# SAT Remote Launcher v0.1

## Purpose

SAT Remote Launcher closes the gap between a validated carrier plan and a real,
fresh execution context.

SAT already has the correct supervisory law:

> Parallelism may multiply capability; it may not merge identity or hide activity.

The launcher adds one native execution seam:

```text
SAT manifest
→ capability discovery
→ isolated executor thread
→ frozen task packet
→ separately attributed artifact
→ completion receipt
→ blind BECOMING review
→ Raven decision
```

## Supervisor and executor split

| Layer | Authority |
|---|---|
| Raven | Approves execution and remains final authority |
| SAT | Validates, launches, monitors, attributes, and receipts |
| Carrier | Supplies bounded model capability |
| Executor | Performs the frozen task in a fresh thread |
| BECOMING | Compares anonymous results without auto-mutation |
| JORM | Preserves the event and path home |

An executor may be deliberately simple. It receives a bounded prompt and
returns an artifact. It does not need authority over task decomposition,
identity, persistence, evaluation, or promotion because SAT retains those
supervisory functions.

## Why App Server

Codex App Server exposes the native lifecycle SAT needs:

- `model/list` discovers the host's actual models and reasoning efforts;
- `thread/start` creates a fresh conversation;
- `turn/start` submits the frozen task;
- streamed item and turn events expose progress and completion;
- stored thread IDs provide continuation and audit handles.

The launcher uses the authenticated Codex host. It does not call the OpenAI API
and does not store an API key.

The `probe` command performs discovery and mission-route validation without
calling `thread/start`, so Raven can verify the host before any provider-side
thread exists.

## Cloud-first boundary

Git/Supabase remain canonical for manifests, receipts, and accepted state. A
Codex host is an execution body. Losing that host cannot redefine SAT, an ISO,
or canon.

The first adapter uses local stdio because it is the smallest stable App Server
transport. A later authenticated WSS adapter may connect a cloud SAT control
plane to an always-on host, but experimental remote transport is not claimed by
v0.1.

## Capability binding

| Requested property | v0.1 binding |
|---|---|
| Carrier/model | `thread/start.model` after `model/list` confirmation |
| Reasoning effort | one-run `model_reasoning_effort` process override |
| Speed | one-run `service_tier` process override |
| Meter | SAT policy metadata only |
| Freshness | new `thread/start` for every leg |
| Blindness | carrier map separated from evaluator-visible files |

If a model or reasoning effort is absent, SAT fails before creating the task
turn. The launcher never silently substitutes another carrier.

## Failure law

SAT fails closed when:

- Raven approval is absent;
- the mission or prompt hash changes;
- the ISO and carrier contract disagree;
- a carrier route is unregistered;
- the host does not advertise the requested model or reasoning effort;
- fresh-thread or blind-evaluation requirements are disabled;
- an output directory contains earlier artifacts;
- App Server requests an unsupported interactive approval;
- a turn fails, times out, or completes without output.

A partial run writes a partial receipt and preserves completed anonymous legs.
It does not relabel partial execution as mission success.

## Growth path

1. Run the deterministic fake-server test.
2. Probe a real authenticated host with the three registered carriers.
3. Execute `ATOM-CARRIER-BLIND-002`.
4. Let BECOMING score anonymous legs before route decode.
5. Add authenticated remote transport only after the local lifecycle is
   receipted and Raven accepts the result.
