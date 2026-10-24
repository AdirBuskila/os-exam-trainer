# -*- coding: utf-8 -*-
"""Loads the course sources and turns them into the shape the app ships (DATA.courses).

  load_sources()  -> list of source course dicts (as authored, with `check`/`has` still on)
  to_data(src)    -> {course_id: {...}} with every text as {en, he}, ids assigned, options placed
"""
import os, sys, zlib, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["sched", "paging", "vmem", "sync"]


def load_sources():
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    out = []
    for cid in ORDER:
        fp = os.path.join(HERE, cid + ".py")
        if not os.path.exists(fp):
            continue
        mod = importlib.import_module(cid)
        importlib.reload(mod)
        out.append(mod.COURSE)
    return out


def tx(x):
    if isinstance(x, tuple):
        assert len(x) == 2 and all(isinstance(s, str) and s.strip() for s in x), x
        return {"en": x[0], "he": x[1]}
    assert isinstance(x, str) and x.strip(), repr(x)
    return {"en": x, "he": x}


def slot(qid, n):
    """Deterministic position of the correct option, spread over 0..n-1."""
    return zlib.crc32(qid.encode("utf-8")) % n


def to_data(sources):
    data = {}
    for c in sources:
        levels = []
        for i, L in enumerate(c["levels"], 1):
            lid = "%s-%d" % (c["id"], i)
            qs = []
            for k, q in enumerate(L["qs"], 1):
                qid = "%s-%d-%d" % (c["id"], i, k)
                opts = q["opts"]
                pos = slot(qid, len(opts))
                ordered = opts[1:]
                ordered.insert(pos, opts[0])
                item = {"id": qid, "q": tx(q["q"]), "opts": [tx(o) for o in ordered], "ans": pos,
                        "why": tx(q["why"]), "recap": tx(q["recap"])}
                if q.get("code"):
                    item["code"] = q["code"]
                if q.get("exam"):
                    item["exam"] = q["exam"]
                qs.append(item)
            levels.append({"id": lid, "order": i, "icon": L["icon"], "boss": bool(L["boss"]),
                           "title": tx(L["title"]), "goal": tx(L["goal"]), "lesson": tx(L["lesson"]),
                           "questions": qs})
        data[c["id"]] = {"id": c["id"], "icon": c["icon"], "title": tx(c["title"]), "intro": tx(c["intro"]),
                         "section": c["section"], "levels": levels}
    return data
