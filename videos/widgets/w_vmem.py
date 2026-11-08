# -*- coding: utf-8 -*-
"""Widgets for the "vmem" course videos (V01-V07): demand paging and page replacement.

Simulation: every FIFO / LRU / OPT run comes from the course simulator sims.replace(refs, frames, algo, strict=True)
(strict: an OPT tie the course does not define raises). sims.replace keeps the resident pages as a list (FIFO: load
order, LRU: recency order); run() adds the physical frame slots (a page stays in its frame until it is evicted, the
new page takes the victim's frame) and asserts that the slots hold exactly the simulator's pages at every step.
Clock (second chance) has no simulator in sims.py: clock() below, asserted on a hand-checked case at import.

Figures (hidden pieces carry ids the timeline shows):
  rtable()   reference string x frames: header {pfx}-r-<i> (always visible) with a ring {pfx}-rr-<i>; the column body
             {pfx}-c-<i> (frames, F/✓ mark, evicted page, optional order row); a ring on the victim's cell in the
             previous column {pfx}-vk-<i>; a column highlight {pfx}-hl-<i>; fault counter {pfx}-n-<k>.
             RTab.col(i) = the actions that reveal column i and step the counter.
  clock_svg() the frames on a circle with their reference bits and the hand: one full drawing per micro-state
             {pfx}-s-<k>; clock_step(pfx, k) hides state k-1 and shows state k.
  ptable()   V01: a page table (valid bit, frame) next to the RAM frames.
Class names start with vm- (all widget css files load into every video of the app).
"""
import sims

_ALGOS = ("FIFO", "LRU", "OPT")


# ---------------------------------------------------------------- simulation with physical frames
def run(refs, frames, algo):
    """sims.replace + frame slots. Returns dict(faults, hits, steps=[dict(page, fault, victim, slot, slots, mem)])."""
    assert algo in _ALGOS
    r = sims.replace(list(refs), frames, algo, strict=True)
    slots, steps = [None] * frames, []
    for p, kind, mem, victim in r["trace"]:
        slot = None
        if kind == "fault":
            slot = slots.index(None) if victim is None else slots.index(victim)
            assert victim is not None or None in slots
            slots[slot] = p
        assert set(s for s in slots if s is not None) == set(mem), (refs, algo, slots, mem)
        steps.append(dict(page=p, fault=kind == "fault", victim=victim, slot=slot, slots=list(slots), mem=list(mem)))
    assert sum(s["fault"] for s in steps) == r["faults"]
    return dict(faults=r["faults"], hits=r["hits"], steps=steps)


def faults(refs, frames, algo):
    return sims.replace(list(refs), frames, algo, strict=True)["faults"]


def resident(refs, frames, algo):
    """the set of resident pages after each reference (for the stack-property checks)"""
    return [set(s["mem"]) for s in run(refs, frames, algo)["steps"]]


# ---------------------------------------------------------------- Clock (second chance)
def clock(refs, slots, bits, hand):
    """Clock from a full snapshot. slots: page per frame (circle order), bits: reference bit per frame, hand: frame
    index. Rules (the course's): a hit sets the page's bit (the MMU does it) and the hand does not move. A fault
    sweeps: bit 1 -> the OS clears it to 0 and the hand moves on; bit 0 -> victim. The new page takes that frame
    with bit 1 (the instruction restarts and touches it) and the hand moves to the next frame.
    Returns micro-states [dict(kind, slots, bits, hand, at, page, victim)] starting with the snapshot ('start'),
    then 'hit' / 'clear' / 'load' states, plus faults and victims."""
    slots, bits = list(slots), list(bits)
    n = len(slots)
    out = [dict(kind="start", slots=list(slots), bits=list(bits), hand=hand, at=None, page=None, victim=None)]
    nf, victims = 0, []
    for p in refs:
        if p in slots:
            i = slots.index(p)
            bits[i] = 1
            out.append(dict(kind="hit", slots=list(slots), bits=list(bits), hand=hand, at=i, page=p, victim=None))
            continue
        nf += 1
        while bits[hand] == 1:
            bits[hand] = 0
            at = hand
            hand = (hand + 1) % n
            out.append(dict(kind="clear", slots=list(slots), bits=list(bits), hand=hand, at=at, page=p, victim=None))
        v = slots[hand]
        victims.append(v)
        slots[hand], bits[hand] = p, 1
        at = hand
        hand = (hand + 1) % n
        out.append(dict(kind="load", slots=list(slots), bits=list(bits), hand=hand, at=at, page=p, victim=v))
    return dict(states=out, faults=nf, victims=victims)


