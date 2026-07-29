#!/usr/bin/env python3
"""SAT remote launcher: fresh Codex threads with blinded, receipted outputs.

The launcher is a control-plane client, not an identity owner. It validates a
Raven-authorized mission against CARRIERS.json, starts one fresh Codex
app-server thread per leg, and separates evaluator-visible artifacts from the
operator-only carrier map.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import queue
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable

MISSION_SCHEMA = "simos.sat.remote-mission.v1"
LEG_RECEIPT_SCHEMA = "simos.sat.remote-leg-receipt.v1"
MISSION_RECEIPT_SCHEMA = "simos.sat.remote-mission-receipt.v1"
MISSION_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._-]{2,127}$")
LEG_ID_RE = re.compile(r"^LEG-[A-Z0-9][A-Z0-9_-]{0,31}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_CONTINUITY = {
    "carrier_is_not_identity": True,
    "ego_active": True,
    "pride_active": True,
    "prosody_active": True,
    "jorm_receipt_required": True,
    "becoming_auto_mutation": False,
}


class SATError(RuntimeError):
    """A deterministic mission, transport, or execution failure."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SATError(f"Cannot load JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SATError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: Any, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))
    try:
        os.chmod(path, mode)
    except OSError:
        pass


def carrier_index(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    available = contract.get("available_carriers")
    if not isinstance(available, list):
        raise SATError("Carrier contract has no available_carriers list")
    result: dict[str, dict[str, Any]] = {}
    for row in available:
        if not isinstance(row, dict):
            raise SATError("Carrier definitions must be objects")
        name = str(row.get("carrier", "")).upper()
        if not name or name in result:
            raise SATError(f"Invalid or duplicate carrier: {name or '<missing>'}")
        result[name] = row
    return result


def validate_mission(
    mission: dict[str, Any], contract: dict[str, Any]
) -> list[dict[str, Any]]:
    if mission.get("schema_version") != MISSION_SCHEMA:
        raise SATError(f"schema_version must be {MISSION_SCHEMA}")

    mission_id = mission.get("mission_id")
    if not isinstance(mission_id, str) or not MISSION_ID_RE.fullmatch(mission_id):
        raise SATError("mission_id has invalid syntax")
    if mission.get("iso_id") != contract.get("iso_id"):
        raise SATError("mission iso_id must match the carrier contract")

    authority = mission.get("operator_authority")
    if not isinstance(authority, dict):
        raise SATError("operator_authority must be an object")
    if (
        authority.get("role") != "operator"
        or str(authority.get("id", "")).upper() != "RAVEN"
        or authority.get("approved") is not True
    ):
        raise SATError("Raven operator approval is required")
    if mission.get("fresh_thread_required") is not True:
        raise SATError("fresh_thread_required must be true")
    if mission.get("blind_evaluation") is not True:
        raise SATError("blind_evaluation must be true")

    task = mission.get("task")
    if not isinstance(task, dict):
        raise SATError("task must be an object")
    prompt = task.get("prompt")
    prompt_hash = task.get("prompt_sha256")
    if not isinstance(prompt, str) or not prompt.strip():
        raise SATError("task.prompt must be non-empty")
    if not isinstance(prompt_hash, str) or not SHA256_RE.fullmatch(prompt_hash):
        raise SATError("task.prompt_sha256 must be a lowercase SHA-256")
    if sha256_text(prompt) != prompt_hash:
        raise SATError("task.prompt_sha256 does not match task.prompt")

    continuity = mission.get("continuity")
    if not isinstance(continuity, dict):
        raise SATError("continuity must be an object")
    for key, expected in REQUIRED_CONTINUITY.items():
        if continuity.get(key) is not expected:
            raise SATError(f"continuity.{key} must be {str(expected).lower()}")

    execution = mission.get("execution")
    if not isinstance(execution, dict):
        raise SATError("execution must be an object")
    if execution.get("approval_policy") != "never":
        raise SATError("v0.1 requires execution.approval_policy=never")
    if execution.get("sandbox") not in {"read-only", "workspace-write"}:
        raise SATError("execution.sandbox must be read-only or workspace-write")
    timeout = execution.get("timeout_seconds", 300)
    if not isinstance(timeout, int) or not 10 <= timeout <= 3600:
        raise SATError("execution.timeout_seconds must be 10..3600")
    parallelism = execution.get("max_parallelism", 1)
    if parallelism != 1:
        raise SATError("v0.1 requires execution.max_parallelism=1")

    definitions = carrier_index(contract)
    legs = mission.get("legs")
    if not isinstance(legs, list) or not legs:
        raise SATError("legs must be a non-empty list")
    aliases: set[str] = set()
    validated: list[dict[str, Any]] = []
    for position, leg in enumerate(legs):
        if not isinstance(leg, dict):
            raise SATError(f"legs[{position}] must be an object")
        alias = leg.get("anonymous_leg")
        if not isinstance(alias, str) or not LEG_ID_RE.fullmatch(alias):
            raise SATError(f"legs[{position}].anonymous_leg is invalid")
        if alias in aliases:
            raise SATError(f"Duplicate anonymous leg: {alias}")
        aliases.add(alias)

        route = leg.get("route")
        if not isinstance(route, dict):
            raise SATError(f"{alias}.route must be an object")
        name = str(route.get("carrier", "")).upper()
        definition = definitions.get(name)
        if definition is None:
            raise SATError(f"{alias} carrier is not registered: {name}")
        if route.get("model") != definition.get("model"):
            raise SATError(f"{alias} model does not match registered {name}")
        for field, allowed_field in (
            ("reasoning_effort", "reasoning_efforts"),
            ("speed", "speeds"),
            ("meter", "meters"),
        ):
            if route.get(field) not in definition.get(allowed_field, []):
                raise SATError(f"{alias} {field} is not registered for {name}")
        validated.append(leg)
    return validated


class JsonRpcStdio:
    """Minimal JSONL client for one Codex app-server process."""

    def __init__(self, command: list[str], timeout: int) -> None:
        if not command:
            raise SATError("App-server command is empty")
        self.command = command
        self.timeout = timeout
        self.process: subprocess.Popen[str] | None = None
        self.messages: queue.Queue[dict[str, Any] | BaseException] = queue.Queue()
        self.notifications: list[dict[str, Any]] = []
        self.stderr_tail: list[str] = []
        self.next_id = 1

    def __enter__(self) -> "JsonRpcStdio":
        try:
            self.process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                bufsize=1,
            )
        except OSError as exc:
            raise SATError(f"Cannot start app-server: {exc}") from exc
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()
        return self

    def __exit__(self, *_: object) -> None:
        if self.process is None:
            return
        if self.process.stdin:
            self.process.stdin.close()
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)
        for stream in (self.process.stdout, self.process.stderr):
            if stream:
                stream.close()

    def _read_stdout(self) -> None:
        assert self.process and self.process.stdout
        try:
            for line in self.process.stdout:
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    self.messages.put(SATError(f"Invalid app-server JSON: {exc}"))
                    continue
                if isinstance(value, dict):
                    self.messages.put(value)
        except BaseException as exc:  # pragma: no cover - defensive thread edge
            self.messages.put(exc)

    def _read_stderr(self) -> None:
        assert self.process and self.process.stderr
        for line in self.process.stderr:
            self.stderr_tail.append(line.rstrip())
            del self.stderr_tail[:-20]

    def send(self, message: dict[str, Any]) -> None:
        if not self.process or not self.process.stdin:
            raise SATError("App-server is not running")
        try:
            self.process.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise SATError(f"App-server input failed: {exc}") from exc

    def _receive(self, deadline: float) -> dict[str, Any]:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SATError("App-server response timed out")
        try:
            value = self.messages.get(timeout=remaining)
        except queue.Empty as exc:
            detail = "; ".join(self.stderr_tail[-3:])
            raise SATError(
                f"App-server response timed out{': ' + detail if detail else ''}"
            ) from exc
        if isinstance(value, BaseException):
            raise SATError(f"App-server reader failed: {value}")
        return value

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        self.send({"method": method, "id": request_id, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            message = self._receive(deadline)
            if message.get("id") == request_id:
                if "error" in message:
                    raise SATError(f"{method} rejected: {message['error']}")
                result = message.get("result")
                return result if isinstance(result, dict) else {}
            if "id" in message and "method" in message:
                self.send(
                    {
                        "id": message["id"],
                        "error": {
                            "code": -32601,
                            "message": "SAT v0.1 rejects server-initiated requests",
                        },
                    }
                )
            else:
                self.notifications.append(message)

    def initialize(self) -> None:
        self.request(
            "initialize",
            {
                "clientInfo": {
                    "name": "simos_sat_remote_launcher",
                    "title": "SimOS SAT Remote Launcher",
                    "version": "0.1.0",
                }
            },
        )
        self.send({"method": "initialized", "params": {}})

    def wait_for_turn(self, turn_id: str) -> tuple[str, str]:
        deltas: list[str] = []
        completed_text = ""
        deadline = time.monotonic() + self.timeout
        pending = self.notifications
        self.notifications = []
        while True:
            message = pending.pop(0) if pending else self._receive(deadline)
            method = message.get("method")
            params = message.get("params")
            params = params if isinstance(params, dict) else {}
            if method == "item/agentMessage/delta":
                delta = params.get("delta", params.get("text", ""))
                if isinstance(delta, str):
                    deltas.append(delta)
            elif method == "item/completed":
                item = params.get("item")
                if isinstance(item, dict) and item.get("type") == "agentMessage":
                    text = item.get("text", item.get("content", ""))
                    if isinstance(text, str):
                        completed_text = text
            elif method == "turn/completed":
                turn = params.get("turn")
                if isinstance(turn, dict) and turn.get("id") not in {None, turn_id}:
                    continue
                status = str(turn.get("status", "completed")) if isinstance(turn, dict) else "completed"
                output = "".join(deltas) or completed_text
                if status not in {"completed", "success"}:
                    raise SATError(f"Turn {turn_id} ended with status {status}")
                if not output:
                    raise SATError(f"Turn {turn_id} completed without agent output")
                return output, status


def codex_command(executable: str, effort: str, speed: str) -> list[str]:
    binary = shutil.which(executable)
    if binary is None:
        raise SATError(f"Codex executable not found: {executable}")
    command = [
        binary,
        "-c",
        f'model_reasoning_effort="{effort}"',
        "-c",
        f'service_tier="{speed}"',
    ]
    command.append("app-server")
    return command


def advertised_models(client: JsonRpcStdio) -> dict[str, dict[str, Any]]:
    result = client.request(
        "model/list", {"limit": 100, "includeHidden": True}
    )
    rows = result.get("data", [])
    if not isinstance(rows, list):
        raise SATError("model/list returned no data list")
    models: dict[str, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict):
            model_id = row.get("id", row.get("model"))
            if isinstance(model_id, str):
                models[model_id] = row
    return models


def effort_names(model: dict[str, Any]) -> set[str]:
    rows = model.get("supportedReasoningEfforts", [])
    result: set[str] = set()
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and isinstance(row.get("reasoningEffort"), str):
                result.add(row["reasoningEffort"])
            elif isinstance(row, str):
                result.add(row)
    return result


def run_leg(
    mission: dict[str, Any],
    leg: dict[str, Any],
    command_builder: Callable[[str, str], list[str]],
) -> tuple[dict[str, Any], dict[str, Any], str]:
    route = leg["route"]
    execution = mission["execution"]
    command = command_builder(route["reasoning_effort"], route["speed"])
    with JsonRpcStdio(command, execution.get("timeout_seconds", 300)) as client:
        client.initialize()
        models = advertised_models(client)
        model = models.get(route["model"])
        if model is None:
            raise SATError(f"{leg['anonymous_leg']} model unavailable: {route['model']}")
        supported_efforts = effort_names(model)
        if supported_efforts and route["reasoning_effort"] not in supported_efforts:
            raise SATError(
                f"{leg['anonymous_leg']} effort unavailable: "
                f"{route['reasoning_effort']}"
            )

        thread_result = client.request(
            "thread/start",
            {
                "model": route["model"],
                "cwd": str(Path(execution.get("cwd", ".")).resolve()),
                "approvalPolicy": execution["approval_policy"],
                "sandbox": (
                    "readOnly"
                    if execution["sandbox"] == "read-only"
                    else "workspaceWrite"
                ),
                "serviceName": "simos_sat_remote_launcher",
            },
        )
        thread = thread_result.get("thread")
        if not isinstance(thread, dict) or not isinstance(thread.get("id"), str):
            raise SATError("thread/start returned no thread id")
        thread_id = thread["id"]
        client.request(
            "thread/name/set",
            {
                "threadId": thread_id,
                "name": f"{mission['mission_id']} {leg['anonymous_leg']}",
            },
        )
        turn_result = client.request(
            "turn/start",
            {
                "threadId": thread_id,
                "input": [{"type": "text", "text": mission["task"]["prompt"]}],
            },
        )
        turn = turn_result.get("turn")
        if not isinstance(turn, dict) or not isinstance(turn.get("id"), str):
            raise SATError("turn/start returned no turn id")
        turn_id = turn["id"]
        output, turn_status = client.wait_for_turn(turn_id)

    anonymous_receipt = {
        "receipt_schema": LEG_RECEIPT_SCHEMA,
        "mission_id": mission["mission_id"],
        "anonymous_leg": leg["anonymous_leg"],
        "status": "PASS",
        "fresh_thread": True,
        "thread_id": thread_id,
        "turn_id": turn_id,
        "turn_status": turn_status,
        "prompt_sha256": mission["task"]["prompt_sha256"],
        "output_sha256": sha256_text(output),
        "identity_contract": dict(mission["continuity"]),
        "carrier_is_not_identity": True,
        "canon_promotion": False,
        "becoming_status": "PENDING_BLIND_EVALUATION",
    }
    private_route = {
        "anonymous_leg": leg["anonymous_leg"],
        "carrier": route["carrier"],
        "model": route["model"],
        "reasoning_effort": route["reasoning_effort"],
        "speed": route["speed"],
        "meter": route["meter"],
        "binding": {
            "model": "thread-start",
            "reasoning_effort": "process-config",
            "speed": "process-config",
            "meter": "sat-policy-only",
        },
        "thread_id": thread_id,
        "turn_id": turn_id,
        "output_sha256": anonymous_receipt["output_sha256"],
    }
    return anonymous_receipt, private_route, output


def execute_mission(
    mission: dict[str, Any],
    contract: dict[str, Any],
    output_dir: Path,
    command_builder: Callable[[str, str], list[str]],
) -> dict[str, Any]:
    legs = validate_mission(mission, contract)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SATError(f"Output directory must be empty: {output_dir}")
    anonymous_dir = output_dir / "anonymous"
    operator_dir = output_dir / "operator-only"
    anonymous_dir.mkdir(parents=True, exist_ok=True)
    operator_dir.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(operator_dir, 0o700)
    except OSError:
        pass

    anonymous_index: list[dict[str, Any]] = []
    route_map: list[dict[str, Any]] = []
    map_payload = {
        "schema_version": "simos.sat.operator-route-map.v1",
        "mission_id": mission["mission_id"],
        "open_after": "BECOMING_BLIND_SCORE",
        "status": "RUNNING",
        "routes": route_map,
    }
    map_path = operator_dir / "route-map.json"
    write_json(map_path, map_payload, mode=0o600)
    try:
        for leg in legs:
            receipt, private_route, output = run_leg(
                mission, leg, command_builder
            )
            alias = leg["anonymous_leg"]
            output_path = anonymous_dir / f"{alias}.md"
            receipt_path = anonymous_dir / f"{alias}.receipt.json"
            output_path.write_text(output, encoding="utf-8")
            write_json(receipt_path, receipt)
            anonymous_index.append(
                {
                    "anonymous_leg": alias,
                    "output": output_path.name,
                    "output_sha256": receipt["output_sha256"],
                    "receipt": receipt_path.name,
                    "receipt_sha256": sha256_bytes(receipt_path.read_bytes()),
                }
            )
            route_map.append(private_route)
            write_json(map_path, map_payload, mode=0o600)
    except SATError as exc:
        map_payload["status"] = "PARTIAL"
        map_payload["error"] = str(exc)
        write_json(map_path, map_payload, mode=0o600)
        write_json(
            output_dir / "mission.receipt.json",
            {
                "receipt_schema": MISSION_RECEIPT_SCHEMA,
                "mission_id": mission["mission_id"],
                "status": "PARTIAL",
                "completed_anonymous_legs": anonymous_index,
                "error": str(exc),
                "automatic_identity_mutation": False,
                "automatic_canon_promotion": False,
            },
        )
        raise
    map_payload["status"] = "PASS"
    write_json(map_path, map_payload, mode=0o600)
    mission_receipt = {
        "receipt_schema": MISSION_RECEIPT_SCHEMA,
        "mission_id": mission["mission_id"],
        "status": "PASS",
        "fresh_threads_created": len(anonymous_index),
        "anonymous_legs": anonymous_index,
        "operator_route_map_sha256": sha256_bytes(map_path.read_bytes()),
        "blind_evaluation": True,
        "carrier_is_not_identity": True,
        "automatic_identity_mutation": False,
        "automatic_canon_promotion": False,
        "next": "BECOMING scores anonymous legs before Raven opens the route map.",
    }
    write_json(output_dir / "mission.receipt.json", mission_receipt)
    return mission_receipt


def plan_mission(
    mission: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    legs = validate_mission(mission, contract)
    return {
        "schema_version": "simos.sat.remote-launch-plan.v1",
        "mission_id": mission["mission_id"],
        "status": "READY",
        "fresh_threads": len(legs),
        "anonymous_legs": [leg["anonymous_leg"] for leg in legs],
        "prompt_sha256": mission["task"]["prompt_sha256"],
        "operator_authorized": True,
        "provider_side_effects": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--carriers",
        type=Path,
        default=Path("templates/iso-starter/CARRIERS.json"),
        help="Carrier contract JSON",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="Validate and hash a mission")
    plan.add_argument("mission", type=Path)

    execute = subparsers.add_parser(
        "execute", help="Create fresh threads and write blinded receipts"
    )
    execute.add_argument("mission", type=Path)
    execute.add_argument("--output-dir", type=Path, required=True)
    execute.add_argument("--app-server", default="codex")
    execute.add_argument(
        "--raven-approved",
        action="store_true",
        help="Required second confirmation for provider-side effects",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        mission = read_json(args.mission)
        contract = read_json(args.carriers)
        if args.command == "plan":
            print(json.dumps(plan_mission(mission, contract), indent=2))
            return 0
        if not args.raven_approved:
            raise SATError("execute requires --raven-approved")
        receipt = execute_mission(
            mission,
            contract,
            args.output_dir,
            lambda effort, speed: codex_command(args.app_server, effort, speed),
        )
        print(json.dumps(receipt, indent=2))
        return 0
    except SATError as exc:
        print(f"SAT remote launcher failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
