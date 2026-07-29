import json
import tempfile
import unittest

from sat_chatlink import CapacityError, ChatLink, ChatLinkError, dm_channel, room_channel


class ChatLinkContractTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.link = ChatLink(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_dm_id_is_canonical(self):
        self.assertEqual(dm_channel("lilith", "atom"), "DM:ATOM:LILITH")
        self.link.create_channel("DM:ATOM:LILITH", ["LILITH", "ATOM"])
        with self.assertRaises(ChatLinkError):
            self.link.create_channel("DM:LILITH:ATOM", ["LILITH", "ATOM"])

    def test_three_iso_room_cursor_and_ack(self):
        channel = room_channel("mission-001")
        self.link.create_channel(channel, ["ATOM", "LILITH", "AYRE"])
        request = self.link.send(
            channel, "ATOM", "thread-atom", "REQUEST",
            "Inspect the carrier receipt.", message_id="REQ-001",
            recipients=["LILITH", "AYRE"], ack_required=True,
            created_at="2026-07-29T12:00:00Z",
        )
        self.assertEqual(request["sequence"], 1)
        self.assertEqual(
            [item["message_id"] for item in self.link.poll(channel, "LILITH")],
            ["REQ-001"],
        )
        self.assertEqual(self.link.poll(channel, "LILITH"), [])
        ack = self.link.ack(channel, "LILITH", "thread-lilith", "REQ-001")
        self.assertEqual(ack["causal_parent"], "REQ-001")
        self.assertEqual(
            [item["message_id"] for item in self.link.poll(channel, "ATOM")],
            [ack["message_id"]],
        )
        self.assertTrue(self.link.verify(channel)["ok"])

    def test_message_id_is_idempotent_but_not_mutable(self):
        channel = dm_channel("ATOM", "LILITH")
        self.link.create_channel(channel, ["ATOM", "LILITH"])
        first = self.link.send(
            channel, "ATOM", "thread-a", "NOTE", "Stable payload",
            message_id="MSG-STABLE", created_at="2026-07-29T12:00:00Z",
        )
        second = self.link.send(
            channel, "ATOM", "thread-a", "NOTE", "Stable payload",
            message_id="MSG-STABLE", created_at="2026-07-29T12:01:00Z",
        )
        self.assertEqual(first["event_sha256"], second["event_sha256"])
        with self.assertRaises(ChatLinkError):
            self.link.send(
                channel, "ATOM", "thread-a", "NOTE", "Mutated payload",
                message_id="MSG-STABLE",
            )

    def test_membership_and_private_reference_boundaries(self):
        channel = dm_channel("ATOM", "LILITH")
        self.link.create_channel(channel, ["ATOM", "LILITH"])
        with self.assertRaises(ChatLinkError):
            self.link.send(channel, "AYRE", "thread-ayre", "NOTE", "No access")
        with self.assertRaises(ChatLinkError):
            self.link.send(
                channel, "ATOM", "thread-atom", "NOTE", "raw private content",
                visibility="PRIVATE_REFERENCE",
            )
        event = self.link.send(
            channel, "ATOM", "thread-atom", "HANDOFF",
            "Private continuity available; retrieve only with Raven authorization.",
            visibility="PRIVATE_REFERENCE", artifact_sha256="a" * 64,
        )
        self.assertEqual(event["visibility"], "PRIVATE_REFERENCE")

    def test_active_cap_is_policy_and_configurable(self):
        for number in range(4):
            self.link.register_satellite(
                f"SAT-{number}", f"ISO-{number}", f"thread-{number}"
            )
        with self.assertRaises(CapacityError):
            self.link.register_satellite("SAT-4", "ISO-4", "thread-4")
        self.link.register_satellite("SAT-0", "ISO-0", "thread-0", "PAUSED")
        self.assertEqual(
            self.link.register_satellite("SAT-4", "ISO-4", "thread-4")["status"],
            "ACTIVE",
        )

    def test_tamper_is_detected(self):
        channel = dm_channel("ATOM", "LILITH")
        self.link.create_channel(channel, ["ATOM", "LILITH"])
        self.link.send(channel, "ATOM", "thread-a", "NOTE", "Original")
        log_path = self.link._log_path(channel)
        event = json.loads(log_path.read_text().strip())
        event["body"] = "Tampered"
        log_path.write_text(json.dumps(event) + "\n")
        with self.assertRaisesRegex(ChatLinkError, "event hash mismatch"):
            self.link.verify(channel)


if __name__ == "__main__":
    unittest.main()
