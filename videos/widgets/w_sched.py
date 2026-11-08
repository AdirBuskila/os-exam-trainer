# -*- coding: utf-8 -*-
"""Widgets for the "sched" course videos (S01-S07): Gantt chart, process table, Round Robin queue strip.

Every schedule comes from the course simulator src/courses/sims.py (`schedule(..., strict=True)`, which raises on a
tie the course does not define). The helpers below replay the same schedule a second way (event by event) and assert
that both agree, so a figure can never show a chart the course checker would not produce:
  run(procs, algo, q)   sims.schedule + checks; returns the result dict
  rr_steps(procs, q)    Round Robin event replay: one step per slice (who ran, who arrived during it, the queue after
                        it), using the course rule "arrivals during the slice first, then the preempted process";
                        refuses an arrival at the exact instant of a preemption (the lesson does not order that case)
  srtf_events(procs)    at every arrival: the running process, its remaining time, the newcomer's burst, preempt?
Figures (hidden pieces carry ids that the timeline shows):
  gantt()   SVG, LTR: {pfx}-s{i} slice i (block + its end tick), {pfx}-i{j} idle gap j, {pfx}-f-P2 completion mark,
            {pfx}-a-P2 arrival mark, {pfx}-hl{i} highlight frame on slice i
  ptable()  HTML table: {pfx}-<name>-<col> one cell (col in arr, burst, fin, turn, wait, resp, first, rem),
            {pfx}-row-<name> a highlight of the row, {pfx}-avg the average line under it
  rrq()     the queue after each slice: {pfx}-r{i} row i (time, who ran, the queue with new arrivals and the preempted
            process marked)
Class names start with sc- (all widget css files load into every video of the app).
"""
from fractions import Fraction as F
from html import escape as esc
import sims

COL = {"P1": "#2dd4bf", "P2": "#38bdf8", "P3": "#c084fc", "P4": "#fbbf24", "P5": "#fb7185", "P6": "#a3e635"}


# ---------------------------------------------------------------- simulation + cross-checks
def run(procs, algo, q=None):
    r = sims.schedule(procs, algo, quantum=q, strict=True)
    n = len(procs)
    for i, (a, b) in enumerate(procs):
        name = r["names"][i]
        ran = sum(e - s for nm, s, e in r["gantt"] if nm == name)
        assert ran == b, (name, ran, b)
        assert r["turn"][i] == r["finish"][i] - a and r["wait"][i] == r["turn"][i] - b
        assert min(s for nm, s, e in r["gantt"] if nm == name) - a == r["resp"][i]
    # slices never overlap and never start before the process arrives
    ends = 0
    for nm, s, e in r["gantt"]:
        assert s >= ends and procs[int(nm[1:]) - 1][0] <= s
        ends = e
    if algo == "RR":
        st = rr_steps(procs, q)
        merged = []
        for s in st:
            if s["run"] is None:
                continue
            if merged and merged[-1][0] == s["run"] and merged[-1][2] == s["start"]:
                merged[-1] = (s["run"], merged[-1][1], s["end"])
            else:
                merged.append((s["run"], s["start"], s["end"]))
        assert merged == r["gantt"], (merged, r["gantt"])
    if algo in ("FCFS", "SJF"):       # non-preemptive: one block per process
        assert len(r["gantt"]) == n
    r["procs"] = procs
    r["algo"] = algo
    r["q"] = q
    return r


def rr_steps(procs, q):
    """event replay of Round Robin with the course's queue rule. steps: dict(start, end, run (None = idle),
    done, arrived [names that arrived during (start, end]], queue [names after the slice], back (preempted name))"""
    names = ["P%d" % (i + 1) for i in range(len(procs))]
    arr = {names[i]: procs[i][0] for i in range(len(procs))}
    rem = {names[i]: procs[i][1] for i in range(len(procs))}
    t = 0
    queue = [n for n in names if arr[n] <= 0]
    admitted = set(queue)
    steps = []
    while any(rem.values()):
        if not queue:
            nxt = min(arr[n] for n in names if n not in admitted)
            new = [n for n in names if arr[n] == nxt]
            queue += new
            admitted |= set(new)
            steps.append(dict(start=t, end=nxt, run=None, done=False, arrived=new, queue=list(queue), back=None))
            t = nxt
            continue
        p = queue.pop(0)
        d = min(q, rem[p])
        s, e = t, t + d
        rem[p] -= d
        new = [n for n in names if n not in admitted and s < arr[n] <= e]
        if rem[p] > 0:
            assert all(arr[n] != e for n in new), f"arrival at the preemption instant {e}: the lesson does not order it"
        queue += new
        admitted |= set(new)
        back = None
        if rem[p] > 0:
            queue.append(p)
            back = p
        steps.append(dict(start=s, end=e, run=p, done=rem[p] == 0, arrived=new, queue=list(queue), back=back))
        t = e
    return steps


