from datetime import date

from app.extract import parse_decision

# A cut-down decision in the same shape as a real Army DRB PDF.
SAMPLE = """
ARMY DISCHARGE REVIEW BOARD CASE REPORT AND DIRECTIVE AR20240000999 1
1. Applicant's Name:
c. Counsel: None
2. R EQUEST, ISSUES, BOARD TYPE, AND DECISION:
b. Board Type and Decision: In a records review conducted on 12 August 2024, and by a 5-0 vote,
the Board voted to deny relief.
3. D ISCHARGE DETAILS:
a. Reason / Authority / Codes / Characterization: Misconduct (Drug Abuse) / AR 635-200 / JKK / RE-4 /
Under Other Than Honorable Conditions
b. Date of Discharge: 4 December 2012
h. The applicant tested positive for THC on a urinalysis.
7. S TATUTORY, REGULATORY AND POLICY REFERENCE(S):
a. Boards consider claims of PTSD, TBI, and military sexual trauma.
8. S UMMARY OF FACT(S):
a. The applicant was discharged UOTHC.
PTSD – Post-Traumatic Stress Disorder TBI – Traumatic Brain Injury UOTHC – Under Other Than Honorable Conditions
"""


def test_reads_the_key_facts():
    record = parse_decision(SAMPLE)
    assert record["decided"] == date(2024, 8, 12)
    assert record["outcome"] == "Denied"
    assert record["before"] == "OTH"
    assert record["after"] == "OTH"
    assert record["narrative_reason"] == "Misconduct (Drug Abuse)"


def test_tags_come_from_case_facts_only():
    tags = parse_decision(SAMPLE)["tags"]
    assert "Marijuana / THC" in tags
    assert "Positive urinalysis" in tags
    # PTSD/TBI/MST appear only in the standard legal text and the abbreviations list.
    assert "PTSD" not in tags
    assert "TBI" not in tags
    assert "MST / sexual assault" not in tags


def test_uothc_is_not_thc():
    text = SAMPLE.replace("tested positive for THC on a urinalysis", "was late to formation")
    assert "Marijuana / THC" not in parse_decision(text)["tags"]
