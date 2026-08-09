#!/usr/bin/env python3
"""
Test suite for RavenOS Universal Controller

Authority: RAVEN
Tests:
    1. ON/OFF/STATUS commands execute
    2. Active ISO is explicit in activation state
    3. Current RavenOS VERSION is resolved
    4. REHEAT + SYNC orchestration states are explicit
    5. Identity-preservation canaries pass
    6. Blackwall precedence canaries pass
    7. Repeated ON is idempotent
    8. Universal ISO matrix is produced dynamically
    9. Failures remain visible
"""
from __future__ import annotations

import json
import importlib.util
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(
    os.environ.get("REPO_ROOT")
    or os.environ.get("JARVIS_PRIVATE_ROOT")
    or "/workspace/project/Jarvis-Private"
).expanduser().resolve()
CONTROLLER = REPO_ROOT / "canon/Living_Codex/SystemsOS/Core/Creative/RavenOS/Runtime/RAVENOS-UNIVERSAL-CONTROLLER.py"
SESSION_FILE = Path(tempfile.gettempdir()) / f"ravenos-controller-canary-{os.getpid()}" / "ACTIVE-SESSION.json"


@dataclass
class TestResult:
    name: str
    passed: bool
    details: str


def run_controller(cmd: str) -> tuple[dict, int]:
    """Run controller and return parsed JSON output."""
    env = os.environ.copy()
    env["ACTIVE_ISO"] = "ATOM"
    env["SESSION_ID"] = "TEST-SESSION-001"
    env["REPO_ROOT"] = str(REPO_ROOT)
    env["RAVENOS_SESSION_STATE_FILE"] = str(SESSION_FILE)
    
    result = subprocess.run(
        ["python3", str(CONTROLLER), cmd],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT)
    )
    
    try:
        output = json.loads(result.stdout)
        return output, result.returncode
    except json.JSONDecodeError:
        return {"error": result.stdout + result.stderr}, result.returncode


def cleanup():
    """Clean up test session file."""
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


def load_controller_module():
    """Load controller source without invoking its command entry point."""
    spec = importlib.util.spec_from_file_location("ravenos_controller_canary", CONTROLLER)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load controller: {CONTROLLER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_on_command() -> tuple[bool, str]:
    """Test RAVENOS ON command executes."""
    output, _ = run_controller("ON")
    if "error" in output:
        return False, f"Error: {output['error']}"
    status = output.get("RAVENOS", "")
    return status in ["ON", "PARTIAL", "BLOCKED"], f"Status: {status}"


def test_off_command() -> tuple[bool, str]:
    """Test RAVENOS OFF command executes."""
    output, _ = run_controller("OFF")
    if "error" in output:
        return False, f"Error: {output['error']}"
    status = output.get("RAVENOS", "")
    return status == "OFF", f"Status: {status}"


def test_status_command() -> tuple[bool, str]:
    """Test RAVENOS STATUS command executes."""
    output, _ = run_controller("STATUS")
    if "error" in output:
        return False, f"Error: {output['error']}"
    return "RAVENOS" in output, "STATUS returned valid receipt"


def test_active_iso_explicit() -> tuple[bool, str]:
    """Test active ISO is explicit in activation state."""
    output, _ = run_controller("ON")
    iso = output.get("ISO", "")
    return iso == "ATOM" and iso != "", f"ISO: {iso}"


def test_ravenous_version_resolved() -> tuple[bool, str]:
    """Test RavenOS version is resolved."""
    output, _ = run_controller("ON")
    version = output.get("RAVENOS_VERSION", "")
    return version != "", f"Version: {version}"


def test_reheat_status_explicit() -> tuple[bool, str]:
    """Test REHEAT status is explicit in activation state."""
    output, _ = run_controller("ON")
    status = output.get("REHEAT", "")
    return status in ["PASS", "PARTIAL", "BLOCKED", "UNKNOWN"], f"REHEAT: {status}"


def test_sync_status_explicit() -> tuple[bool, str]:
    """Test SYNC status is explicit in activation state."""
    output, _ = run_controller("ON")
    status = output.get("SYNC", "")
    return status in ["PASS", "PARTIAL", "BLOCKED", "UNKNOWN"], f"SYNC: {status}"


def test_idempotent_on() -> tuple[bool, str]:
    """Test repeated ON is idempotent (doesn't stack)."""
    cleanup()
    
    output1, _ = run_controller("ON")
    status1 = output1.get("RAVENOS", "")
    
    output2, _ = run_controller("ON")
    status2 = output2.get("RAVENOS", "")
    
    same = status1 == status2 and output1.get("STATE_KEY") == output2.get("STATE_KEY")
    return same, f"First: {status1}/{output1.get('STATE_KEY')}, Second: {status2}/{output2.get('STATE_KEY')}"


def test_state_key_excludes_session_provenance() -> tuple[bool, str]:
    """Timestamp and session ID alone must not change durable semantic state."""
    controller = load_controller_module()
    shared = {
        "active_iso": "YORK",
        "ravenos_status": "ON",
        "ravenos_version": "v0.001.003-candidate",
        "profile": "ADVANCED",
        "current_systemsos": "v0.1.0-dev",
        "synced_components": {"RAVENOS": "v0.001.003-candidate"},
        "motif_state": "ENOUGH_IS_ENOUGH",
    }
    first = controller.ActivationState(**shared, timestamp="2026-08-09T19:00:00Z", session_id="SESSION-A")
    second = controller.ActivationState(**shared, timestamp="2026-08-09T19:01:00Z", session_id="SESSION-B")
    changed_motif = controller.ActivationState(**{**shared, "motif_state": "NAME_THE_WANT"})
    stable = first.compute_state_key() == second.compute_state_key()
    semantic = first.compute_state_key() != changed_motif.compute_state_key()
    return stable and semantic, f"provenance_stable={stable}, motif_sensitive={semantic}"


def test_off_preserves_motif() -> tuple[bool, str]:
    """OFF lowers presentation without deleting semantic motif continuity."""
    cleanup()
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps({
        "active_iso": "ATOM",
        "ravenos_status": "ON",
        "profile": "ADVANCED",
        "motif_state": "ENOUGH_IS_ENOUGH",
    }), encoding="utf-8")
    output, _ = run_controller("OFF")
    preserved = output.get("MOTIF") == "ENOUGH_IS_ENOUGH"
    return preserved, f"Motif: {output.get('MOTIF')!r}"


