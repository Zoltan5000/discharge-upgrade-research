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
