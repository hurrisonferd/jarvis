from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import RuntimeState


class StateStore:
    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / "data"
        self.state_path = self.data_dir / "runtime-state.json"
        self.snapshots_dir = self.data_dir / "snapshots"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> RuntimeState:
        if not self.state_path.exists():
            state = RuntimeState(
                runtime_id="musicos-portable-v1",
                owner="Raven / John Barber",
                version="1.0.0",
                mode="local-portable",
                active_profile="raven-main",
            )
            self.save(state)
            return state
        raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        return RuntimeState(**raw)

    def save(self, state: RuntimeState) -> None:
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(state), indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.state_path)

    def event(self, state: RuntimeState, event_type: str, payload: dict) -> None:
        state.event_log.append({
            "time": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "payload": payload,
        })
        state.event_log = state.event_log[-500:]
        self.save(state)

    def snapshot(self, state: RuntimeState, name: str) -> Path:
        safe = "".join(c for c in name if c.isalnum() or c in "-_ ").strip().replace(" ", "-") or "snapshot"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.snapshots_dir / f"{stamp}-{safe}.json"
        path.write_text(json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8")
        state.snapshots.append(path.name)
        state.snapshots = state.snapshots[-10:]
        self.event(state, "SNAPSHOT_CREATED", {"path": str(path)})
        return path