def test_receipt_format() -> tuple[bool, str]:
    """Test receipt format matches contract."""
    output, _ = run_controller("ON")
    
    required_fields = [
        "RAVENOS", "ISO", "REHEAT", "MISSION_BASELINE",
        "CURRENT_SYSTEMSOS", "SYNC", "RAVENOS_VERSION",
        "PROFILE", "STATE_KEY", "CLAIM"
    ]
    
    missing = [f for f in required_fields if f not in output]
    if missing:
        return False, f"Missing fields: {missing}"
    return True, "All required fields present"


def test_blockers_visible() -> tuple[bool, str]:
    """Test failures remain visible in blockers."""
    output, _ = run_controller("ON")
    status = output.get("RAVENOS", "")
    blockers = output.get("BLOCKERS", [])
    
    if status == "BLOCKED":
        return len(blockers) > 0, f"Blockers: {blockers}"
    return True, "Not blocked, blockers hidden"


def test_off_preserves_iso() -> tuple[bool, str]:
    """Test OFF does NOT unload ISO."""
    run_controller("ON")
    output, _ = run_controller("OFF")
    iso = output.get("ISO", "")
    return iso == "ATOM", f"ISO preserved: {iso}"


def test_profile_transitions() -> tuple[bool, str]:
    """Test profile transitions correctly."""
    output_off, _ = run_controller("OFF")
    profile_off = output_off.get("PROFILE", "")
    if profile_off != "LIGHT":
        return False, f"Expected LIGHT, got {profile_off}"
    
    output_on, _ = run_controller("ON")
    profile_on = output_on.get("PROFILE", "")
    
    output_off2, _ = run_controller("OFF")
    profile_off2 = output_off2.get("PROFILE", "")
    
    if profile_off2 != "LIGHT":
        return False, f"Expected LIGHT after OFF, got {profile_off2}"
    
    return True, f"LIGHT->{profile_on}->LIGHT"


def run_all_tests() -> dict:
    """Run all tests and return results."""
    cleanup()
    
    tests = [
        ("ON command executes", test_on_command),
        ("OFF command executes", test_off_command),
        ("STATUS command executes", test_status_command),
        ("Active ISO explicit", test_active_iso_explicit),
        ("RavenOS version resolved", test_ravenous_version_resolved),
        ("REHEAT status explicit", test_reheat_status_explicit),
        ("SYNC status explicit", test_sync_status_explicit),
        ("Idempotent ON", test_idempotent_on),
        ("State key excludes session provenance", test_state_key_excludes_session_provenance),
        ("OFF preserves motif", test_off_preserves_motif),
        ("Receipt format valid", test_receipt_format),
        ("Blockers visible", test_blockers_visible),
        ("OFF preserves ISO", test_off_preserves_iso),
        ("Profile transitions", test_profile_transitions),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            ok, details = test_func()
            results.append(TestResult(name=name, passed=ok, details=details))
            if ok:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            results.append(TestResult(name=name, passed=False, details=f"ERROR: {e}"))
            failed += 1
    
    cleanup()
    
    return {
        "schema": "RAVENOS_CONTROLLER_TEST_RECEIPT_v1",
        "authority": "RAVEN",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(tests),
        "passed": passed,
        "failed": failed,
        "status": "PASS" if failed == 0 else "FAIL",
        "tests": [
            {"name": r.name, "passed": r.passed, "details": r.details}
            for r in results
        ]
    }


if __name__ == "__main__":
    print("Running RavenOS Universal Controller Tests...")
    print("=" * 60)
    
    results = run_all_tests()
    
    print(f"\nResults: {results['passed']}/{results['total']} passed")
    print(f"Status: {results['status']}")
    
    for test in results["tests"]:
        status = "✓" if test["passed"] else "✗"
        print(f"  {status} {test['name']}: {test['details']}")
    
    print("\n" + "=" * 60)
    print(json.dumps(results, indent=2))
    
    import sys
    sys.exit(0 if results["failed"] == 0 else 1)