# hand-checked: frames [A B C D], bits [1 1 0 1], hand at A. Fault on E: A 1->0, B 1->0, C has 0 -> victim C,
# E in C's frame with bit 1, hand at D. Then a hit on A sets A's bit. Fault on F: D 1->0, A 1->0 (it was set again),
# B has 0 -> victim B, hand at C (now E).
_c = clock(["E", "A", "F"], ["A", "B", "C", "D"], [1, 1, 0, 1], 0)
assert _c["victims"] == ["C", "B"] and _c["faults"] == 2
assert [s["kind"] for s in _c["states"]] == ["start", "clear", "clear", "load", "hit", "clear", "clear", "load"]
assert _c["states"][-1]["slots"] == ["A", "F", "E", "D"] and _c["states"][-1]["bits"] == [0, 1, 1, 0]
assert _c["states"][-1]["hand"] == 2
# a full sweep: every bit 1 -> the hand clears all N and comes back to where it started (the O(N) worst case)
_w = clock(["Z"], ["A", "B", "C"], [1, 1, 1], 1)
assert [s["kind"] for s in _w["states"]] == ["start", "clear", "clear", "clear", "load"] and _w["victims"] == ["B"]


# ---------------------------------------------------------------- small html helpers
def ltr(s):
    return f'<span class="vm-ltr">{s}</span>'


def mono(s):
    return f'<span class="vm-mono">{s}</span>'


def refline(refs):
    return " ".join(str(x) for x in refs)


def stack(*parts, gap=22):
    return f'<div class="vm-stack" style="gap:{gap}px">{"".join(parts)}</div>'


def row(id_, html_, hidden=True, cls=""):
    return f'<div id="{id_}" class="vm-row {cls}{" h" if hidden else ""}">{html_}</div>'


def ltrflex(id_, parts, hidden=True, cls=""):
    """pieces laid out left to right, each its own bidi island (a Hebrew word next to digits inside one LTR span
    would be reordered by the bidi algorithm)"""
    sp = "".join(f'<span class="vm-fp">{p}</span>' for p in parts)
    return f'<div id="{id_}" class="vm-flex {cls}{" h" if hidden else ""}">{sp}</div>'


def queue(id_, items, left="ותיק", right="חדש", hidden=True, head=None):
    """a FIFO queue / LRU list drawn left (oldest) to right (newest); head: optional Hebrew label before it"""
    parts = ([head] if head else []) + [left, f'<b class="vm-qb">[ {" ".join(str(x) for x in items)} ]</b>', right]
    return ltrflex(id_, parts, hidden, "q")


def qcode(frames, refs, extra=""):
    return f'<pre class="qcode">frames: {frames}\nreferences: {refline(refs)}{extra}</pre>'


def qans(id_, html_, hidden=True):
    return f'<div id="{id_}" class="qans{" h" if hidden else ""}">{html_}</div>'


# ---------------------------------------------------------------- reference string x frames table
class RTab:
    def __init__(self, pfx, html, sim, algo, refs, frames):
        self.pfx, self.html, self.sim, self.algo, self.refs, self.frames = pfx, html, sim, algo, refs, frames
        self.steps = sim["steps"]
        self.faults = sim["faults"]

    def nfaults_upto(self, i):
        return sum(s["fault"] for s in self.steps[:i + 1])

    def col(self, i, *more):
        """reveal column i (and the given extra columns), stepping the fault counter"""
        acts = []
        for j in (i,) + more:
            acts += [("show", f"{self.pfx}-c-{j}")]
            if self.steps[j]["fault"]:
                k = self.nfaults_upto(j)
                acts += [("hide", f"{self.pfx}-n-{k - 1}"), ("show", f"{self.pfx}-n-{k}")]
        return acts

    def cols(self, a, b):
        """reveal columns a..b inclusive"""
        return self.col(a, *range(a + 1, b + 1))


