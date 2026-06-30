# Semaphore hero animation + home rotation — design

**Date:** 2026-06-30
**Status:** Approved

## Goal

Add a second home-page hero animation depicting the **producer–consumer bounded
buffer** with live semaphore operations, and rotate it with the existing fork
animation so each page load/refresh shows the other one.

## Background

The home view (`renderHome` in `js/app.js`) renders a `.hero-tree` strip
(`#heroTree`, 160px tall) with a `fork()` corner cap and mounts the forking
process-tree canvas via `window.HERO.mount(container)` (`js/hero.js`). `HERO`
exposes `mount(container)` / `destroy()`; the instance reads theme colors from
CSS vars, mirrors for RTL, pauses off-screen / when the tab is hidden, honors
`prefers-reduced-motion`, and self-destructs once its canvas leaves the DOM.

The course's sync lesson uses exactly this vocabulary: three semaphores
`mutex=1, empty=N, full=0`; operations `wait(S)` / `signal(S)` (System V
`sem_op = -1 / +1`); process states `RUNNING` / `WAITING (blocked)`.

## Scene: producer–consumer bounded buffer

A bounded buffer of N slots, sized to the same 160px strip:

```
[ Producer ]      ┌─ buffer (N slots) ─┐      [ Consumer ]
    P  ──token──▶ │ ▣ ▣ ▢ ▢ ▢ │ ◀──token── C
                  └────────────────────┘
   empty = 3      full = 2      mutex = 1        ← live semaphore chips
   wait(empty)    signal(full)   …               ← op label flashes near actor
```

- **Producer** (`--acc`): `wait(empty) → wait(mutex) → [drop token in next free slot]
  → signal(mutex) → signal(full)`.
- **Consumer** (`--acc2`): `wait(full) → wait(mutex) → [take token from a filled slot]
  → signal(mutex) → signal(empty)`.
- **Semaphore chips** `empty` (init N), `full` (init 0), `mutex` (init 1) tick and
  briefly highlight (`--good`) as each op fires.
- **Operation labels** flash beside the active actor: green on success, amber
  (`--warn`) when the op blocks.
- **Blocking is the focus:** buffer full → `empty=0` → producer's `wait(empty)`
  blocks → producer turns amber, shows `WAITING`, stays until the consumer's
  `signal(empty)` wakes it. Symmetric when the buffer empties (consumer blocks on
  `full=0`). `mutex` serializes the critical section — a small padlock closes
  while one actor is inside.

### Labels & i18n

Like the fork animation (only PIDs + `fork()`), labels stay in the technical
notation the exam uses — `P`, `C`, `empty`, `full`, `mutex`, `wait()`, `signal()`,
`WAITING` (the lesson writes these in English). Only the **geometry mirrors for
RTL** (producer/consumer swap sides); no i18n wiring needed.

## Code structure

- **New `js/sema.js`** → `window.SEMA = { mount, destroy }`, mirroring `HERO`'s API.
  Reuses the `.hero-canvas` class/CSS and re-implements the small lifecycle
  boilerplate (resize / IntersectionObserver / visibility-pause / self-destruct /
  reduced-motion static frame). `js/hero.js` is left untouched — the two
  animations stay fully isolated.
- **`index.html`**: add `<script src="js/sema.js"></script>` before `js/app.js`.
- **`js/app.js`**: a small scene registry + `pickHeroScene()`; the cap label moves
  out of the hardcoded `#heroTree` HTML so it can switch per scene.

## Rotation (swap per page load/refresh)

A scene is chosen **once per page load** and cached for that session, so navigating
home↔section↔home keeps the same animation; only a refresh/reopen swaps it.

- First `renderHome` of the page: read `localStorage['os_trainer_hero']`
  (default `0`), pick that scene, then immediately write `(idx+1) % 2` back, so the
  *next* page load shows the other scene. Strict alternation: fork →
  producer-consumer → fork → …
- Subsequent home renders in the same session reuse the cached index (no re-flip).

Scenes:
| idx | cap | mount |
|-----|-----|-------|
| 0 | `fork()` | `HERO.mount` |
| 1 | `producer ⇄ consumer` | `SEMA.mount` |

## Robustness (parity with hero.js)

Reduced-motion static frame (half-full buffer, no motion), pause when off-screen
or tab hidden, self-destruct when the canvas leaves the DOM, theme colors re-read
live, DPR-aware crisp rendering.

## Out of scope

- No changes to the fork animation.
- No i18n string additions.
- No new build/test steps (build.py only generates data; animation is verified
  visually).

## Verification

- `python build.py` still succeeds (unaffected).
- Serve (`python -m http.server 8080`); on the home page confirm scene 0 = fork.
- Refresh → scene 1 = producer-consumer; refresh again → back to fork.
- Confirm semaphore values, op labels, blocking/waking, RTL mirroring (toggle
  עברית), light/dark theme, and reduced-motion static frame.
