# -*- coding: utf-8 -*-
"""Widgets for the "sync" course videos (Y01-Y07): small simulators of the course's synchronization rules, asserted
against src/courses/sims.py where it has one, and the HTML/SVG figures drawn from what they return.

Simulators
  sem_steps(init, ops)      one semaphore, the course model (sims.semaphore): wait -1, negative -> the caller joins the
                            FIFO queue; signal +1, still <= 0 -> the head of the queue wakes. Every step is replayed and
                            the end state + log are asserted equal to sims.semaphore.
  Sems                      several named semaphores (same model) with a blocked set: a blocked process may not act
                            until a signal wakes it. Each semaphore's op string is re-run through sims.semaphore.
  interleave(progs, order)  two threads of load / add / store on shared variables, run in a given order.
  deadlock_path(procs)      the semantics of sims.can_deadlock (take locks in order, release all at the end), but
                            returns the shortest interleaving into a stuck state, who holds what and who waits for
                            what; asserted to agree with sims.can_deadlock.
  linux_semop(vals, ops)    one Linux semop call: all-or-nothing; sem_op < 0 needs value >= |sem_op|, else the caller
                            sleeps and nothing changes; sem_op > 0 adds.
  tas_run(sched)            a TestAndSet spin-lock, one action per turn.
  bakery_order(tickets)     the order of entry: by (ticket, PID).
Figures (hidden pieces carry ids the timeline shows): table(), sem_table(), il_view() + il_do(), graph() (processes
as circles, resources as squares, hold / wait arrows, cycle overlay). Classes start with sy-.
"""
from collections import deque
from html import escape as esc
import math

import sims


# ================================================================ one semaphore (course model)
def sem_steps(init, ops):
    """rows: dict(who, op 'P'|'V', value after, queue after, ev ('pass'|'block'|'wake'|'sig'), woken)"""
    ref = sims.semaphore(init, ops)
    v, q, rows, log = init, [], [], []
    for tok in ops.split():
        op, who = tok.split(":")
        woken = None
        if op == "P":
            v -= 1
            if v < 0:
                q.append(who)
                ev = "block"
                log.append(f"{who} blocks")
            else:
                ev = "pass"
                log.append(f"{who} passes")
        else:
            v += 1
            if v <= 0 and q:
                woken = q.pop(0)
                ev = "wake"
                log.append(f"{who} wakes {woken}")
            else:
                ev = "sig"
                log.append(f"{who} signals")
        rows.append(dict(who=who, op=op, value=v, queue=list(q), ev=ev, woken=woken))
    assert v == ref["value"] and q == ref["queue"] and log == ref["log"], (ops, ref)
    return rows


EV_HE = {"pass": "עובר", "block": "נחסם, נכנס לתור", "sig": "הערך עולה"}


def ltr(s, cls=""):
    return f'<span class="sy-ltr {cls}">{s}</span>'


def mono(s):
    return f'<span class="sy-mono">{esc(s)}</span>'


def val(v):
    """a semaphore value; negative in red"""
    return f'<span class="sy-v{" neg" if v < 0 else ""}">{ltr(str(v))}</span>'


def qhtml(q):
    return ltr(" ".join(q)) if q else '<span class="sy-mut">ריק</span>'


