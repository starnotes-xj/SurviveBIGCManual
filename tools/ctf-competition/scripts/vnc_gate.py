#!/usr/bin/env python3
"""Serialize VNC keyboard/mouse input per operator machine across cooperating agents."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


LOCK_PREFIX = "vnc-input-"


def lock_path(state_dir: Path, target: str) -> Path:
    """Return a stable per-machine lock path without using target text as a path."""
    key = hashlib.sha256(target.strip().casefold().encode("utf-8")).hexdigest()[:16]
    return state_dir / f"{LOCK_PREFIX}{key}.lock"


def read_lock(path: Path) -> dict[str, str]:
    """Read lock metadata. Any malformed or unreadable lock must remain blocking."""
    try:
        if path.is_symlink():
            raise ValueError("lock path is a symbolic link; treat it as held and inspect manually")
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read lock safely ({exc}); treat it as held") from exc
    if not isinstance(data, dict) or not all(
        isinstance(data.get(key), str) and data[key]
        for key in ("owner", "target", "acquired_utc")
    ):
        raise ValueError("lock metadata is invalid; treat it as held")
    return data


def acquire(state_dir: Path, owner: str, target: str) -> int:
    state_dir.mkdir(parents=True, exist_ok=True)
    path = lock_path(state_dir, target)
    payload = {
        "owner": owner,
        "target": target,
        "acquired_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        try:
            current = read_lock(path)
            print(
                f"BUSY: owner={current['owner']} target={current['target']} "
                f"acquired_utc={current['acquired_utc']}",
                file=sys.stderr,
            )
        except ValueError as exc:
            print(f"BUSY: {exc}", file=sys.stderr)
        return 3
    except OSError as exc:
        print(f"ERROR: cannot create VNC gate: {exc}", file=sys.stderr)
        return 2

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        # Leave a partial lock in place: a possibly active controller must not be
        # accidentally overlapped. The operator can inspect it and recover manually.
        print(f"ERROR: lock was created but metadata write failed; it remains blocking: {exc}", file=sys.stderr)
        return 2
    print(f"ACQUIRED: owner={owner} target={target} state_dir={state_dir}")
    return 0


def status(state_dir: Path, target: str | None = None) -> int:
    if target is not None:
        paths = [lock_path(state_dir, target)]
    elif state_dir.is_dir():
        paths = sorted(state_dir.glob(f"{LOCK_PREFIX}*.lock"))
    else:
        paths = []

    held = False
    invalid = False
    for path in paths:
        if not path.exists() and not path.is_symlink():
            continue
        try:
            current = read_lock(path)
        except FileNotFoundError:
            continue
        except ValueError as exc:
            held = True
            print(f"HELD: lock={path.name}: {exc}", file=sys.stderr)
            invalid = True
            continue
        held = True
        print(
            f"HELD: owner={current['owner']} target={current['target']} "
            f"acquired_utc={current['acquired_utc']}"
        )
    if invalid:
        return 3
    if not held:
        print("FREE" if target is not None else "FREE: no VNC targets are locked")
    return 0


def release(state_dir: Path, owner: str, target: str) -> int:
    path = lock_path(state_dir, target)
    try:
        current = read_lock(path)
    except FileNotFoundError:
        print("ERROR: no VNC gate is currently held", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if current["owner"] != owner:
        print(f"ERROR: gate belongs to {current['owner']!r}, not {owner!r}", file=sys.stderr)
        return 2
    try:
        path.unlink()
    except OSError as exc:
        print(f"ERROR: cannot release VNC gate: {exc}", file=sys.stderr)
        return 2
    print(f"RELEASED: owner={owner}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    acquire_parser = subparsers.add_parser("acquire", help="claim the shared VNC input gate")
    acquire_parser.add_argument("--state-dir", type=Path, required=True)
    acquire_parser.add_argument("--owner", required=True, help="unique AI session/agent label")
    acquire_parser.add_argument("--target", required=True, help="operator-machine/console alias, no credentials")

    status_parser = subparsers.add_parser("status", help="show whether VNC input is currently claimed")
    status_parser.add_argument("--state-dir", type=Path, required=True)
    status_parser.add_argument("--target", help="show one operator machine; omit to list all held targets")

    release_parser = subparsers.add_parser("release", help="release a gate owned by this session")
    release_parser.add_argument("--state-dir", type=Path, required=True)
    release_parser.add_argument("--owner", required=True)
    release_parser.add_argument("--target", required=True, help="operator-machine/console alias")

    args = parser.parse_args()
    if args.command == "acquire":
        if not args.owner.strip() or not args.target.strip():
            parser.error("--owner and --target must not be blank")
        return acquire(args.state_dir, args.owner, args.target)
    if args.command == "status":
        return status(args.state_dir, args.target)
    return release(args.state_dir, args.owner, args.target)


if __name__ == "__main__":
    raise SystemExit(main())
