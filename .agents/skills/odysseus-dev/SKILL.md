---
name: odysseus-dev
description: How to set up, run, test, and syntax-check Odysseus locally, plus the repo's code and PR conventions. Use when working on any part of this repo (backend routes/services, src/ agent logic, or static/ UI).
---

# Working on Odysseus

FastAPI backend (`app.py`, `routes/`, `services/`, `src/`, `core/`) with a vanilla-JS ES-module frontend in `static/`. SQLite DB at `./data/app.db`.

## Setup

Python 3.11+ is what CI uses (3.10 also installs the pinned requirements fine).

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt   # ~ full core deps, no torch
mkdir -p data                                # sqlite DB lives at ./data/app.db
```

`requirements-optional.txt` holds per-feature extras (faster-whisper for local STT, ddgs for DuckDuckGo search, PDF form filling, …). Install only what the task needs; the app degrades gracefully without them.

Run the app:

```bash
./venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 7000
# or: cp .env.example .env && docker compose up -d --build   (also port 7000)
```

The first admin password is printed in the startup logs (`docker compose logs odysseus` under Docker).

## Checks

Always use the venv interpreter — the system `python3` lacks pinned deps and produces fake import errors.

```bash
./venv/bin/python -m pytest -q                 # full suite
./venv/bin/python -m pytest -q tests/test_x.py # focused run while iterating
```

The two blocking CI checks are syntax-only, so run them before pushing:

```bash
python3 -m compileall -q app.py core routes src services scripts tests
node --check static/js/<file>.js
```

`node --check` treats `.js` as CommonJS, so it fails on ES-module entrypoints such as `static/app.js` with a `MODULE_SUMMARY`/import error. Check those through stdin instead:

```bash
node --input-type=module --check < static/app.js
```

Most files under `static/js/` pass plain `node --check`.

The pytest job in CI is `continue-on-error` (known flaky/environment-dependent failures), so a red pytest job is not automatically your fault — but confirm on the base branch before calling a failure preexisting.

## Code conventions

- Never hardcode filesystem paths, ports, or loopback URLs. Every persisted file/dir has a named constant in `src/constants.py` (`AUTH_FILE`, `USER_PREFS_FILE`, `SETTINGS_FILE`, `TTS_CACHE_DIR`, `CHROMA_DIR`, `DATA_DIR`). Use `internal_api_base()` from `src.constants` instead of `http://localhost:7000`. `core/constants.py` only re-exports `src/constants.py`.
- The source tree is read-only under Docker and `/app/...` does not exist on native runs — guard directory creation so an unwritable path degrades instead of crashing at import.
- UI changes must reuse the existing CSS variables (`--red`, `--fg`, `--bg`, `--card`, `--border`), existing button/input/card classes, the monospaced font, and the dark-first theme system. No Unicode emoji in the UI — inline SVG only. Attach a screenshot of the running app for anything visual.
- Tests follow `tests/TESTING_STANDARD.md`: deterministic, behavior-first (no assertions on source text/AST), explicit setup. Shared helpers live in `tests/helpers/` and are documented in `tests/README.md`.

## PRs

- Conventional Commits: `type(scope): summary` (`fix`, `feat`, `refactor`, `docs`, `test`, `chore`, `ci`).
- Upstream (`odysseus-dev/odysseus`) takes PRs against `dev`, not `main`; this fork currently only has `main`.
- Keep PRs small and single-purpose, and state in the description which checks were actually run.
