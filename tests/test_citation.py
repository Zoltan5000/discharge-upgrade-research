from datetime import date

import pytest

from app.citation import format_citation


def test_citation_matches_house_format():
    text = format_citation(
        board="Army Discharge Review Board",
        docket="AR20230001234",
        decided=date(2024, 3, 5),
        outcome="Granted",
        before="General",
        after="Honorable",
        url="https://boards.law.af.mil/example",
    )
    assert text == (
        "Army Discharge Review Board, Docket No. AR20230001234 (March 5, 2024) "
        "(Granted; General → Honorable), available at https://boards.law.af.mil/example."
    )


def test_citation_refuses_missing_url():
    with pytest.raises(ValueError):
        format_citation("Board", "1", date(2024, 1, 1), "Denied", "OTH", "OTH", url="")
