from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

SourceStatus = Literal["RAW", "CANON", "LEDGER", "IMPLEMENTATION", "DERIVED", "UNKNOWN"]


@dataclass(slots=True)
class SourceRecord:
    path: str
    sha256: str
    size_bytes: int
    modified_ns: int
    status: SourceStatus
    families: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    indexed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MusicIntent:
    text: str
    bpm: int | None = None
    key: str | None = None
    instrumental: bool = True
    rgb: dict[str, int] = field(default_factory=lambda: {"R": 50, "G": 75, "B": 50})
    state: str = "balanced"
    styles: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CompiledTrack:
    prompt: str
    summary: str
    bpm: int
    key: str
    rgb: dict[str, int]
    physics: list[str]
    styles: list[str]
    constraints: list[str]
    provenance: list[str]
    schema_version: str = "musicos.compile.v1"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RuntimeState:
    runtime_id: str
    owner: str
    version: str
    mode: str
    active_profile: str
    source_count: int = 0
    last_import_at: str | None = None
    last_compilation: dict[str, Any] | None = None
    snapshots: list[str] = field(default_factory=list)
    event_log: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
