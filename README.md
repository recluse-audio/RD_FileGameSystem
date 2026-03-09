# RD_FileGameSystem

A release pipeline and unified distribution for the **RD File Game** suite — an engine and project builder for making simple "file games" compatible with ESP32 and a Raylib desktop app.

## Components

| Submodule | Description |
|---|---|
| [RD_FileGameEngine](https://github.com/recluse-audio/RD_FileGameEngine) | Core runtime engine for file games |
| [RD_FileGameBuilder](https://github.com/recluse-audio/RD_FileGameBuilder) | Project builder / authoring tool |

Both are included as git submodules under the `SUBMODULES/` directory.

## Getting Started

Clone with submodules:

```bash
git clone --recurse-submodules https://github.com/recluse-audio/RD_FileGameSystem.git
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

## Build & Install

`build_and_install.py` builds both products, collects the executables into `DIST/`, and optionally installs them to `C:/FILE_GAMES`.

**Requirements:** Python 3, CMake, a C++ compiler (MSVC or MinGW), PyInstaller (`pip install pyinstaller`).

```bash
# Build only — outputs to DIST/
python build_and_install.py

# Build + install to C:/FILE_GAMES
python build_and_install.py --install
```

Outputs:
- `DIST/FileGameBuilder.exe`
- `DIST/GameEngine_Raylib.exe`

## Updating Submodules

```bash
git submodule update --remote --merge
```