def srtf_events(procs, r):
    """for each arrival after time 0 while a process runs: (time, newcomer, its burst, running, its remaining,
    preempt?) replayed from the Gantt chart r['gantt']"""
    names = r["names"]
    out = []
    for i, (a, b) in enumerate(procs):
        if a == 0:
            continue
        at = lambda t: next((nm for nm, s, e in r["gantt"] if s <= t < e), None)
        runner, nxt = at(a - 1), at(a)        # who held the CPU just before the arrival, who holds it just after
        if runner is None or r["finish"][names.index(runner)] == a:
            out.append((a, names[i], b, None, None, nxt == names[i]))
            continue
        j = names.index(runner)
        left = procs[j][1] - sum(min(e, a) - s for nm, s, e in r["gantt"] if nm == runner and s < a)
        out.append((a, names[i], b, runner, left, nxt == names[i]))
        assert (b < left) == (nxt == names[i]), (a, names[i], b, runner, left)
    return out


# ---------------------------------------------------------------- number words / formatting
def num(x):
    """2.5 -> '2.5', 3 -> '3', 16/3 -> '5.33' (two decimals, as the course prints)"""
    x = F(x).limit_denominator(1000)
    if x.denominator == 1:
        return str(x.numerator)
    v = round(float(x), 2)
    return ("%.2f" % v).rstrip("0").rstrip(".")


ONES_F = ["אפס", "אחת", "שתיים", "שלוש", "ארבע", "חמש", "שש", "שבע", "שמונה", "תשע", "עשר", "אחת עשרה",
          "שתים עשרה", "שלוש עשרה", "ארבע עשרה", "חמש עשרה", "שש עשרה", "שבע עשרה", "שמונה עשרה", "תשע עשרה"]
TENS_F = {20: "עשרים", 30: "שלושים", 40: "ארבעים", 50: "חמישים", 60: "שישים", 70: "שבעים", 80: "שמונים", 90: "תשעים"}


def hn(n):
    """an integer 0..99 in Hebrew, feminine counting form (numbers, times): 13 -> 'שלוש עשרה', 21 -> 'עשרים ואחת'"""
    n = int(n)
    assert 0 <= n < 100
    if n < 20:
        return ONES_F[n]
    t, o = n - n % 10, n % 10
    return TENS_F[t] + ("" if o == 0 else " ו" + ONES_F[o])


def hdec(x):
    """a decimal as spoken: 3.5 -> 'שלוש וחצי', 4.25 -> 'ארבע ורבע', 4.75 -> 'ארבע שלושה רבעים'... 5.33 -> 'חמש נקודה
    שלוש שלוש'"""
    x = F(x).limit_denominator(1000)
    i = x.numerator // x.denominator
    f = x - i
    if f == 0:
        return hn(i)
    if f == F(1, 2):
        return hn(i) + " וחצי"
    if f == F(1, 4):
        return hn(i) + " ורבע"
    s = num(x)
    ip, fp = s.split(".")
    return hn(int(ip)) + " נקודה " + " ".join(ONES_F[int(d)] for d in fp)


# ---------------------------------------------------------------- small html helpers
def ltr(s):
    return f'<span class="sc-ltr">{s}</span>'


def chip(name, cls=""):
    return f'<span class="sc-chip {cls}" style="--c:{COL[name]}">{esc(name)}</span>'


def big(id_, tex, hidden=True, cls=""):
    return f'<div id="{id_}" class="sc-big {cls}{" h" if hidden else ""}">${tex}$</div>'


def line(id_, html_, hidden=True, cls=""):
    return f'<div id="{id_}" class="sc-line {cls}{" h" if hidden else ""}">{html_}</div>'


def stack(*parts, gap=22):
    return f'<div class="sc-stack" style="gap:{gap}px">{"".join(parts)}</div>'


