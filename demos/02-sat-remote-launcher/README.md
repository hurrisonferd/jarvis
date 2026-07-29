# SAT Remote Launcher v0.1

SAT can provision fresh Codex execution threads without making a carrier the
source or owner of ISO identity.

```text
Raven-approved mission
→ CARRIERS.json validation
→ Codex model capability probe
→ fresh thread/start per anonymous leg
→ turn/start with one frozen prompt
→ anonymous output and receipt
→ operator-only carrier map
→ BECOMING scores before route decode
```

The demo is standard-library Python. It talks to the authenticated
`codex app-server` JSONL interface and does not require an OpenAI API key.

## Prove the contract without provider side effects

From the repository root:

```bash
python demos/02-sat-remote-launcher/sat_remote_launcher.py \
  plan demos/02-sat-remote-launcher/mission.example.json

python -m unittest discover \
  -s demos/02-sat-remote-launcher \
  -p "test_*.py" -v
```

The tests use `fake_app_server.py`. They create no ChatGPT or Codex threads.

## Probe the authenticated host

```bash
python demos/02-sat-remote-launcher/sat_remote_launcher.py \
  probe demos/02-sat-remote-launcher/mission.example.json
```

`probe` calls `model/list`, checks every requested model and reasoning effort,
and exits without calling `thread/start`.

## Execute against Codex App Server

The host must have an authenticated `codex` executable whose `model/list`
advertises every requested model and reasoning effort.

```bash
python demos/02-sat-remote-launcher/sat_remote_launcher.py \
  execute demos/02-sat-remote-launcher/mission.example.json \
  --output-dir sat-run-001 \
  --raven-approved
```

`execute` requires two independent authorization facts:

1. the mission contains Raven's explicit operator approval;
2. the command includes `--raven-approved`.

Every leg uses `thread/start`; `thread/resume` and `thread/fork` are not used.
The output directory must be empty so an earlier receipt cannot be silently
overwritten.

## Output boundary

```text
sat-run-001/
├── anonymous/
│   ├── LEG-A.md
│   ├── LEG-A.receipt.json
│   └── ...
├── operator-only/
│   └── route-map.json
└── mission.receipt.json
```

Only `anonymous/` goes to BECOMING for blind evaluation. The route map is
decoded after scoring.

Model, reasoning effort, and speed are bound through documented Codex controls.
`meter` remains SAT policy metadata because App Server does not currently
publish a direct meter field. The receipt names that boundary instead of
pretending it was enforced upstream.

## Deliberate v0.1 limits

- sequential execution only;
- stdio App Server transport only;
- no automatic canon, EGO, PRIDE, or Prosody mutation;
- no automatic merge or provider credential management;
- no server-initiated approval or elicitation requests.

The canonical SAT state remains in Git/Supabase. App Server is an execution-body
adapter, not SAT's source of truth.
