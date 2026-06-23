# Terms Glossary — OS Exam Trainer (HE/EN)

Single source of truth for how each recurring term is rendered when the UI/lessons
are translated to Hebrew. The rule of thumb mirrors how an Israeli CS course is
actually taught: **the technical token stays English; the surrounding prose is Hebrew.**

Legend
- **Keep English** — render verbatim in both languages (and bidi-isolate inside Hebrew prose).
- **Hebrew** — translate the prose word; the agreed Hebrew rendering is given.
- First mention of a translated *concept* in a lesson may use the form `עברית (English)` once, then stay Hebrew.

> Anything in this table marked *Keep English* MUST be wrapped with `<bdi dir="ltr">…</bdi>`
> (or rendered inside a `dir="ltr"` code block) when it appears inside Hebrew prose, so the
> Unicode bidi algorithm cannot reorder it. Tokens with punctuation/parens
> (`fork()`, `wait(&status)`, `P(s)`/`V(s)`, `PID 4 → 5 → 6`, `2^k`) are the ones that break.

## System calls / C API — **Keep English** (always)
`fork()`, `exec()` / `execvp()`, `wait()` / `waitpid()`, `exit()`, `printf()`, `fflush()`,
`malloc()` / `free()`, `semget`, `semop`, `semctl`, `shmget`, `shmat`, `shmdt`, `shmctl`,
`IPC_RMID`, `nsops`, `main()`, `mmap`, file descriptors (`fd`).

## Acronyms / register & flag names — **Keep English** (always)
`OS`, `CPU`, `MMU`, `TLB`, `PCB`, `PID`, `PPID`, `IPC`, `I/O`, `ISR`, `IRQL`, `IVT`,
`FIFO`, `LRU`, `LFU`, `RR`, `FCFS`, `SJF`, `SRTF`, `MLFQ`, `COW`, `R`/`W`/`X` bits,
reference bit, dirty bit, present/valid bit. Units: `KB`, `MB`, `GB`, `TB`, `ms`, `bit`.

## Algorithm names — **Keep English** (always)
`FCFS`, `SJF`, `SRTF`, `Round Robin (RR)`, `MLFQ`, `Multilevel Queue`, `Clock / Second-Chance`,
`Optimal (OPT)`, `Belady`, `Banker's algorithm`, `Peterson`, `Dekker`.

## Concepts — **Hebrew prose** (agreed renderings)
| English | Hebrew (agreed) | Notes |
|---|---|---|
| process | תהליך | plural תהליכים |
| thread | חוט / thread | keep `thread` if ambiguous; prefer חוט |
| parent / child (process) | תהליך אב / תהליך בן | |
| zombie | תהליך זומבי | keep "זומבי" |
| orphan | תהליך יתום | |
| scheduling | תזמון | |
| context switch | החלפת הקשר (context switch) | |
| preemptive / non-preemptive | מפנה (preemptive) / לא-מפנה | |
| starvation | הרעבה | the *consequence*, not a CS condition |
| deadlock | קיפאון (deadlock) | course mostly says "deadlock" |
| critical section | קטע קריטי | |
| mutual exclusion | מניעה הדדית (mutual exclusion) | |
| bounded waiting | המתנה חסומה (bounded waiting) | the violated *condition* behind starvation |
| progress | התקדמות (progress) | |
| semaphore | סמפור (semaphore) | wait/signal = `P`/`V`, kept English |
| wait / signal (P/V) | wait / signal | keep `P(s)` / `V(s)` English+isolated |
| atomic | אטומי | |
| race condition | מצב מרוץ (race condition) | |
| memory / paging | זיכרון / דפדוף | |
| page / frame | דף / מסגרת (frame) | |
| page fault | שגיאת דף (page fault) | |
| page replacement | החלפת דפים | |
| thrashing | thrashing | keep English (course uses it) |
| virtual / physical address | כתובת וירטואלית / פיזית | |
| page table | טבלת דפים | |
| offset | היסט (offset) | |
| swap | החלפה (swap) | |
| interrupt | פסיקה | |
| trap / system call | מלכודת (trap) / קריאת מערכת (system call) | |
| kernel mode / user mode | מצב גרעין (kernel mode) / מצב משתמש (user mode) | keep `kernel`/`user` if cleaner |
| disk / cylinder / track / sector / surface / platter | דיסק / צילינדר / מסילה / סקטור / משטח / פלטה | |
| sectors per track | סקטורים למסילה | |
| capacity | קיבולת | |
| real-time (soft/hard) | זמן-אמת (soft/hard real-time) | keep soft/hard English |
| turnaround / waiting time | זמן סבב / זמן המתנה | |
| Gantt chart | תרשים Gantt | keep `Gantt` |
| quantum | קוונטום (quantum) | |
| burst | זמן ריצה (burst) | |
| arrival time | זמן הגעה | |

## Course-specific labels — **Keep as data**
- Course code `61206`, term ids like `2024A` / `2023B` — never translate.
- `HIT` (institution acronym) — keep English.

## Open judgment calls (surfaced for review)
These were decided to keep the build moving; each can be overridden in one place
(edit the glossary + the relevant `lesson_*.he.html` and re-run `python build.py`).

1. `thrashing` — kept English (course decks use the English term) rather than תזזית/השתבללות.
2. `thread` → חוט (English `thread` kept in the table's English-term column).
3. UI type tags `concept/compute/trick` → מושג / חישוב / מלכודת.
4. **Intentional dual renderings inside a lesson.** Each source lesson already shipped a
   "Hebrew term" table column with its *own* Hebrew wording. Per rule "leave that column
   as-is", the prose now uses the glossary term while the column keeps the lesson's term —
   so a concept can appear two ways in one lesson. Confirmed cases:
   - **burst** → prose keeps `burst` (English, isolated); table column says `פרץ חישוב`
     (glossary preference would be זמן ריצה).
   - **preemptive / non-preemptive** → prose `מפנה / לא-מפנה`; table column `נשלף / לא נשלף`.
   - **page fault** → prose/Concept `שגיאת דף`; table column `פסיקת דף / כשל דף`.
   If you want a single rendering per lesson, pick one and update both spots.
5. **short-circuit** → rendered `קצר חשמלי` ("electrical short"). Common but debatable; some
   courses prefer keeping `short-circuit` English or `הערכת קצר`. Easy to change.
6. **`vs`** → translated to `מול` (e.g. "Cylinder מול Track").
7. **Table header labels** (`Concept / English term / Hebrew term / One-line identifier`) left
   English — they are structural column-type labels, not lesson prose.
8. **Arrows in prose** — `disk` uses HTML entities `&rarr;`/`&harr;`; `sync` kept literal `→`.
   Both render LTR correctly; purely a source-style difference.

## Bidi isolation policy (enforced by tooling, not by hand)
`js/i18n.js` `autoIsolate()` and the build-time text-node pass wrap every Latin/code/number
run that sits in Hebrew text in `<bdi dir="ltr">…</bdi>`. A deterministic checker confirms
**0** un-isolated Latin tokens remain in Hebrew lesson prose, and that every `<pre>`/`<code>`
block is byte-identical between the English and Hebrew lessons.