def rtable(pfx, refs, frames, algo, cw=78, order=False, counter=True, label=None, hidden_body=True, out=True, sm=False):
    """the table for one algorithm. cw: column width (px). order: add the simulator's list (FIFO: load order,
    LRU: recency order, oldest on the left). label: a caption over the table (e.g. 'FIFO, 3 מסגרות')."""
    sim = run(refs, frames, algo)
    steps = sim["steps"]
    lab = ['<div class="vm-lab vm-lh">הפניה</div>']
    lab += [f'<div class="vm-lab">מסגרת {k + 1}</div>' for k in range(frames)]
    lab += ['<div class="vm-lab vm-lm">שגיאה</div>'] + (['<div class="vm-lab vm-lo">יוצא</div>'] if out else [])
    if order:
        lab += [f'<div class="vm-lab vm-lq">{"סדר טעינה" if algo == "FIFO" else "סדר שימוש"}</div>']
    cols = [f'<div class="vm-labs">{"".join(lab)}</div>']
    for i, s in enumerate(steps):
        cells = []
        for k, pg in enumerate(s["slots"]):
            cls = "vm-cell" + (" new" if s["fault"] and k == s["slot"] else "") + (" emp" if pg is None else "")
            ring = ""
            nxt = steps[i + 1] if i + 1 < len(steps) else None
            if nxt and nxt["victim"] is not None and nxt["slot"] == k:
                ring = f'<i id="{pfx}-vk-{i + 1}" class="vm-vk h"></i>'
            hitring = '' if s["fault"] or pg != s["page"] else ' hit'
            cells.append(f'<div class="{cls}{hitring}">{"" if pg is None else pg}{ring}</div>')
        mark = '<div class="vm-mark f">F</div>' if s["fault"] else '<div class="vm-mark ok">✓</div>'
        outc = f'<div class="vm-out">{s["victim"] if s["victim"] is not None else ""}</div>' if out else ""
        ordr = ""
        if order:
            ordr = f'<div class="vm-ord">{" ".join(str(x) for x in s["mem"])}</div>'
        body = (f'<div id="{pfx}-c-{i}" class="vm-body{" h" if hidden_body else ""}">'
                f'{"".join(cells)}{mark}{outc}{ordr}</div>')
        cols.append(f'<div class="vm-col" style="width:{cw}px">'
                    f'<div class="vm-ref">{s["page"]}<i id="{pfx}-rr-{i}" class="vm-ring h"></i></div>{body}'
                    f'<i id="{pfx}-hl-{i}" class="vm-colhl h"></i></div>')
    cnt = ""
    if counter:
        nums = "".join(f'<b id="{pfx}-n-{k}" class="vm-num{"" if k == 0 else " h"}">{k}</b>'
                       for k in range(sim["faults"] + 1))
        cnt = f'<div class="vm-cnt">שגיאות דף: <span class="vm-nums">{nums}</span></div>'
    tab = f'<div class="vm-tab">{"".join(cols)}</div>'
    if label:
        body = f'<div class="vm-head"><div class="vm-cap">{label}</div>{cnt}</div>{tab}'
    else:
        body = tab + cnt
    html = f'<div class="vm-tabw{" sm" if sm else ""}" id="{pfx}">{body}</div>'
    return RTab(pfx, html, sim, algo, list(refs), frames)


