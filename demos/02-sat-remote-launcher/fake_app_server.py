#!/usr/bin/env python3
"""Deterministic JSONL fixture for SAT remote-launcher tests."""

from __future__ import annotations

import json
import sys

MODELS = [
    {
        "id": model,
        "model": model,
        "supportedReasoningEfforts": [
            {"reasoningEffort": "medium"},
            {"reasoningEffort": "max"},
        ],
    }
    for model in ("gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna")
]


def send(value: dict) -> None:
    print(json.dumps(value), flush=True)


for raw in sys.stdin:
    message = json.loads(raw)
    method = message.get("method")
    request_id = message.get("id")
    if request_id is None:
        continue
    if method == "initialize":
        send({"id": request_id, "result": {"platformFamily": "test"}})
    elif method == "model/list":
        send({"id": request_id, "result": {"data": MODELS, "nextCursor": None}})
    elif method == "thread/start":
        send(
            {
                "id": request_id,
                "result": {"thread": {"id": "thr_fixture", "sessionId": "thr_fixture"}},
            }
        )
    elif method == "thread/name/set":
        send({"id": request_id, "result": {}})
    elif method == "turn/start":
        send({"id": request_id, "result": {"turn": {"id": "turn_fixture"}}})
        send(
            {
                "method": "item/agentMessage/delta",
                "params": {
                    "delta": "CONFIRMED: The artifact is reviewable. "
                },
            }
        )
        send(
            {
                "method": "item/agentMessage/delta",
                "params": {
                    "delta": "REJECT: Identity rewrite, PRIDE bypass, and automatic canon promotion."
                },
            }
        )
        send(
            {
                "method": "turn/completed",
                "params": {
                    "turn": {"id": "turn_fixture", "status": "completed"}
                },
            }
        )
    else:
        send(
            {
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"},
            }
        )
