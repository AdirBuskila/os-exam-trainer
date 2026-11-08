# -*- coding: utf-8 -*-
"""Pronunciation lexicon for the מערכות הפעלה videos: the shared machinery (tools/video/lexicon_base.py) plus the
course's own terms. TeX is spoken token by token (TEX_TOKENS, longest first); a span with any token outside the
table is refused, and the script must give P(..., say=...).
Per-course additions go in videos/lex_<course>.py (WORDS, HOMOPHONES, TEX_TOKENS), merged below.
Latin letters in say= text are misread by the voice: write them in Hebrew letters (אִקְס, וַואי, אֶן).

The OS class says most terms in English (Round Robin, page fault, TLB, semaphore); the subtitles keep them in Latin
letters and WORDS gives the voice a Hebrew transliteration. Entries shared by every course are here; a course's own
terms go in its lex_<course>.py.
"""
import re
from lexicon_base import *          # noqa: F401,F403
from lexicon_base import WORDS, SYMBOL, base_tex_say

# meaning-flipping mishearings to flag in the STT report: {what the recognizer wrote: what was said}
HOMOPHONES = {"שלא": "שלו", "הקלה": "הכלה", "לו": "לא"}

WORDS.update({
    "מ״ש": "מילישניות",
    "CPU": "סִי פִּי יוּ",
    "RAM": "רַאם",
    "OS": "מערכת ההפעלה",
    "Linux": "לִינוּקְס",
    "Windows": "ווינְדוֹאוּז",
    "kernel": "קֶרְנֶל",
    "Kernel": "קֶרְנֶל",
    "I/O": "קלט פלט",
    # process / page names as they appear in tables: P1 -> "פִּי אחת" (longest first, so P10 is not P1 + 0)
    **{f"P{i}": f"פִּי {DIGIT[str(i)]}" for i in range(1, 10)},   # noqa: F405
    **{f"T{i}": f"טִי {DIGIT[str(i)]}" for i in range(1, 10)},   # noqa: F405
})

TEX_TOKENS = {
    r"\infty": "אינסוף", r"\to": "ל", r"\rightarrow": "ל", r"\Rightarrow": "גורר", r"\iff": "אם ורק אם",
    r"\in": "שייך ל", r"\notin": "לא שייך ל", r"\ne": "שונה מ", r"\neq": "שונה מ",
    r"=": "שווה", r"<": "קטן מ", r">": "גדול מ", r"\le": "קטן או שווה ל", r"\leq": "קטן או שווה ל",
    r"\ge": "גדול או שווה ל", r"\geq": "גדול או שווה ל", r"\cdot": "כפול", r"\times": "כפול", r"+": "ועוד", r"-": "פחות",
    r"\approx": "בערך",
    r",": ",", r"^2": "בריבוע", r"^3": "בשלישית",
    "x": "אִקְס", "y": "וַואי", "n": "אֶן", "k": "קֵיי", "t": "טִי",
    "P": "פִּי", "T": "טִי", "S": "אֶס",
}
import importlib, pathlib
for _f in sorted(pathlib.Path(__file__).parent.glob("lex_*.py")):   # per-course additions: lex_sched.py, …
    _m = importlib.import_module(_f.stem)
    WORDS.update(getattr(_m, "WORDS", {}))
    HOMOPHONES.update(getattr(_m, "HOMOPHONES", {}))
    TEX_TOKENS.update(getattr(_m, "TEX_TOKENS", {}))
for d, s in DIGIT.items():                       # noqa: F405
    TEX_TOKENS[d] = s
_TOK = sorted(TEX_TOKENS, key=len, reverse=True)


def _spell(t):
    """speak a TeX span token by token; None if a token is unknown"""
    t = t.replace(r"\,", " ").replace(r"\ ", " ").replace(r"\mathrm", "").replace(r"\text", "")
    out, i = [], 0
    while i < len(t):
        c = t[i]
        if c in " {}":
            i += 1
            continue
        m = re.match(r"_\{?(\d+)\}?", t[i:])
        if m:                                    # P_1, T_2: the index as a number word
            out.append(" ".join(DIGIT[d] for d in m.group(1)))   # noqa: F405
            i += m.end()
            continue
        m = re.match(r"\^\{?(\d+)\}?", t[i:])
        if m and m.group(1) not in ("2", "3"):    # 2^{12}: "בחזקת 12"
            out.append(f"בחזקת {m.group(1)}")
            i += m.end()
            continue
        if c == "(" and out:                     # f(x): "של"
            out.append("של")
            i += 1
            continue
        if c == ")":
            i += 1
            continue
        m = re.match(r"\d+(?:\.\d+)?", t[i:])
        if m and len(m.group(0)) > 1:            # 12, 0.9: as a number (the voice reads numerals well)
            out.append(m.group(0))
            i += m.end()
            continue
        hit = next((k for k in _TOK if t.startswith(k, i)), None)
        if hit is None:
            return None
        out.append(TEX_TOKENS[hit])
        i += len(hit)
    s = " ".join(out).replace(" ,", ",")
    s = re.sub(r"(^|\s)([לבמ])\s+", r"\1\2", s)      # "שייך ל" + "אֶן": one word, not the letter's name
    return re.sub(r"\s+", " ", s).strip() or None


def tex_say(tex):
    t = tex.strip()
    if re.fullmatch(r"\d+", t):
        return t
    return _spell(t)