# ---------------------------------------------------------------- Gantt chart
def gantt(pfx, r, slices=None, width=1000, unit=None, arrivals=False, finishes=True, hidden=True, top_pad=None,
          bands=()):
    """slices: [(name, start, end)] to draw (default r['gantt']; for Round Robin pass the per-quantum slices from
    rr_slices so two quanta of the same process stay two blocks). Idle gaps are drawn where the CPU has nothing."""
    sl = list(slices if slices is not None else r["gantt"])
    total = max(e for _, _, e in sl)
    x0, x1 = 30, width - 30
    k = unit or (x1 - x0) / total
    st_a = max((row for _, row in _stagger([(a, n) for (a, b), n in zip(r["procs"], r["names"])], lambda t: x0 + t * k)),
               default=0) if arrivals else 0
    st_f = max((row for _, row in _stagger([(f, n) for f, n in zip(r["finish"], r["names"])], lambda t: x0 + t * k)),
               default=0) if finishes else 0
    top = (44 + 26 * st_a if arrivals else 14) if top_pad is None else top_pad
    bh = 84
    yb = top + bh
    h = yb + 50 + (40 + 28 * st_f if finishes else 0) + (34 if bands else 0)
    X = lambda t: x0 + t * k
    o = [f'<svg class="sc-gantt" id="{pfx}" viewBox="0 0 {width} {h}" width="{width}" height="{h}" direction="ltr">']
    o.append(f'<line x1="{X(0)}" y1="{yb}" x2="{X(total)}" y2="{yb}" class="sc-ax"/>'
             f'<line x1="{X(0)}" y1="{top}" x2="{X(0)}" y2="{yb + 10}" class="sc-tk"/>'
             f'<text x="{X(0)}" y="{yb + 40}" class="sc-tt">0</text>')
    # idle gaps
    gaps, t = [], 0
    for nm, s, e in sl:
        if s > t:
            gaps.append((t, s))
        t = max(t, e)
    for j, (s, e) in enumerate(gaps):
        o.append(f'<g id="{pfx}-i{j}" class="{"h" if hidden else ""}">'
                 f'<rect x="{X(s) + 2:.1f}" y="{top}" width="{(e - s) * k - 4:.1f}" height="{bh}" rx="8" class="sc-idle"/>'
                 + (f'<text x="{(X(s) + X(e)) / 2:.1f}" y="{top + bh / 2 + 10}" class="sc-it">סרק</text>'
                    if (e - s) * k >= 70 else "") +
                 f'<line x1="{X(e)}" y1="{top}" x2="{X(e)}" y2="{yb + 10}" class="sc-tk"/>'
                 f'<text x="{X(e):.1f}" y="{yb + 40}" class="sc-tt">{e}</text></g>')
    for i, (nm, s, e) in enumerate(sl):
        w = (e - s) * k
        fs = 30 if w >= 62 else (24 if w >= 44 else 19)
        o.append(f'<g id="{pfx}-s{i}" class="{"h" if hidden else ""}">'
                 f'<rect x="{X(s) + 2:.1f}" y="{top}" width="{w - 4:.1f}" height="{bh}" rx="8" class="sc-blk" '
                 f'style="fill:{COL[nm]}"/>'
                 f'<text x="{(X(s) + X(e)) / 2:.1f}" y="{top + bh / 2 + fs * 0.36:.1f}" class="sc-bn" '
                 f'font-size="{fs}">{nm}</text>'
                 f'<line x1="{X(e)}" y1="{top}" x2="{X(e)}" y2="{yb + 10}" class="sc-tk"/>'
                 f'<text x="{X(e):.1f}" y="{yb + 40}" class="sc-tt">{e}</text></g>'
                 f'<rect id="{pfx}-hl{i}" x="{X(s) - 3:.1f}" y="{top - 5}" width="{w + 6:.1f}" height="{bh + 10}" '
                 f'rx="11" class="sc-hl h"/>')
    if finishes:
        rows = _stagger([(r["finish"][i], nm) for i, nm in enumerate(r["names"])], X)
        for (f, nm), row in rows:
            o.append(f'<text id="{pfx}-f-{nm}" x="{X(f):.1f}" y="{yb + 80 + 28 * row}" class="sc-fin h" '
                     f'style="fill:{COL[nm]}">✓{nm}</text>')
    for b in bands:                   # (key, start, end[, css class]): a bar under the time axis, {pfx}-b-<key>
        key, s, e = b[:3]
        c = b[3] if len(b) > 3 else ("sc-bt" if key == "tt" else "sc-bw")
        y = yb + 54 + (40 + 28 * st_f if finishes else 0)
        o.append(f'<rect id="{pfx}-b-{key}" x="{X(s):.1f}" y="{y}" width="{(e - s) * k:.1f}" height="16" rx="8" '
                 f'class="{c} h"/>')
    if arrivals:
        rows = _stagger([(a, r["names"][i]) for i, (a, b) in enumerate(r["procs"])], X)
        for (a, nm), row in rows:
            o.append(f'<g id="{pfx}-a-{nm}" class="h"><text x="{X(a):.1f}" y="{top - 14 - 26 * row}" class="sc-arr" '
                     f'style="fill:{COL[nm]}">{nm}↓</text></g>')
    o.append("</svg>")
    return "".join(o)


