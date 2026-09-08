# Learning checklists

*What to actually learn from each feature, so shipping code and understanding it are the same act.*

This project exists to learn Python and Django. Code that works but taught nothing is a failed
feature. Every feature gets one file here.

## How to use them

1. When a feature or milestone chunk is done, run **`/learning-checklist`**. It reads what actually
   changed — including the mistakes — and writes or updates the file.
2. Work through **Hands-on** yourself, without Claude. That is the whole point.
3. Answer the **Quiz** from memory before opening the `<details>`. A question you cannot answer is
   a concept you have not learned yet, however green the tests are.
4. Tick your own boxes. Claude never ticks them for you.

## Index

| #  | Checklist                                                   | Milestone | Status      |
|----|-------------------------------------------------------------|-----------|-------------|
| 00 | [Foundation & infrastructure](00-milestone-0-foundation.md) | 0         | in progress |

New entries are appended here by `/learning-checklist`.

## Conventions

- Filename: `NN-<slug>.md`, two-digit prefix, in the order the work happened.
- Under 100 lines. A checklist nobody finishes teaches nothing.
- Specific to this repo. "Learn about forms" is useless; "why `clean_pseudo` strips before
  measuring length" is not.
- **Honest about gaps.** If Claude wrote something you did not follow, that belongs in the
  checklist, not hidden.

## See also

- Template: [TEMPLATE.md](TEMPLATE.md)
- The skill that generates these: `.claude/skills/learning-checklist/SKILL.md`
- Where this step sits in the loop: [../AI-WORKFLOW.md](../AI-WORKFLOW.md)
