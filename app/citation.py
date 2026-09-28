"""Turn one decision record into a one-line legal citation.

Format (from CLAUDE.md, section 6):
[Board name], Docket No. [number] ([Month Day, Year]) ([outcome]; [before] → [after]), available at [official URL].
"""

from datetime import date


def format_citation(board, docket, decided, outcome, before, after, url):
    """Build the citation text for a single decision."""
    if not url:
        # The official link is required. Never make a citation without it.
        raise ValueError("A citation needs the official source URL.")

    # e.g. date(2024, 3, 5) -> "March 5, 2024"
    date_text = f"{decided:%B} {decided.day}, {decided.year}"

    return (
        f"{board}, Docket No. {docket} ({date_text}) "
        f"({outcome}; {before} → {after}), available at {url}."
    )


if __name__ == "__main__":
    # Try it: python -m app.citation
    print(format_citation(
        board="Army Discharge Review Board",
        docket="AR20230001234",
        decided=date(2024, 3, 5),
        outcome="Granted",
        before="General",
        after="Honorable",
        url="https://boards.law.af.mil/example",
    ))