def _stagger(items, X, gap=58):
    """[(t, name)] -> [((t, name), row)]: a label goes one row further when it would touch the previous one"""
    out, last = [], {}
    for t, nm in sorted(items):
        row = 0
        while row in last and X(t) - last[row] < gap:
            row += 1
        last[row] = X(t)
        out.append(((t, nm), row))
    return out


def rr_slices(steps):
    return [(s["run"], s["start"], s["end"]) for s in steps if s["run"] is not None]


# ---------------------------------------------------------------- process table
HEAD = {"name": "תהליך", "arr": "הגעה", "burst": "פרץ", "fin": "סיום", "turn": "סבב", "wait": "המתנה",
        "resp": "תגובה", "first": "ריצה ראשונה", "rem": "נשאר"}


def ptable(pfx, r, cols=("arr", "burst", "fin", "turn", "wait"), shown=("arr", "burst"), extra=None, avg=None,
           hidden_rows=False, cls=""):
    """extra: {(name, col): html} overrides a cell's content (e.g. '13 − 1 = 12'). avg: html of the average line."""
    extra = extra or {}
    val = {}
    for i, nm in enumerate(r["names"]):
        a, b = r["procs"][i]
        val[(nm, "arr")] = a
        val[(nm, "burst")] = b
        val[(nm, "fin")] = r["finish"][i]
        val[(nm, "turn")] = r["turn"][i]
        val[(nm, "wait")] = r["wait"][i]
        val[(nm, "resp")] = r["resp"][i]
        val[(nm, "first")] = r["resp"][i] + a
    th = "".join(f"<th>{HEAD[c]}</th>" for c in ("name",) + tuple(cols))
    trs = []
    for nm in r["names"]:
        tds = [f'<td class="sc-nm"><i id="{pfx}-row-{nm}" class="sc-rowhi h"></i>{chip(nm)}</td>']
        for c in cols:
            v = extra.get((nm, c), val.get((nm, c), ""))
            h = "" if c in shown else " h"
            tds.append(f'<td><span id="{pfx}-{nm}-{c}" class="sc-v{h}">{v}</span></td>')
        rid = f' id="{pfx}-tr-{nm}" class="h"' if hidden_rows else ""
        trs.append(f"<tr{rid}>" + "".join(tds) + "</tr>")
    out = (f'<table id="{pfx}" class="sc-tab {cls}" dir="rtl"><thead><tr>{th}</tr></thead>'
           f'<tbody>{"".join(trs)}</tbody></table>')
    if avg is not None:
        out += f'<div id="{pfx}-avg" class="sc-avg h">{avg}</div>'
    return out


# ---------------------------------------------------------------- Round Robin queue strip
def rrq(pfx, steps, hidden=True):
    """one row per step: [start–end] [who ran ✓ if done] [queue after the slice]. New arrivals are outlined in teal,
    the preempted process (going to the back) in amber."""
    rows = [f'<div class="sc-qh"><span>זמן</span><span>רץ</span><span>התור אחרי הפרוסה</span></div>']
    for i, s in enumerate(steps):
        who = (chip(s["run"]) + (' <b class="sc-done">✓</b>' if s["done"] else "")) if s["run"] else '<span class="sc-idl">סרק</span>'
        q = []
        for n in s["queue"]:
            c = "sc-new" if n in s["arrived"] else ("sc-back" if n == s["back"] else "")
            q.append(chip(n, c))
        qh = " ".join(q) if q else '<span class="sc-empty">ריק</span>'
        rows.append(f'<div id="{pfx}-r{i}" class="sc-qr{" h" if hidden else ""}"><span class="sc-qt">{s["start"]}–{s["end"]}</span>'
                    f'<span class="sc-qw">{who}</span><span class="sc-qq">{qh}</span></div>')
    return f'<div class="sc-q" id="{pfx}">{"".join(rows)}</div>'


