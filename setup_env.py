#!/usr/bin/env python3
"""
Create a local .venv and install all build dependencies.

Run this once before using build_and_install.py:
    python setup_env.py
"""

import subprocess
import sys
import venv
from pathlib import Path

ROOT     = Path(__file__).parent
VENV_DIR = ROOT / ".venv"
VENV_PY  = VENV_DIR / "Scripts" / "python.exe"
REQS     = ROOT / "requirements.txt"


def run(cmd, cwd=ROOT):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main():
    if not VENV_PY.exists():
        print(f"Creating venv at {VENV_DIR} ...")
        venv.create(str(VENV_DIR), with_pip=True)
    else:
        print(f"Venv already exists at {VENV_DIR}")

    print("Installing dependencies from requirements.txt ...")
    run([str(VENV_PY), "-m", "pip", "install", "--quiet", "-r", str(REQS)])
    print("Done. You can now run: python build_and_install.py --install")


if __name__ == "__main__":
    main()
