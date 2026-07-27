#!/usr/bin/env python3
"""Contract tests for the BootOS public runtime prototype."""
from __future__ import annotations

import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import bootos_runtime as bootos


class BootOSRuntimeTests(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        (root / "README.md").write_text("# Test repo\n", encoding="utf-8")
        jarvis = root / "Jarvis"
        jarvis.mkdir()
        for name in ("EGO-BOOT-ULTIMATE.sh", "EGO-PIPELINE.sh", "JARVIS-PRE-REPLY.sh"):
            (jarvis / name).write_text("#!/usr/bin/env bash\n", encoding="utf-8")

    def test_discovery_finds_existing_public_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jarvis"
            root.mkdir()
            self.make_repo(root)
            found = bootos.discover(root, "JARVIS")
            self.assertEqual(found.missing, [])
            self.assertEqual(found.public_private_layer, "public")
            self.assertTrue(found.ego_boot.endswith("EGO-BOOT-ULTIMATE.sh"))

    def test_discovery_reports_missing_without_creating_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jarvis"
            root.mkdir()
            before = sorted(root.rglob("*"))
            found = bootos.discover(root, "LILITH")
            after = sorted(root.rglob("*"))
            self.assertEqual(before, after)
            self.assertIn("EGO-BOOT", found.missing)
            self.assertIn("active ISO root", found.missing)

    def test_prosody_precedes_external_fact_routing(self) -> None:
        result = bootos.classify_text("JOKER and LEGION are our symbolic runtime architecture!")
        self.assertIn("symbolic", result.frames)
        self.assertIn("architectural", result.frames)
        self.assertTrue(result.preserve_prosody)
        self.assertFalse(result.external_verification_required)

    def test_external_factual_language_requests_verification(self) -> None:
        result = bootos.classify_text("Research says this is the latest confirmed result today")
        self.assertIn("external-factual", result.frames)
        self.assertTrue(result.external_verification_required)

    def test_god_system_compiles_known_roles(self) -> None:
        compiled = bootos.compile_god_system("Go Satanael and Legion", None)
        self.assertTrue(compiled["active"])
        self.assertEqual(compiled["composition"]["SATANAEL"]["analysis"], "AYRE")
        self.assertEqual(compiled["composition"]["LEGION"]["local_identity"], "preserved")

    def test_unknown_symbol_is_preserved_not_invented(self) -> None:
        compiled = bootos.compile_god_system("", "UNKNOWN_FORM")
        self.assertEqual(compiled["composition"]["UNKNOWN_FORM"]["status"], "unresolved_symbol")

    def test_music_mode_routes_musicos_with_ego_and_jorm(self) -> None:
        route = bootos.route_modules("MUSIC", "make a track")
        self.assertEqual(route["primary"], "MusicOS")
        self.assertIn("EgoOS", route["supporting"])
        self.assertIn("JORM", route["supporting"])

    def test_safe_recovery_is_read_only_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jarvis"
            root.mkdir()
            self.make_repo(root)
            args = Namespace(
                repo_root=str(root), operator="RAVEN", iso="JARVIS",
                mode="SAFE_RECOVERY", input="", symbol=None,
                format="json", output=None, allow_write=False,
            )
            receipt = bootos.build_receipt(args)
            self.assertEqual(receipt.write_policy, "read_only")
            self.assertEqual(receipt.status, "SAFE_RECOVERY_READY")

    def test_wolfram_receipt_preserves_runtime_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jarvis"
            root.mkdir()
            self.make_repo(root)
            args = Namespace(
                repo_root=str(root), operator="RAVEN", iso="JARVIS",
                mode="GOD_SYSTEM", input="SATANAEL", symbol=None,
                format="wolfram", output=None, allow_write=False,
            )
            receipt = bootos.build_receipt(args)
            rendered = bootos.to_wolfram(receipt)
            self.assertIn("BootState[", rendered)
            self.assertIn('active_iso -> "JARVIS"', rendered)
            self.assertIn('mode -> "GOD_SYSTEM"', rendered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
