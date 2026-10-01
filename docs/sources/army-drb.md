# Source notes: Army Discharge Review Board (ADRB)

Checked: October 1, 2026.

## How the site is organized

- Index page: https://boards.law.af.mil/ARMY_DRB.htm links to one page per calendar year, CY1996 to CY2026.
- Year page: e.g. `ARMY_DRB_CY2024.htm`, a table listing each decision's file name, a date and the file size.
  The date seems to be when the file was posted, **not** the decision date.
- Decision file: `ARMY/DRB/CY2024/AR20240000003-Redacted.pdf`. The file name is the docket number.
- `robots.txt`: none (404), so no crawl rules are published. We still go slowly (one request every few seconds).

## Decisions per year (count of PDFs on each year page)

| Year | Decisions |
|---|---|
| 2023 | 371 |
| 2024 | 308 |
| 2025 | 123 |
| 2026 (so far) | 628 |

The prototype range of about 3 years is roughly 1,000 to 1,400 PDFs, around 170 KB each.
At one download every 3 seconds, a first full run takes about an hour. Later runs only fetch new files.

## File format

- PDF with real, selectable text, not scans, so no OCR is needed for the samples checked.
- Same heading on every page: "ARMY DISCHARGE REVIEW BOARD CASE REPORT AND DIRECTIVE" plus the docket number.
- Names are blanked out (redacted).

## Where the fields we want live in the text

| Field | Where it appears |
|---|---|
| Docket number | Top of every page, e.g. `AR20240000003` |
| Decision date | "In a records review conducted on **17 April 2024**" (or a personal-appearance hearing) |
| Outcome | Same paragraph: "voted to grant relief" or deny; also the vote, e.g. "5-0" |
| Discharge before | Section 3a, "Reason / Authority / Codes / Characterization", last item |
| Discharge after | "upgrade of the characterization of service to **Honorable**" |
| Narrative reason, separation code | Section 3a (before) and the decision paragraph (after) |
| Counsel | Section 1c, "Counsel: None" |

## Obstacles and quirks

1. **Two templates.** Many 2026 decisions are COVID-19 vaccine "Proactive Review Board" cases. The government
   started these itself, under a December 10, 2025 memo, and their layout differs from regular applications.
   The reader must handle both, and we should tag these so they don't swamp other results.
2. **Text glitches.** Extraction sometimes splits words ("R EQUEST", "D ISCHARGE"), so matching needs to be forgiving.
3. **Posted date ≠ decision date.** Take the decision date from the decision text, not the listing.
4. Auto-extracted fields must be labeled as such (per CLAUDE.md); the PDF governs.
