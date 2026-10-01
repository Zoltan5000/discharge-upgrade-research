# Learning Python, one small piece at a time

Each lesson uses real code from this project. Open the file it mentions and look along.

## Lesson 1: A function is a recipe (`app/citation.py`)

```python
def format_citation(board, docket, decided, outcome, before, after, url):
```

- `def` means "here's a new recipe."
- `format_citation` is the recipe's name.
- The words in the brackets are the **ingredients** you hand it.
- `return` is the finished dish it hands back to you.

**The f-string trick:** a string with an `f` in front can hold blanks in `{curly brackets}`, and Python fills them in:

```python
name = "Army Discharge Review Board"
print(f"Hello from the {name}")   # Hello from the Army Discharge Review Board
```

**Try it:** run `python -m app.citation`. Then open the file, change `"Granted"` to `"Denied"` near the bottom, and run it again.

## Lesson 2: `if` is a gatekeeper (`app/citation.py`)

```python
if not url:
    raise ValueError("A citation needs the official source URL.")
```

- `if` asks a yes/no question. If the answer is yes, Python runs the indented lines underneath.
- `not url` means "is the link missing?" An empty `""` counts as missing.
- `raise` stops everything and shows an error message. It's like a guard saying "you can't come in without a ticket."

**Indentation matters:** the 4 spaces before `raise` are how Python knows that line belongs to the `if`.

**Try it:** run `pytest`. One of the tests checks that this gatekeeper really says no.

## Lesson 3: A list is a shopping list

```python
allowed = ["boards.law.af.mil", "www.courtlistener.com", "www.va.gov"]
```

- Square brackets `[ ]` hold the whole list; each item has its own quotes.
- Commas go **between** the quoted items, never inside them.
- `["a.com,b.com"]` is ONE odd item, not two. (That is why the network settings box rejected it.)

## Lesson 4: A loop does the same chore many times

To check how many decisions each year has, Claude did this (in the terminal's language, but Python's idea is the same):

```python
for year in [2023, 2024, 2025, 2026]:
    print("Checking", year)
```

- `for year in [...]` means "take each item from the list, one at a time, and call it `year`."
- The indented lines run once for **each** item, so this prints 4 lines.
- Our downloader will do this for ~1,000 PDFs, with a pause between each one so we stay polite to the website.

## Lesson 5: A dictionary is a labeled box (`app/extract.py`)

```python
ISSUE_TAGS = {
    "Marijuana / THC": r"marijuana|cannabis|\bTHC\b",
    "Alcohol": r"\balcohol|\bDUI\b",
}
```

- Curly brackets `{ }` make a **dictionary**: each item has a **label** (left of the colon) and a **value** (right).
- Like a real dictionary: look up a word, get its meaning. `ISSUE_TAGS["Alcohol"]` gives back the alcohol search words.
- The `|` inside the search words means "or": marijuana **or** cannabis **or** THC.
- `\b` means "word edge." It stops `THC` from matching inside `UOTHC` (Under Other Than Honorable Conditions).
  A real bug we caught!

**Try it:** add `"pot"` to the marijuana line? Careful: `\bpot\b` would also match "pot" in cooking... words are tricky, which is why every tag says "auto-extracted."

## Lesson 6: Tests are robot checkers (`tests/test_extract.py`)

```python
def test_grant_is_not_mistaken_for_denial():
    record = parse_decision(GRANT)
    assert record["outcome"] == "Granted"
```

- A **test** is a tiny recipe that checks another recipe still works.
- `assert` means "this MUST be true." If it isn't, the test fails loudly.
- We found a real bug: some granted cases were labeled "Denied" because the words "proper and equitable"
  appeared nearby (about the reentry code). After fixing it, we wrote this test so the bug can never sneak back.
- A test even caught Claude's own mistake today: the sample text said "arrested," which correctly
  earns the arrest tag. The test was wrong, not the code. Tests keep everyone honest!

**Try it:** run `pytest`. Eight green dots means eight checks passed.