# ---------------------------------------------------------------- freshness: never a course/quiz table
def course_tables():
    """every process table of every question of every course level (quiz and boss), as tuples"""
    import loader
    out = set()
    for c0 in loader.load_sources():
        for L in c0["levels"]:
            for q in L["qs"]:
                ch = q.get("check")
                for c in (ch if isinstance(ch, list) else [ch]):
                    if isinstance(c, dict) and "procs" in c:
                        out.add(tuple(map(tuple, c["procs"])))
    return out


def assert_fresh(*sets):
    used = course_tables()
    for s in sets:
        assert tuple(map(tuple, s)) not in used, f"{s} is a course question's table"


# ---------------------------------------------------------------- process states (theory level)
def states_svg(pfx, w=960, h=520):
    """ready / running / waiting boxes with the transitions; every arrow is hidden: {pfx}-e-<key> for key in
    disp (ready->running), pre (running->ready, preemption), io (running->waiting), back (waiting->ready),
    exit (running->done). Boxes {pfx}-b-<ready|run|wait> are visible; {pfx}-hl-<box> highlight frames."""
    B = {"ready": (90, 70, "מוכן"), "run": (610, 70, "רץ"), "wait": (320, 360, "ממתין לקלט/פלט")}
    bw, bh = 260, 96
    W = {"wait": 320}
    o = [f'<svg class="sc-st" id="{pfx}" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
         '<defs>' + "".join(f'<marker id="{pfx}-ah{c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                            f'markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>'
                            for c, col in (("", "#c9cdf0"), ("w", "#fbbf24"))) + '</defs>']
    for k, (x, y, t) in B.items():
        ww = W.get(k, bw)
        o.append(f'<rect x="{x}" y="{y}" width="{ww}" height="{bh}" rx="18" class="sc-sbox"/>'
                 f'<text x="{x + ww / 2}" y="{y + bh / 2 + 12}" class="sc-stt">{t}</text>'
                 f'<rect id="{pfx}-hl-{k}" x="{x - 6}" y="{y - 6}" width="{ww + 12}" height="{bh + 12}" rx="22" '
                 f'class="sc-shl h"/>')
    rx, ry = B["ready"][0] + bw, B["ready"][1]
    ux = B["run"][0]
    E = {
        "disp": (f"M{rx + 6},{ry + 26} L{ux - 8},{ry + 26}", "נבחר", (rx + ux) / 2, ry + 10, ""),
        "pre": (f"M{ux - 6},{ry + bh - 22} L{rx + 8},{ry + bh - 22}", "נשלף", (rx + ux) / 2, ry + bh + 22, "w"),
        "io": (f"M{ux + 70},{ry + bh + 6} L{B['wait'][0] + W['wait'] - 50},{B['wait'][1] - 8}", "בקשת קלט/פלט",
               ux + 170, ry + bh + 140, ""),
        "back": (f"M{B['wait'][0] + 50},{B['wait'][1] - 6} L{B['ready'][0] + bw - 70},{ry + bh + 8}",
                 "קלט/פלט הסתיים", B["ready"][0] + 40, ry + bh + 140, ""),
        "exit": (f"M{ux + bw / 2},{ry - 6} L{ux + bw / 2},{ry - 60}", "סיים", ux + bw / 2 + 60, ry - 34, ""),
    }
    for k, (d, lab, lx, ly, c) in E.items():
        o.append(f'<g id="{pfx}-e-{k}" class="h"><path d="{d}" class="sc-sar{" w" if c else ""}" '
                 f'marker-end="url(#{pfx}-ah{c})"/><text x="{lx}" y="{ly}" class="sc-sl{" w" if c else ""}">{lab}</text></g>')
    o.append("</svg>")
    return "".join(o)


def burst_strip(pfx, parts, unit=58):
    """a process's life as alternating bursts: parts [(kind 'cpu'|'io', length)]; each piece {pfx}-p<i> hidden"""
    cells = []
    for i, (k, n) in enumerate(parts):
        lab = "CPU" if k == "cpu" else "I/O"
        cells.append(f'<div id="{pfx}-p{i}" class="sc-bp {k} h" style="width:{n * unit}px">{lab}</div>')
    return f'<div class="sc-bstrip" id="{pfx}">{"".join(cells)}</div>'
