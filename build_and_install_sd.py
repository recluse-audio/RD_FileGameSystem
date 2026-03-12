#!/usr/bin/env python3
"""
Refresh game data and install a FILE_GAME to the SD card for the ESP32
FileGame sketch.

Usage:
    python build_and_install_sd.py [<game>] [--dry-run]

  <game>     Name of the game folder in SUBMODULES/RD_FileGames/ (e.g. BBB).
             Required only when multiple games are present; omit if only one exists.
  --dry-run  Print what would be synced without making any changes.

Run setup_env.py first to create the venv and install dependencies.

SD card layout after install (E:\\):
    FILE_GAMES\\GAMES\\<game>\\   <- mirrors C:\\FILE_GAMES\\GAMES\\<game>\\ on desktop
        GUI\\
        LEVELS\\
        GAME_STATE\\
    FILE_GAME_SAVES\\             <- created if absent; matches DATA_ROOT in FileGame.ino

Notes:
  - Only files newer than the destination are copied (robocopy-style mirror).
  - _HiRes.png files are skipped — the ESP32 uses _320x240.png variants only.
  - The SD card must be mounted at E:\\ before running this script.
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "SUBMODULES" / "RD_FileGameBuilder"))
from file_game_builder import refresh_game_data

ROOT      = Path(__file__).parent
SUBS      = ROOT / "SUBMODULES"
GAMES_SRC = SUBS / "RD_FileGames"

SD_DRIVE   = Path("E:\\")
GAMES_ROOT = "FILE_GAMES/GAMES"   # mirrors C:\FILE_GAMES\GAMES\ on desktop
SAVES_ROOT = "FILE_GAME_SAVES"    # mirrors C:\FILE_GAME_SAVES\ on desktop

SKIP_SUFFIXES = {"_HiRes.png"}  # desktop-only assets, not needed on ESP32

# ---------------------------------------------------------------------------


def discover_games():
    if not GAMES_SRC.is_dir():
        print(f"Error: games directory not found: {GAMES_SRC}")
        sys.exit(1)
    return sorted(
        d.name for d in GAMES_SRC.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def refresh_games(games):
    print("\n=== Refreshing game data ===")
    for game_name in games:
        print(f"  {game_name}:")
        refresh_game_data.run(str(GAMES_SRC / game_name))


def should_skip(path: Path) -> bool:
    for suffix in SKIP_SUFFIXES:
        if path.name.endswith(suffix):
            return True
    return False


def sync_file(src: Path, dst: Path, dry_run: bool) -> bool:
    if dst.exists() and src.stat().st_mtime <= dst.stat().st_mtime:
        return False
    if dry_run:
        print(f"  [copy]   {dst.relative_to(SD_DRIVE)}")
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  copied   {dst.relative_to(SD_DRIVE)}")
    return True


def remove_extra(dst_root: Path, src_root: Path, dry_run: bool) -> int:
    removed = 0
    if not dst_root.exists():
        return 0
    for dst_file in dst_root.rglob("*"):
        if not dst_file.is_file():
            continue
        src_file = src_root / dst_file.relative_to(dst_root)
        if not src_file.exists():
            if dry_run:
                print(f"  [remove] {dst_file.relative_to(SD_DRIVE)}")
            else:
                dst_file.unlink()
                print(f"  removed  {dst_file.relative_to(SD_DRIVE)}")
            removed += 1
    return removed


def sync_tree(src_root: Path, dst_root: Path, dry_run: bool):
    copied = 0
    skipped = 0
    for src_file in src_root.rglob("*"):
        if not src_file.is_file():
            continue
        if should_skip(src_file):
            skipped += 1
            continue
        dst_file = dst_root / src_file.relative_to(src_root)
        if sync_file(src_file, dst_file, dry_run):
            copied += 1
    removed = remove_extra(dst_root, src_root, dry_run)
    return copied, skipped, removed


def ensure_dir(path: Path, dry_run: bool):
    if path.exists():
        return
    if dry_run:
        print(f"  [mkdir]  {path.relative_to(SD_DRIVE)}")
    else:
        path.mkdir(parents=True, exist_ok=True)
        print(f"  created  {path.relative_to(SD_DRIVE)}")


def main():
    args    = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry_run = "--dry-run" in sys.argv

    # --- Resolve game ---------------------------------------------------------
    all_games = discover_games()
    if not all_games:
        print(f"Error: no games found in {GAMES_SRC}")
        sys.exit(1)

    if args:
        game_name = args[0]
        if game_name not in all_games:
            print(f"Error: game '{game_name}' not found in {GAMES_SRC}")
            print(f"Available: {', '.join(all_games)}")
            sys.exit(1)
    elif len(all_games) == 1:
        game_name = all_games[0]
    else:
        print("Multiple games found — specify which to install:")
        for g in all_games:
            print(f"  python build_and_install_sd.py {g}")
        sys.exit(1)

    # --- Refresh game data ----------------------------------------------------
    if not dry_run:
        refresh_games([game_name])

    # --- Verify SD card -------------------------------------------------------
    if not SD_DRIVE.exists():
        print(f"\nError: SD card not found at {SD_DRIVE}")
        print("Insert the SD card and try again.")
        sys.exit(1)

    src   = GAMES_SRC / game_name
    dst   = SD_DRIVE / GAMES_ROOT / game_name
    saves = SD_DRIVE / SAVES_ROOT

    # --- Install --------------------------------------------------------------
    mode = "DRY RUN — " if dry_run else ""
    print(f"\n=== {mode}Installing {game_name} → {dst} ===")

    copied, skipped, removed = sync_tree(src, dst, dry_run)
    ensure_dir(saves, dry_run)

    # --- Report ---------------------------------------------------------------
    print()
    print(f"Done.  copied={copied}  removed={removed}  skipped(HiRes)={skipped}")
    if dry_run:
        print("(dry run — no files were changed)")


if __name__ == "__main__":
    main()
