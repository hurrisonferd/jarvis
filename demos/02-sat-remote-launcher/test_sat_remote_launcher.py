#!/usr/bin/env python3
"""Contract tests for SAT Remote Launcher v0.1."""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sat_remote_launcher import (  # noqa: E402
    SATError,
    execute_mission,
    plan_mission,
    probe_mission,
    read_json,
)

ROOT = HERE.parents[1]
CARRIERS = Path(
    os.environ.get(
        "SAT_CARRIERS",
        str(ROOT / "templates" / "iso-starter" / "CARRIERS.json"),
    )
)
MISSION = HERE / "mission.example.json"
FAKE_SERVER = HERE / "fake_app_server.py"


class SATRemoteLauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = read_json(CARRIERS)
        self.mission = read_json(MISSION)

    def test_plan_is_side_effect_free(self) -> None:
        plan = plan_mission(self.mission, self.contract)
        self.assertEqual(plan["status"], "READY")
        self.assertEqual(plan["fresh_threads"], 3)
        self.assertFalse(plan["provider_side_effects"])

    def test_prompt_hash_is_enforced(self) -> None:
        mission = copy.deepcopy(self.mission)
        mission["task"]["prompt"] += " drift"
        with self.assertRaisesRegex(SATError, "does not match"):
            plan_mission(mission, self.contract)

    def test_probe_checks_capabilities_without_threads(self) -> None:
        result = probe_mission(
            self.mission,
            self.contract,
            [sys.executable, str(FAKE_SERVER)],
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["provider_threads_created"], 0)
        self.assertTrue(
            all(row["reasoning_effort_available"] for row in result["legs"])
        )

    def test_raven_authority_is_enforced(self) -> None:
        mission = copy.deepcopy(self.mission)
        mission["operator_authority"]["approved"] = False
        with self.assertRaisesRegex(SATError, "Raven operator approval"):
            plan_mission(mission, self.contract)

    def test_fake_server_creates_blinded_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp)
            receipt = execute_mission(
                self.mission,
                self.contract,
                output_dir,
                lambda _effort, _speed: [sys.executable, str(FAKE_SERVER)],
            )
            self.assertEqual(receipt["status"], "PASS")
            self.assertEqual(receipt["fresh_threads_created"], 3)
            for alias in ("LEG-A", "LEG-B", "LEG-C"):
                public = (output_dir / "anonymous" / f"{alias}.receipt.json").read_text()
                self.assertNotIn('"carrier"', public)
                self.assertNotIn('"model"', public)
                self.assertIn("PENDING_BLIND_EVALUATION", public)
            private = json.loads(
                (output_dir / "operator-only" / "route-map.json").read_text()
            )
            self.assertEqual(private["status"], "PASS")
            self.assertEqual(
                [row["carrier"] for row in private["routes"]],
                ["TERRA", "LUNA", "SOL"],
            )
            self.assertTrue(
                all(
                    row["binding"]["meter"] == "sat-policy-only"
                    for row in private["routes"]
                )
            )

    def test_nonempty_output_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp)
            (output_dir / "existing.txt").write_text("keep")
            with self.assertRaisesRegex(SATError, "must be empty"):
                execute_mission(
                    self.mission,
                    self.contract,
                    output_dir,
                    lambda _effort, _speed: [sys.executable, str(FAKE_SERVER)],
                )


if __name__ == "__main__":
    unittest.main()
