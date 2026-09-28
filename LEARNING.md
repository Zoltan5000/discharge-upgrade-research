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
