#!/usr/bin/env python3
from __future__ import annotations
import unittest
import bootos_menu as menu

class BootMenuTests(unittest.TestCase):
    def test_root_menu_opens_submenu(self):
        engine = menu.BootMenu()
        engine.execute("4")
        self.assertEqual(engine.state.menu, "MUSICOS")
        self.assertEqual(engine.state.path, ["ROOT", "MUSICOS"])

    def test_repeated_hotkey_direct_opens(self):
        engine = menu.BootMenu()
        engine.execute("66")
        self.assertEqual(engine.state.menu, "JORM")
        self.assertIn("direct_hotkey=true", engine.state.results)

    def test_recursive_compact_path(self):
        engine = menu.BootMenu()
        engine.execute("41")
        self.assertEqual(engine.state.menu, "MUSICOS")
        self.assertIn("action=CREATE", engine.state.results)

    def test_zero_returns_to_root(self):
        engine = menu.BootMenu()
        engine.execute("3")
        engine.execute("0")
        self.assertEqual(engine.state.menu, "ROOT")

    def test_invalid_command_stays_put(self):
        engine = menu.BootMenu()
        engine.execute("2")
        engine.execute("hello")
        self.assertEqual(engine.state.menu, "EGO")
        self.assertIn("COMMAND REJECTED", engine.state.results)

    def test_safe_exit_is_non_writing(self):
        engine = menu.BootMenu()
        engine.execute("99")
        self.assertTrue(engine.state.exited)
        self.assertIn("writes=none", engine.state.runtime)

    def test_trilog_is_exact_height(self):
        rendered = menu.BootMenu().render(width=108, height=30)
        self.assertEqual(len(rendered.splitlines()), 30)
        self.assertIn("DISPLAY_LOG", rendered.splitlines()[0])
        self.assertIn("RESULTS_LOG", rendered)
        self.assertIn("RUNTIME_LOG", rendered)

    def test_wide_menu_uses_three_columns(self):
        rendered = menu.BootMenu().render(width=108, height=30)
        display = rendered.split("RESULTS_LOG", 1)[0]
        self.assertIn(" | ", display)

    def test_iso_registry_contains_core_roles(self):
        self.assertEqual(menu.ISO_REGISTRY["RAVEN"], "operator")
        self.assertEqual(menu.ISO_REGISTRY["ROBOBOY"], "anti-flattening audit")

if __name__ == "__main__":
    unittest.main(verbosity=2)
