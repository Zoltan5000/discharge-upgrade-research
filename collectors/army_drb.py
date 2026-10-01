"""Download Army Discharge Review Board decisions from the DoD Boards Reading Room.

Run it:  python -m collectors.army_drb            (default: 2024 to this year)
         python -m collectors.army_drb 2023 2024  (only those years)

It is safe to stop and re-run: files already downloaded are skipped.
"""

import re
import sys
import time
from datetime import date
from pathlib import Path

import requests

SITE = "https://boards.law.af.mil/"
RAW_DIR = Path("data/raw/army_drb")
PAUSE_SECONDS = 3  # be polite: one request every few seconds
HEADERS = {
    "User-Agent": "DischargeUpgradeResearchTool/0.1 "
    "(public-records research; contact: oboe.zoltan@gmail.com)"
}

# Matches links like ARMY/DRB/CY2024/AR20240000003-Redacted.pdf
PDF_LINK = re.compile(r'href="(ARMY/DRB/CY\d{4}/[^"]+\.pdf)"', re.IGNORECASE)


def list_decisions(session, year):
    """Return the PDF links on one year's listing page (no duplicates)."""
    page = session.get(f"{SITE}ARMY_DRB_CY{year}.htm", timeout=60)
    page.raise_for_status()
    links = PDF_LINK.findall(page.text)
    return list(dict.fromkeys(links))  # removes repeats, keeps order


def download_year(session, year):
    folder = RAW_DIR / f"CY{year}"
    folder.mkdir(parents=True, exist_ok=True)

    links = list_decisions(session, year)
    new = [link for link in links if not (folder / Path(link).name).exists()]
    print(f"CY{year}: {len(links)} decisions listed, {len(new)} new to download")

    for count, link in enumerate(new, start=1):
        time.sleep(PAUSE_SECONDS)
        target = folder / Path(link).name
        try:
            response = session.get(SITE + link, timeout=120)
            response.raise_for_status()
        except requests.RequestException as error:
            print(f"  skipped {target.name} ({error}); it will be retried next run")
            continue
        # Write to a temp name first, so a stopped run never leaves half a file behind.
        partial = target.with_suffix(".part")
        partial.write_bytes(response.content)
        partial.rename(target)
        if count % 25 == 0 or count == len(new):
            print(f"  {count}/{len(new)} downloaded")


def main(years):
    with requests.Session() as session:
        session.headers.update(HEADERS)
        for year in years:
            download_year(session, year)
            time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    chosen = [int(arg) for arg in sys.argv[1:]] or list(range(2024, date.today().year + 1))
    main(chosen)
