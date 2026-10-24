# -*- coding: utf-8 -*-
"""Machine-checks the "צריך עזרה?" guided courses.

  python tests/courses_check.py     (also part of `npm test`)

What it asserts, per question:
  * the stored correct answer equals what an independent simulator computes (`check=` specs:
    scheduling Gantt / waiting / turnaround, page replacement, address translation, TLB
    effective access time, semaphores, deadlock reachability, plain arithmetic);
  * a question that carries a real exam id (`exam=`) matches the deck's own answer (`has=`);
  * the options are distinct, the correct one is unique, numeric distractors never equal it;
  * every English/Hebrew pair is really translated, lessons keep identical code in both languages.
Scheduling averages are also cross-checked against the app's own engine (js/engines.js) in node.
Finally the built js/data.js must contain exactly what the sources produce (no stale build).
"""
import glob, json, math, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "courses"))
import sims, loader  # noqa: E402

errors = []


def err(m):
    errors.append(m)


HEB = re.compile(r"[֐-׿]")

# ------------------------------------------------------------------ deck
DECK = {}
for fp in glob.glob(os.path.join(ROOT, "src", "data", "q_*.json")):
    exam = os.path.basename(fp)[2:-5]
    for q in json.load(open(fp, encoding="utf-8")):
        DECK["%s-%s" % (exam, q["q"])] = q


# ------------------------------------------------------------------ evaluators
def ev_sched(c):
    r = sims.schedule(c["procs"], c["algo"], c.get("q"))
    ask = c["ask"]
    nm = {n: i for i, n in enumerate(r["names"])}
    if ask == "avg_wait":
        return sims.fmt_num(round(r["avg_wait"], 2))
    if ask == "avg_turn":
        return sims.fmt_num(round(r["avg_turn"], 2))
    if ask == "avg_resp":
        return sims.fmt_num(round(r["avg_resp"], 2))
    if ask == "switches":
        return str(r["switches"])
    if ask == "order":
        names = [g[0] for g in r["gantt"]]
        return ", ".join(names)
    if ask.startswith("slice:"):
        return r["gantt"][int(ask[6:])][0]
    kind, who = ask.split(":")
    i = nm[who]
    if kind == "wait":
        return str(r["wait"][i])
    if kind == "turn":
        return str(r["turn"][i])
    if kind == "finish":
        return str(r["finish"][i])
    if kind == "resp":
        return str(r["resp"][i])
    if kind == "start":
        return str(r["resp"][i] + c["procs"][i][0])
    raise ValueError(ask)


def ev_repl(c):
    ask = c["ask"]
    r = sims.replace(c["refs"], c["frames"], c["algo"], strict=not ask in ("faults", "hits"))
    if ask == "faults":
        return str(r["faults"])
    if ask == "hits":
        return str(r["hits"])
    if ask.startswith("victim:"):
        v = r["trace"][int(ask[7:])][3]
        return "none" if v is None else str(v)
    if ask == "final":
        return " ".join(str(x) for x in sorted(r["trace"][-1][2]))
    if ask.startswith("fault_at:"):
        return r["trace"][int(ask[9:])][1]
    raise ValueError(ask)


def ev_addr(c):
    ask = c["ask"]
    page, off = sims.split_address(c["vaddr"], c["page_size"])
    if ask == "page":
        return str(page)
    if ask == "offset":
        return str(off)
    if ask == "paddr":
        return str(sims.translate(c["vaddr"], c["page_size"], c["table"]))
    raise ValueError(ask)


def ev_calc(c):
    ns = {"math": math, "log2": lambda x: int(round(math.log2(x))), "pow2": sims.pow2,
          "sorted": sorted, "min": min, "max": max, "sum": sum, "len": len, "range": range}
    v = eval(c["v"], {"__builtins__": {}}, ns)
    if isinstance(v, str):
        return v
    f = c.get("fmt", "num")
    if f == "pow2":
        return sims.pow2(v)
    if f == "round1":
        return "%.1f" % v
    return sims.fmt_num(round(v, 2) if isinstance(v, float) else v)


