# Book memory: make each chapter better than the last

A multi-chapter source (a book, a course, a long report) gets one shared folder next to its
chapter folders. Each chapter reads it before planning and adds to it after delivery. Without
it, every chapter starts cold and repeats the same review findings.

```
books/<book>/
  shared/                 # book memory, hand-maintained, small
    book.json             # identity + production settings for the whole book
    glossary.json         # author terms, meaning, page, how this video says them, avoid list
    lessons.md            # findings that repeated, layout fixes, mode notes, costs
    verbatim-allow.txt    # short attributed key phrases allowed book-wide
    (figures)             # book-only figures (a metaphor only this book uses)
  <ch>-full/ <ch>-recap/  # chapter-mode folders (engine copy + design + outputs)
  meta.json               # GENERATED status: chapters, modes, durations, hashes, QA, cost, publish
```

## What goes where

| File | Holds | Never holds |
|---|---|---|
| `book.json` | title, author, edition, source hash, header prefix, printed ↔ PDF page offset, TOC location, chapter naming, TTS provider/voice/mode | keys, account details |
| `glossary.json` | `term`, `page`, `origin` (author / cited person), short `meaning`, `say` (how the video phrases it), `avoid` (phrases that drift or overstate), `why` | source sentences |
| `lessons.md` | review findings that recurred (attribution, dropped hedges, unsourced examples), QA/layout fixes, what the user said about a mode, cost per character | full findings dumps, source text |
| `verbatim-allow.txt` | short key phrases the video quotes on purpose, with attribution in the scene | anything long enough to count as reading the source |
| `meta.json` | generated from each folder's verification files; never hand-edited | anything not backed by a file on disk |

## Lifecycle

1. **First chapter:** produce it normally. After delivery, create `shared/` from what the
   chapter taught: confirmed page offset, terms, repeated findings, allow-list.
2. **New chapter:** the chapter scaffold applies `book.json` (header, bibliographic fields,
   page-map hint) and appends the book allow-list. Read `glossary.json` and `lessons.md`
   **before** writing the scene table, and pass both to the fidelity reviewers as context.
3. **Planning check:** the plan step flags any `avoid` phrase found in narration or
   on-screen text. Treat it as a warning to resolve, not an automatic rewrite.
4. **After delivery:** add new terms and only the lessons that are likely to recur; mark
   lessons that turned out wrong instead of silently deleting them. Regenerate `meta.json`.
5. **Promotion:** a figure used in two or more chapters of one book stays in that book's
   memory; one used across two or more books moves to the shared engine (and its gallery).

## Rules

- Book memory is private working material like the chapter folders. Keep it out of public
  skill packages; it may name the book and author but never contains source text.
- The glossary records how *this video* says a term so meaning stays fixed across chapters.
  One word, one meaning: if a term is reused with a different sense, add it to `avoid`.
- Lessons are claims about the process. Write them so the next reviewer can check them
  ("dropped hedge on probability claims", not "be careful").
- `meta.json` is the input for any library/index page. Build the page from it instead of
  copying numbers by hand.
