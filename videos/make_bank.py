# -*- coding: utf-8 -*-
"""videos/bank.json: the app's question bank in the shape the video engine reads ({"questions": [{id, ...}]}).

The bank itself is src/data/q_<EXAM>.json (short-answer, he + en). build.py's load_questions() gives every item its
id "<EXAM>-<q>" (the same ids the guided courses cite with exam="2022B-4") and applies the verified OVERRIDES, so
this file is exactly what the app shows. Written only when the content changes. Called by videos/app_config.py.

usage:  PYTHONUTF8=1 python videos/make_bank.py
"""
import importlib.util, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "bank.json"
KEEP = ("id", "exam", "q", "section", "type", "he", "en", "code", "answer_he", "answer_en", "note")


def questions():
    spec = importlib.util.spec_from_file_location("os_build", ROOT / "build.py")   # not `import build` (a pip name)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return [{k: q[k] for k in KEEP if k in q} for q in m.load_questions()]


def write():
    qs = questions()
    ids = [q["id"] for q in qs]
    assert len(ids) == len(set(ids)), "duplicate bank ids"
    text = json.dumps({"questions": qs}, ensure_ascii=False, indent=1) + "\n"
    if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
        OUT.write_text(text, encoding="utf-8")
    return len(qs)


if __name__ == "__main__":
    print(f"videos/bank.json: {write()} questions")
