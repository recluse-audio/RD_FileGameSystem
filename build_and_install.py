#!/usr/bin/env python3
"""
Build RD_FileGameBuilder and RD_FileGameEngine, collect their executables,
and optionally install them to C:/FILE_GAMES.

Usage:
    python build_and_install.py           # build only
    python build_and_install.py --install # build + install

Run setup_env.py first to create the venv and install dependencies.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "SUBMODULES" / "RD_FileGameBuilder"))
from file_game_builder import refresh_game_data

ROOT      = Path(__file__).parent
SUBS      = ROOT / "SUBMODULES"
ENGINE    = SUBS / "RD_FileGameEngine"
BUILDER   = SUBS / "RD_FileGameBuilder"
GAMES_SRC = SUBS / "RD_FileGames"
DIST      = ROOT / "DIST"
INSTALL   = Path("C:/FILE_GAMES")
VENV_PY   = ROOT / ".venv" / "Scripts" / "python.exe"


def run(cmd, cwd):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)


def python():
    """Use venv python if available, otherwise system python."""
    return str(VENV_PY) if VENV_PY.exists() else sys.executable


def build_builder():
    print("\n=== Building RD_FileGameBuilder ===")
    run([
        python(), "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "FileGameBuilder",
        "--distpath", "BUILD",
        "--workpath", "BUILD/_work",
        "--specpath", "BUILD",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageTk",
        "view_data_layout.py",
    ], BUILDER)
    exe = BUILDER / "BUILD" / "FileGameBuilder.exe"
    if not exe.exists():
        sys.exit(f"ERROR: expected output not found: {exe}")
    return exe


def build_engine():
    print("\n=== Building RD_FileGameEngine ===")
    run([python(), "SCRIPTS/build_raylib.py"], ENGINE)
    for candidate in [
        ENGINE / "BUILD" / "Release" / "GameEngine_Raylib.exe",
        ENGINE / "BUILD" / "GameEngine_Raylib.exe",
    ]:
        if candidate.exists():
            return candidate
    sys.exit("ERROR: GameEngine_Raylib.exe not found after build.")


def collect(builder_exe: Path, engine_exe: Path) -> Path:
    print("\n=== Collecting executables into DIST/ ===")
    DIST.mkdir(exist_ok=True)
    for src in (builder_exe, engine_exe):
        dest = DIST / src.name
        shutil.copy2(src, dest)
        print(f"  {src.name}  ->  {dest}")
    return DIST


def install(dist: Path):
    print(f"\n=== Installing to {INSTALL} ===")
    INSTALL.mkdir(parents=True, exist_ok=True)
    games_dir = INSTALL / "GAMES"
    games_dir.mkdir(exist_ok=True)
    for exe in dist.glob("*.exe"):
        dest = INSTALL / exe.name
        shutil.copy2(exe, dest)
        print(f"  {exe.name}  ->  {dest}")
    if GAMES_SRC.is_dir():
        for game in sorted(GAMES_SRC.iterdir()):
            if not game.is_dir() or game.name.startswith("."):
                continue
            dest = games_dir / game.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(game, dest)
            print(f"  {game.name}/  ->  {dest}")
    print("Install complete.")


def refresh_games():
    print("\n=== Refreshing game data ===")
    for game in sorted(GAMES_SRC.iterdir()):
        if not game.is_dir() or game.name.startswith("."):
            continue
        print(f"  {game.name}:")
        refresh_game_data.run(str(game))


def main():
    parser = argparse.ArgumentParser(description="Build and optionally install the File Game suite.")
    parser.add_argument("--install", action="store_true", help="Install executables to C:/FILE_GAMES after building.")
    args = parser.parse_args()

    refresh_games()
    builder_exe = build_builder()
    engine_exe  = build_engine()
    dist        = collect(builder_exe, engine_exe)

    if args.install:
        install(dist)
    else:
        print(f"\nBuild complete. Run with --install to copy to {INSTALL}")
        print(f"Executables in: {DIST}")


if __name__ == "__main__":
    main()
