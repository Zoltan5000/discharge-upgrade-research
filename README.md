# Discharge Upgrade Case Research Tool

A free tool for searching past military discharge upgrade and Character of Discharge decisions from public government sources, with a clean citation for each result.

> **This is a research tool, not legal advice.** Past decisions don't predict any individual outcome. The official decision always governs.

**Status:** early setup. Nothing is searchable yet. See `CLAUDE.md` for the full project brief.

## What's in here

| Folder | What it holds |
|---|---|
| `app/` | The search website, plus helpers such as the citation formatter |
| `collectors/` | Scripts that download decisions from each source |
| `data/raw/` | Original downloaded files, kept as-is (not stored in GitHub) |
| `data/processed/` | The search database built from the raw files (not stored in GitHub) |
| `tests/` | Automatic checks that the code still works |
| `docs/` | Notes on each data source |
| `LEARNING.md` | Short Python lessons that go with the code in this project |

## Run it on your computer

You need Python 3.11 or newer (https://www.python.org/downloads/).

```bash
# 1. One-time setup: make a private Python "box" for this project and install its tools
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Try the citation formatter
python -m app.citation

# 3. Run the automatic checks
pytest
```

## Updating the data

Coming later, once the collectors are built.

## Deploying

Coming later.
