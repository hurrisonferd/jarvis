from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from musicos.models import MusicIntent
from musicos.runtime import MusicOSRuntime


class MusicOSRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime_root = Path(__file__).resolve().parent.parent
        self.runtime = MusicOSRuntime(self.runtime_root)

    def test_compile_preserves_defaults(self) -> None:
        track = self.runtime.compile(MusicIntent(text="neon race with elastic bass and dry drums"))
        self.assertEqual(track.bpm, 102)
        self.assertEqual(track.key, "F# minor")
        self.assertIn("elasticity", track.physics)
        self.assertIn("subdivision precision", track.physics)
        self.assertIn("102 BPM", track.prompt)

    def test_vault_import_tracks_raw_and_canon(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            vault = Path(temp)
            (vault / "Inbox" / "raw-chat-exports").mkdir(parents=True)
            (vault / "Canon").mkdir()
            (vault / "Inbox" / "raw-chat-exports" / "music.txt").write_text("MusicOS PromptAI rail authority", encoding="utf-8")
            (vault / "Canon" / "music.md").write_text("MusicOS many parts, one rail", encoding="utf-8")
            result = self.runtime.import_vault(vault)
            self.assertEqual(result["source_count"], 2)
            self.assertEqual(result["status_counts"]["RAW"], 1)
            self.assertEqual(result["status_counts"]["CANON"], 1)


if __name__ == "__main__":
    unittest.main()
