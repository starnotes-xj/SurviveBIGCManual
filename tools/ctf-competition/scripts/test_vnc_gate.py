"""Focused tests for cross-session VNC input serialization."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import vnc_gate


class VncGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.state = Path(self.temp.name) / "shared-state"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_same_machine_is_serialized_and_owner_releases(self) -> None:
        self.assertEqual(vnc_gate.acquire(self.state, "agent-a", "ops-kali-01"), 0)
        self.assertEqual(vnc_gate.acquire(self.state, "agent-b", "OPS-KALI-01"), 3)
        self.assertEqual(vnc_gate.release(self.state, "agent-b", "ops-kali-01"), 2)
        self.assertEqual(vnc_gate.status(self.state, "ops-kali-01"), 0)
        self.assertEqual(vnc_gate.release(self.state, "agent-a", "ops-kali-01"), 0)
        self.assertEqual(vnc_gate.acquire(self.state, "agent-b", "ops-kali-01"), 0)

    def test_distinct_machines_can_be_claimed_independently(self) -> None:
        self.assertEqual(vnc_gate.acquire(self.state, "agent-a", "ops-kali-01"), 0)
        self.assertEqual(vnc_gate.acquire(self.state, "agent-b", "ops-kali-02"), 0)
        self.assertEqual(vnc_gate.status(self.state, "ops-kali-01"), 0)
        self.assertEqual(vnc_gate.status(self.state, "ops-kali-02"), 0)
        self.assertEqual(vnc_gate.release(self.state, "agent-a", "ops-kali-01"), 0)
        self.assertEqual(vnc_gate.status(self.state, "ops-kali-02"), 0)
        self.assertEqual(vnc_gate.release(self.state, "agent-b", "ops-kali-02"), 0)

    def test_malformed_lock_is_fail_closed(self) -> None:
        self.state.mkdir()
        vnc_gate.lock_path(self.state, "ops-kali-01").write_text("partial", encoding="utf-8")
        self.assertEqual(vnc_gate.acquire(self.state, "agent-b", "ops-kali-01"), 3)
        self.assertEqual(vnc_gate.status(self.state, "ops-kali-01"), 3)
        self.assertEqual(vnc_gate.release(self.state, "agent-b", "ops-kali-01"), 2)
        self.assertTrue(vnc_gate.lock_path(self.state, "ops-kali-01").exists())


if __name__ == "__main__":
    unittest.main()
