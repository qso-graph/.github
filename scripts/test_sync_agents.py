import tempfile
from pathlib import Path
import unittest

import sync_agents as s


class SyncAgentsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.guide = self.root / "AGENTS.md"
        self.block = s.canonical_block()

    def test_missing_file(self):
        self.assertFalse(s.synchronize(self.root, check=True))
        self.assertFalse(self.guide.exists())
        s.synchronize(self.root)
        self.assertEqual(self.guide.read_bytes(), b"# Agent guide\n\n" + self.block + b"\n\n## This repository\n\nAdd repository-specific guidance here.\n")
        self.assertEqual((self.root / "CLAUDE.md").read_bytes(), b"@AGENTS.md\n")
        self.assertTrue(s.synchronize(self.root, check=True))

    def test_without_block(self):
        self.guide.write_bytes(b"# Guide\n\nExisting guidance.\n")
        (self.root / "CLAUDE.md").write_bytes(b"Existing content\n")
        s.synchronize(self.root)
        self.assertEqual(self.guide.read_bytes(), b"# Guide\n\n" + self.block + b"\n\nExisting guidance.\n")
        self.assertEqual((self.root / "CLAUDE.md").read_bytes(), b"Existing content\n")

    def test_old_block(self):
        self.guide.write_bytes(b"# Guide\n\n" + s.START + b"\nOld\n" + s.END + b"\n\nKeep this.\n")
        self.assertFalse(s.synchronize(self.root, check=True))
        s.synchronize(self.root)
        self.assertEqual(self.guide.read_bytes(), b"# Guide\n\n" + self.block + b"\n\nKeep this.\n")

    def test_current_is_idempotent(self):
        self.guide.write_bytes(b"# Guide\n\n" + self.block + b"\n\nKeep this.\n")
        before = self.guide.read_bytes()
        self.assertTrue(s.synchronize(self.root, check=True))
        s.synchronize(self.root)
        s.synchronize(self.root)
        self.assertEqual(self.guide.read_bytes(), before)

    def test_incomplete_markers_are_rejected(self):
        self.guide.write_bytes(b"# Guide\n" + s.START)
        with self.assertRaises(ValueError):
            s.synchronize(self.root)
        self.assertEqual(self.guide.read_bytes(), b"# Guide\n" + s.START)


if __name__ == "__main__":
    unittest.main()
