from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GPT = ROOT / "gpt"
ACTIVE = GPT / "knowledge/Active"
LINEAGE = GPT / "knowledge/Lineage/Active-v5-16-cartridges"

ACTIVE_KNOWLEDGE = {
    "MASTER-WIZARD-SCROLL.md",
    "JUICE-NEUROMAX-AND-LEARNING.md",
    "JUICE-AUDIO-REMIX-AND-EVIDENCE.md",
    "JUICE-JOHNPL-KAOMOJIOS.md",
    "WIZARD-MUSIC-LEXICON-DRUMMER-EINSTEIN.md",
    "DETERMINISTIC-STYLE-EQ-SPATIAL-NEURO-PRESETS.md",
    "LIVE-PERFORMANCE-EMBODIMENT-LAB.md",
}

PROMOTED_DEEP_SOURCES = {
    "WIZARD-MUSIC-LEXICON-DRUMMER-EINSTEIN.md",
    "DETERMINISTIC-STYLE-EQ-SPATIAL-NEURO-PRESETS.md",
    "LIVE-PERFORMANCE-EMBODIMENT-LAB.md",
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

STARTERS = [
    "Forge a song from this weird idea. LOCK what matters and SMART SCRABBLE the rest.",
    "Remix this without losing its identity. Stage the delta instead of rewriting the song.",
    "Read this track. Tell me what survived, what moved, and what is still UNKNOWN.",
    "Teach me this like Einstein is a drummer.",
]


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
            *[f"gpt/knowledge/Active/{name}" for name in ACTIVE_KNOWLEDGE],
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

    def test_v5_instructions_are_short_scroll_first_and_shell_driven(self):
        text = (GPT / "SYSTEM-INSTRUCTIONS.v5.md").read_text(encoding="utf-8")
        self.assertLess(len(text), 9000)
        for term in [
            "MASTER-WIZARD-SCROLL.md",
            "MASTER FIRST",
            "[MUSICOS::WIZARD]",
            "0–9   = MENU ROUTES",
            "S1–S5 = CANONICAL WIZARD SPELLS",
            "A–Z   = REGULAR CONTEXT OPTIONS",
            "MORE OPTIONS MEANS MORE OPTIONS",
            "RAVEN CHEAT",
            "SHOW CONVERSATION STARTERS",
            "UNKNOWN != MEASURED",
        ]:
            self.assertIn(term.upper(), text.upper())

    def test_manifest_is_exact_seven_file_contract(self):
        manifest = json.loads((GPT / "KNOWLEDGE-MANIFEST.json").read_text())
        self.assertEqual(manifest["schema"], "musicos.gpt-knowledge-manifest.v7")
        self.assertEqual(manifest["knowledge_file_count"], 7)
        names = {Path(item["path"]).name for item in manifest["files"]}
        self.assertEqual(names, ACTIVE_KNOWLEDGE)
        self.assertEqual(set(manifest["dual_homed_lineage_sources"]), PROMOTED_DEEP_SOURCES)

    def test_active_shelf_contains_only_manifest_files_plus_readme(self):
        actual = {p.name for p in ACTIVE.iterdir() if p.is_file()}
        self.assertEqual(actual, ACTIVE_KNOWLEDGE | {"README.md"})

    def test_old_shelf_is_preserved_and_selected_sources_are_dual_homed(self):
        self.assertTrue(LINEAGE.is_dir())
        for name in OLD_CARTRIDGES:
            self.assertTrue((LINEAGE / name).is_file(), name)
            if name in PROMOTED_DEEP_SOURCES:
                self.assertTrue((ACTIVE / name).is_file(), name)
                self.assertEqual((LINEAGE / name).read_bytes(), (ACTIVE / name).read_bytes(), name)

    def test_master_scroll_has_legacy_shell_and_disjoint_namespaces(self):
        text = (ACTIVE / "MASTER-WIZARD-SCROLL.md").read_text(encoding="utf-8")
        for term in [
            "[MUSICOS::WIZARD]",
            "0 BACK",
            "1 SONG_FORGE",
            "3 VOICE_LAB",
            "S1 ADVANCE",
            "S3 MUTATE",
            "A–Z   = REGULAR CONTEXT OPTIONS",
            "MORE OPTIONS / SHOW MORE / EXPAND SPELLBOOK",
            "SHOW ALL OPTIONS",
            "SHOW CONVERSATION STARTERS",
            "RAVEN CHEAT",
            "LEGACY SHELL, LOW COGNITIVE LOAD",
        ]:
            self.assertIn(term, text)

    def test_more_options_is_not_five_spell_alias(self):
        instructions = (GPT / "SYSTEM-INSTRUCTIONS.v5.md").read_text(encoding="utf-8")
        self.assertIn("expands the A–Z option rail", instructions)
        self.assertIn("Do not merely repeat the five spell categories", instructions)
        self.assertIn("REFRESH WIZARD SPELLS", instructions)

    def test_conversation_starter_source_is_exact_and_queryable(self):
        text = (GPT / "CONVERSATION-STARTERS.md").read_text(encoding="utf-8")
        for starter in STARTERS:
            self.assertIn(starter, text)
        self.assertIn("SHOW CONVERSATION STARTERS", text)
        self.assertIn("DO NOT INVENT A SUBSTITUTE CATALOG", text)

    def test_neuromax_juice_is_non_diagnostic(self):
        text = (ACTIVE / "JUICE-NEUROMAX-AND-LEARNING.md").read_text(encoding="utf-8")
        for term in [
            "DRUMMER–EINSTEIN",
            "PERSON = LIVING GRAPH ACROSS TIME",
            "SONG != DIAGNOSIS",
            "BILATERAL MUSIC != EMDR THERAPY",
        ]:
            self.assertIn(term, text)

    def test_audio_juice_keeps_target_fact_boundary(self):
        text = (ACTIVE / "JUICE-AUDIO-REMIX-AND-EVIDENCE.md").read_text(encoding="utf-8")
        self.assertIn("PROMPT SIGNAL != MEASURED PROPERTY", text)
        self.assertIn("SOURCE AUDIO = WHAT THE SONG ALREADY KNOWS", text)

    def test_john_pl_juice_keeps_visual_authority_boundary(self):
        text = (ACTIVE / "JUICE-JOHNPL-KAOMOJIOS.md").read_text(encoding="utf-8")
        self.assertIn("VISUAL INTENSITY NEVER ADDS AUTHORITY", text)
        self.assertIn("COGNITIVE LOAD BUDGET != DIAGNOSIS", text)

    def test_promoted_deep_sources_keep_unique_depth(self):
        lexicon = (ACTIVE / "WIZARD-MUSIC-LEXICON-DRUMMER-EINSTEIN.md").read_text(encoding="utf-8")
        presets = (ACTIVE / "DETERMINISTIC-STYLE-EQ-SPATIAL-NEURO-PRESETS.md").read_text(encoding="utf-8")
        live = (ACTIVE / "LIVE-PERFORMANCE-EMBODIMENT-LAB.md").read_text(encoding="utf-8")
        self.assertIn("Universal term compiler", lexicon)
        self.assertIn("SAME PRESET NAME", presets)
        self.assertIn("Fixture 1 — Thunderclap and Run", live)

    def test_action_schema_is_non_deployed(self):
        text = (ROOT / "actions/openapi.v0.yaml").read_text(encoding="utf-8")
        self.assertIn("https://musicos.example.invalid", text)
        self.assertNotIn("/save", text.lower())
        self.assertNotIn("/project", text.lower())


if __name__ == "__main__":
    unittest.main()
