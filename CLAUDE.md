# Project Brief: Discharge Upgrade Case Research Tool

> Paste this into Claude Code at the start of the project, or save it as `CLAUDE.md` in the root of the repository so Claude Code reads it automatically every session.

## 1. What we're building

A free, easy-to-use web app for searching past military discharge upgrade and Character of Discharge (COD) decisions across multiple government databases, in one place.

Today these decisions are scattered across several government sites, most with no real search. This tool collects them, makes them searchable and filterable, and presents every result as a clean, verifiable legal citation that links to the official source.

## 2. Who it's for

1. **Attorneys and advocates at a veterans legal services firm** (the first users). They are not technical. They need fast, precise research and citations they can drop into briefs and case memos.
2. **Later, possibly: the public, especially veterans applying for upgrades on their own.** They need plain-language explanations and must not mistake the tool for legal advice.

Build it once, using public data only, so the same app can serve both groups.

## 3. About the project owner (how to work with me)

- **I don't write code.** I'm an investigator and researcher (OSINT, public records, FOIA), not a developer. You write all the code. I set direction and check results.
- **Explain in plain English.** Tell me what you're doing and why, briefly, without jargon. When you need a decision from me, give me options with a recommendation.
- **Ask before anything that costs money** or creates accounts or services in my name.
- **Keep it simple and low-maintenance.** Prefer boring, well-supported tools over clever ones. I need to be able to keep this running long-term.
- **Commit in small, clearly described steps to GitHub,** so we can always go back to a working version.
- **Keep a `README.md` up to date** with plain-language instructions: how to run it locally, how to update the data, how to deploy it.

## 4. Data sources

Every source must be labeled separately in the app (its own name, filter option and citation format), even when several are hosted on the same site.

### A. Military review boards: DoD Boards Reading Room

- **Main site:** https://boards.law.af.mil/
- **Coverage:** decisions from October 1998 to present, updated quarterly (by Mar 31, Jun 30, Sep 30 and Dec 31).
- **Search:** none. Decisions are organized in folders by department, board and year, so we need to download them and build our own index.
- **Department index pages:**
  - Army: https://boards.law.af.mil/ARMYboards.htm (sub-pages: `ARMY_DRB.htm`, `ARMY_BCMR.htm`)
  - Navy / Marine Corps: https://boards.law.af.mil/NAVYboards.htm (includes `NAVY_BCNR.htm` and NDRB)
  - Air Force / Space Force: https://boards.law.af.mil/AFboards.htm
  - Coast Guard: https://boards.law.af.mil/CGboards.htm (includes `CG_BCMR.htm`)
  - OSD / DoD-wide: https://boards.law.af.mil/OSDboards.htm

