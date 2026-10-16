"""Focused security and regression tests for safe_extract.py."""

from __future__ import annotations

import stat
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

import safe_extract


class SafeExtractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_extracts_regular_zip_and_tar_files(self) -> None:
        zip_path = self.root / "normal.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("src/solver.py", "print('review me')\n")
        zip_dest = self.root / "zip-out"
        zip_dest.mkdir()
        self.assertEqual(safe_extract.extract_zip(zip_path, zip_dest, 10, 1024), 1)
        self.assertEqual((zip_dest / "src/solver.py").read_text(), "print('review me')\n")

        tar_path = self.root / "normal.tar.gz"
        source = self.root / "note.txt"
        source.write_text("evidence, not instructions")
        with tarfile.open(tar_path, "w:gz") as tf:
            tf.add(source, arcname="nested/note.txt")
        tar_dest = self.root / "tar-out"
        tar_dest.mkdir()
        self.assertEqual(safe_extract.extract_tar(tar_path, tar_dest, 10, 1024), 1)
        self.assertEqual((tar_dest / "nested/note.txt").read_text(), "evidence, not instructions")

    def test_rejects_zip_traversal_before_writing(self) -> None:
        path = self.root / "traversal.zip"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("../outside.txt", "no")
        dest = self.root / "out"
        dest.mkdir()
        with self.assertRaises(safe_extract.UnsafeArchive):
            safe_extract.extract_zip(path, dest, 10, 1024)
        self.assertEqual(list(dest.iterdir()), [])
        self.assertFalse((self.root / "outside.txt").exists())

    def test_rejects_zip_symlink(self) -> None:
        path = self.root / "link.zip"
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr(info, "target")
        with self.assertRaises(safe_extract.UnsafeArchive):
            safe_extract.extract_zip(path, self.root / "out", 10, 1024)

    def test_rejects_tar_link(self) -> None:
        path = self.root / "link.tar"
        with tarfile.open(path, "w") as tf:
            info = tarfile.TarInfo("link")
            info.type = tarfile.SYMTYPE
            info.linkname = "target"
            tf.addfile(info)
        with self.assertRaises(safe_extract.UnsafeArchive):
            safe_extract.extract_tar(path, self.root / "out", 10, 1024)

    def test_rejects_path_collision_and_limits(self) -> None:
        with self.assertRaises(safe_extract.UnsafeArchive):
            safe_extract.preflight([("node", 0, "file"), ("node/child", 1, "file")], 10, 1024)
        with self.assertRaises(safe_extract.UnsafeArchive):
            safe_extract.preflight([("a", 1, "file"), ("b", 1, "file")], 1, 1024)
        with self.assertRaises(safe_extract.UnsafeArchive):
            safe_extract.preflight([("a", 1025, "file")], 10, 1024)

    def test_rejects_windows_special_paths(self) -> None:
        for name in ("C:/outside.txt", "folder/file:stream", "CON.txt", "trailing./name"):
            with self.subTest(name=name), self.assertRaises(safe_extract.UnsafeArchive):
                safe_extract.safe_relative(name)


if __name__ == "__main__":
    unittest.main()
