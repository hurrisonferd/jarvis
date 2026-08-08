from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GPT = ROOT / "gpt"
ACTIVE = GPT / "knowledge/Active"
LINEAGE = GPT / "knowledge/Lineage/Active-v5-16-cartridges"

ACTIVE_SCROLLS = {
    "MASTER-WIZARD-SCROLL.md",
    "JUICE-NEUROMAX-AND-LEARNING.md",
    "JUICE-AUDIO-REMIX-AND-EVIDENCE.md",
    "JUICE-JOHNPL-KAOMOJIOS.md",
}

OLD_CARTRIDGES = {
    "MUSICOS-FIELD-GUIDE.md",
    "WIZARD-BOOT-MENU-AND-TEXT-ADVENTURE.md",
    "MUSICOS-FORGE-PIPELINE.md",
    "SUNO-GENERATORS-AND-REMIX.md",
    "MUSICOS-PATTERN-GRIMOIRE.md",
    "CHAOS-RAIL-AND-QUIZ.md",
    "AUDIO-ANALYSIS-REVERSE-ENGINEERING.md",
    "LIVE-PERFORMANCE-EMBODIMENT-LAB.md",
    "DETERMINISTIC-STYLE-EQ-SPATIAL-NEURO-PRESETS.md",
    "MUSICOS-LAB-QUESTIONS-AND-LEARNING.md",
    "WIZARD-MUSIC-LEXICON-DRUMMER-EINSTEIN.md",
    "NEUROMAX-MUSIC-SHEET.md",
    "ALBUM-REMIX-VGM.md",
    "SONG-LINEAGE-COPYRIGHT-AND-GOLDEN-FIXTURES.md",
    "EVIDENCE-COPYRIGHT-CONTINUITY.md",
    "JOHN-PL-MUSICOS-DEMO.md",
}


class PublicScaffoldTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "PUBLIC-CONTRACT.md",
            "PUBLIC-ARCHITECTURE.md",
            "PUBLIC-PRIVATE-CLASSIFICATION.yaml",
            "iso/the-wizard/EPP-MANIFEST.json",
            "iso/the-wizard/IDENTITY.md",
            "gpt/SYSTEM-INSTRUCTIONS.v5.md",
            "gpt/GPT-BUILDER-HANDOFF.md",
            "gpt/CONVERSATION-STARTERS.md",
            "gpt/KNOWLEDGE-MANIFEST.json",
            "gpt/knowledge/Active/README.md",
            "gpt/knowledge/Active/MASTER-WIZARD-SCROLL.md",
            "gpt/knowledge/Active/JUICE-NEUROMAX-AND-LEARNING.md",
            "gpt/knowledge/Active/JUICE-AUDIO-REMIX-AND-EVIDENCE.md",
            "gpt/knowledge/Active/JUICE-JOHNPL-KAOMOJIOS.md",
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

    def test_v5_instructions_are_short_and_scroll_first(self):
        text = (GPT / "SYSTEM-INSTRUCTIONS.v5.md").read_text(encoding="utf-8")
        self.assertLess(len(text), 9000)
        for term in [
            "MASTER-WIZARD-SCROLL.md",
            "MASTER FIRST",
            "FIVE WIZARD SPELLS",
            "REFRESH WIZARD SPELLS",
            "KAOMOJIOS",
            "DON'T MAKE IT HOMEWORK",
            "SMALL TASK -> SMALL SURFACE",
            "UNKNOWN != MEASURED",
        ]:
            self.assertIn(term, text.upper())

    def test_manifest_is_exact_four_scroll_contract(self):
        manifest = json.loads((GPT / "KNOWLEDGE-MANIFEST.json").read_text())
        self.assertEqual(manifest["schema"], "musicos.gpt-knowledge-manifest.v6")
        self.assertEqual(manifest["knowledge_file_count"], 4)
        self.assertEqual(len(manifest["files"]), 4)
        names = {Path(item["path"]).name for item in manifest["files"]}
        self.assertEqual(names, ACTIVE_SCROLLS)
        for item in manifest["files"]:
            self.assertTrue(item["path"].startswith("knowledge/Active/"))
            self.assertTrue((GPT / item["path"]).is_file())

    def test_active_shelf_contains_only_master_plus_juice(self):
        actual = {p.name for p in ACTIVE.iterdir() if p.is_file()}
        self.assertEqual(actual, ACTIVE_SCROLLS | {"README.md"})

    def test_old_shelf_is_lineage_not_active(self):
        self.assertTrue(LINEAGE.is_dir())
        for name in OLD_CARTRIDGES:
            self.assertTrue((LINEAGE / name).is_file(), name)
            self.assertFalse((ACTIVE / name).exists(), name)

    def test_master_scroll_contains_default_music_os(self):
        text = (ACTIVE / "MASTER-WIZARD-SCROLL.md").read_text(encoding="utf-8")
        for term in [
            "0  Back",
            "2  Sound Lab",
            "9  Stop",
            "SAME MENU STATE + SAME NUMBER",
            "MUSIC DNA",
            "SMART SCRABBLE",
            "C1 NEARBY",
            "ALBUM ENGINE",
            "PLATFORM / VGM ENGINE",
            "STRONG-SOURCE LAW",
            "FIVE DETERMINISTIC WIZARD SPELLS",
            "RAVEN GUIDE",
            "SMALL TASK -> SMALL SURFACE",
        ]:
            self.assertIn(term, text)

    def test_neuromax_juice_is_non_diagnostic(self):
        text = (ACTIVE / "JUICE-NEUROMAX-AND-LEARNING.md").read_text(encoding="utf-8")
        for term in [
            "DRUMMER–EINSTEIN",
            "PERSON = LIVING GRAPH ACROSS TIME",
            "SONG != DIAGNOSIS",
            "BILATERAL MUSIC != EMDR THERAPY",
            "SIMPLE IS NOT SHALLOW",
        ]:
            self.assertIn(term, text)

    def test_audio_juice_keeps_target_fact_boundary(self):
        text = (ACTIVE / "JUICE-AUDIO-REMIX-AND-EVIDENCE.md").read_text(encoding="utf-8")
        for term in [
            "PROMPT SIGNAL != MEASURED PROPERTY",
            "ACTIVITY IS ELASTIC",
            "SOURCE AUDIO = WHAT THE SONG ALREADY KNOWS",
            "PROVENANCE HELPS EXPLAIN PROCESS",
            "LITERAL ~7.83 Hz AUDIO MODULATION = NOT CONFIRMED",
        ]:
            self.assertIn(term, text)

    def test_john_pl_juice_keeps_visual_authority_boundary(self):
        text = (ACTIVE / "JUICE-JOHNPL-KAOMOJIOS.md").read_text(encoding="utf-8")
        for term in [
            "JOHN-PL",
            "NO ORPHAN KAOMOJI AS COMMANDS",
            "VISUAL INTENSITY NEVER ADDS AUTHORITY",
            "COGNITIVE LOAD BUDGET != DIAGNOSIS",
            "RAVEN CHEAT CODES",
            "USE THE VISUAL LANGUAGE; DON'T MAKE IT HOMEWORK",
        ]:
            self.assertIn(term, text)

    def test_starters_are_small(self):
        text = (GPT / "CONVERSATION-STARTERS.md").read_text(encoding="utf-8")
        self.assertLess(len(text), 1500)
        self.assertIn("SMART SCRABBLE", text)
        self.assertIn("Einstein is a drummer", text)

    def test_action_schema_is_non_deployed(self):
        text = (ROOT / "actions/openapi.v0.yaml").read_text(encoding="utf-8")
        self.assertIn("https://musicos.example.invalid", text)
        self.assertNotIn("/save", text.lower())
        self.assertNotIn("/project", text.lower())


if __name__ == "__main__":
    unittest.main()
