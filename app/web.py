"""The search website.

Run it:  python -m app.web     then open http://127.0.0.1:5000 in your browser.
"""

import logging
from datetime import date
from urllib.parse import urlencode

from flask import Flask, Response, render_template, request
from markupsafe import Markup, escape

from app.build_index import DB_PATH
from app.export import to_csv, to_docx
from app.extract import EXTRA_TAG_GROUPS, TAG_GROUPS
from app.search import HIT_END, HIT_START, Query, search, sources_info

app = Flask(__name__)

# Privacy: don't write visitors' searches to the log. The standard request log
# prints every web address, and the address contains the search words.
logging.getLogger("werkzeug").setLevel(logging.ERROR)

PAGE_SIZE = 25
EXPORT_LIMIT = 2000
OUTCOMES = ["Granted", "Granted in part", "Denied", "Other"]
DISCHARGES = ["Honorable", "General", "OTH", "Bad Conduct", "Dishonorable", "Uncharacterized"]
TAG_CHOICES = {**{group: list(tags) for group, tags in TAG_GROUPS.items()}, **EXTRA_TAG_GROUPS}


def read_query(args):
    def year(name):
        value = args.get(name, "").strip()
        return int(value) if value.isdigit() else None

    return Query(
        words=args.get("q", "").strip(),
        sources=args.getlist("source"),
        outcomes=args.getlist("outcome"),
        before=args.getlist("before"),
        after=args.getlist("after"),
        tags=args.getlist("tag"),
        year_from=year("from"),
        year_to=year("to"),
        sort=args.get("sort", "relevance"),
        ids=[int(i) for i in args.getlist("id") if i.isdigit()],
    )


def describe(q):
    """A plain-English summary of the search, printed at the top of exports."""
    parts = [f'"{q.words}"' if q.words else "all decisions"]
    for label, values in [("source", q.sources), ("outcome", q.outcomes), ("before", q.before),
                          ("after", q.after), ("tags", q.tags)]:
        if values:
            parts.append(f"{label}: {', '.join(values)}")
    if q.year_from or q.year_to:
        parts.append(f"years {q.year_from or '…'}–{q.year_to or '…'}")
    if q.ids:
        parts.append(f"{len(q.ids)} selected")
    return "; ".join(parts)


@app.context_processor
def link_helpers():
    def with_args(path="/", **changes):
        """The current search's address, with some settings changed (e.g. page=2)."""
        args = request.args.to_dict(flat=False)
        args.pop("page", None)
        for key, value in changes.items():
            args[key] = [value]
        return f"{path}?{urlencode(args, doseq=True)}"

    return {"with_args": with_args}


@app.template_filter("highlight")
def highlight(text):
    """Escape the snippet safely, then turn our markers into <mark> highlights."""
    if not text:
        return ""
    safe = str(escape(text))
    return Markup(safe.replace(HIT_START, "<mark>").replace(HIT_END, "</mark>"))


@app.template_filter("long_date")
def long_date(value):
    if not value:
        return "Date not found"
    d = date.fromisoformat(value)
    return f"{d:%B} {d.day}, {d.year}"


@app.route("/")
def home():
    if not DB_PATH.exists():
        return render_template("no_data.html")
    q = read_query(request.args)
    page = max(1, request.args.get("page", 1, type=int))
    total, results, per_source = search(q, limit=PAGE_SIZE, offset=(page - 1) * PAGE_SIZE)
    return render_template(
        "search.html", q=q, results=results, total=total, per_source=per_source, page=page,
        pages=max(1, -(-total // PAGE_SIZE)), sources=sources_info(), outcomes=OUTCOMES,
        discharges=DISCHARGES, tag_choices=TAG_CHOICES, args=request.args,
    )


@app.route("/export")
def export():
    q = read_query(request.args)
    if request.args.get("selected") and not q.ids:
        return "No decisions were selected. Go back, tick the boxes next to the decisions you want, and try again.", 400
    _, results, _ = search(q, limit=EXPORT_LIMIT)
    stamp = date.today().isoformat()
    if request.args.get("format") == "docx":
        return Response(
            to_docx(results, describe(q)),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=citations-{stamp}.docx"},
        )
    return Response(to_csv(results), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=citations-{stamp}.csv"})


@app.route("/about")
def about():
    return render_template("about.html", sources=sources_info() if DB_PATH.exists() else [])


if __name__ == "__main__":
    app.run(debug=False)
