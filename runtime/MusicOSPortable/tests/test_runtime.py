from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from musicos.models import MusicIntent
from musicos.rehydration import rehydrate_sources
from musicos.runtime import MusicOSRuntime


class MusicOSRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime_root = Path(__file__).resolve().parent.parent
        self.runtime = MusicOSRuntime(self.runtime_root)

    def test_compile_preserves_raven_defaults_and_prompt_contract(self) -> None:
        track = self.runtime.compile(MusicIntent(
            text="neon race with elastic bass and dry drums",
            styles=["synthpop rock", "PS1 racing-game drive"],
        ))
        self.assertEqual(track.bpm, 102)
        self.assertEqual(track.key, "F# minor")
        self.assertIn("elasticity", track.physics)
        self.assertIn("subdivision precision", track.physics)
        self.assertEqual(len(track.styles), 2)
        self.assertTrue(track.prompt.endswith("102 BPM."))
        self.assertIn("This track conveys", track.prompt)
        self.assertNotIn("Suno", track.prompt)

    def test_named_influence_is_translated(self) -> None:
        track = self.runtime.compile(MusicIntent(
            text="Copeland and Bonham drums, no vocals",
        ))
        self.assertNotIn("Copeland", track.prompt)
        self.assertNotIn("Bonham", track.prompt)
        self.assertIn("articulate hi-hat intelligence", track.prompt)
        self.assertIn("heavyweight kick-snare authority", track.prompt)
        self.assertIn("instrumental focus", track.prompt)

    def test_vault_import_tracks_raw_and_canon(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            vault = Path(temp)
            (vault / "Inbox" / "raw-chat-exports").mkdir(parents=True)
            (vault / "Canon").mkdir()
            (vault / "Inbox" / "raw-chat-exports" / "music.txt").write_text(
                "MusicOS PromptAI rail authority", encoding="utf-8"
            )
            (vault / "Canon" / "music.md").write_text(
                "MusicOS many parts, one rail", encoding="utf-8"
            )
            result = self.runtime.import_vault(vault)
            self.assertEqual(result["source_count"], 2)
            self.assertEqual(result["status_counts"]["RAW"], 1)
            self.assertEqual(result["status_counts"]["CANON"], 1)

    def test_rehydration_marks_missing_required_without_promoting_raw(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / "Jorm" / "Vault" / "Sources" / "MusicOS").mkdir(parents=True)
            (repo / "Jorm" / "Vault" / "GLOBAL_CAPTURE_INDEX.md").write_text(
                "MusicOS", encoding="utf-8"
            )
            (repo / "Jorm" / "Vault" / "Sources" / "MusicOS" / "contract.md").write_text(
                "MusicOS permanence", encoding="utf-8"
            )
            result = rehydrate_sources(repo, repo / "receipt.json")
            self.assertEqual(result["coverage"], "PARTIAL")
            self.assertIn("musicos_raw_exports", result["missing_required"])
            self.assertTrue(all(
                source["canon_promotion"] == "PROHIBITED_AUTOMATICALLY"
                for source in result["sources"]
            ))


if __name__ == "__main__":
    unittest.main()
