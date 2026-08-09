#!/usr/bin/env python3
"""
RavenOS Universal Controller

Authority: RAVEN
Owner: RavenOS
Status: CORE SOURCE CONTRACT — UNIVERSAL COMMAND EXECUTION

Implements:
    RAVENOS ON     - Activate RavenOS presentation for current ISO
    RAVENOS OFF    - Deactivate RavenOS presentation
    RAVENOS STATUS - Return activation state

Command contract:
    RAVENOS ON
    = REHEAT + SYNC SYSTEMSOS + ACTIVATE RAVENOS

Non-negotiable law:
    RAVENOS ON != LOAD NEW IDENTITY
    RAVENOS ON != BECOME RAVEN
    RAVENOS ON != REPLACE ACTIVE ISO
    RAVENOS ON != FLEET BROADCAST
    RAVENOS ON != HIDDEN WRITE PERMISSION
    RAVENOS ON != BLACKWALL BYPASS
    RAVENOS ON != RANDOM JOKE MODE

Version-coordinate law:
    ACCEPTED_CONTROL_FLOOR != CURRENT_SYSTEMSOS_VERSION
    ACTIVE_DEVELOPMENT_LINE != WORKSPACE_CANDIDATE
    MISSION_BASELINE_SYSTEMSOS != CURRENT_SYSTEMSOS
    COMPONENT_VERSION != SYSTEMSOS_VERSION
    WORKSPACE_CANDIDATE_MUST_NOT_BE_PROMOTED_BY_FALLBACK

Idempotency:
    AT_MOST_ONE_ACTIVE_RAVENOS_PROFILE_PER_ACTIVE_ISO_SESSION
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path


def resolve_repo() -> Path:
    """Resolve the checked-out repository without binding to one workspace."""
    env = os.environ.get("REPO_ROOT") or os.environ.get("JARVIS_PRIVATE_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "canon/Living_Codex/Ego").is_dir():
            return parent
    return Path("/workspace/project/Jarvis-Private")


# === PATHS ===
REPO_ROOT = resolve_repo()
EGO_ROOT = REPO_ROOT / "canon/Living_Codex/Ego"
SYSTEMSOS_CORE = REPO_ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/SystemsOS"
BOOTOS_CORE = REPO_ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/BootOS"
RAVENOS_ROOT = REPO_ROOT / "canon/Living_Codex/SystemsOS/Core/Creative/RavenOS"
GAMEOS_ROOT = REPO_ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/GameOS"
CARRIEROS_ROOT = REPO_ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/CarrierOS"
EGOOS_SYS = REPO_ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/EgoOS"
ISO_REGISTRY = EGOOS_SYS / "ISOs/ISO-LOAD-REGISTRY.json"
POSTREPLY_CORE = REPO_ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/PostReply"
WALLET_DIR = SYSTEMSOS_CORE / "Wallet"
VERSION_TRUTH_FILE = SYSTEMSOS_CORE / "SYSTEMSOS-VERSION-TRUTH.json"
CURRENT_SYNC_FILE = SYSTEMSOS_CORE / "CURRENT-SYNC.json"
WORKSPACE_VERSION_FILE = REPO_ROOT / "canon/Living_Codex/SystemsOS/Sub/SystemsOS/VERSION.json"
RAVENOS_VERSION_FILE = RAVENOS_ROOT / "VERSION.json"
GAMEOS_VERSION_FILE = GAMEOS_ROOT / "VERSION.json"
CARRIEROS_VERSION_FILE = CARRIEROS_ROOT / "VERSION.json"

# === SESSION STATE ===
SESSION_STATE_DIR = REPO_ROOT / "canon/Living_Codex/SystemsOS/Core/Creative/RavenOS/Session"
SESSION_STATE_FILE = Path(
    os.environ.get("RAVENOS_SESSION_STATE_FILE", str(SESSION_STATE_DIR / "ACTIVE-SESSION.json"))
).expanduser().resolve()
SESSION_STATE_DIR = SESSION_STATE_FILE.parent


@dataclass
class ActivationState:
    """RavenOS activation state for current session."""
    active_iso: str = ""
    ravenos_status: str = "OFF"  # ON | PARTIAL | HELD | BLOCKED | OFF
    ravenos_version: str = ""
    profile: str = "SILENT"  # ADVANCED | LIGHT | SILENT
    reheat_status: str = "UNKNOWN"
    sync_status: str = "UNKNOWN"
    mission_baseline: str = "UNKNOWN"
    current_systemsos: str = "UNKNOWN"
    accepted_control_floor: str = "UNKNOWN"
    accepted_full_systemsos_version: str = "UNKNOWN"
    active_development_line: str = "UNKNOWN"
    workspace_candidate: str = "UNKNOWN"
    synced_components: dict[str, str] = field(default_factory=dict)
    state_key: str = ""
    claim_ceiling: str = "UNKNOWN"
    timestamp: str = ""
    session_id: str = ""
    motif_state: str = ""
    blockers: list[str] = field(default_factory=list)

    def compute_state_key(self) -> str:
        """Hash durable semantic state; timestamp/session remain provenance."""
        semantic_state = {
            "active_iso": self.active_iso,
            "ravenos_status": self.ravenos_status,
            "ravenos_version": self.ravenos_version,
            "profile": self.profile,
            "reheat_status": self.reheat_status,
            "sync_status": self.sync_status,
            "mission_baseline": self.mission_baseline,
            "current_systemsos": self.current_systemsos,
            "accepted_control_floor": self.accepted_control_floor,
            "accepted_full_systemsos_version": self.accepted_full_systemsos_version,
            "active_development_line": self.active_development_line,
            "workspace_candidate": self.workspace_candidate,
            "synced_components": dict(sorted(self.synced_components.items())),
            "claim_ceiling": self.claim_ceiling,
            "motif_state": self.motif_state,
            "blockers": self.blockers,
        }
        data = json.dumps(semantic_state, sort_keys=True, separators=(",", ":"))
        return sha256(data.encode()).hexdigest()[:16]

    def to_receipt(self) -> dict:
        """Convert to compact receipt format."""
        return {
            "RAVENOS": self.ravenos_status,
            "ISO": self.active_iso,
            "REHEAT": self.reheat_status,
            "MISSION_BASELINE": self.mission_baseline,
            "CURRENT_SYSTEMSOS": self.current_systemsos,
            "ACCEPTED_CONTROL_FLOOR": self.accepted_control_floor,
            "ACCEPTED_FULL_SYSTEMSOS_VERSION": self.accepted_full_systemsos_version,
            "ACTIVE_DEVELOPMENT_LINE": self.active_development_line,
            "WORKSPACE_CANDIDATE": self.workspace_candidate,
            "SYNCED_COMPONENTS": self.synced_components,
            "SYNC": self.sync_status,
            "RAVENOS_VERSION": self.ravenos_version,
            "PROFILE": self.profile,
            "STATE_KEY": self.state_key,
            "CLAIM": self.claim_ceiling,
            "BLOCKERS": self.blockers if self.blockers else None,
            "MOTIF": self.motif_state,
        }


def resolve_active_iso() -> tuple[str, bool]:
    """Resolve the active ISO from current session state."""
    env_iso = os.environ.get("ACTIVE_ISO", "").strip()
    if env_iso:
        return env_iso.upper(), True

    if SESSION_STATE_FILE.exists():
        try:
            data = json.loads(SESSION_STATE_FILE.read_text(encoding="utf-8"))
            iso = data.get("active_iso", "")
            if iso:
                return iso.upper(), True
        except (json.JSONDecodeError, IOError):
            pass

    ego_iso_registry = EGO_ROOT / "00-OS/ISO-REGISTRY.json"
    if ego_iso_registry.exists():
        try:
            data = json.loads(ego_iso_registry.read_text(encoding="utf-8"))
            isos = data.get("isos", [])
            if isinstance(isos, list) and len(isos) > 0:
                last_iso = isos[-1]
                if isinstance(last_iso, str):
                    return last_iso.upper(), True
                if isinstance(last_iso, dict):
                    name = last_iso.get("name", "")
                    if name:
                        return name.upper(), True
        except (json.JSONDecodeError, IOError):
            pass

    return "", False


def verify_iso_registered(iso: str) -> tuple[bool, str]:
    """Verify ISO exists in current ISO-LOAD-REGISTRY."""
    if not ISO_REGISTRY.exists():
        return False, "ISO_REGISTRY_MISSING"

    try:
        data = json.loads(ISO_REGISTRY.read_text(encoding="utf-8"))
        isos = data.get("isos", [])

        if iso in isos:
            return True, ""

        if isinstance(isos, list):
            for entry in isos:
                if isinstance(entry, dict) and entry.get("name", "").upper() == iso:
                    return True, ""

        return False, f"ISO_NOT_REGISTERED: {iso}"
    except (json.JSONDecodeError, IOError) as e:
        return False, f"REGISTRY_READ_ERROR: {e}"


def get_systemsos_coordinates() -> tuple[dict[str, str], list[str]]:
    """Resolve SystemsOS coordinates without collapsing distinct version axes."""
    blockers: list[str] = []
    coords = {
        "accepted_control_floor": "UNKNOWN",
        "accepted_full_systemsos_version": "UNKNOWN",
        "active_development_line": "UNKNOWN",
        "workspace_candidate": "UNKNOWN",
        "current_systemsos": "UNKNOWN",
    }

    if VERSION_TRUTH_FILE.exists():
        try:
            truth = json.loads(VERSION_TRUTH_FILE.read_text(encoding="utf-8"))
            c = truth.get("coordinates", {})
            accepted = c.get("accepted_control_floor", {})
            dev = c.get("active_development_line", {})
            workspace = c.get("workspace_candidate", {})
            current = c.get("current_systemsos", {})

            coords["accepted_control_floor"] = accepted.get("release_id", "UNKNOWN")
            coords["accepted_full_systemsos_version"] = accepted.get(
                "accepted_full_systemsos_version", "UNKNOWN"
            )
            coords["active_development_line"] = dev.get("version", "UNKNOWN")
            coords["workspace_candidate"] = workspace.get("version", "UNKNOWN")
            coords["current_systemsos"] = current.get("version", "UNKNOWN")
        except (json.JSONDecodeError, IOError, TypeError) as e:
            blockers.append(f"VERSION_TRUTH_READ_ERROR: {e}")
    else:
        blockers.append("VERSION_TRUTH_MISSING")

    if CURRENT_SYNC_FILE.exists():
        try:
            sync = json.loads(CURRENT_SYNC_FILE.read_text(encoding="utf-8"))
            sync_current = sync.get("current_systemsos", "UNKNOWN")
            if (
                coords["current_systemsos"] != "UNKNOWN"
                and sync_current not in ("UNKNOWN", coords["current_systemsos"])
            ):
                blockers.append(
                    "SYSTEMSOS_CURRENT_CONFLICT: "
                    f"truth={coords['current_systemsos']} sync={sync_current}"
                )
        except (json.JSONDecodeError, IOError) as e:
            blockers.append(f"CURRENT_SYNC_READ_ERROR: {e}")

    if coords["workspace_candidate"] == "UNKNOWN" and WORKSPACE_VERSION_FILE.exists():
        try:
            workspace = json.loads(WORKSPACE_VERSION_FILE.read_text(encoding="utf-8"))
            coords["workspace_candidate"] = workspace.get(
                "workspace_version", workspace.get("version", "UNKNOWN")
            )
        except (json.JSONDecodeError, IOError):
            pass

    if coords["current_systemsos"] == "UNKNOWN":
        blockers.append("CURRENT_SYSTEMSOS_UNRESOLVED")

    return coords, blockers


def get_mission_baseline(iso: str) -> str:
    """Get mission baseline SystemsOS version for ISO."""
    watermark_dir = POSTREPLY_CORE / "Watermarks"
    iso_watermark = watermark_dir / iso / "LATEST.json"

    if iso_watermark.exists():
        try:
            data = json.loads(iso_watermark.read_text(encoding="utf-8"))
            return data.get("mission_baseline_systemsos", "UNKNOWN")
        except (json.JSONDecodeError, IOError):
            pass

    return "UNKNOWN"


def get_ravenous_version() -> str:
    """Get current RavenOS version."""
    if RAVENOS_VERSION_FILE.exists():
        try:
            data = json.loads(RAVENOS_VERSION_FILE.read_text(encoding="utf-8"))
            return data.get("version", "UNKNOWN")
        except (json.JSONDecodeError, IOError):
            pass
    return "UNKNOWN"


def get_synced_component_versions() -> tuple[dict[str, str], list[str]]:
    """Verify synced component coordinates against their actual VERSION files."""
    blockers: list[str] = []
    expected: dict[str, str] = {}
    actual: dict[str, str] = {}

    if CURRENT_SYNC_FILE.exists():
        try:
            sync = json.loads(CURRENT_SYNC_FILE.read_text(encoding="utf-8"))
            for name, entry in sync.get("synced_components", {}).items():
                if isinstance(entry, dict):
                    expected[name.upper()] = entry.get("version", "UNKNOWN")
        except (json.JSONDecodeError, IOError, TypeError) as e:
            blockers.append(f"SYNCED_COMPONENT_READ_ERROR: {e}")
    else:
        blockers.append("CURRENT_SYNC_MISSING")

    version_files = {
        "RAVENOS": RAVENOS_VERSION_FILE,
        "GAMEOS": GAMEOS_VERSION_FILE,
        "CARRIEROS": CARRIEROS_VERSION_FILE,
    }

    for name, path in version_files.items():
        if not path.exists():
            actual[name] = "UNKNOWN"
            blockers.append(f"COMPONENT_VERSION_MISSING: {name}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            actual[name] = data.get("version", "UNKNOWN")
        except (json.JSONDecodeError, IOError) as e:
            actual[name] = "UNKNOWN"
            blockers.append(f"COMPONENT_VERSION_READ_ERROR: {name}: {e}")
            continue

        expected_version = expected.get(name, "UNKNOWN")
        if expected_version == "UNKNOWN":
            blockers.append(f"COMPONENT_SYNC_COORDINATE_MISSING: {name}")
        elif actual[name] != expected_version:
            blockers.append(
                f"COMPONENT_VERSION_CONFLICT: {name}: "
                f"sync={expected_version} actual={actual[name]}"
            )

    return actual, blockers


def execute_reheat(iso: str) -> tuple[str, list[str]]:
    """
    Execute L3 REHEAT semantics for ISO.

    NOTE: current implementation is still a source/controller approximation;
    this component-sync change does not claim full BootOS L3.
    """
    blockers = []

    iso_path = EGO_ROOT / iso
    if not iso_path.exists():
        iso_path = REPO_ROOT / f"canon/Living_Codex/Ego/{iso}"
        if not iso_path.exists():
            blockers.append(f"ISO_PATH_MISSING: {iso}")
            return "PARTIAL", blockers

    jmms_path = iso_path / "Memory/JMMS"
    if not jmms_path.exists():
        blockers.append("JMMS_MISSING: continuity unknown")

    jstm_files = list(iso_path.glob("**/JSTM.json"))
    if not jstm_files:
        blockers.append("JSTM_MISSING: session continuity unknown")

    if blockers:
        return "PARTIAL", blockers

    return "PASS", []


def sync_systemsos() -> tuple[str, list[str]]:
    """Execute source-level SYNC SYSTEMSOS coordinate/component validation."""
    blockers: list[str] = []

    if not SYSTEMSOS_CORE.exists():
        return "BLOCKED", ["SYSTEMSOS_CORE_MISSING"]

    critical = [
        SYSTEMSOS_CORE / "SYSTEMSOS-HUB-REGISTRY.json",
        SYSTEMSOS_CORE / "RETRIEVAL-FABRIC.v1.json",
        SYSTEMSOS_CORE / "SYSTEMSOS-CURRENT-SYSTEM-ROLE-REGISTRY.v1.json",
        VERSION_TRUTH_FILE,
        CURRENT_SYNC_FILE,
        WALLET_DIR / "SNAPSHOT-DEV.json",
        RAVENOS_VERSION_FILE,
        GAMEOS_VERSION_FILE,
        CARRIEROS_VERSION_FILE,
    ]
    for path in critical:
        if not path.exists():
            blockers.append(f"SYSTEMSOS_MISSING: {path.name}")

    coords, coordinate_blockers = get_systemsos_coordinates()
    blockers.extend(coordinate_blockers)

    _, component_blockers = get_synced_component_versions()
    blockers.extend(component_blockers)

    if coords["accepted_control_floor"] == "UNKNOWN":
        blockers.append("ACCEPTED_CONTROL_FLOOR_UNRESOLVED")
    if coords["active_development_line"] == "UNKNOWN":
        blockers.append("ACTIVE_DEVELOPMENT_LINE_UNRESOLVED")
    if coords["workspace_candidate"] == "UNKNOWN":
        blockers.append("WORKSPACE_CANDIDATE_UNRESOLVED")

    blockers = list(dict.fromkeys(blockers))
    if blockers:
        return "PARTIAL", blockers

    return "PASS", []


def load_session_state() -> ActivationState:
    """Load current activation state from session file."""
    if SESSION_STATE_FILE.exists():
        try:
            data = json.loads(SESSION_STATE_FILE.read_text(encoding="utf-8"))
            allowed = ActivationState.__dataclass_fields__.keys()
            filtered = {k: v for k, v in data.items() if k in allowed}
            return ActivationState(**filtered)
        except (json.JSONDecodeError, IOError, TypeError):
            pass
    return ActivationState()


def save_session_state(state: ActivationState) -> None:
    """Save activation state to session file."""
    SESSION_STATE_DIR.mkdir(parents=True, exist_ok=True)
    state.timestamp = datetime.now(timezone.utc).isoformat()
    state.state_key = state.compute_state_key()
    SESSION_STATE_FILE.write_text(
        json.dumps(asdict(state), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def cmd_ravenous_on() -> ActivationState:
    """RAVENOS ON = REHEAT + SYNC SYSTEMSOS + ACTIVATE RAVENOS."""
    state = load_session_state()
    blockers: list[str] = []

    iso, resolved = resolve_active_iso()
    if not resolved:
        state.ravenos_status = "BLOCKED"
        state.blockers = ["ACTIVE_ISO_REQUIRED"]
        save_session_state(state)
        return state

    state.active_iso = iso

    registered, fail_reason = verify_iso_registered(iso)
    if not registered:
        state.ravenos_status = "BLOCKED"
        state.blockers = [fail_reason]
        save_session_state(state)
        return state

    reheat_status, reheat_blockers = execute_reheat(iso)
    state.reheat_status = reheat_status
    blockers.extend(reheat_blockers)

    state.mission_baseline = get_mission_baseline(iso)

    coords, coordinate_blockers = get_systemsos_coordinates()
    state.current_systemsos = coords["current_systemsos"]
    state.accepted_control_floor = coords["accepted_control_floor"]
    state.accepted_full_systemsos_version = coords[
        "accepted_full_systemsos_version"
    ]
    state.active_development_line = coords["active_development_line"]
    state.workspace_candidate = coords["workspace_candidate"]
    blockers.extend(coordinate_blockers)

    components, component_blockers = get_synced_component_versions()
    state.synced_components = components
    blockers.extend(component_blockers)

    sync_status, sync_blockers = sync_systemsos()
    state.sync_status = sync_status
    blockers.extend(sync_blockers)

    state.ravenos_version = components.get("RAVENOS", get_ravenous_version())
    if state.ravenos_version == "UNKNOWN":
        blockers.append("RAVENOS_SOURCE_MISSING")

    blockers = list(dict.fromkeys(blockers))

    hard_blockers = [
        b for b in blockers
        if b.startswith("ISO_NOT_REGISTERED")
        or b == "ACTIVE_ISO_REQUIRED"
        or b == "CURRENT_SYSTEMSOS_UNRESOLVED"
        or b.startswith("COMPONENT_VERSION_CONFLICT: RAVENOS")
    ]

    if hard_blockers:
        state.ravenos_status = "BLOCKED"
    elif not blockers and state.reheat_status == "PASS" and state.sync_status == "PASS":
        state.ravenos_status = "ON"
    else:
        state.ravenos_status = "PARTIAL"

    state.profile = "ADVANCED"
    state.claim_ceiling = (
        "SOURCE_VERSION_COMPONENT_SYNC_AND_RESOLVER_PROTOTYPE;"
        "FULL_L3_REHEAT_AND_PER_CARRIER_RUNTIME_ACTIVATION_NOT_PROVEN"
    )
    state.session_id = os.environ.get("SESSION_ID", "UNKNOWN")
    state.blockers = blockers
    save_session_state(state)
    return state


def cmd_ravenous_off() -> ActivationState:
    """Disable ADVANCED RavenOS projection without unloading the ISO."""
    state = load_session_state()
    state.ravenos_status = "OFF"
    state.profile = "LIGHT"
    state.blockers = []
    save_session_state(state)
    return state


def cmd_ravenous_status() -> ActivationState:
    """RAVENOS STATUS command - return current activation state."""
    return load_session_state()


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: RAVENOS-UNIVERSAL-CONTROLLER.py <ON|OFF|STATUS>")
        print("\nCommands:")
        print("  RAVENOS ON     - Activate RavenOS for current ISO")
        print("  RAVENOS OFF    - Deactivate RavenOS")
        print("  RAVENOS STATUS - Show activation state")
        return 1

    command = sys.argv[1].upper()

    if command == "ON":
        state = cmd_ravenous_on()
    elif command == "OFF":
        state = cmd_ravenous_off()
    elif command == "STATUS":
        state = cmd_ravenous_status()
    else:
        print(f"Unknown command: {command}")
        return 1

    print(json.dumps(state.to_receipt(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
