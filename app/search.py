"""Search the decisions database. The website and the command line both use search().

Command line:
    python -m app.search marijuana
    python -m app.search "positive urinalysis" --outcome Denied
    python -m app.search --tag "Marijuana / THC" --tag PTSD
"""

import argparse
import json
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import date

from app.build_index import DB_PATH
from app.citation import format_citation

# Snippet highlight markers; the website turns them into <mark> after escaping the text.
HIT_START, HIT_END = "\x02", "\x03"


@dataclass
class Query:
    words: str = ""
    sources: list = field(default_factory=list)
    outcomes: list = field(default_factory=list)
    before: list = field(default_factory=list)
    after: list = field(default_factory=list)
    tags: list = field(default_factory=list)   # a decision must have ALL of these
    year_from: int = None
    year_to: int = None
    sort: str = "relevance"                    # or "newest" / "oldest"
    ids: list = field(default_factory=list)    # only these decisions (for "export selected")


def to_match(words):
    """Turn what a person typed into a safe full-text query.

    "exact phrase" stays a phrase, OR and NOT work between terms, word* matches word beginnings,
    and stray punctuation (which would otherwise cause an error) is ignored.
    """
    items = []
    for phrase, word in re.findall(r'"([^"]*)"|(\S+)', words):
        if word.upper() in ("OR", "NOT", "AND"):
            items.append(word.upper())
            continue
        prefix = word.endswith("*")
        cleaned = " ".join(re.findall(r"\w+", phrase or word))
        if cleaned:
            items.append(f'"{cleaned}"' + ("*" if prefix and not phrase else ""))

    # Keep an operator only when it sits between two search terms.
    query = []
    for i, item in enumerate(items):
        is_operator = item in ("OR", "NOT", "AND")
        if is_operator and (not query or query[-1] in ("OR", "NOT", "AND") or i == len(items) - 1):
            continue
        query.append(item)
    while query and query[-1] in ("OR", "NOT", "AND"):
        query.pop()
    return " ".join(query)


def _where(q, include_sources=True):
    conditions, params = [], []
    match = to_match(q.words)
    if match:
        conditions.append("decisions_fts MATCH ?")
        params.append(match)
    lists = [("d.outcome", q.outcomes), ("d.discharge_before", q.before), ("d.discharge_after", q.after),
             ("d.id", q.ids)]
    if include_sources:
        lists.append(("d.source", q.sources))
    for column, values in lists:
        if values:
            conditions.append(f"{column} IN ({','.join('?' * len(values))})")
            params.extend(values)
    for tag in q.tags:
        conditions.append("EXISTS (SELECT 1 FROM json_each(d.tags) WHERE value = ?)")
        params.append(tag)
    if q.year_from:
        conditions.append("d.decided >= ?")
        params.append(f"{q.year_from}-01-01")
    if q.year_to:
        conditions.append("d.decided <= ?")
        params.append(f"{q.year_to}-12-31")
    return " AND ".join(conditions) or "1", params, bool(match)


def search(q, limit=25, offset=0):
    """Return (total count, one page of results, counts per source)."""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    tables = "decisions d JOIN decisions_fts ON decisions_fts.rowid = d.id"

    where, params, has_words = _where(q)
    order = {"newest": "d.decided DESC", "oldest": "d.decided ASC"}.get(q.sort)
    if not order:
        order = "rank" if has_words else "d.decided DESC"
    snippet = (f"snippet(decisions_fts, 0, '{HIT_START}', '{HIT_END}', '…', 40)" if has_words else "NULL")

    rows = db.execute(
        f"SELECT d.*, {snippet} AS snippet FROM {tables} WHERE {where} ORDER BY {order} LIMIT ? OFFSET ?",
        params + [limit, offset],
    ).fetchall()
    total = db.execute(f"SELECT COUNT(*) FROM {tables} WHERE {where}", params).fetchone()[0]

    # Counts per source ignore the source filter, so people can see what they'd get by switching.
    where_all, params_all, _ = _where(q, include_sources=False)
    per_source = dict(db.execute(
        f"SELECT d.source, COUNT(*) FROM {tables} WHERE {where_all} GROUP BY d.source", params_all
    ).fetchall())
    db.close()

    results = []
    for row in rows:
        result = dict(row)
        result["tags"] = json.loads(result["tags"])
        result["citation"] = citation_for(result)
        results.append(result)
    return total, results, per_source


def sources_info():
    """Every source with its decision count and last-updated date."""
    db = sqlite3.connect(DB_PATH)
    rows = db.execute(
        "SELECT s.source, s.last_updated, COUNT(d.id) FROM sources s LEFT JOIN decisions d ON d.source = s.source "
        "GROUP BY s.source ORDER BY s.source"
    ).fetchall()
    db.close()
    return rows


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
    parser.add_argument("words", nargs="?", default="", help="search words; use quotes for a phrase")
    parser.add_argument("--outcome", action="append", default=[],
                        choices=["Granted", "Granted in part", "Denied", "Other"])
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--from", dest="year_from", type=int)
    parser.add_argument("--to", dest="year_to", type=int)
    parser.add_argument("--sort", choices=["relevance", "newest", "oldest"], default="relevance")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    q = Query(words=args.words, outcomes=args.outcome, tags=args.tag,
              year_from=args.year_from, year_to=args.year_to, sort=args.sort)
    total, rows, _ = search(q, limit=args.limit)
    print(f"{total} matching decisions (showing {len(rows)})\n")
    for row in rows:
        print(row["citation"])
        print(f"  Tags (auto-extracted): {', '.join(row['tags']) or 'none'}")
        text = row["snippet"] or row["summary"] or ""
        print(f"  …{text.replace(HIT_START, '[').replace(HIT_END, ']')}…\n")


if __name__ == "__main__":
    main()
