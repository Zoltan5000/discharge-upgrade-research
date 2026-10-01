"""Build the search database from the downloaded decisions.

Run it:  python -m app.build_index

Reads PDFs from data/raw/, saves the extracted text to data/processed/text/
(so later rebuilds are fast), and writes data/processed/decisions.db.
The database is rebuilt from scratch each time, so it's always in step with the raw files.
"""

import json
import sqlite3
from datetime import date
from pathlib import Path

from app.extract import parse_decision, pdf_to_text

RAW_DIR = Path("data/raw/army_drb")
TEXT_DIR = Path("data/processed/text/army_drb")
DB_PATH = Path("data/processed/decisions.db")
SITE = "https://boards.law.af.mil/"

SCHEMA = """
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,          -- e.g. 'Army Discharge Review Board'
    branch TEXT NOT NULL,
    docket TEXT NOT NULL,
    decided TEXT,                  -- YYYY-MM-DD (auto-extracted)
    outcome TEXT,                  -- auto-extracted
    discharge_before TEXT,         -- auto-extracted
    discharge_after TEXT,          -- auto-extracted
    narrative_reason TEXT,         -- auto-extracted
    tags TEXT,                     -- JSON list, auto-extracted
    url TEXT NOT NULL,
    collected TEXT NOT NULL
);
CREATE VIRTUAL TABLE decisions_fts USING fts5(text, tokenize = 'porter unicode61');
CREATE TABLE sources (source TEXT PRIMARY KEY, last_updated TEXT);
"""


def read_text(pdf):
    """Extract text once, then reuse the saved copy on later runs."""
    cached = TEXT_DIR / pdf.parent.name / (pdf.stem + ".txt")
    if cached.exists() and cached.stat().st_mtime >= pdf.stat().st_mtime:
        return cached.read_text()
    text = pdf_to_text(pdf)
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text(text)
    return text


def build():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.unlink(missing_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)

    pdfs = sorted(RAW_DIR.glob("CY*/*.pdf"))
    problems = 0
    for pdf in pdfs:
        try:
            record = parse_decision(read_text(pdf))
        except Exception as error:  # a damaged PDF shouldn't stop the whole build
            print(f"  could not read {pdf.name}: {error}")
            problems += 1
            continue
        cursor = db.execute(
            "INSERT INTO decisions (source, branch, docket, decided, outcome, discharge_before,"
            " discharge_after, narrative_reason, tags, url, collected) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                "Army Discharge Review Board",
                "Army",
                pdf.stem.replace("-Redacted", ""),
                record["decided"].isoformat() if record["decided"] else None,
                record["outcome"],
                record["before"],
                record["after"],
                record["narrative_reason"],
                json.dumps(record["tags"]),
                f"{SITE}ARMY/DRB/{pdf.parent.name}/{pdf.name}",
                date.fromtimestamp(pdf.stat().st_mtime).isoformat(),
            ),
        )
        db.execute("INSERT INTO decisions_fts (rowid, text) VALUES (?, ?)", (cursor.lastrowid, record["text"]))

    db.execute("INSERT INTO sources VALUES ('Army Discharge Review Board', ?)", (date.today().isoformat(),))
    db.commit()
    db.close()
    print(f"Indexed {len(pdfs) - problems} decisions into {DB_PATH} ({problems} could not be read)")


if __name__ == "__main__":
    build()
