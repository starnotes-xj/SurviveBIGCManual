#!/usr/bin/env python3
"""Safely extract regular files from ZIP/TAR archives without executing them."""

from __future__ import annotations

import argparse
import os
import stat
import tarfile
import zipfile
from pathlib import Path, PurePosixPath


class UnsafeArchive(ValueError):
    pass


def safe_relative(name: str) -> Path:
    """Convert an archive member name to a safe platform path."""
    if not name or "\x00" in name:
        raise UnsafeArchive(f"empty or NUL-containing member path: {name!r}")
    normalized = name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or normalized.startswith("//"):
        raise UnsafeArchive(f"absolute member path: {name!r}")
    if any(part in ("", ".", "..") for part in pure.parts):
        raise UnsafeArchive(f"unsafe member path: {name!r}")
    for part in pure.parts:
        stem = part.split(".", 1)[0].upper()
        if ":" in part or part.startswith("~") or part.endswith((".", " ")):
            raise UnsafeArchive(f"Windows-special path component: {name!r}")
        if stem in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
            raise UnsafeArchive(f"Windows device path: {name!r}")
    return Path(*pure.parts)


def preflight(items: list[tuple[str, int, str]], max_files: int, max_bytes: int) -> list[tuple[Path, int, str]]:
    if len(items) > max_files:
        raise UnsafeArchive(f"archive has {len(items)} entries; limit is {max_files}")
    result: list[tuple[Path, int, str]] = []
    seen: set[str] = set()
    total = 0
    for name, size, kind in items:
        rel = safe_relative(name.rstrip("/\\")) if kind != "dir" else safe_relative(name.rstrip("/\\"))
        key = rel.as_posix().casefold()
        if key in seen:
            raise UnsafeArchive(f"duplicate/case-colliding path: {name!r}")
        seen.add(key)
        if size < 0:
            raise UnsafeArchive(f"negative member size: {name!r}")
        total += size
        if total > max_bytes:
            raise UnsafeArchive(f"uncompressed size exceeds limit ({max_bytes} bytes)")
        result.append((rel, size, kind))
    # Reject a regular file that is also a parent directory of another entry.
    files = {p.as_posix().casefold() for p, _, kind in result if kind == "file"}
    for rel, _, _ in result:
        for parent in rel.parents:
            if parent != Path(".") and parent.as_posix().casefold() in files:
                raise UnsafeArchive(f"file/directory path collision: {rel}")
    return result


def extract_zip(archive: Path, dest: Path, max_files: int, max_bytes: int) -> int:
    with zipfile.ZipFile(archive) as zf:
        infos = zf.infolist()
        items: list[tuple[str, int, str]] = []
        for info in infos:
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise UnsafeArchive(f"symbolic link is not allowed: {info.filename!r}")
            kind = "dir" if info.is_dir() else "file"
            if kind == "file" and mode and not (stat.S_ISREG(mode) or stat.S_IFMT(mode) == 0):
                raise UnsafeArchive(f"special file is not allowed: {info.filename!r}")
            items.append((info.filename, 0 if kind == "dir" else info.file_size, kind))
        preflight(items, max_files, max_bytes)
        count = 0
        for info in infos:
            rel = safe_relative(info.filename.rstrip("/\\"))
            target = dest / rel
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation prevents overwriting files or following an existing leaf symlink.
            with zf.open(info, "r") as src, target.open("xb") as out:
                remaining = info.file_size
                while remaining:
                    chunk = src.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise UnsafeArchive(f"truncated member: {info.filename!r}")
                    out.write(chunk)
                    remaining -= len(chunk)
                if src.read(1):
                    raise UnsafeArchive(f"member exceeded declared size: {info.filename!r}")
            count += 1
        return count


def extract_tar(archive: Path, dest: Path, max_files: int, max_bytes: int) -> int:
    with tarfile.open(archive, mode="r:*") as tf:
        members = tf.getmembers()
        items: list[tuple[str, int, str]] = []
        for member in members:
            if member.isdir():
                kind = "dir"
            elif member.isreg():
                kind = "file"
            else:
                raise UnsafeArchive(f"link or special file is not allowed: {member.name!r}")
            items.append((member.name, 0 if kind == "dir" else member.size, kind))
        preflight(items, max_files, max_bytes)
        count = 0
        for member in members:
            rel = safe_relative(member.name.rstrip("/\\"))
            target = dest / rel
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            src = tf.extractfile(member)
            if src is None:
                raise UnsafeArchive(f"cannot read member: {member.name!r}")
            with src, target.open("xb") as out:
                remaining = member.size
                while remaining:
                    chunk = src.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise UnsafeArchive(f"truncated member: {member.name!r}")
                    out.write(chunk)
                    remaining -= len(chunk)
                if src.read(1):
                    raise UnsafeArchive(f"member exceeded declared size: {member.name!r}")
            count += 1
        return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--max-files", type=int, default=2000)
    parser.add_argument("--max-bytes", type=int, default=200 * 1024 * 1024)
    parser.add_argument("--max-archive-bytes", type=int, default=200 * 1024 * 1024)
    args = parser.parse_args()
    if args.archive.is_symlink():
        parser.error("archive must not be a symbolic link")
    archive = args.archive.resolve(strict=True)
    dest = args.destination.resolve()
    if not archive.is_file():
        parser.error("archive must be a regular file")
    if args.max_files < 1 or args.max_bytes < 1 or args.max_archive_bytes < 1:
        parser.error("limits must be positive")
    if archive.stat().st_size > args.max_archive_bytes:
        parser.error(f"archive exceeds compressed-size limit ({args.max_archive_bytes} bytes)")
    if dest == archive.parent or dest == archive:
        parser.error("destination must be a separate directory")
    if dest.exists() and (not dest.is_dir() or any(dest.iterdir())):
        parser.error("destination must be an empty directory or not exist")
    dest.mkdir(parents=True, exist_ok=True)
    try:
        if zipfile.is_zipfile(archive):
            count = extract_zip(archive, dest, args.max_files, args.max_bytes)
        elif tarfile.is_tarfile(archive):
            count = extract_tar(archive, dest, args.max_files, args.max_bytes)
        else:
            raise UnsafeArchive("unsupported or invalid archive (supported: ZIP, TAR, TAR.GZ, TGZ)")
    except (UnsafeArchive, zipfile.BadZipFile, tarfile.TarError, OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 2
    print(f"Extracted {count} regular file(s) to {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
