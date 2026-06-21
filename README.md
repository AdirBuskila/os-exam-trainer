# OS Exam Trainer — HIT 61206

A self-contained, offline-friendly web app for cramming the **Operating Systems** exam
(HIT 61206 — Weissman / Meir / Hagiz). Flashcards + micro-lessons + **verified practice
generators** for the computational question types, built from every modern past exam
(2017–2024, the 10-question / ≤5-word-answer format).

**Live:** _enable GitHub Pages on this repo (Settings → Pages → Deploy from branch → `main` / root)._

## Features
- **137 questions** from 14 exams, auto-sorted into **9 sections**, each answer in Hebrew + English.
- **A lesson per section** — exact terms (EN+HE), solving recipes, and a "traps" box.
- **Flashcards** with self-grading; missed cards resurface (spaced repetition via `localStorage`).
- **Practice Generators** for fork / scheduling / disk / paging — infinite fresh problems,
  answers computed by an engine validated against the official keys.
- **Mock Exam** (10 Q, scored), **Review Weak**, **Browse by Year**.
- Hebrew/English/both toggle, dark/light, mobile-first. No build step needed to *use* it.

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
- **2017–2023** questions and model answers are transcribed from the official past-exam PDFs.
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
