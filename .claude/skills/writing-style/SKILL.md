---
name: writing-style
description: Sentence-level writing rules for pykaraoke. Structure every explanation as why, then how, then what. Never use the em dash. Keep code comments rare and short. Use when writing documentation prose, PR descriptions, commit bodies, docstrings, chat replies, or code comments.
---

# Writing style (pykaraoke)

Three rules. No exceptions.

## 1. Why, how, what, in that order

Every explanation answers three questions, in this order:

1. **Why** the reason this exists or matters.
2. **How** the mechanism, briefly.
3. **What** the concrete result.

Fold them into one or two plain sentences. Do not label them in the actual text.

Wrong: "This function reserves a seat."
Right: "Sign-ups can arrive after the event is full, so `reserve_seat` checks `seats_left` before
writing. A full event gets a waiting-list row instead of a confirmed one."

## 2. Never use "—"

No em dash. Anywhere: docs, comments, commit messages, chat replies. Use a period, a colon, or
parentheses.

Wrong: "Multi-stage build — build tools never reach the runtime image."
Right: "Multi-stage build. Build tools never reach the runtime image."

## 3. Code comments: rare and short

Comment only when the *why* is not obvious from the code. One line. Never a block. Never restate
what the code already says.

```python
# Django forces locmem in tests, so this check can never pass there.
if "test" not in sys.argv:
    ...
```

No comment needed here, the name already says it:

```python
def is_open(self) -> bool:
    return self.seats_left > 0
```

## See also

- Doc structure and mermaid rules: skill `docs-writing`
- Docstring and comment conventions: skill `python-standards`
