# -*- coding: utf-8 -*-
"""
Generates js/data.js (window.DATA) from the source content in src/data/.
Run:  python build.py     (or: npm run build)

Inputs:
  src/data/q_<EXAM>.json   one file per exam (14 exams, 10 questions each)
  src/data/lesson_<sec>.html  one micro-lesson per section
Output:
  js/data.js               window.DATA = { meta, lessons, questions }

OVERRIDES below are the *verified corrections / notes* applied at build time
(blank-answer fills + the three official-key clarifications surfaced by audit).
"""
import json, os, glob, re

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "src", "data")
OUT  = os.path.join(ROOT, "js", "data.js")

SECTIONS = [
    ("fork",        "Fork Counting",        "ספירת fork"),
    ("processes",   "Processes & States",   "תהליכים ומצבים"),
    ("scheduling",  "Scheduling",           "תזמון"),
    ("disk",        "Disk & Storage",       "דיסק ואחסון"),
    ("memory",      "Memory & Paging",      "זיכרון ודפדוף"),
    ("replacement", "Page Replacement",     "החלפת דפים"),
    ("sync",        "Synchronization",      "סנכרון"),
    ("interrupts",  "Interrupts & Mode",    "פסיקות ומצב"),
    ("systems",     "Systems Concepts",     "מושגי מערכת"),
]
SECTION_IDS = [s[0] for s in SECTIONS]

# Verified corrections / notes applied at build time, keyed by (exam, q).
OVERRIDES = {
    ("2017B", 10): {"answer_he": "מחזיר 1- (שגיאה)", "answer_en": "returns -1 (error)"},
    ("2019A", 9):  {"answer_he": "2 תהליכים, שניהם רצים (R)", "answer_en": "2 processes, both running (R)"},
    ("2019A", 10): {"answer_he": "semget", "answer_en": "semget"},
    ("2019B", 8):  {"answer_he": "הדף שלא ייעשה בו שימוש לזמן הארוך ביותר", "answer_en": "page used furthest in future"},
    ("2019B", 9):  {"answer_he": "1", "answer_en": "1"},
    ("2019B", 10): {"answer_he": "shmctl (IPC_RMID)", "answer_en": "shmctl (IPC_RMID)"},
    ("2017A", 9):  {"answer_he": "00", "answer_en": '"00"'},
    ("2020B", 6):  {"answer_he": "3 (לפי המחוון); SJF נוקשה=4", "answer_en": "3 ms (key); strict SJF=4",
                    "note": "Course key computed SJF as preemptive (SRTF) -> 3. Pure non-preemptive SJF = 4 ms. Write the course's value."},
    ("2023B", 6):  {"answer_he": "הרעבה / Bounded waiting", "answer_en": "Bounded waiting (-> starvation)",
                    "note": "Official key: 'starvation/הרעבה'. The violated CONDITION is Bounded Waiting; starvation is its consequence. Both usually accepted."},
    ("2017A", 7):  {"note": "Official phrasing. Real reason: the MMU translates on every memory access — far faster than trapping to the OS each time."},
    ("2023A", 2):  {"note": "Course answer (sequential model). Strictly: a higher-IRQL interrupt preempts the current ISR (nested handling); equal- or lower-priority interrupts wait until it finishes."},
}

_HEB = re.compile(r"[֐-׿]")
_CODE = re.compile(r"[{};#]|==|!=|<stdio|<unistd|\bmain\b|\bprintf\b|\bfork\b|\bsemget\b|\bsemop\b|\bsemctl\b|\bshm\w+\b|\bint\b|\bvoid\b|if\s*\(|for\s*\(|while\s*\(|IPC_")

def split_code(he):
    """Separate an embedded C/code block (LTR) from the Hebrew prose so it renders correctly.
    Code in this dataset always trails the prose on its own lines."""
    lines = he.split("\n")
    idx = None
    for i, l in enumerate(lines):
        s = l.strip()
        if not s or _HEB.search(s):
            continue
        if _CODE.search(s):
            idx = i
            break
    if idx is None:
        return he, None
    return "\n".join(lines[:idx]).strip(), "\n".join(lines[idx:]).strip()

def load_questions():
    qs = []
    for fp in sorted(glob.glob(os.path.join(DATA, "q_*.json"))):
        exam = os.path.basename(fp)[2:-5]            # q_2017A.json -> 2017A
        arr = json.load(open(fp, encoding="utf-8"))
        for item in arr:
            item["exam"] = exam
            key = (exam, int(item.get("q", 0)))
            if OVERRIDES.get(key):
                item.update(OVERRIDES[key])
            item["id"] = f"{exam}-{item.get('q')}"
            if item["section"] not in SECTION_IDS:
                raise SystemExit(f"Bad section '{item['section']}' in {item['id']}")
            if not item.get("he") or not (item.get("answer_he") or item.get("answer_en")):
                raise SystemExit(f"Missing text/answer in {item['id']}")
            prose, code = split_code(item["he"])
            if code:
                item["he"] = prose
                item["code"] = code
            qs.append(item)
    return qs

def load_lessons():
    """Each lesson is bilingual: {en, he}. lesson_<sid>.he.html holds the Hebrew
    version; if it is missing we fall back to the English text so nothing breaks."""
    out = {}
    for sid, *_ in SECTIONS:
        fp_en = os.path.join(DATA, f"lesson_{sid}.html")
        fp_he = os.path.join(DATA, f"lesson_{sid}.he.html")
        en = open(fp_en, encoding="utf-8").read() if os.path.exists(fp_en) else "<p><em>Lesson pending.</em></p>"
        he = open(fp_he, encoding="utf-8").read() if os.path.exists(fp_he) else en
        out[sid] = {"en": en, "he": he}
    return out

def load_i18n():
    """Inline the UI string dictionaries so the app needs no fetch (works on file://)."""
    out = {}
    for lang in ("en", "he"):
        fp = os.path.join(DATA, "i18n", f"{lang}.json")
        out[lang] = json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else {}
    return out

def load_scope():
    fp = os.path.join(DATA, "scope.json")
    if not os.path.exists(fp):
        return {"focus": None, "offExam": {}}
    return json.load(open(fp, encoding="utf-8"))

def main():
    questions = load_questions()
    scope = load_scope()
    off = scope.get("offExam", {})
    off_he = scope.get("offExamHe", {})
    n_off = 0
    for q in questions:
        if q["id"] in off:
            q["offExam"] = True
            q["offReason"] = off[q["id"]]
            q["offReason_he"] = off_he.get(q["id"], off[q["id"]])
            n_off += 1
    counts = {s: 0 for s in SECTION_IDS}
    for q in questions:
        counts[q["section"]] += 1
    data = {
        "meta": {
            "course": "HIT 61206 — Operating Systems",
            "examDate": "2026-07-01",
            "sections": [{"id": s[0], "title": s[1], "he": s[2], "n": counts[s[0]]} for s in SECTIONS],
            "focus": scope.get("focus"),
        },
        "lessons": load_lessons(),
        "i18n": load_i18n(),
        "questions": questions,
    }
    payload = json.dumps(data, ensure_ascii=False, indent=0)
    header = ("/* AUTO-GENERATED by build.py — do not edit by hand.\n"
              "   Edit the source content in src/data/ and re-run: python build.py */\n")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(header + "window.DATA = " + payload + ";\n")
    print(f"Wrote {OUT}")
    print(f"  {len(questions)} questions across {len(SECTIONS)} sections: {counts}")
    print(f"  focus: {n_off} question(s) marked off-exam ({scope.get('focus',{}).get('label','-') if scope.get('focus') else '-'})")

if __name__ == "__main__":
    main()
