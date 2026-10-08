# Using this pipeline for code review / PR explanation

Same pipeline, different "source verification". The goal is a narrated explanation of a
change so it can be *heard* while walking, not a summary of the diff text.

## 1. The source is the change, not the description

Collect, in this order:

1. The diff itself (`git diff <base>..<head>`, or the PR patch).
2. The files the diff touches, at least the functions whose behaviour changed.
3. Test evidence actually executed for that revision (which tests, which command, output).
4. The stated intent: issue text, PR description, commit messages.
5. What is **not** covered: unrun tests, unverified claims, TODO paths.

Record the revision hashes. A video explaining "the fix" is worthless if it cannot say
which commit it describes.

## 2. Scene shape for code sources

- Scene 1: what the change claims to make possible, in one sentence, no code.
- Scene 2–3: the current behaviour path, as boxes and connectors — the shape of the
  problem, with the failing or missing link marked.
- Scene 4–6: the change — show the connector opening, the state being replaced, or a
  bounded region being moved. One structural change per scene.
- Scene 7: what could now regress, drawn as a second path that must keep working.
- Scene 8: what the tests actually prove versus what remains unverified.
- Last: what to check before merging.

## 3. Rules that matter more than usual here

- **Do not narrate the diff line by line.** Explain the behavioural delta; the diff is a
  reference the viewer can open afterwards.
- Keep identifiers, file paths and API names verbatim. Do not translate symbol names, and
  do not "tidy" a path.
- Never describe a test as passing unless you ran it for that revision, and never claim a
  fix works because the diff looks right.
- Distinguish "this code now does X" (verifiable in the source) from "this will fix the
  user-visible problem" (a hypothesis until measured).
- If the review is of *someone else's* unreleased work, do not publish the video or the
  diff outside the authorised audience — generating the explanation is not a licence to
  redistribute the code.
- Redact secrets, customer data and internal hostnames from both narration and diagrams.
  A hosted diagram or an uploaded video can leak what the diff contained.

## 4. Why video can beat an interactive page here

An interactive page requires attention at a desk. A narrated explanation can be heard
while commuting, so a reviewer arrives already holding the shape of the change: which
path moved, which invariant the change protects, and what is still unverified. Keep the
narration under ~8 minutes for a single change, and keep the diagram vocabulary identical
across episodes so the series becomes scannable.

## 5. Minimum QA for code-sourced episodes

- Every symbol, path and number in the narration exists in the recorded revision.
- Every condition stated in narration appears in the diagram, and vice versa.
- The "not verified" scene is present whenever anything was not run.
- No fabricated line numbers or coverage percentages.
