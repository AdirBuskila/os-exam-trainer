# -*- coding: utf-8 -*-
"""
EN/HE parity validator for the OS Exam Trainer.
Validates the BUILT artifact js/data.js (the ground truth the app loads):

  1. Every question carries both languages: non-empty he/en/answer_he/answer_en.
  2. The UI string dictionaries (DATA.i18n.en / .he) have identical key sets,
     identical {placeholder} sets per key, and no empty Hebrew values.
  3. Every lesson is bilingual ({en, he}, both non-empty) and its code is
     identical across languages: every <pre> and inline <code> block matches,
     and the Hebrew lesson is actually translated (he != en).

Exit code 1 on any problem.  Run:  python tests/parity.py   (or: npm test)
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_JS = os.path.join(ROOT, "js", "data.js")

errors = []
def err(m): errors.append(m)

def load_data():
    txt = open(DATA_JS, encoding="utf-8").read()
    m = re.search(r"window\.DATA\s*=\s*", txt)
    if not m:
        sys.exit("parity: could not find 'window.DATA =' in js/data.js — run python build.py first")
    body = txt[m.end():].rstrip()
    if body.endswith(";"):
        body = body[:-1]
    return json.loads(body)

D = load_data()

# ---- 1. question-level EN/HE parity ----------------------------------------
qs = D.get("questions", [])
for q in qs:
    qid = q.get("id", "?")
    for f in ("he", "en", "answer_he", "answer_en"):
        if not (q.get(f) and str(q[f]).strip()):
            err(f"Q {qid}: missing/empty '{f}'")

# ---- 2. i18n dictionary parity ---------------------------------------------
i18n = D.get("i18n", {})
en, he = i18n.get("en", {}), i18n.get("he", {})
ek, hk = set(en), set(he)
for k in sorted(ek - hk): err(f"i18n: key '{k}' present in en but missing in he")
for k in sorted(hk - ek): err(f"i18n: key '{k}' present in he but missing in en")
ph = lambda s: set(re.findall(r"\{(\w+)\}", s))
for k in sorted(ek & hk):
    if not str(he[k]).strip():
        err(f"i18n: empty Hebrew value for '{k}'")
    if ph(en[k]) != ph(he[k]):
        err(f"i18n: placeholder mismatch for '{k}': en={sorted(ph(en[k]))} he={sorted(ph(he[k]))}")

# ---- 3. lessons: bilingual + code identical --------------------------------
PRE  = re.compile(r"<pre\b[^>]*>(.*?)</pre>", re.S | re.I)
CODE = re.compile(r"<code\b[^>]*>(.*?)</code>", re.S | re.I)
lessons = D.get("lessons", {})
for sid, lo in sorted(lessons.items()):
    if not isinstance(lo, dict):
        err(f"lesson {sid}: expected bilingual {{en, he}} object"); continue
    if not str(lo.get("en", "")).strip():
        err(f"lesson {sid}: missing/empty 'en'"); continue
    if not str(lo.get("he", "")).strip():
        err(f"lesson {sid}: missing/empty 'he'"); continue
    en_pre = [x.strip() for x in PRE.findall(lo["en"])]
    he_pre = [x.strip() for x in PRE.findall(lo["he"])]
    if en_pre != he_pre:
        err(f"lesson {sid}: <pre> code blocks differ across languages (en={len(en_pre)}, he={len(he_pre)})")
    en_code = [x.strip() for x in CODE.findall(lo["en"])]
    he_code = [x.strip() for x in CODE.findall(lo["he"])]
    if en_code != he_code:
        err(f"lesson {sid}: inline <code> differs across languages (en={len(en_code)}, he={len(he_code)})")
    if lo["he"].strip() == lo["en"].strip():
        err(f"lesson {sid}: Hebrew lesson is identical to English (untranslated fallback)")

# ---- report ----------------------------------------------------------------
if errors:
    print(f"PARITY: {len(errors)} problem(s):")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"PARITY OK: {len(qs)} questions bilingual; "
      f"{len(ek)} i18n keys x2 (placeholders aligned); "
      f"{len(lessons)} lessons bilingual with identical code.")