def ev_eat(c):
    return sims.fmt_num(round(sims.eat(c["hit"], c["mem"], c["levels"], c.get("tlb", 0)), 2))


def ev_sem(c):
    r = sims.semaphore(c["init"], c["ops"])
    ask = c["ask"]
    if ask == "value":
        return str(r["value"])
    if ask == "waiting":
        return str(len(r["queue"]))
    if ask.startswith("blocks:"):
        return "yes" if ("%s blocks" % ask[7:]) in r["log"] else "no"
    raise ValueError(ask)


def ev_dead(c):
    if "n" in c:
        procs = sims.philosophers(c["n"], c.get("ordered", False))
    else:
        procs = c["procs"]
    return "deadlock" if sims.can_deadlock(procs) else "safe"


EVAL = {"sched": ev_sched, "repl": ev_repl, "addr": ev_addr, "calc": ev_calc, "eat": ev_eat, "sem": ev_sem, "dead": ev_dead}


def plain(o):
    return o if isinstance(o, str) else o[0]


def numeric(s):
    try:
        return float(s.replace(",", ""))
    except Exception:
        return None


# ------------------------------------------------------------------ main loop
sources = loader.load_sources()
stats = dict(courses=0, levels=0, questions=0, checked=0, exam=0)
node_jobs = []
if len(sources) != 4:
    err("expected 4 courses, found %d" % len(sources))

for c in sources:
    stats["courses"] += 1
    nlev = len(c["levels"])
    if not 6 <= nlev <= 8:
        err("%s: %d levels (need 6-8)" % (c["id"], nlev))
    if not c["levels"][-1]["boss"]:
        err("%s: last level is not the boss" % c["id"])
    if any(L["boss"] for L in c["levels"][:-1]):
        err("%s: boss flag on a non-final level" % c["id"])
    seen_q = set()
    for i, L in enumerate(c["levels"], 1):
        stats["levels"] += 1
        lid = "%s-%d" % (c["id"], i)
        nq = len(L["qs"])
        if not 4 <= nq <= 6:
            err("%s: %d questions (need 4-6)" % (lid, nq))
        # lesson parity
        en, he = L["lesson"]
        for tag in ("pre", "code"):
            rx = re.compile(r"<%s\b[^>]*>(.*?)</%s>" % (tag, tag), re.S)
            if [x.strip() for x in rx.findall(en)] != [x.strip() for x in rx.findall(he)]:
                err("%s: <%s> blocks differ between en and he lesson" % (lid, tag))
        if not HEB.search(he):
            err("%s: Hebrew lesson has no Hebrew" % lid)
        for tag in ("<p>", "<table>", "<ol>", "<ul>"):
            if en.count(tag) != he.count(tag):
                err("%s: lesson structure differs (%s count en=%d he=%d)" % (lid, tag, en.count(tag), he.count(tag)))
        for fld in ("title", "goal"):
            if not HEB.search(L[fld][1]):
                err("%s: %s has no Hebrew" % (lid, fld))
        if "{" in en and "{" in he and False:
            pass
        for k, q in enumerate(L["qs"], 1):
            qid = "%s-%d" % (lid, k)
            stats["questions"] += 1
            key = (q["q"], q["code"])
            if key in seen_q:
                err("%s: duplicate question (same text and table)" % qid)
            seen_q.add(key)
            # texts translated
            for fld in ("q", "why", "recap"):
                v = q[fld]
                if not isinstance(v, tuple) or not HEB.search(v[1]) or v[0] == v[1]:
                    err("%s: %s must be an (en, he) pair with real Hebrew" % (qid, fld))
                if isinstance(v, tuple) and HEB.search(v[0]):
                    err("%s: %s English side contains Hebrew" % (qid, fld))
            opts = q["opts"]
            ens = [plain(o) for o in opts]
            hes = [o if isinstance(o, str) else o[1] for o in opts]
            if len(set(ens)) != len(ens) or len(set(hes)) != len(hes):
                err("%s: duplicate options %s" % (qid, ens))
            for o in opts:
                if isinstance(o, tuple) and not HEB.search(o[1]):
                    err("%s: option %r lacks Hebrew" % (qid, o))
            correct = plain(opts[0])
            nc = numeric(correct)
            if nc is not None:
                for o in ens[1:]:
                    if numeric(o) is not None and abs(numeric(o) - nc) < 1e-9:
                        err("%s: distractor %r equals the answer" % (qid, o))
            # machine check
            checks = q["check"]
            if checks is not None and not isinstance(checks, list):
                checks = [checks]
            for ck in checks or []:
                stats["checked"] += 1
                try:
                    got = EVAL[ck["k"]](ck)
                except sims.Ambiguous as e:
                    err("%s: ambiguous question (%s)" % (qid, e))
                    continue
                want = ck.get("want", correct)
                if got != want:
                    err("%s: simulator says %r, stored answer %r" % (qid, got, want))
                if ck["k"] == "sched" and ck["ask"] == "avg_wait":
                    node_jobs.append((qid, ck, got))
            # real exam link
            if q["exam"]:
                stats["exam"] += 1
                d = DECK.get(q["exam"])
                if d is None:
                    err("%s: exam id %s is not in the deck" % (qid, q["exam"]))
                elif q["has"]:
                    blob = ((d.get("answer_en") or "") + " " + (d.get("answer_he") or "")).lower()
                    if q["has"].lower() not in blob:
                        err("%s: deck %s answer %r lacks %r" % (qid, q["exam"], d.get("answer_en"), q["has"]))
                else:
                    err("%s: exam question without `has=`" % qid)
            elif q["has"]:
                err("%s: has= without exam=" % qid)
            if checks is None and not q["exam"] and (c["id"] in ("sched",) and L["qs"]):
                pass
    # the boss must be mostly real exam items
    boss = c["levels"][-1]["qs"]
    n_real = sum(1 for q in boss if q["exam"])
    if n_real < len(boss) // 2:
        err("%s boss: only %d/%d questions carry a real exam id" % (c["id"], n_real, len(boss)))

