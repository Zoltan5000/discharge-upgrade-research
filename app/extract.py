"""Read an Army DRB decision and pull out the facts we show in search results.

Everything here is AUTO-EXTRACTED: it is our best reading of the text and can be wrong.
The official decision always governs.
"""

import re
from datetime import datetime

from pypdf import PdfReader

# Issue tags: tag name -> words that signal it. \b means "whole word only",
# so "THC" does not match inside "UOTHC" (Under Other Than Honorable Conditions).
ISSUE_TAGS = {
    "Marijuana / THC": r"marijuana|marihuana|cannabis|\bTHC\b|tetrahydrocannabinol|\bdelta[- ]8\b",
    "Other drug use": r"cocaine|methamphetamine|\bamphetamine|opioid|opiate|heroin|oxycodone|fentanyl"
                      r"|\bLSD\b|ecstasy|\bMDMA\b|illegal drug|illicit drug|drug abuse|wrongful use",
    "Positive urinalysis": r"urinalysis|tested positive",
    "Alcohol": r"\balcohol|\bDUI\b|\bDWI\b|intoxicat|drunk",
    "PTSD": r"\bPTSD\b|post[- ]?traumatic stress",
    "TBI": r"\bTBI\b|traumatic brain injury",
    "Other mental health": r"depressi|\bMDD\b|anxiety|adjustment disorder|bipolar|personality disorder"
                           r"|panic disorder|schizo|mental health condition",
    "MST / sexual assault": r"\bMST\b|military sexual trauma|sexual assault|sexual harassment",
    "AWOL / desertion": r"\bAWOL\b|absent without leave|desert(ed|ion)",
    "DADT / sexual orientation": r"don.t ask|\bDADT\b|homosexual|sexual orientation",
    "COVID-19 vaccine": r"COVID",
}

CHARACTERIZATIONS = [
    # Order matters: check "Other Than Honorable" before plain "Honorable".
    ("OTH", r"other than honorable|\bUOTHC\b|\bOTH\b"),
    ("Dishonorable", r"dishonorable"),
    ("Bad Conduct", r"bad conduct|\bBCD\b"),
    ("Uncharacterized", r"uncharacterized|entry level"),
    ("General", r"general"),
    ("Honorable", r"honorable"),
]

DATE = r"(\d{1,2} [A-Z][a-z]+ \d{4})"


def pdf_to_text(path):
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def flatten(text):
    """Put the text on one line and fix split headings like 'R EQUEST' -> 'REQUEST'."""
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"\b([A-Z]) ([A-Z]{2,})", r"\1\2", text)


def case_facts(flat):
    """Remove the standard legal-reference sections that are the same in every decision.

    They mention PTSD, TBI, drugs, etc. in general terms, which would put the
    wrong tags on every case.
    """
    facts = re.sub(
        r"\d{1,2}\. (STATUTORY, REGULATORY AND POLICY REFERENCE|COVID-19 PROACTIVE POLICY GUIDANCE).*?"
        r"(?=\d{1,2}\. (SUMMARY OF FACT|BOARD DISCUSSION|DISCUSSION))",
        " ",
        flat,
    )
    # Some decisions end with an abbreviations list ("PTSD – Post-Traumatic Stress Disorder ...").
    # Cut it off at the first run of three or more such entries.
    glossary = re.search(r"(?:\b[A-Z][A-Z0-9/]{1,7}(?: \([A-Z]+\))? – [^–]{2,60}?\s){3,}", facts)
    return facts[: glossary.start()] if glossary else facts


def characterization(text):
    for name, pattern in CHARACTERIZATIONS:
        if re.search(pattern, text, re.IGNORECASE):
            return name
    return None


def find(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_decision(raw_text):
    flat = flatten(raw_text)
    facts = case_facts(flat)

    decided = find(r"(?:review|hearing) conducted on " + DATE, flat) or find(r"conducted on " + DATE, flat)
    try:
        decided = datetime.strptime(decided, "%d %B %Y").date() if decided else None
    except ValueError:
        decided = None

    before_text = find(r"Reason / Authority / Codes / Characterization:(.*?)(?= [b-z]\. [A-Z]| \(\d+\) [A-Z]|$)", flat) or ""
    before = characterization(before_text.split("/")[-1]) if before_text else None

    # The decision paragraph; if page 1 is a scanned image, fall back to the Board's discussion section.
    decision = find(r"Board Type and Decision:(.{0,900})", flat) or find(r"(voted (?:to|not to) .{0,600})", flat) or ""
    if re.search(r"deny relief|denied relief|voted to deny|voted not to (?:grant|upgrade|change the char)|proper and equitable", decision, re.IGNORECASE):
        outcome = "Denied"
    elif re.search(r"partial relief", decision, re.IGNORECASE):
        outcome = "Granted in part"
    elif re.search(r"grant relief|granted relief|voted to grant", decision, re.IGNORECASE):
        outcome = "Granted"
    else:
        outcome = "Other"

    after_text = find(r"Change Characterization to:(.{0,60})", flat) or find(
        r"upgrade (?:of|to) the characterization of service to (.{0,60})", decision
    )
    after = characterization(after_text) if after_text and not re.match(r"\s*(no|n/?a)\b", after_text, re.I) else None
    if outcome == "Denied" or after is None:
        after = before
    if outcome == "Granted" and after == before:
        outcome = "Granted in part"  # relief given (e.g. new narrative reason), but same characterization

    tags = [tag for tag, pattern in ISSUE_TAGS.items() if re.search(pattern, facts, re.IGNORECASE)]
    if re.search(r"proactive review", flat, re.IGNORECASE):
        tags.append("COVID-19 proactive review")
    if re.search(r"personal appearance hearing (was )?conducted|in a personal appearance hearing", decision, re.I):
        tags.append("Personal appearance hearing")
    counsel = find(r"Counsel:\s*(.{0,40}?)\s*\d\.", flat)
    if counsel and not re.match(r"(none|nif|n/?a)\b", counsel, re.IGNORECASE):
        tags.append("Counsel present")

    return {
        "decided": decided,
        "outcome": outcome,
        "before": before,
        "after": after,
        "narrative_reason": before_text.split("/")[0].strip() or None,
        "tags": tags,
        "text": facts,
    }
