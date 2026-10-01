# Discharge Upgrade Case Research Tool

A free tool for searching past military discharge upgrade and Character of Discharge decisions from public government sources, with a clean citation for each result.

> **This is a research tool, not legal advice.** Past decisions don't predict any individual outcome. The official decision always governs.

**Status:** prototype in progress. Army Discharge Review Board decisions (2024 onward) can be downloaded and searched from the command line. The website comes next. See `CLAUDE.md` for the full project brief.

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

# 2. Run the automatic checks
pytest
```

## Search (command line, for now)

```bash
python -m app.search marijuana
python -m app.search "positive urinalysis" --outcome Denied
python -m app.search --tag "Marijuana / THC"          # also catches "THC", "cannabis", "Delta-8"
python -m app.search '"liberal consideration"' --from 2025 --sort date
```

- Put quotes around an exact phrase. Search also matches word forms: `deny` finds "denied".
- Outcome choices: `Granted`, `Granted in part`, `Denied`, `Other`.
- Tags: Marijuana / THC, Other drug use, Positive urinalysis, Alcohol, PTSD, TBI, Other mental health,
  MST / sexual assault, AWOL / desertion, DADT / sexual orientation, COVID-19 vaccine,
  COVID-19 proactive review, Personal appearance hearing, Counsel present.

**Outcome, discharge types and tags are read automatically from the text and may be wrong. The official decision governs.**
Tags skip the standard legal paragraphs that appear in every decision, so a "PTSD" tag means PTSD came up in that case's facts.

## Updating the data

```bash
python -m collectors.army_drb          # downloads new Army DRB decisions (2024 to this year)
python -m collectors.army_drb 2023     # or choose years
python -m app.build_index              # rebuilds the search database
```

The downloader waits 3 seconds between files, so a first run takes a while (the site can be slow).
It's safe to stop and re-run: it only fetches files it doesn't already have.

## Deploying

Coming later.