# ------------------------------------------------------------------ cross-check vs js/engines.js
if node_jobs:
    jobs = []
    for qid, ck, got in node_jobs:
        jobs.append({"id": qid, "algo": ck["algo"], "q": ck.get("q"), "procs": ck["procs"], "want": got})
    js = """
const O=require(%s);const jobs=JSON.parse(process.argv[1]);let bad=0;
for(const j of jobs){const ps=j.procs.map((p,i)=>({name:'P'+(i+1),arrival:p[0],burst:p[1]}));
 const r=O.schedule(ps,j.algo,j.q);const a=+r.avg.toFixed(2);
 if(Math.abs(a-parseFloat(j.want))>0.011){bad++;console.log('ENGINE MISMATCH '+j.id+' engine='+a+' sim='+j.want);}}
console.log('engine cross-check: '+jobs.length+' scheduling averages, '+bad+' mismatches');process.exit(bad?1:0);
""" % json.dumps(os.path.join(ROOT, "js", "engines.js"))
    try:
        out = subprocess.run(["node", "-e", js, json.dumps(jobs)], capture_output=True, text=True, timeout=60)
        print(out.stdout.strip())
        if out.returncode:
            err("engine cross-check failed: " + out.stdout.strip())
    except FileNotFoundError:
        err("node not found for the engine cross-check")

# ------------------------------------------------------------------ built data is current
built = loader.to_data(sources)
txt = open(os.path.join(ROOT, "js", "data.js"), encoding="utf-8").read()
m = re.search(r"window\.DATA\s*=\s*", txt)
data = json.loads(txt[m.end():].rstrip().rstrip(";"))
if data.get("courses") != built:
    err("js/data.js courses are stale: run `python build.py`")

# ------------------------------------------------------------------ report
if errors:
    print("COURSES: %d problem(s):" % len(errors))
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("COURSES OK: %(courses)d courses, %(levels)d levels, %(questions)d questions; "
      "%(checked)d simulator-checked, %(exam)d tied to real deck questions." % stats)
