"""Read an Army DRB decision and pull out the facts we show in search results.

Everything here is AUTO-EXTRACTED: it is our best reading of the text and can be wrong.
The official decision always governs.
"""

import re
from datetime import datetime

from pypdf import PdfReader

# Issue tags, in groups: tag name -> words that signal it (matched against the case facts only).
# \b means "whole word only", so "THC" does not match inside "UOTHC"
# (Under Other Than Honorable Conditions). (?<!sexual ) means "not right after 'sexual '".
TAG_GROUPS = {
    "Conditions and experiences": {
        "PTSD": r"\bPTSD\b|post[- ]?traumatic stress",
        "TBI": r"\bTBI\b|traumatic brain injury|concussion|blast (exposure|injury|wave)|\bIED\b",
        "Depression / anxiety / other mental health": r"depressi|\bMDD\b|anxiety|\bGAD\b|adjustment disorder"
            r"|bipolar|personality disorder|panic disorder|schizo|mood disorder|mental health condition",
        "MST / sexual assault": r"\bMST\b|military sexual trauma|sexual assault|sexual harassment|\braped?\b",
        "Personal assault (victim)": r"(was|were|been) (physically )?(assaulted|attacked|beaten)|victim of (an )?assault",
        "Domestic violence / IPV": r"intimate partner violence|\bIPV\b|spousal abuse|domestic (abuse|violence)",
        "Physical injury / chronic pain": r"chronic pain|physical (injury|injuries)|(back|knee|neck|shoulder) "
            r"(injury|pain)|surgery",
        "Self-medication": r"self[- ]?medicat",
        "Medication side effects": r"side[- ]effects?|adverse (reaction|effect)|prescribed medication|medication (caused|induced|made)|due to (the |their |his |her )?medication",
        "DADT / sexual orientation": r"don.t ask|\bDADT\b|homosexual|sexual orientation",
    },
    "Misconduct": {
        "Marijuana / THC": r"marijuana|marihuana|cannabis|\bTHC\b|tetrahydrocannabinol|\bdelta[- ]8\b",
        "Other drug use": r"cocaine|methamphetamine|\bamphetamine|opioid|opiate|heroin|oxycodone|fentanyl"
            r"|\bLSD\b|ecstasy|\bMDMA\b|illegal drug|illicit drug|drug abuse|wrongful use",
        "Positive urinalysis": r"urinalysis|tested positive",
        "DUI / DWI": r"\bDUI\b|\bDWI\b|driving under the influence|driving while (intoxicated|impaired)"
            r"|drunk driving|drunken driving",
        "Alcohol": r"\balcohol|intoxicat|drunk",
        "Larceny / theft": r"larceny|\btheft|\bstole|stealing|shoplift|wrongful appropriation|burglary|robbery",
        "Assault": r"(?<!sexual )\bassault|\bbattery\b|\bstruck\b|\bpunch|strangl|\bchok(ed|ing)\b",
        "AWOL / desertion": r"\bAWOL\b|absent without leave|desert(ed|ion)|unauthorized absence",
        "Failure to report": r"failure to report|failed to report|\bFTR\b|failure to repair",
        "Disobeying orders / disrespect": r"fail(ure|ed) to obey|disobey|disrespect|insubordinat",
        "False statement / fraud": r"false official statement|\bfraud|\bforg(ed|ery)\b|false statement",
        "Weapons": r"firearm|weapon|pistol|handgun|\brifle\b",
        "Civilian arrest / conviction": r"civil(ian)? conviction|civil(ian)? authorities|arrested|convicted",
        "Court-martial / in lieu of": r"court[- ]martial|chapter 10\b",
        "COVID-19 vaccine": r"COVID",
    },
    "Mitigating factors": {
        "Combat / deployment": r"\bcombat (service|deployment|tour|veteran)|deploy(ed|ment)|\bOIF\b|\bOEF\b"
            r"|Iraq|Afghanistan|Operation (Enduring|Iraqi) Freedom",
        "Length / quality of service": r"length and quality|length of service|quality of service"
            r"|in-service (mitigating )?factors?",
        "Prior honorable service": r"prior (period of )?honorable|previous honorable",
        "Prior good conduct / awards": r"good conduct medal|\bAGCM\b|\bARCOM\b|commendation medal|exemplary"
            r"|outstanding (service|performance)",
        "Post-service conduct / accomplishments": r"post[- ]?service (accomplishment|conduct|achievement|factor)"
            r"|since (their|his|her) discharge",
        "Character letters / references": r"character (reference|letter|statement)|letters? of (support|recommendation"
            r"|reference)|support letter|buddy statement",
        "Family / personal hardship": r"hardship|family (issue|problem|emergenc|matter|obligation)|pregnan|divorce"
            r"|death of|(ailing|sick|ill|terminally ill|dying) (spouse|wife|husband|child|son|daughter|parent|mother"
            r"|father|grandmother|grandfather)|care (for|of) (a |their |his |her )?(sick|ill|ailing)",
        "Duress / coercion": r"duress|coerc|threaten(ed)? by|pressured by",
        "VA service connection": r"service[- ]?connect",
        "Discrimination / hazing": r"discriminat|racis[mt]|hazing|bullying",
        "Youth / immaturity": r"immatur|youthful",
    },
}

# Labels of the standard form fields; removed before tagging so a label like
# "Overseas Service / Combat Service: None" doesn't count as combat service.
FORM_LABELS = r"Overseas Service / Combat Service:|Combat Service:|POST[- ]?SERVICE ACCOMPLISHMENTS:"

