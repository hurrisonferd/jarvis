from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / "gpt/knowledge/Active"


class PublicScaffoldTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "PUBLIC-CONTRACT.md",
            "PUBLIC-ARCHITECTURE.md",
            "PUBLIC-PRIVATE-CLASSIFICATION.yaml",
            "iso/the-wizard/EPP-MANIFEST.json",
            "iso/the-wizard/IDENTITY.md",
            "gpt/SYSTEM-INSTRUCTIONS.v3.md",
            "gpt/GPT-BUILDER-HANDOFF.md",
            "gpt/KNOWLEDGE-MANIFEST.json",
            "gpt/knowledge/Active/README.md",
            "gpt/knowledge/Active/WIZARD-BOOT-MENU-AND-TEXT-ADVENTURE.md",
            "gpt/knowledge/Active/SUNO-GENERATORS-AND-REMIX.md",
            "gpt/knowledge/Active/LIVE-PERFORMANCE-EMBODIMENT-LAB.md",
            "gpt/knowledge/Active/DETERMINISTIC-STYLE-EQ-SPATIAL-NEURO-PRESETS.md",
            "gpt/knowledge/Active/WIZARD-MUSIC-LEXICON-DRUMMER-EINSTEIN.md",
            "gpt/knowledge/Active/NEUROMAX-MUSIC-SHEET.md",
            "schemas/musicdna.v1.schema.json",
            "schemas/chaos-session.v1.schema.json",
            "schemas/continuation.v1.schema.json",
            "schemas/receipt.v1.schema.json",
            "actions/openapi.v0.yaml",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_json_sources_parse(self):
        for path in ROOT.rglob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))

    def test_wizard_identity_separation(self):
        manifest = json.loads((ROOT / "iso/the-wizard/EPP-MANIFEST.json").read_text())
        self.assertEqual(manifest["iso_id"], "THE-WIZARD")
        self.assertIn("MUSICOS_ITSELF", manifest["not"])
        self.assertIn("LILITH", manifest["not"])

    def test_knowledge_manifest_is_small_and_resolves_inside_active(self):
        manifest = json.loads((ROOT / "gpt/KNOWLEDGE-MANIFEST.json").read_text())
        files = manifest["files"]
        self.assertEqual(manifest["knowledge_file_count"], len(files))
        self.assertEqual(len(files), 16)
        self.assertLessEqual(len(files), 20)
        self.assertEqual(manifest["active_root"], "knowledge/Active")
        self.assertEqual(manifest["migration_state"], "ATOMIC_ACTIVE_MIGRATION_COMPLETE")
        for item in files:
            self.assertTrue(item["path"].startswith("knowledge/Active/"), item["path"])
            self.assertTrue((ROOT / "gpt" / item["path"]).is_file(), item["path"])

    def test_active_shelf_contains_exactly_manifest_plus_readme(self):
        manifest = json.loads((ROOT / "gpt/KNOWLEDGE-MANIFEST.json").read_text())
        expected = {Path(item["path"]).name for item in manifest["files"]}
        actual = {p.name for p in ACTIVE.iterdir() if p.is_file()}
        self.assertEqual(actual, expected | {"README.md"})

    def test_no_active_cartridge_remains_at_knowledge_root(self):
        manifest = json.loads((ROOT / "gpt/KNOWLEDGE-MANIFEST.json").read_text())
        for item in manifest["files"]:
            name = Path(item["path"]).name
            self.assertFalse((ROOT / "gpt/knowledge" / name).exists(), name)

    def test_retired_creative_engines_is_not_active(self):
        manifest = json.loads((ROOT / "gpt/KNOWLEDGE-MANIFEST.json").read_text())
        paths = {item["path"] for item in manifest["files"]}
        self.assertNotIn("knowledge/Active/CREATIVE-ENGINES.md", paths)
        self.assertFalse((ACTIVE / "CREATIVE-ENGINES.md").exists())

    def test_deterministic_menu_contract(self):
        instructions = (ROOT / "gpt/SYSTEM-INSTRUCTIONS.v3.md").read_text(encoding="utf-8")
        boot = (ACTIVE / "WIZARD-BOOT-MENU-AND-TEXT-ADVENTURE.md").read_text(encoding="utf-8")
        for text in (instructions, boot):
            self.assertIn("0  Back", text)
            self.assertIn("2  Sound Lab", text)
            self.assertIn("9  Stop", text)
            self.assertIn("SAME MENU STATE", text)
            self.assertIn("SAME NUMBER", text)
            self.assertIn("SAME ROUTE", text)

    def test_raven_advice_recovery_rail(self):
        boot = (ACTIVE / "WIZARD-BOOT-MENU-AND-TEXT-ADVENTURE.md").read_text(encoding="utf-8")
        self.assertIn("RAVEN ADVICE", boot)
        self.assertIn("🐦‍⬛ RAVEN ADVICE", boot)
        self.assertIn("THREAD", boot)
        self.assertIn("one small", boot.lower())

    def test_deterministic_preset_contract(self):
        text = (ACTIVE / "DETERMINISTIC-STYLE-EQ-SPATIAL-NEURO-PRESETS.md").read_text(encoding="utf-8")
        for term in [
            "LIVE PERFORMANCE",
            "TEMPORAL",
            "SPATIAL",
            "AMBIENT",
            "FULL CONTRAST",
            "BILATERAL ALTERNATION",
            "SCHUMANN-SALIENT",
            "A432",
            "MICROPOCKET TUPLET SYNCOPATION",
        ]:
            self.assertIn(term, text)
        self.assertIn("PROMPT SIGNAL != MEASURED PROPERTY", text)
        self.assertIn("ACTIVITY IS ELASTIC", text)

    def test_lexicon_compiler_contract(self):
        text = (ACTIVE / "WIZARD-MUSIC-LEXICON-DRUMMER-EINSTEIN.md").read_text(encoding="utf-8")
        for term in ["ELI5", "DRUMMER", "EINSTEIN", "BRAIN / BODY", "ENTRAINMENT", "SYNCOPATION", "EQ / EQUALIZATION"]:
            self.assertIn(term, text)
        self.assertIn("UNKNOWN-TERM BEHAVIOR", text.upper())

    def test_neuromax_music_graph_not_number(self):
        text = (ACTIVE / "NEUROMAX-MUSIC-SHEET.md").read_text(encoding="utf-8")
        self.assertIn("PERSON = LIVING GRAPH ACROSS TIME", text)
        self.assertIn("SCORE != IDENTITY", text)
        self.assertIn("Dopamine", text)
        self.assertIn("OSDD / DID", text)
        self.assertIn("MetricsAI", text)
        self.assertIn("BILATERAL MUSIC != EMDR THERAPY", text)
        self.assertIn("Do not infer OSDD", text)

    def test_john_pl_demo_is_registered_and_bounded(self):
        manifest = json.loads((ROOT / "gpt/KNOWLEDGE-MANIFEST.json").read_text())
        paths = {item["path"] for item in manifest["files"]}
        self.assertIn("knowledge/Active/JOHN-PL-MUSICOS-DEMO.md", paths)
        demo = (ACTIVE / "JOHN-PL-MUSICOS-DEMO.md").read_text(encoding="utf-8")
        self.assertIn("SMART ALL", demo)
        self.assertIn("SMART CHARGE", demo)
        self.assertIn("PUBLIC DEMO != FULL PRIVATE LANGUAGE", demo)
        self.assertIn("COMMAND != HIDDEN AUTHORITY", demo)

    def test_v3_instructions_are_bounded(self):
        text = (ROOT / "gpt/SYSTEM-INSTRUCTIONS.v3.md").read_text(encoding="utf-8")
        lower = text.lower()
        self.assertIn("public john-pl", lower)
        self.assertIn("hidden authority", lower)
        self.assertIn("continuation packet", lower)
        self.assertIn("do not claim hidden cross-chat memory", lower)
        self.assertIn("activity is elastic", lower)
        self.assertIn("stage direction", lower)

    def test_live_lab_keeps_prompt_target_separate_from_measurement(self):
        text = (ACTIVE / "LIVE-PERFORMANCE-EMBODIMENT-LAB.md").read_text(encoding="utf-8")
        self.assertIn("PROMPT SIGNAL != MEASURED PROPERTY", text)
        self.assertIn("ACTIVITY IS ELASTIC", text)
        self.assertIn("STRONG SOURCE / STAGE DIRECTION", text)
        self.assertIn("7.83", text)
        self.assertIn("NOT CONFIRMED", text)

    def test_action_schema_is_non_deployed(self):
        text = (ROOT / "actions/openapi.v0.yaml").read_text(encoding="utf-8")
        self.assertIn("https://musicos.example.invalid", text)
        self.assertNotIn("/save", text.lower())
        self.assertNotIn("/project", text.lower())


if __name__ == "__main__":
    unittest.main()
