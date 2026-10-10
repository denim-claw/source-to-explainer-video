# Repository → architecture review

English | [한국어](README.ko.md)

A seven-scene review of YC Software's [QM](https://github.com/yc-software/qm) at commit
`daeb2deb`. It covers the shape of the whole system, not one PR. The video follows one
request through the system, one behaviour per scene, drawn as paths rather than read line
by line.

![A silent worker's run travels back to the queue while the reaper replaces the lease token](preview/en.gif)

| | English | Korean |
|---|---|---|
| Video | [en.mp4](preview/en.mp4) · 3:54 · 5.4 MB | [ko.mp4](preview/ko.mp4) · 3:56 · 5.2 MB |
| Captions | [en.srt](preview/en.srt) · 45 cues | [ko.srt](preview/ko.srt) · 45 cues |
| Still | [en.png](preview/en.png) | [ko.png](preview/ko.png) |

This is an unofficial explanation, not documentation from the QM maintainers. QM is MIT-licensed.

## Pinned source

`plan.py` records the repository, the commit and the Git blob hash of each of the seven
cited files. `pipeline.py` fetches those files at that commit, recomputes the blob hashes
and stops on any mismatch.

| File | Scenes |
|---|---|
| `README.md` lines 89–92 | 1, 6 |
| `docs/SPEC.md` lines 15–21 | 1, 5, 6 |
| `docs/session-tape-spec.md` lines 5–60 | 4, 5 |
| `src/runs/postgres-run-store.ts` lines 218–271, 340–345, 527–563 | 2, 3 |
| `src/runs/worker.ts` line 34 | 2 |
| `src/runs/run-store.ts`, `src/runs/reaper.ts` | 2, 3 |

## Scenes

| Scene | Claim | Visual change |
|---|---|---|
| 1 | every turn passes the core and the run queue; state lives in Postgres | boxes draw one by one from Slack to the model |
| 2 | workers claim the oldest run per session without blocking and take a lease | run 1 leaves the queue and the worker starts running |
| 3 | the reaper fences with a new token, then requeues or fails the run | the worker goes silent and run 1 returns to the queue |
| 4 | the model reads only what the tape holds, with stated exceptions | records append and the box becomes a fold |
| 5 | one tool catalog, swappable harnesses, and the switch is recorded | the harness changes from Pi to Codex |
| 6 | scopes are isolated; crossing needs an explicit grant | the wall between two scopes lowers |
| 7 | tests actually run and what was not verified | four check cells light up, coloured by status |

Security postures (Strict, Auto, Dangerous), credentials and background work are left for
another episode.

## Tests actually run

At the same commit (Node v24.20.0, macOS arm64):

```bash
npm ci --ignore-scripts && npm run build:connector-sdk
node --experimental-test-module-mocks --test test/run-store.test.ts test/run-stale.test.ts \
  test/lease-keepalive.test.ts test/scope-reach.test.ts test/worker-reaper.test.ts \
  test/tape-fold.test.ts test/session-tape.test.ts test/sandbox-resources.test.ts
```

166 of 170 passed. All 4 failures are in `scope-reach.test.ts`, where the connector SDK
install in the local exec sandbox fails (`rc=64`), so that behaviour stays unverified. The
tests used in-memory stores; the Postgres SQL paths were read, not executed.

## Build

```bash
export GEMINI_API_KEY=...                       # only for scenes without cached speech
export WHISPER_MODEL=/path/to/ggml-small.bin    # optional ASR comparison
.venv/bin/python example-architecture/pipeline.py
```

The layout matches the [book-section example](../example-concept/README.md): scenes live
in `plan.py`, and `pipeline.py` verifies the source and runs the shared pipeline per language.

## What was checked

| Check | Result |
|---|---|
| Format | 1280×720, 30 fps, H.264 + mono 48 kHz AAC; 7,028 (en) and 7,093 (ko) frames counted |
| Full decode | no errors |
| Cuts | 24 cut frames extracted from the encoded master |
| Layout | 89 samples per language, no overlaps |
| Audio | peak 0.829 (en) and 0.739 (ko), no clipped samples |
| Package replay | the 60-file archive renders a 2-second MP4 from a clean folder and matches RGB hashes |
| ASR comparison | per-scene similarity 0.965–1.0 (en), 0.825–0.931 (ko) |

The lower Korean scores (scenes 2, 5, 6) come from English identifiers such as `pending`,
`harness` and `grant`, which the ASR model writes out in Hangul. Those scenes are flagged
for a human listen.

Speech: Gemini `gemini-3.8-flash-lite-tts`, voice `Kore`.

## Not checked

- No one listened to the full videos end to end.
- Caption timing is an estimate, not forced alignment.
- No independent review by the QM maintainers or anyone else.
- No cloud deployment, production Postgres or "millions of agents" scale was tested.
- Run numbers, the wall between scopes and the run's motion back to the queue are metaphors.