# ---------------------------------------------------------------- Clock figure
def clock_svg(pfx, states, size=560, names=None, hidden_first=False):
    """one drawing per micro-state; frames on a circle (frame 0 at the top, clockwise), each a box with the page and
    its bit, the hand from the centre to the frame it points at; the frame just touched is outlined
    (clear: amber, load: green, hit: blue)."""
    import math
    n = len(states[0]["slots"])
    c = size / 2
    rad = size / 2 - 92
    bw, bh = 150, 112
    groups = []
    for k, s in enumerate(states):
        g = [f'<g id="{pfx}-s-{k}" class="{"h" if (k or hidden_first) else ""}">']
        for i in range(n):
            a = -math.pi / 2 + 2 * math.pi * i / n
            x, y = c + rad * math.cos(a), c + rad * math.sin(a)
            cls = "vm-cf"
            if s["at"] == i:
                cls += {"clear": " clr", "load": " lod", "hit": " hit"}.get(s["kind"], "")
            g.append(f'<rect x="{x - bw / 2:.1f}" y="{y - bh / 2:.1f}" width="{bw}" height="{bh}" rx="16" class="{cls}"/>')
            g.append(f'<text x="{x:.1f}" y="{y - 6:.1f}" class="vm-cpg">{s["slots"][i]}</text>')
            bit = s["bits"][i]
            g.append(f'<text x="{x:.1f}" y="{y + 38:.1f}" class="vm-cbit b{bit}">R={bit}</text>')
            if names:
                g.append(f'<text x="{x:.1f}" y="{y - bh / 2 - 12:.1f}" class="vm-cnm">{names[i]}</text>')
        a = -math.pi / 2 + 2 * math.pi * s["hand"] / n
        hx, hy = c + (rad - bh / 2 - 26) * math.cos(a), c + (rad - bh / 2 - 26) * math.sin(a)
        g.append(f'<line x1="{c}" y1="{c}" x2="{hx:.1f}" y2="{hy:.1f}" class="vm-hand" marker-end="url(#{pfx}-ah)"/>')
        g.append(f'<circle cx="{c}" cy="{c}" r="12" class="vm-hub"/>')
        g.append("</g>")
        groups.append("".join(g))
    return (f'<svg class="vm-clk" viewBox="0 0 {size} {size}" width="{size}" height="{size}" direction="ltr">'
            f'<defs><marker id="{pfx}-ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" '
            f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#fbbf24"/></marker></defs>{"".join(groups)}</svg>')


def clock_step(pfx, k):
    return [("hide", f"{pfx}-s-{k - 1}"), ("show", f"{pfx}-s-{k}")]


# ---------------------------------------------------------------- V01: page table + RAM
def ptable(pfx, npages, nframes, rows_hidden=False):
    """a page table (page, valid bit, frame) and the RAM frames. Ids: {pfx}-v0-<p> / {pfx}-v1-<p> (the bit as 0 / 1),
    {pfx}-f-<p>-<k> (frame number k in page p's row), {pfx}-hl-<p> row highlight, {pfx}-ram-<k>-<p> (page p in
    frame k), {pfx}-fl-<k> frame highlight."""
    rows = []
    for p in range(npages):
        fr = "".join(f'<span id="{pfx}-f-{p}-{k}" class="vm-pf h">{k}</span>' for k in range(nframes))
        rows.append(f'<div class="vm-ptr"><i id="{pfx}-hl-{p}" class="vm-prh h"></i><span class="vm-pc">{p}</span>'
                    f'<span class="vm-pc vm-pv"><b id="{pfx}-v0-{p}" class="vm-v0">0</b>'
                    f'<b id="{pfx}-v1-{p}" class="vm-v1 h">1</b></span><span class="vm-pc vm-pfr">{fr}</span></div>')
    pt = ('<div class="vm-pt"><div class="vm-ptc">טבלת הדפים</div><div class="vm-ptr vm-pth"><span class="vm-pc">דף</span>'
          '<span class="vm-pc">valid</span><span class="vm-pc">מסגרת</span></div>' + "".join(rows) + "</div>")
    ram = []
    for k in range(nframes):
        pages = "".join(f'<span id="{pfx}-ram-{k}-{p}" class="vm-rp h">דף {p}</span>' for p in range(npages))
        ram.append(f'<div class="vm-rf"><i id="{pfx}-fl-{k}" class="vm-rfh h"></i><span class="vm-rk">{k}</span>'
                   f'<span class="vm-rslot">{pages}</span></div>')
    rm = '<div class="vm-ram"><div class="vm-ptc">RAM</div>' + "".join(ram) + "</div>"
    return f'<div class="vm-ptw" id="{pfx}">{pt}{rm}</div>'