def table(id_, head, rows, ids=None, hidden=False, cls=""):
    """an RTL table; rows of html cells; ids: an id per row (those rows start hidden)"""
    th = "".join(f"<th>{h}</th>" for h in head)
    trs = []
    for i, r in enumerate(rows):
        rid = f' id="{ids[i]}" class="h"' if ids and ids[i] else ""
        trs.append(f"<tr{rid}>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    return (f'<table id="{id_}" class="sy-tab {cls}{" h" if hidden else ""}"><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(trs)}</tbody></table>')


def sem_table(pfx, init, ops, cls=""):
    """the trace of one semaphore: row 0 = the initial value (shown), rows {pfx}-r1.. hidden"""
    rows = sem_steps(init, ops)
    body = [["", "", '<span class="sy-mut">התחלה</span>', val(init), qhtml([]), ""]]
    for i, r in enumerate(rows, 1):
        opn = mono("wait" if r["op"] == "P" else "signal")
        ev = f"מעיר את {ltr(r['woken'])}" if r["ev"] == "wake" else EV_HE[r["ev"]]
        body.append([str(i), ltr(r["who"]), opn, val(r["value"]), qhtml(r["queue"]), ev])
    ids = [None] + [f"{pfx}-r{i}" for i in range(1, len(rows) + 1)]
    return table(pfx, ["#", "מי", "פעולה", "ערך", "תור", "מה קרה"], body, ids=ids, cls=cls), rows


# ================================================================ several semaphores with blocking
class Sems:
    def __init__(self, **init):
        self.init = dict(init)
        self.v = dict(init)
        self.q = {k: [] for k in init}
        self.blocked = set()
        self.ops = {k: [] for k in init}

    def P(self, who, s):
        assert who not in self.blocked, f"{who} is asleep and cannot act"
        self.ops[s].append(("P", who))
        self.v[s] -= 1
        if self.v[s] < 0:
            self.q[s].append(who)
            self.blocked.add(who)
            return "block"
        return "pass"

    def V(self, who, s):
        assert who not in self.blocked, f"{who} is asleep and cannot act"
        self.ops[s].append(("V", who))
        self.v[s] += 1
        if self.v[s] <= 0 and self.q[s]:
            w = self.q[s].pop(0)
            self.blocked.discard(w)
            return w
        return None

    def check(self):
        tok = {}                                     # names may hold spaces: sims.semaphore gets w0, w1, ...
        for k in self.init:
            ops = " ".join(f"{op}:w{tok.setdefault(who, len(tok))}" for op, who in self.ops[k])
            r = sims.semaphore(self.init[k], ops)
            assert r["value"] == self.v[k] and r["queue"] == [f"w{tok[x]}" for x in self.q[k]], (k, r, self.v[k])


def pc_run(n, script, mutex_first=False):
    """bounded buffer of n slots. script: [(who, 'put'|'take'|'resume')]. A process that blocks keeps the rest of its
    code for a later 'resume' (only after a signal woke it). Producer: wait(empty) wait(mutex) put signal(mutex)
    signal(full); mutex_first swaps its two waits (the deadlock trap). Consumer: wait(full) wait(mutex) take
    signal(mutex) signal(empty). Returns rows dict(who, kind, empty, full, mutex, items, blocked, woke) and Sems."""
    S = Sems(empty=n, full=0, mutex=1)
    items, pend, rows = 0, {}, []

    def prog(who, kind):
        if kind == "put":
            w1, w2 = (("mutex", "empty") if mutex_first else ("empty", "mutex"))
            return [("P", w1), ("P", w2), ("put",), ("V", "mutex"), ("V", "full")]
        return [("P", "full"), ("P", "mutex"), ("take",), ("V", "mutex"), ("V", "empty")]

    for who, kind in script:
        code = pend.pop(who) if kind == "resume" else prog(who, kind)
        woke = []
        while code:
            ins = code.pop(0)
            if ins[0] == "P":
                if S.P(who, ins[1]) == "block":
                    pend[who] = code
                    break
            elif ins[0] == "V":
                w = S.V(who, ins[1])
                if w:
                    woke.append(w)
            elif ins[0] == "put":
                items += 1
                assert items <= n
            else:
                items -= 1
                assert items >= 0
        rows.append(dict(who=who, kind=kind, empty=S.v["empty"], full=S.v["full"], mutex=S.v["mutex"], items=items,
                         blocked=sorted(S.blocked), woke=woke, waiting_on={w: k for k in S.q for w in S.q[k]}))
    S.check()
    return rows, S


def rw_run(script):
    """the classroom readers-writers (readers' preference): mutex=1, wrt=1, readcount.
    reader enter: wait(mutex) rc++ [rc==1: wait(wrt)] signal(mutex); leave: wait(mutex) rc-- [rc==0: signal(wrt)]
    signal(mutex). writer: wait(wrt) ... signal(wrt). script: [(who, 'in'|'out'|'win'|'wout')]. A writer that blocks
    is inside once a signal wakes it. Returns rows dict(who, kind, rc, wrt, inside(list), blocked)."""
    S = Sems(mutex=1, wrt=1)
    rc, inside, rows = 0, [], []
    for who, kind in script:
        woke = None
        if kind == "in":
            assert S.P(who, "mutex") == "pass"
            rc += 1
            if rc == 1:
                assert S.P(who, "wrt") == "pass", "a reader blocking on wrt is not used here"
            S.V(who, "mutex")
            inside.append(who)
        elif kind == "out":
            assert S.P(who, "mutex") == "pass"
            rc -= 1
            inside.remove(who)
            if rc == 0:
                woke = S.V(who, "wrt")
                if woke:
                    inside.append(woke)
            S.V(who, "mutex")
        elif kind == "win":
            if S.P(who, "wrt") == "pass":
                inside.append(who)
        else:
            inside.remove(who)
            S.V(who, "wrt")
        rows.append(dict(who=who, kind=kind, rc=rc, wrt=S.v["wrt"], inside=list(inside), blocked=sorted(S.blocked),
                         woke=woke))
    S.check()
    return rows


# ================================================================ two threads interleaved
def interleave(progs, order, shared):
    """progs: {thread: [ins]} with ins ('ld', reg, var) | ('add', reg, k) | ('st', var, reg); order: thread per step.
    Returns states [(shared dict, {thread: {reg: value}}, (thread, line index) or None)], states[0] = start."""
    sh, regs, pc = dict(shared), {t: {} for t in progs}, {t: 0 for t in progs}
    out = [(dict(sh), {t: dict(r) for t, r in regs.items()}, None)]
    for t in order:
        ins = progs[t][pc[t]]
        if ins[0] == "ld":
            regs[t][ins[1]] = sh[ins[2]]
        elif ins[0] == "add":
            regs[t][ins[1]] = regs[t][ins[1]] + ins[2]
        elif ins[0] == "st":
            sh[ins[1]] = regs[t][ins[2]]
        else:
            raise ValueError(ins)
        out.append((dict(sh), {u: dict(r) for u, r in regs.items()}, (t, pc[t])))
        pc[t] += 1
    return out


def ins_text(ins):
    if ins[0] == "ld":
        return f"{ins[1]} = {ins[2]};"
    if ins[0] == "add":
        return f"{ins[1]} = {ins[1]} + {ins[2]};"
    return f"{ins[1]} = {ins[2]};"


# hand-checked: count = 5, two increments; serial order gives 7, the order T1,T2,T1,T2,T1,T2 loses one (6)
_INC = {"T1": [("ld", "r1", "count"), ("add", "r1", 1), ("st", "count", "r1")],
        "T2": [("ld", "r2", "count"), ("add", "r2", 1), ("st", "count", "r2")]}
assert interleave(_INC, ["T1"] * 3 + ["T2"] * 3, {"count": 5})[-1][0]["count"] == 7
assert interleave(_INC, ["T1", "T2", "T1", "T2", "T1", "T2"], {"count": 5})[-1][0]["count"] == 6


def _layers(pfx, key, values, cls=""):
    """one value per step at the same spot: {pfx}-{key}{k}; k=0 shown"""
    sp = "".join(f'<span id="{pfx}-{key}{k}" class="sy-ly{"" if k == 0 else " h"}">{v}</span>'
                 for k, v in enumerate(values))
    return f'<span class="sy-lay {cls}">{sp}</span>'


def il_view(pfx, progs, order, shared, var="count", titles=None):
    """two code columns (T1 left, T2 right, LTR) and the shared variable between them. Step k (1..n) highlights the
    executed line ({pfx}-h{k}) and updates the register / variable layers. Returns (html, states)."""
    states = interleave(progs, order, shared)
    n = len(order)
    names = list(progs)
    titles = titles or {t: t for t in names}
    cols = {}
    for t in names:
        lines = []
        for li, ins in enumerate(progs[t]):
            hls = "".join(f'<span id="{pfx}-h{k}" class="sy-hl h"></span>' for k in range(1, n + 1)
                          if states[k][2] == (t, li))
            lines.append(f'<div class="sy-ln">{hls}<span class="sy-lt">{esc(ins_text(ins))}</span></div>')
        reg = next(i[1] for i in progs[t] if i[0] == "ld")
        rv = [str(s[1][t].get(reg, "?")) for s in states]
        cols[t] = (f'<div class="sy-col"><div class="sy-ct">{titles[t]}</div><div class="sy-code">{"".join(lines)}</div>'
                   f'<div class="sy-reg"><span class="sy-mono">{reg} =</span> {_layers(pfx, "r" + t, rv)}</div></div>')
    vv = [str(s[0][var]) for s in states]
    mid = (f'<div class="sy-shared"><div class="sy-sn sy-mono">{var}</div>'
           f'<div class="sy-sv">{_layers(pfx, "v", vv)}</div><div class="sy-sl">משותף</div></div>')
    html = f'<div class="sy-il" id="{pfx}">{cols[names[0]]}{mid}{cols[names[1]]}</div>'
    return html, states


def il_do(pfx, progs, k):
    """the show/hide actions of step k (1-based) of an il_view"""
    acts = [("show", f"{pfx}-h{k}"), ("show", f"{pfx}-v{k}"), ("hide", f"{pfx}-v{k - 1}")]
    if k > 1:
        acts.append(("hide", f"{pfx}-h{k - 1}"))
    for t in progs:
        acts += [("show", f"{pfx}-r{t}{k}"), ("hide", f"{pfx}-r{t}{k - 1}")]
    return acts


def il_clear(pfx, k):
    return [("hide", f"{pfx}-h{k}")]


# ================================================================ deadlock search
def deadlock_path(procs):
    """BFS over interleavings with sims.can_deadlock's rules; None if no stuck state, else dict(path=[(proc, lock)],
    held={lock: proc}, waits={proc: lock}, cycle=[proc, lock, proc, lock, ...]) for the shortest path."""
    n = len(procs)
    start = (tuple([0] * n), frozenset())
    par = {start: None}
    dq = deque([start])
    found = None
    while dq:
        st = dq.popleft()
        pcs, held = st
        if all(pcs[i] == len(procs[i]) for i in range(n)):
            continue
        holders = {lock: who for lock, who in held}
        moved = False
        for i in range(n):
            if pcs[i] == len(procs[i]):
                continue
            lock = procs[i][pcs[i]]
            if lock in holders and holders[lock] != i:
                continue
            moved = True
            npcs = list(pcs)
            npcs[i] += 1
            nheld = set(held) | {(lock, i)}
            if npcs[i] == len(procs[i]):
                nheld = {h for h in nheld if h[1] != i}
            ns = (tuple(npcs), frozenset(nheld))
            if ns not in par:
                par[ns] = (st, (i, lock))
                dq.append(ns)
        if not moved:
            found = st
            break
    assert (found is not None) == sims.can_deadlock(procs), procs
    if found is None:
        return None
    path, s = [], found
    while par[s] is not None:
        s, mv = par[s]
        path.append(mv)
    path.reverse()
    pcs, held = found
    hmap = {lock: who for lock, who in held}
    waits = {i: procs[i][pcs[i]] for i in range(n) if pcs[i] < len(procs[i])}
    # follow wait -> holder until a process repeats: that is the cycle
    i, seen, chain = next(iter(waits)), [], []
    while i not in seen:
        seen.append(i)
        chain += [i, waits[i]]
        i = hmap[waits[i]]
    k = chain.index(i)
    return dict(path=path, held=hmap, waits=waits, cycle=chain[k:])


COFFMAN = [("הדדיות", "משאב מוחזק בידי אחד בלבד"),
           ("החזק והמתן", "מחזיקים משאב ומחכים לעוד אחד"),
           ("אין הפקעה", "אי אפשר לקחת משאב בכוח"),
           ("המתנה מעגלית", "מעגל של ממתינים")]


# ================================================================ Linux semop (all or nothing)
def linux_semop(vals, ops):
    """vals: list of semaphore values; ops: [(sem_num, sem_op)] of ONE call. Returns (new values, 'ok'|'sleep').
    The Linux rule: sem_op < 0 needs value >= |sem_op|; sem_op == 0 needs value == 0; one failing op = the whole
    call sleeps and nothing is applied."""
    new = list(vals)
    for num, op in ops:
        if op < 0 and new[num] < -op:
            return list(vals), "sleep"
        if op == 0 and new[num] != 0:
            return list(vals), "sleep"
        new[num] += op
    return new, "ok"


assert linux_semop([1, 0], [(0, -1), (1, -1)]) == ([1, 0], "sleep")       # neither is taken
assert linux_semop([1, 1], [(0, -1), (1, -1)]) == ([0, 0], "ok")
assert linux_semop([2], [(0, -3)]) == ([2], "sleep")


# ================================================================ TestAndSet spin-lock
def tas_run(sched, threads):
    """one action per turn: a spinning thread runs TestAndSet once (enters if the old value was false); a thread in
    the critical section leaves and releases (lock = false) and wants in again at once. Rows: dict(t, act, old, lock,
    res, inside) and the entry count per thread."""
    lock, state, rows, ent = False, {t: "spin" for t in threads}, [], {t: 0 for t in threads}
    for t in sched:
        if state[t] == "spin":
            old, lock = lock, True
            if not old:
                state[t] = "cs"
                ent[t] += 1
                res = "in"
            else:
                res = "spin"
            rows.append(dict(t=t, act="tas", old=old, lock=lock, res=res))
        else:
            lock = False
            state[t] = "spin"
            rows.append(dict(t=t, act="rel", old=None, lock=lock, res="out"))
        assert sum(1 for s in state.values() if s == "cs") <= 1          # mutual exclusion holds
    return rows, ent


def bakery_order(tickets):
    """tickets {pid: ticket} -> PIDs in entry order: the smaller (ticket, pid) first"""
    return [p for t, p in sorted((t, p) for p, t in tickets.items())]


# ================================================================ resource graph (SVG)
def ring(names, cx, cy, r, start=-90):
    """positions on a circle, clockwise from `start` degrees"""
    out = {}
    for i, nm in enumerate(names):
        a = math.radians(start + 360 * i / len(names))
        out[nm] = (cx + r * math.cos(a), cy + r * math.sin(a))
    return out


def graph(pfx, pos, kinds, edges, w=900, h=640, labels=None, cycle=(), node_ids=False):
    """pos {name: (x, y)}, kinds {name: 'p'|'r'}; edges [(key, src, dst, 'hold'|'wait')] each hidden as {pfx}-e-<key>;
    cycle: keys of the edges re-drawn red in one hidden group {pfx}-cy. node_ids: nodes hidden as {pfx}-n-<name>."""
    labels = labels or {}
    R, S = 50, 46
    o = [f'<svg class="sy-g" id="{pfx}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" direction="ltr">',
         '<defs>' + "".join(f'<marker id="{pfx}-ah-{c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{mw}" '
                            f'markerHeight="{mw}" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>'
                            for c, col, mw in (("hold", "#2dd4bf", 5), ("wait", "#fbbf24", 5), ("cy", "#fb7185", 3.6)))
         + '</defs>']

    def seg(a, b):
        (x0, y0), (x1, y1) = pos[a], pos[b]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        ra = R + 4 if kinds[a] == "p" else S * 0.8 + 4
        rb = R + 10 if kinds[b] == "p" else S * 0.8 + 12
        return x0 + ux * ra, y0 + uy * ra, x1 - ux * rb, y1 - uy * rb

    for key, a, b, kind in edges:
        x0, y0, x1, y1 = seg(a, b)
        o.append(f'<line id="{pfx}-e-{key}" class="sy-e {kind} h" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" '
                 f'y2="{y1:.1f}" marker-end="url(#{pfx}-ah-{kind})"/>')
    if cycle:
        o.append(f'<g id="{pfx}-cy" class="h">')
        for key, a, b, kind in edges:
            if key in cycle:
                x0, y0, x1, y1 = seg(a, b)
                o.append(f'<line class="sy-e cy" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                         f'marker-end="url(#{pfx}-ah-cy)"/>')
        o.append('</g>')
    for nm, (x, y) in pos.items():
        lab = esc(labels.get(nm, nm))
        nid = f' id="{pfx}-n-{nm}" class="h"' if node_ids else ""
        if kinds[nm] == "p":
            o.append(f'<g{nid}><circle cx="{x:.1f}" cy="{y:.1f}" r="{R}" class="sy-np"/>'
                     f'<text x="{x:.1f}" y="{y + 12:.1f}" class="sy-nl">{lab}</text></g>')
        else:
            o.append(f'<g{nid}><rect x="{x - S:.1f}" y="{y - S * 0.8:.1f}" width="{2 * S}" height="{1.6 * S}" rx="10" '
                     f'class="sy-nr"/><text x="{x:.1f}" y="{y + 11:.1f}" class="sy-nl r">{lab}</text></g>')
    o.append("</svg>")
    return "".join(o)


def legend():
    return ('<div class="sy-leg"><span><i class="sy-li hold"></i>מחזיק</span>'
            '<span><i class="sy-li wait"></i>ממתין ל־</span></div>')
