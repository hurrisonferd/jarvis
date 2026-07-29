#!/usr/bin/env python3
"""SAT ChatLink v0.1: brokered, durable chat-to-chat messaging."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows stays single-writer
    fcntl = None

SCHEMA_VERSION = "sat.chatlink.v0.1"
MESSAGE_TYPES = {
    "NOTE", "REQUEST", "RESPONSE", "HANDOFF", "ACK", "BLOCKER",
    "HEARTBEAT", "RECEIPT",
}
VISIBILITIES = {"PUBLIC", "GRID", "CHANNEL", "OPERATOR_ONLY", "PRIVATE_REFERENCE"}
SATELLITE_STATUSES = {"ACTIVE", "PAUSED", "OFF"}
IDENTITY_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{0,63}$")
MAX_BODY_BYTES = 8_000
GENESIS_HASH = "0" * 64


class ChatLinkError(ValueError):
    """Contract violation."""


class CapacityError(ChatLinkError):
    """Active-satellite policy cap reached."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_identity(value: str, field: str = "identity") -> str:
    normalized = value.strip().upper()
    if not IDENTITY_RE.fullmatch(normalized):
        raise ChatLinkError(f"{field} has an invalid identity: {value!r}")
    return normalized


def dm_channel(first: str, second: str) -> str:
    members = sorted(
        {normalize_identity(first, "first"), normalize_identity(second, "second")}
    )
    if len(members) != 2:
        raise ChatLinkError("DM requires two different participants")
    return f"DM:{members[0]}:{members[1]}"


def room_channel(mission_id: str) -> str:
    return f"ROOM:{normalize_identity(mission_id, 'mission_id')}"