| Branch | Board | What it decides |
|---|---|---|
| Army | Army Discharge Review Board (ADRB) | Discharge upgrades within 15 years of discharge |
| Army | Army Board for Correction of Military Records (ABCMR) | Upgrades after 15 years, and other record corrections |
| Navy / USMC | Naval Discharge Review Board (NDRB) | Discharge upgrades within 15 years |
| Navy / USMC | Board for Correction of Naval Records (BCNR) | Upgrades after 15 years, and record corrections |
| Air Force / Space Force | Air Force Discharge Review Board (AFDRB) | Discharge upgrades within 15 years |
| Air Force / Space Force | Air Force Board for Correction of Military Records (AFBCMR) | Upgrades after 15 years, and record corrections |
| Coast Guard | Coast Guard Discharge Review Board | Discharge upgrades within 15 years |
| Coast Guard | Coast Guard Board for Correction of Military Records | Upgrades after 15 years, and record corrections |
| DoD-wide | Discharge Appeal Review Board (DARB) | Final review after a service DRB denial (established 2024; see https://www.federalregister.gov/documents/2024/11/29/2024-27268/dod-discharge-appeal-review-board) |
| DoD-wide | Physical Disability Board of Review (PDBR) | Medical separation ratings (lower priority) |

**To verify:** whether the Navy (secnav.navy.mil, CORB/NDRB and BCNR pages) or other branches publish decisions anywhere beyond the Reading Room. Also check the file formats used (PDF, DOC, TXT, HTML); scanned documents may need OCR.

### B. VA Character of Discharge decisions: Board of Veterans' Appeals (BVA)

- **Search page:** https://www.index.va.gov/search/va/bva.html (keyword search plus year filter; no official API; decisions are de-identified, so name and SSN searches don't work; loaded monthly).
- **Individual decisions** are plain-text files, for example `https://www.va.gov/vetappYY/FilesN/<citation>.txt`.
- **Open data:** https://www.data.va.gov/dataset/Board-of-Veterans-Appeals-Decisions/3ydu-9hm5 and https://catalog.data.gov/dataset/board-of-veterans-appeals-decisions
- **Focus:** only decisions involving character of discharge, the statutory and regulatory bars to benefits, "insanity" exceptions, and similar. Don't index all BVA decisions.

### C. Federal courts

- **CourtListener API (free, needs a token):** https://www.courtlistener.com/help/api/
  - Court of Appeals for Veterans Claims (court id `cavc`)
  - Court of Federal Claims (`uscfc`), which hears challenges to BCMR decisions
  - Federal Circuit (`cafc`)
  - Federal district courts, for Administrative Procedure Act challenges to board decisions (later)
- **The CAVC's own search:** http://search.uscourts.cavc.gov/

## 5. What each record should contain

Pull out as many of these fields as possible. Fields extracted automatically (not from structured metadata) should be marked that way in the data.

- Source / board (e.g. "Army Discharge Review Board")
- Branch
- Docket or case number, exactly as it appears in the decision
- Decision date
- Outcome: Granted / Granted in part / Denied / Other
- Discharge characterization before and after (Honorable, General, OTH, BCD, DD, Uncharacterized)
- Narrative reason and separation code, if stated
- Issue tags: PTSD, TBI, other mental health condition, MST, liberal consideration (Hagel 2014 / Kurta 2017 / Wilkie 2018 memos), DADT / sexual orientation, misconduct type, in-service vs. post-service conduct, medical evidence, personal appearance hearing, counsel present, etc.
- Full text (for search)
- Official source URL (required, never blank)
- Date we collected it

## 6. How results and citations should look

The users are lawyers, so every result must read like a proper, verifiable citation.

Each result card shows:

- **Board name, docket number and decision date**, clearly at the top
- **Outcome badge** (Granted / Partial / Denied) and **before → after discharge type**
- **Issue tags**
- **A short text snippet** with the search terms highlighted
- **"View official decision" link** to the government's copy
- **"Copy citation" button**

Citation format, one line per decision, for example:
`[Board name], Docket No. [number] ([Month Day, Year]) ([outcome]; [before] → [after]), available at [official URL].`

Include an **export** of the current results (or selected results) as a citation list, in formats that work for Word (and CSV for spreadsheets).

Results must be **groupable and filterable by source**, so users always know which board a decision came from.

## 7. Search and filters

- Full-text keyword search, with support for exact phrases in quotes
- Filters:
  - Board / source
  - Branch
  - Decision year (range)
  - Outcome
  - Discharge type before and after
  - Issue tags
- Sort by relevance or by date
- Show result counts per source

## 8. Scope

### Prototype (build this first)

1. CourtListener: CAVC and Court of Federal Claims decisions that mention discharge upgrades or character of discharge.
2. Army Discharge Review Board: the last 3 years of decisions from the Reading Room.
3. The search page, result cards, citations and export described above.
4. It runs on my computer, with clear README instructions.

**Goal:** something I can show my firm to get feedback.

### Later phases

- All remaining boards in the Reading Room, going back to 1998
- BVA character-of-discharge decisions
- Automatic quarterly and monthly data updates (e.g. via a scheduled GitHub Action)
- Deploy to a low-cost public host
- Public-facing guide pages
- Optional firm-only features behind a login (saved searches, notes)

## 9. Technical preferences

Your call, but keep in mind:

- It must be **cheap to host** (ideally a few dollars a month or free) and **simple to maintain**.
- A single-file search database is fine (e.g. SQLite with full-text search) unless the data volume says otherwise.
- The collection scripts must be **re-runnable and incremental**: only fetch what's new, and resume if interrupted.
- Save the raw downloaded documents separately from the processed data, so we can re-process without re-downloading.
- Keep the site fast and accessible, with plain, professional design and readable type. It should work on phones.

## 10. Guardrails (non-negotiable)

**Scraping etiquette**

- Respect `robots.txt` and each site's terms.
- Rate-limit requests (e.g. one request every few seconds) and set a descriptive User-Agent with a contact email.
- Use APIs and bulk data where they exist, instead of scraping.

**Privacy**

- Use only public, already-redacted decisions. Never add client or firm data.
- Never try to re-identify anyone in a decision.
- Don't track or log what visitors search for, beyond basic error logs.
- These decisions involve MST, mental health and other sensitive subjects; treat them with care.

**Accuracy**

- Always link to the official decision.
- Label automatically extracted fields (outcome, discharge type, tags) as auto-extracted and possibly incorrect. The official decision governs.
- Show "last updated" dates for each source.

**Not legal advice**

- Include a clear disclaimer: this is a research tool, not legal advice, and results don't predict any individual outcome.
- Don't build outcome predictions or "your odds" features.
- Link to free legal help resources.
- Add plain-language explainers on: DRB vs. BCMR, the 15-year rule, what "granted in part" means, and liberal consideration.

**Independence**

- Build this project independently, using only public data and my own accounts and equipment.

## 11. First steps for Claude Code

1. Set up the GitHub repository and project structure, with a README.
2. Explore the Reading Room's Army DRB pages and a sample of decisions. Report back in plain English on how they're organized, their file formats, and any obstacles, before building the collector.
3. Get a CourtListener API token. Walk me through signing up, and store the token as a secret, never in the code.
4. Build the prototype (section 8), then show me how to run it and what to test.