NOTHING = r"\s*(none|nif|n/?a|not applicable)\b"

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


def all_tags():
    """Every tag name, in display order (used by the website's filter list)."""
    names = [tag for group in TAG_GROUPS.values() for tag in group]
    return names + [tag for tags in EXTRA_TAG_GROUPS.values() for tag in tags]


EXTRA_TAG_GROUPS = {
    "Liberal consideration (Kurta)": [
        "Board found mitigating condition",
        "Condition outweighed discharge",
        "Condition did not outweigh discharge",
    ],
    "Board's reasoning": ["Found inequitable", "Found improper"],
    "Procedure": ["Personal appearance hearing", "Counsel present", "COVID-19 proactive review"],
}


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
    # Standard sentences quoting Army Regulation 635-200 that list every kind of misconduct.
    facts = re.sub(r"[^.]*(Specific categories include|establishes policy and prescribes procedures"
                   r"|Action will be taken to separate)[^.]*\.", " ", facts)
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


def read_outcome(decision):
    """Granted / Denied / Other, from the Board's decision paragraph. Grant is checked first,
    because grants often add 'the reentry code was proper and equitable'."""
    if re.search(r"partial relief", decision, re.IGNORECASE):
        return "Granted in part"
    if re.search(r"(voted to|board) grant(ed)? (the )?(relief|request)|grant relief|granted relief|voted to upgrade"
                 r"|directed the issue of a new DD", decision, re.IGNORECASE):
        return "Granted"
    if re.search(r"den(y|ied) (the )?(relief|request)|voted to deny|voted not to (grant|upgrade|change the char)"
                 r"|proper and equitable", decision, re.IGNORECASE):
        return "Denied"
    return "Other"


def read_tags(flat, facts, decision):
    # Blank out form labels (and an empty "None" answer after them) before matching.
    facts = re.sub(f"(?:{FORM_LABELS})(?:{NOTHING})?", " ", facts, flags=re.IGNORECASE)
    tags = [tag for group in TAG_GROUPS.values() for tag, pattern in group.items()
            if re.search(pattern, facts, re.IGNORECASE)]

    # Section 6 states post-service accomplishments directly ("None submitted..." if there are none).
    post = find(r"POST[- ]?SERVICE ACCOMPLISHMENTS:(.{0,40})", flat)
    if post and not re.match(r"\s*(none|nif|n/?a)", post, re.IGNORECASE):
        if "Post-service conduct / accomplishments" not in tags:
            tags.append("Post-service conduct / accomplishments")

    # The four Kurta (liberal consideration) questions are answered Yes / No / N/A.
    if find(r"condition or experience that (?:may )?excuse or mitigate the discharge\?\s*(\w+)", flat) == "Yes":
        tags.append("Board found mitigating condition")
    outweigh = find(r"outweigh the discharge\?\s*(\w+)", flat)
    if outweigh == "Yes":
        tags.append("Condition outweighed discharge")
    elif outweigh == "No":
        tags.append("Condition did not outweigh discharge")

    if re.search(r"\binequitable\b", decision, re.IGNORECASE):
        tags.append("Found inequitable")
    if re.search(r"(?<!not )\bimproper\b", decision, re.IGNORECASE):
        tags.append("Found improper")
    if re.search(r"personal appearance (hearing )?(was )?conducted|in a personal appearance", decision, re.I):
        tags.append("Personal appearance hearing")
    counsel = find(r"Counsel:\s*(.{0,40}?)\s*\d\.", flat)
    if counsel and not re.match(r"(none|nif|n/?a)\b", counsel, re.IGNORECASE):
        tags.append("Counsel present")
    if re.search(r"proactive review", flat, re.IGNORECASE):
        tags.append("COVID-19 proactive review")
    return tags


def parse_decision(raw_text):
    flat = flatten(raw_text)
    facts = case_facts(flat)

    decided = find(r"(?:review|hearing|appearance) conducted on " + DATE, flat) or find(r"conducted on " + DATE, flat)
    try:
        decided = datetime.strptime(decided, "%d %B %Y").date() if decided else None
    except ValueError:
        decided = None

    before_text = find(r"Reason / Authority / Codes / Characterization:(.*?)(?= [b-z]\. [A-Z]| \(\d+\) [A-Z]|$)", flat) or ""
    before = characterization(before_text.split("/")[-1]) if before_text else None

    # The decision paragraph (up to Section 3); if page 1 is a scanned image,
    # fall back to the Board's discussion section.
    decision = (find(r"Board Type and Decision:(.{0,900}?)(?:3\. DISCHARGE|Please see|$)", flat)
                or find(r"((?:voted|board) (?:to|not to|grant|den).{0,600})", facts) or "")
    outcome = read_outcome(decision)

    after_text = find(r"Change Characterization to:(.{0,60})", flat) or find(
        r"upgrade (?:of|to) the characterization of service to (.{0,60})", decision
    )
    after = characterization(after_text) if after_text and not re.match(NOTHING, after_text, re.I) else None
    if outcome == "Denied" or after is None:
        after = before
    if outcome == "Granted" and after == before:
        outcome = "Granted in part"  # relief given (e.g. new narrative reason or RE code), same characterization

    return {
        "decided": decided,
        "outcome": outcome,
        "before": before,
        "after": after,
        "narrative_reason": before_text.split("/")[0].strip() or None,
        "tags": read_tags(flat, facts, decision),
        "summary": decision[:700] or None,
        "text": facts,
    }