class ChatLink:
    """Filesystem-backed SAT message broker."""

    def __init__(self, state_dir: Path | str, max_active_satellites: int = 4):
        self.root = Path(state_dir)
        if max_active_satellites < 1:
            raise ChatLinkError("max_active_satellites must be positive")
        self.max_active_satellites = max_active_satellites
        for name in ("channels", "logs", "cursors"):
            (self.root / name).mkdir(parents=True, exist_ok=True)

    @property
    def satellites_path(self) -> Path:
        return self.root / "satellites.json"

    def _key(self, value: str) -> str:
        return sha256(value.encode("utf-8"))

    def _manifest_path(self, channel_id: str) -> Path:
        return self.root / "channels" / f"{self._key(channel_id)}.json"

    def _log_path(self, channel_id: str) -> Path:
        return self.root / "logs" / f"{self._key(channel_id)}.jsonl"

    def _cursor_path(self, channel_id: str, participant: str) -> Path:
        directory = self.root / "cursors" / self._key(participant)
        directory.mkdir(parents=True, exist_ok=True)
        return directory / f"{self._key(channel_id)}.json"

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _atomic_json(self, path: Path, value: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(temp_name)

    def register_satellite(
        self, satellite_id: str, iso: str, thread_id: str, status: str = "ACTIVE"
    ) -> dict[str, Any]:
        satellite_id = normalize_identity(satellite_id, "satellite_id")
        iso = normalize_identity(iso, "iso")
        status = status.strip().upper()
        if status not in SATELLITE_STATUSES:
            raise ChatLinkError(f"unsupported satellite status: {status}")
        records = self._read_json(self.satellites_path, {})
        active_others = sum(
            1 for key, value in records.items()
            if key != satellite_id and value["status"] == "ACTIVE"
        )
        if status == "ACTIVE" and active_others >= self.max_active_satellites:
            raise CapacityError(
                f"SAT policy cap is {self.max_active_satellites} active satellites; "
                "pause one or raise the configured cap"
            )
        record = {
            "satellite_id": satellite_id,
            "iso": iso,
            "thread_id": thread_id,
            "status": status,
            "updated_at": now_utc(),
        }
        records[satellite_id] = record
        self._atomic_json(self.satellites_path, records)
        return record

    def create_channel(
        self, channel_id: str, participants: Iterable[str], created_by: str = "RAVEN"
    ) -> dict[str, Any]:
        participants = sorted(
            {normalize_identity(item, "participant") for item in participants}
        )
        created_by = normalize_identity(created_by, "created_by")
        if channel_id.startswith("DM:"):
            if len(participants) != 2 or channel_id != dm_channel(*participants):
                raise ChatLinkError("DM id must be canonical and match participants")
            kind, mission_id = "DM", None
        elif channel_id.startswith("ROOM:"):
            mission_id = normalize_identity(channel_id[5:], "mission_id")
            channel_id = room_channel(mission_id)
            if len(participants) < 2:
                raise ChatLinkError("ROOM requires at least two participants")
            kind = "ROOM"
        else:
            raise ChatLinkError("channel id must start with DM: or ROOM:")
        path = self._manifest_path(channel_id)
        proposed = {
            "schema_version": SCHEMA_VERSION,
            "channel_id": channel_id,
            "kind": kind,
            "mission_id": mission_id,
            "participants": participants,
            "created_by": created_by,
        }
        if path.exists():
            existing = self._read_json(path, {})
            if {key: existing.get(key) for key in proposed} != proposed:
                raise ChatLinkError("channel already exists with a different contract")
            return existing
        proposed["created_at"] = now_utc()
        self._atomic_json(path, proposed)
        return proposed

    def channel(self, channel_id: str) -> dict[str, Any]:
        path = self._manifest_path(channel_id)
        if not path.exists():
            raise ChatLinkError(f"unknown channel: {channel_id}")
        return self._read_json(path, {})

    def _events_unlocked(self, channel_id: str) -> list[dict[str, Any]]:
        path = self._log_path(channel_id)
        if not path.exists():
            return []
        events = []
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1
        ):
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ChatLinkError(
                        f"corrupt channel log at line {line_number}"
                    ) from error
        return events

    def _validate_message(
        self, channel: dict[str, Any], sender: str, message_type: str, body: str,
        visibility: str, recipients: list[str], artifact_sha256: str | None,
    ) -> None:
        if sender not in channel["participants"]:
            raise ChatLinkError(f"{sender} is not a channel participant")
        if message_type not in MESSAGE_TYPES:
            raise ChatLinkError(f"unsupported message type: {message_type}")
        if visibility not in VISIBILITIES:
            raise ChatLinkError(f"unsupported visibility: {visibility}")
        if len(body.encode("utf-8")) > MAX_BODY_BYTES:
            raise ChatLinkError(f"message body exceeds {MAX_BODY_BYTES} bytes")
        unknown = sorted(set(recipients) - set(channel["participants"]))
        if unknown:
            raise ChatLinkError(f"recipients are not channel participants: {unknown}")
        if visibility == "PRIVATE_REFERENCE":
            if not artifact_sha256 or not re.fullmatch(r"[0-9a-fA-F]{64}", artifact_sha256):
                raise ChatLinkError("PRIVATE_REFERENCE requires an artifact SHA-256")
            if len(body.encode("utf-8")) > 240:
                raise ChatLinkError(
                    "PRIVATE_REFERENCE body must be a short non-sensitive summary"
                )

    def send(
        self, channel_id: str, sender: str, from_thread: str, message_type: str,
        body: str, *, message_id: str | None = None,
        recipients: Iterable[str] | None = None, visibility: str = "CHANNEL",
        consent: str = "RAVEN_AUTHORIZED", causal_parent: str | None = None,
        artifact_sha256: str | None = None, ack_required: bool = False,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        channel = self.channel(channel_id)
        sender = normalize_identity(sender, "sender")
        message_type, visibility = message_type.strip().upper(), visibility.strip().upper()
        recipients = (
            sorted({normalize_identity(item, "recipient") for item in recipients})
            if recipients else list(channel["participants"])
        )
        self._validate_message(
            channel, sender, message_type, body, visibility, recipients, artifact_sha256
        )
        supplied = {
            "schema_version": SCHEMA_VERSION,
            "channel_id": channel_id,
            "mission_id": channel["mission_id"],
            "from_iso": sender,
            "from_thread": from_thread,
            "to": recipients,
            "type": message_type,
            "body": body,
            "body_sha256": sha256(body.encode("utf-8")),
            "artifact_sha256": artifact_sha256,
            "causal_parent": causal_parent,
            "visibility": visibility,
            "consent": consent,
            "ack_required": bool(ack_required),
            "created_at": created_at or now_utc(),
        }
        if message_id is None:
            message_id = f"MSG-{sha256(canonical_json(supplied))[:24].upper()}"
        supplied["message_id"] = message_id

        log_path = self._log_path(channel_id)
        with log_path.open("a+", encoding="utf-8") as handle:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            handle.seek(0)
            events = [json.loads(line) for line in handle if line.strip()]
            for event in events:
                if event["message_id"] == message_id:
                    keys = set(supplied) - {"created_at"}
                    if {k: event.get(k) for k in keys} != {
                        k: supplied.get(k) for k in keys
                    }:
                        raise ChatLinkError(
                            "message_id already exists with different content"
                        )
                    return event
            event = dict(supplied)
            event["sequence"] = len(events) + 1
            event["previous_event_sha256"] = (
                events[-1]["event_sha256"] if events else GENESIS_HASH
            )
            event["event_sha256"] = sha256(canonical_json(event))
            handle.seek(0, os.SEEK_END)
            handle.write(canonical_json(event).decode("utf-8") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            return event

    def poll(
        self, channel_id: str, participant: str, *, limit: int = 100,
        advance: bool = True,
    ) -> list[dict[str, Any]]:
        channel = self.channel(channel_id)
        participant = normalize_identity(participant, "participant")
        if participant not in channel["participants"]:
            raise ChatLinkError(f"{participant} is not a channel participant")
        if limit < 1:
            raise ChatLinkError("limit must be positive")
        cursor_path = self._cursor_path(channel_id, participant)
        cursor = self._read_json(cursor_path, {"last_seen_sequence": 0})
        events = [
            event for event in self._events_unlocked(channel_id)
            if event["sequence"] > cursor["last_seen_sequence"]
            and participant in event["to"]
        ][:limit]
        if advance and events:
            self._atomic_json(
                cursor_path,
                {
                    "channel_id": channel_id,
                    "participant": participant,
                    "last_seen_sequence": events[-1]["sequence"],
                    "updated_at": now_utc(),
                },
            )
        return events

    def ack(
        self, channel_id: str, participant: str, from_thread: str, message_id: str
    ) -> dict[str, Any]:
        source = next(
            (event for event in self._events_unlocked(channel_id)
             if event["message_id"] == message_id),
            None,
        )
        if source is None:
            raise ChatLinkError(f"unknown message_id: {message_id}")
        participant = normalize_identity(participant)
        return self.send(
            channel_id, participant, from_thread, "ACK", "ACK",
            message_id=f"ACK:{participant}:{message_id}",
            recipients=[source["from_iso"]], causal_parent=message_id,
        )

    def verify(self, channel_id: str) -> dict[str, Any]:
        self.channel(channel_id)
        previous = GENESIS_HASH
        events = self._events_unlocked(channel_id)
        for expected_sequence, event in enumerate(events, 1):
            if event.get("sequence") != expected_sequence:
                raise ChatLinkError(f"sequence break at {expected_sequence}")
            if event.get("previous_event_sha256") != previous:
                raise ChatLinkError(f"hash-chain break at {expected_sequence}")
            claimed = event.get("event_sha256")
            unsigned = dict(event)
            unsigned.pop("event_sha256", None)
            if claimed != sha256(canonical_json(unsigned)):
                raise ChatLinkError(f"event hash mismatch at {expected_sequence}")
            previous = claimed
        return {
            "ok": True, "channel_id": channel_id, "events": len(events),
            "head_sha256": previous,
        }


def json_out(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", required=True, type=Path)
    parser.add_argument("--max-active", type=int, default=4)
    commands = parser.add_subparsers(dest="command", required=True)

    register = commands.add_parser("register")
    register.add_argument("satellite_id")
    register.add_argument("iso")
    register.add_argument("thread_id")
    register.add_argument("--status", default="ACTIVE")

    create = commands.add_parser("create")
    create.add_argument("channel_id")
    create.add_argument("participants", nargs="+")
    create.add_argument("--created-by", default="RAVEN")

    send = commands.add_parser("send")
    send.add_argument("channel_id")
    send.add_argument("sender")
    send.add_argument("from_thread")
    send.add_argument("message_type")
    send.add_argument("body")
    send.add_argument("--to", nargs="*")
    send.add_argument("--message-id")
    send.add_argument("--visibility", default="CHANNEL")
    send.add_argument("--causal-parent")
    send.add_argument("--artifact-sha256")
    send.add_argument("--ack-required", action="store_true")

    poll = commands.add_parser("poll")
    poll.add_argument("channel_id")
    poll.add_argument("participant")
    poll.add_argument("--limit", type=int, default=100)
    poll.add_argument("--peek", action="store_true")

    ack = commands.add_parser("ack")
    ack.add_argument("channel_id")
    ack.add_argument("participant")
    ack.add_argument("from_thread")
    ack.add_argument("message_id")

    verify = commands.add_parser("verify")
    verify.add_argument("channel_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    link = ChatLink(args.state_dir, args.max_active)
    try:
        if args.command == "register":
            result = link.register_satellite(
                args.satellite_id, args.iso, args.thread_id, args.status
            )
        elif args.command == "create":
            result = link.create_channel(
                args.channel_id, args.participants, args.created_by
            )
        elif args.command == "send":
            result = link.send(
                args.channel_id, args.sender, args.from_thread, args.message_type,
                args.body, message_id=args.message_id, recipients=args.to,
                visibility=args.visibility, causal_parent=args.causal_parent,
                artifact_sha256=args.artifact_sha256,
                ack_required=args.ack_required,
            )
        elif args.command == "poll":
            result = link.poll(
                args.channel_id, args.participant, limit=args.limit,
                advance=not args.peek,
            )
        elif args.command == "ack":
            result = link.ack(
                args.channel_id, args.participant, args.from_thread, args.message_id
            )
        else:
            result = link.verify(args.channel_id)
        json_out(result)
        return 0
    except ChatLinkError as error:
        json_out({"ok": False, "error": str(error)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
