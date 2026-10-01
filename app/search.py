"""Search the decisions database.

Run it:  python -m app.search marijuana
         python -m app.search "positive urinalysis" --outcome Denied
         python -m app.search --tag "Marijuana / THC"

The website will use the same search() function.
"""

import argparse
import json
import sqlite3
from datetime import date

from app.build_index import DB_PATH
from app.citation import format_citation


def search(words="", outcome=None, tag=None, year_from=None, year_to=None, sort="relevance", limit=50):
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row

    conditions, params = [], []
    if words:
        conditions.append("decisions_fts MATCH ?")
        params.append(words)  # quotes work for exact phrases: "liberal consideration"
    if outcome:
        conditions.append("d.outcome = ?")
        params.append(outcome)
    if tag:
        conditions.append("EXISTS (SELECT 1 FROM json_each(d.tags) WHERE value = ?)")
        params.append(tag)
    if year_from:
        conditions.append("d.decided >= ?")
        params.append(f"{year_from}-01-01")
    if year_to:
        conditions.append("d.decided <= ?")
        params.append(f"{year_to}-12-31")

    where = " AND ".join(conditions) or "1"
    order = "rank" if words and sort == "relevance" else "d.decided DESC"
    snippet = "snippet(decisions_fts, 0, '[', ']', ' … ', 30)" if words else "substr(f.text, 1, 200)"

    rows = db.execute(
        f"SELECT d.*, {snippet} AS snippet FROM decisions d JOIN decisions_fts f ON f.rowid = d.id "
        f"WHERE {where} ORDER BY {order} LIMIT ?",
        params + [limit],
    ).fetchall()
    total = db.execute(
        f"SELECT COUNT(*) FROM decisions d JOIN decisions_fts f ON f.rowid = d.id WHERE {where}", params
    ).fetchone()[0]
    db.close()
    return total, [dict(row) for row in rows]


def citation_for(row):
    return format_citation(
        board=row["source"],
        docket=row["docket"],
        decided=date.fromisoformat(row["decided"]) if row["decided"] else None,
        outcome=row["outcome"],
        before=row["discharge_before"] or "unknown",
        after=row["discharge_after"] or "unknown",
        url=row["url"],
    )


def main():
    parser = argparse.ArgumentParser(description="Search discharge upgrade decisions.")
    parser.add_argument("words", nargs="?", default="", help='search words; use quotes for a phrase')
    parser.add_argument("--outcome", choices=["Granted", "Granted in part", "Denied", "Other"])
    parser.add_argument("--tag")
    parser.add_argument("--from", dest="year_from", type=int)
    parser.add_argument("--to", dest="year_to", type=int)
    parser.add_argument("--sort", choices=["relevance", "date"], default="relevance")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    total, rows = search(args.words, args.outcome, args.tag, args.year_from, args.year_to, args.sort, args.limit)
    print(f"{total} matching decisions (showing {len(rows)})\n")
    for row in rows:
        print(citation_for(row))
        print(f"  Tags (auto-extracted): {', '.join(json.loads(row['tags'])) or 'none'}")
        print(f"  …{row['snippet']}…\n")


if __name__ == "__main__":
    main()
