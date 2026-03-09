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

## Updating Submodules

```bash
git submodule update --remote --merge
```
