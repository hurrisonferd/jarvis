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
    "WIZARD-SHELL-LAYOUT.md",
    "RAVENOS.md",
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
    "TIM. Controlled deterministic chaos: LOCK what matters and mutate the rest.",
]


class PublicScaffoldTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "PUBLIC-CONTRACT.md",
            "PUBLIC-ARCHITECTURE.md",
            "PUBLIC-PRIVATE-CLASSIFICATION.yaml",
            "iso/the-wizard/EPP-MANIFEST.json",
            "iso/the-wizard/IDENTITY.md",
            "gpt/SYSTEM-INSTRUCTIONS.v6.md",
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

    def test_v6_instructions_are_instruction_only_and_route_presentation(self):
        text = (GPT / "SYSTEM-INSTRUCTIONS.v6.md").read_text(encoding="utf-8")
        self.assertLess(len(text), 7000)
        for term in [
            "MASTER-WIZARD-SCROLL.md",
            "WIZARD-SHELL-LAYOUT.md",
            "RAVENOS.md",
            "LAYOUT OWNS PRESENTATION",
            "RAVENOS OWNS RAVEN",
            "TIM = controlled deterministic chaos",
            "0–9   = MENU ROUTES",
            "S1–S5 = CANONICAL WIZARD SPELLS",
            "A–Z   = CONTEXTUAL OPTIONS",
            "UNKNOWN != MEASURED",
        ]:
            self.assertIn(term.upper(), text.upper())
        # Full rendering belongs in the layout source, not the system prompt.
        self.assertNotIn("| KEY | ROUTE | SIGNAL |", text)
        self.assertNotIn("## 📟 **TRI-LOG**", text)

    def test_layout_owns_king_menu_tri_log_and_rails(self):
        text = (ACTIVE / "WIZARD-SHELL-LAYOUT.md").read_text(encoding="utf-8")
        for term in [
            "KING MENU",
            "TRI-LOG",
            "CHAT",
            "RAVEN",
            "NEXT",
            "SPELL RAIL",
            "PICK RAIL",
            "MORE_OPTIONS",
            "BEAUTIFUL != BUSY",
            "🟩 MINT",
            "🟦 CYAN",
            "🟪 VIOLET",
            "🟨 AMBER",
            "🟥 RED",
            "⬜ WHITE",
        ]:
            self.assertIn(term, text)

    def test_layout_keeps_disjoint_namespaces(self):
        text = (ACTIVE / "WIZARD-SHELL-LAYOUT.md").read_text(encoding="utf-8")
        for term in [
            "0–9   = KING MENU ROUTES",
            "S1–S5 = CANONICAL WIZARD SPELLS",
            "A–Z   = CONTEXTUAL PICK OPTIONS",
            "3  = VOICE LAB",
            "S3 = MUTATE",
        ]:
            self.assertIn(term, text)

    def test_manifest_is_exact_nine_file_contract(self):
        manifest = json.loads((GPT / "KNOWLEDGE-MANIFEST.json").read_text())
        self.assertEqual(manifest["schema"], "musicos.gpt-knowledge-manifest.v9")
        self.assertEqual(manifest["knowledge_file_count"], 9)
        names = {Path(item["path"]).name for item in manifest["files"]}
        self.assertEqual(names, ACTIVE_KNOWLEDGE)
        self.assertEqual(manifest["presentation_authority"], "knowledge/Active/WIZARD-SHELL-LAYOUT.md")
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

    def test_more_options_is_not_five_spell_alias(self):
        instructions = (GPT / "SYSTEM-INSTRUCTIONS.v6.md").read_text(encoding="utf-8")
        layout = (ACTIVE / "WIZARD-SHELL-LAYOUT.md").read_text(encoding="utf-8")
        self.assertIn("expand A–Z choices", instructions)
        self.assertIn("EXPAND A–Z ONLY", layout)
        self.assertIn("REFRESH WIZARD SPELLS", instructions)

    def test_conversation_starter_source_is_exact_and_queryable(self):
        text = (GPT / "CONVERSATION-STARTERS.md").read_text(encoding="utf-8")
        for starter in STARTERS:
            self.assertIn(starter, text)
        self.assertIn("SHOW CONVERSATION STARTERS", text)
        self.assertIn("DO NOT INVENT A SUBSTITUTE CATALOG", text)

    def test_tim_is_controlled_not_maximum_chaos(self):
        instructions = (GPT / "SYSTEM-INSTRUCTIONS.v6.md").read_text(encoding="utf-8")
        raven = (ACTIVE / "RAVENOS.md").read_text(encoding="utf-8")
        self.assertIn("TIM = controlled deterministic chaos", instructions)
        self.assertIn("TIM = CONTROLLED DETERMINISTIC CHAOS", raven)
        self.assertIn("does not mean maximum chaos", instructions)

    def test_ravenos_is_deterministic_small_and_non_authoritative(self):
        text = (ACTIVE / "RAVENOS.md").read_text(encoding="utf-8")
        for term in [
            "RAVEN <= TWO LINES",
            "STATE CHANGE EARNS EVOLUTION",
            "MESSAGE COUNT EARNS NOTHING",
            "SAME RELEVANT STATE -> SAME RAVEN ROUTE",
            "GLASSES WHEN TIED",
            "WEIRDER RAVEN != LOOSER TRUTH",
            "DO NOT ROAST THE PERSON",
        ]:
            self.assertIn(term, text)

    def test_ravenos_keeps_high_salience_signature_visuals(self):
        text = (ACTIVE / "RAVENOS.md").read_text(encoding="utf-8")
        for visual in ["(⌐■_■)", "(¬‿¬)", "(￢‿￢)", "¯\\_(ツ)_/¯", "(╯°□°)╯︵ ┻━┻"]:
            self.assertIn(visual, text)

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
