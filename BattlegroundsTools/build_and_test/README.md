# build_and_test

Everything for developing bgtools, kept apart from the program itself.

| Item | What it is |
|---|---|
| `build_exe.bat` | Builds `release\bgtools.exe` with PyInstaller. |
| `tests\` | Automated tests. |
| `samples\` | Sample data for tests and demos. |
| `build\` | PyInstaller work files. Created by `build_exe.bat`, not committed. |
| `release\` | The finished `.exe` plus the license and README. Created by `build_exe.bat`, not committed. |

## Run the tests

From the repo root (the folder with `run_bgtools.bat`):

```powershell
python -m unittest discover -s build_and_test/tests -v
```

If you use pytest, `pytest` from the repo root does the same (settings are in `pyproject.toml`).

The tests do not need Hearthstone or an internet connection. They replay a made-up game (`tests\fake_game.py`) through the log parser, the tracker data and the screen layout, and `test_architecture.py` checks that imports only point inward (see `docs\ARCHITECTURE.md`).

## Build the .exe

1. Install PyInstaller once: `python -m pip install pyinstaller`
2. Double-click `build_exe.bat`.
3. Find `release\bgtools.exe`. Put the folder it is in anywhere; a `data\` folder next to it holds your triple targets and saved games.

The license is AGPL-3.0. If you give the `.exe` to other people, also give them the matching source: link the release tag in the README and the release notes. `build_exe.bat` copies `docs\LICENSE` next to the `.exe`.

## Publishing

Do not commit `build\` or `release\`. Upload `release\bgtools.exe` to a GitHub Release instead.
