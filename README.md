# OS Exam Trainer — HIT 61206

A self-contained, offline-friendly web app for cramming the **Operating Systems** exam
(HIT 61206 — Weissman / Meir / Hagiz). Flashcards + micro-lessons + **verified practice
generators** for the computational question types, built from every modern past exam
(2014–2024, the 10-question / ≤5-word-answer format).

**Live:** _enable GitHub Pages on this repo (Settings → Pages → Deploy from branch → `main` / root)._

## Features
- **216 questions** from 22 exams, auto-sorted into **9 sections**, each answer in Hebrew + English.
- **A lesson per section** — exact terms (EN+HE), solving recipes, and a "traps" box.
- **Flashcards** with self-grading; missed cards resurface (spaced repetition via `localStorage`).
- **Practice Generators** for fork / scheduling / disk / paging — infinite fresh problems,
  answers computed by an engine validated against the official keys.
- **Review Weak**, **Test Mode** (take any past exam question-by-question — reveal each answer, then mark Got it / Missed, like the flashcards).
- Every card shows the **Hebrew question + the code (LTR) + an English hint** together; dark/light; mobile-first. No build step needed to *use* it.

## Focused mode (current-semester exam scope)
Chapters get dropped in a shortened semester. The **🎯 Focus** toggle (top bar) — or the URL
**`?focus=1`** — hides app content that's off the *current* exam while keeping the full course intact.

- Per the 2026 coordinator note (`docs/exam-scope-2026.jpeg`, Dr. Yair Weissman): chapters
  **7 (Deadlock), 11 (File-System Implementation), 12 (Disk Structure)** plus slides 6.25–6.27 and
  10.11→end were dropped.
- Verified against the actual course slide decks (os6–os12): the only app topic affected is
  **disk geometry** (ch 12). Focus hides those 5 questions + the disk-geometry generator; everything
  else stays on.
- Scope is data-driven in `src/data/scope.json` — edit it and run `python build.py` to change it.

Share the focused link with classmates: `https://<user>.github.io/os-exam-trainer/?focus=1`

## Project layout
```
index.html          app shell (loads css + js)
css/styles.css       styling (dark/light, RTL-aware)
js/
  engines.js         verified compute engines (fork sim, scheduler, disk, paging) — also a Node module
  app.js             UI, router, state + localStorage (spaced repetition)
  data.js            AUTO-GENERATED question/lesson data (window.DATA) — do not edit by hand
src/data/            SOURCE content (edit here)
  q_<EXAM>.json      one file per exam (10 questions each)
  lesson_<sec>.html  one micro-lesson per section
build.py             regenerates js/data.js from src/data/
tests/
  verify.py          engine validation vs known official answers
  gentest.js         generator fuzz test (6000 random problems)
```

## Develop
```bash
# regenerate js/data.js after editing src/data/
npm run build          # = python build.py

# run all verification (engine self-test + generator fuzz + python checks)
npm test               # = node js/engines.js && node tests/gentest.js && python tests/verify.py

# preview locally
npm run serve          # http://localhost:8080
```
Editing content: change a file in `src/data/`, run `npm run build`, commit `js/data.js`.

## Content & accuracy
- **2014–2023** questions and model answers are transcribed from the official past-exam PDFs
  (including the summer-2017 sitting, exam ids `2017SA`/`2017SB`, distinct from the winter `2017A`/`2017B`).
- **2024 A/B** (`q_2024A.json`, `q_2024B.json`) are **reconstructed from solution notes** and
  marked with `"source": "reconstructed-…"`; computational answers are engine-verified, and any
  uncertain item carries a `note`.
- A few answers carry a `note` because the **official course key is loose** (e.g. it labels a
  *Bounded Waiting* violation as "starvation", or computes "SJF" preemptively). The app shows the
  official answer **and** the precise correction so you write what the grader expects without
  learning it wrong.
- Every computational answer (fork counts, scheduling waiting-times, disk geometry, paging) is
  reproduced by `tests/` against the official keys.

Found a mistake? Fix `src/data/`, run `npm run build && npm test`, open a PR.

## License
MIT.
