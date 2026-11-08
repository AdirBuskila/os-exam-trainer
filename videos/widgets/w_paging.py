# -*- coding: utf-8 -*-
"""Widgets for the "paging" course videos (P01-P07): address splits, page tables, translation, the TLB path, a
multilevel walk and the CPU/RAM pieces. Every number a figure shows is computed here and checked against the
course simulators (src/courses/sims.py: split_address, translate, eat). Class names start with pg- (all widget css
files load into every video of the app). Figures are LTR; fonts only "Segoe UI" / Consolas.
"""
import html as _html
import math
import sims

esc = lambda s: _html.escape(str(s), quote=True)


# ---------------------------------------------------------------- arithmetic (checked against sims)
def log2(n):
    k = int(round(math.log2(n)))
    assert 2 ** k == n, n
    return k


def split(vaddr, page_size):
    """(page, offset): integer division and remainder, and the same thing as a cut of the bits"""
    p, o = sims.split_address(vaddr, page_size)
    k = log2(page_size)
    assert p == vaddr >> k and o == vaddr & (page_size - 1)
    return p, o


def translate(vaddr, page_size, table):
    """physical address or 'fault' (sims.translate), cross-checked as frame bits glued to the offset bits"""
    r = sims.translate(vaddr, page_size, table)
    p, o = split(vaddr, page_size)
    if table.get(p) is None:
        assert r == "fault"
    else:
        assert r == (table[p] << log2(page_size)) | o == table[p] * page_size + o
    return r


def eat(hit, mem, levels, tlb=0):
    """effective access time (sims.eat), cross-checked by hand: hit = tlb + mem, miss = tlb + (levels + 1) mem"""
    e = sims.eat(hit, mem, levels, tlb)
    h_cost, m_cost = tlb + mem, tlb + (levels + 1) * mem
    assert abs(e - (hit * h_cost + (1 - hit) * m_cost)) < 1e-9
    return e, h_cost, m_cost


def num(x):
    return sims.fmt_num(x)


def bits(v, n):
    assert 0 <= v < 2 ** n, (v, n)
    return format(v, f"0{n}b")


# ---------------------------------------------------------------- small html helpers
def ltr(s):
    return f'<span class="pg-ltr">{s}</span>'


def mono(s):
    return f'<span class="pg-mono">{esc(s)}</span>'


def row(id_, html_, hidden=True, cls=""):
    return f'<div id="{id_}" class="pg-row {cls}{" h" if hidden else ""}">{html_}</div>'


def big(id_, tex, hidden=True, cls=""):
    return f'<div id="{id_}" class="pg-big {cls}{" h" if hidden else ""}">${tex}$</div>'


def stack(*parts, gap=22):
    return f'<div class="pg-stack" style="gap:{gap}px">{"".join(parts)}</div>'


def table(id_, head, rows, hidden=True, ids=None, cls=""):
    """a small RTL table of html cells; ids: an id per row (those rows start hidden)"""
    th = "".join(f"<th>{h}</th>" for h in head)
    trs = []
    for i, r in enumerate(rows):
        rid = f' id="{ids[i]}" class="h"' if ids and ids[i] else ""
        trs.append(f"<tr{rid}>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    return (f'<table id="{id_}" class="pg-tab {cls}{" h" if hidden else ""}"><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(trs)}</tbody></table>')


def qans(id_, html_):
    """the official answer box of a short-answer exam question (hidden until shown)"""
    return f'<div id="{id_}" class="qans h"><span class="k">תשובה:</span> {html_}</div>'


# ---------------------------------------------------------------- bit strip split into fields
FIELD = {"page": "#2dd4bf", "off": "#fbbf24", "frame": "#c084fc", "outer": "#38bdf8", "inner": "#fb7185",
         "plain": "#9aa0cf"}


def strip(pfx, value, fields, cw=None, hidden=False, vals=True, tint_hidden=True, caption=None, maxw=1000, digits=True):
    """the bits of `value`, MSB first, cut into fields [(n_bits, label, kind)] (kind: page/off/frame/outer/inner).
    Ids: {pfx}-t<j> tint of field j and {pfx}-l<j> its label + bit count (hidden when tint_hidden),
    {pfx}-v<j> the field's decimal value (hidden), {pfx}-cap a caption over the strip.
    Returns (svg, [decimal value of each field])."""
    n = sum(f[0] for f in fields)
    b = bits(value, n)
    G = 22
    cw = cw or min(56, (maxw - 20 - G * (len(fields) - 1)) // n)
    xs, x, starts = [], 10, []
    for j, (k, _, _) in enumerate(fields):
        starts.append(x)
        for i in range(k):
            xs.append(x + i * cw)
        x += k * cw + G
    w = x - G + 10
    yc, hc = 44 if caption else 10, 58
    h = yc + hc + (128 if vals else 84)
    out_vals, pos = [], 0
    o = [f'<svg class="pg-strip{" h" if hidden else ""}" id="{pfx}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
         f'direction="ltr">']
    if caption:
        o.append(f'<text id="{pfx}-cap" x="{w / 2:.1f}" y="30" class="pg-cap">{esc(caption)}</text>')
    th = " h" if tint_hidden else ""
    for j, (k, lab, kind) in enumerate(fields):
        x0, x1 = starts[j], starts[j] + k * cw
        col = FIELD[kind]
        o.append(f'<rect id="{pfx}-t{j}" x="{x0 - 3}" y="{yc - 4}" width="{x1 - x0 + 4}" height="{hc + 8}" rx="8" '
                 f'fill="{col}" fill-opacity=".30" stroke="{col}" stroke-width="3" class="pg-tint{th}"/>')
        out_vals.append(int(b[pos:pos + k], 2))
        pos += k
    for i, c in enumerate(b):
        o.append(f'<rect x="{xs[i]}" y="{yc}" width="{cw - 2}" height="{hc}" rx="4" class="pg-cell"/>'
                 f'<text x="{xs[i] + (cw - 2) / 2:.1f}" y="{yc + 40}" class="pg-bit" '
                 f'style="font-size:{min(30, cw - 4)}px">{c if digits else ""}</text>')
    for j, (k, lab, kind) in enumerate(fields):
        x0, x1 = starts[j], starts[j] + k * cw
        cx = (x0 + x1 - 2) / 2
        col = FIELD[kind]
        yb = yc + hc + 14
        o.append(f'<g id="{pfx}-l{j}" class="{th.strip()}"><path d="M{x0},{yb} v10 H{x1 - 2} v-10" fill="none" stroke="{col}" '
                 f'stroke-width="3"/><text x="{cx:.1f}" y="{yb + 44}" class="pg-lab" fill="{col}">{esc(lab)} · {k}</text></g>')
        if vals:
            o.append(f'<text id="{pfx}-v{j}" x="{cx:.1f}" y="{yb + 94}" class="pg-val h">= {out_vals[j]}</text>')
    o.append("</svg>")
    return "".join(o), out_vals


def ids(pfx, kind, js):
    """the ids {pfx}-<kind><j> for the fields js (kind: t tint, l label, v value)"""
    return [f"{pfx}-{kind}{j}" for j in js]


# ---------------------------------------------------------------- page table
def page_table(pfx, table, pages=None, hidden=False, valid_col=True, head=("דף", "מסגרת", "valid")):
    """rows page -> frame (None = invalid). Ids: {pfx}-r<p> row, {pfx}-hi<p> its highlight (hidden)."""
    pages = sorted(table) if pages is None else pages
    cols = 3 if valid_col else 2
    o = [f'<div class="pg-pt{" h" if hidden else ""}" id="{pfx}" style="grid-template-columns:repeat({cols},auto)">']
    o += [f'<span class="pg-pth">{h}</span>' for h in head[:cols]]
    for p in pages:
        fr = table.get(p)
        bad = fr is None
        cells = [str(p), "—" if bad else str(fr)] + (["0" if bad else "1"] if valid_col else [])
        cl = " pg-inv" if bad else ""
        o.append(f'<div class="pg-ptr{cl}" id="{pfx}-r{p}" style="grid-column:1 / span {cols}">'
                 f'<i id="{pfx}-hi{p}" class="pg-hi{" bad" if bad else ""} h"></i>'
                 + "".join(f"<span>{c}</span>" for c in cells) + "</div>")
    o.append("</div>")
    return "".join(o)


# ---------------------------------------------------------------- the TLB path
def tlb_flow(pfx, levels=1, hidden=False):
    """CPU -> TLB -> data on a hit; CPU -> TLB -> page table level(s) in RAM -> data on a miss.
    Ids: {pfx}-hit (the hit arrows + tag), {pfx}-miss (the miss arrows + tag), {pfx}-b-<name> each box
    (cpu, tlb, pt0.., data), {pfx}-hc / {pfx}-mc the access counts (hidden)."""
    w, h = 1000, 470
    bw, bh = 170, 86
    pts = [f"pt{i}" for i in range(levels)]
    assert 1 <= levels <= 3
    box = {"cpu": (20, 60), "tlb": (280, 60), "data": (800, 60)}
    x0 = {1: 455, 2: 330, 3: 250}[levels]
    for i, p in enumerate(pts):
        box[p] = (x0 + i * (bw + 50), 320)
    lab = {"cpu": "CPU", "tlb": "TLB", "data": "data (RAM)"}
    for i, p in enumerate(pts):
        lab[p] = "page table" if levels == 1 else f"level {i + 1}"
    o = [f'<svg class="pg-flow{" h" if hidden else ""}" id="{pfx}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" direction="ltr">',
         f'<defs><marker id="{pfx}-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="#2dd4bf"/></marker>'
         f'<marker id="{pfx}-am" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="#fbbf24"/></marker></defs>']
    # RAM area
    o.append(f'<rect x="{min(box[p][0] for p in pts) - 26:.0f}" y="290" width="{1000 - 24 - (min(box[p][0] for p in pts) - 26):.0f}" '
             f'height="160" rx="16" class="pg-ram"/><text x="{min(box[p][0] for p in pts) - 10:.0f}" y="440" class="pg-ramt">RAM</text>')
    cx = lambda n: box[n][0] + bw / 2
    cy = lambda n: box[n][1] + bh / 2
    # hit path: cpu -> tlb -> data (top row)
    hit = [f'<path d="M{box["cpu"][0] + bw},{cy("cpu") - 14} H{box["tlb"][0] - 4}" class="pg-ah" marker-end="url(#{pfx}-ah)"/>',
           f'<path d="M{box["tlb"][0] + bw},{cy("tlb") - 14} H{box["data"][0] - 4}" class="pg-ah" marker-end="url(#{pfx}-ah)"/>',
           f'<text x="{(box["tlb"][0] + bw + box["data"][0]) / 2:.0f}" y="{cy("tlb") - 30}" class="pg-ft hit">hit</text>']
    o.append(f'<g id="{pfx}-hit" class="h">{"".join(hit)}</g>')
    miss = [f'<path d="M{box["cpu"][0] + bw},{cy("cpu") + 14} H{box["tlb"][0] - 4}" class="pg-am" marker-end="url(#{pfx}-am)"/>']
    prev = "tlb"
    for p in pts:
        if prev == "tlb":
            miss.append(f'<path d="M{cx("tlb")},{box["tlb"][1] + bh + 2} L{cx(p) - 10},{box[p][1] - 6}" class="pg-am" '
                        f'marker-end="url(#{pfx}-am)"/>')
        else:
            miss.append(f'<path d="M{box[prev][0] + bw},{cy(p)} H{box[p][0] - 4}" class="pg-am" marker-end="url(#{pfx}-am)"/>')
        prev = p
    miss.append(f'<path d="M{cx(prev) + 20},{box[prev][1] - 4} L{cx("data")},{box["data"][1] + bh + 6}" class="pg-am" '
                f'marker-end="url(#{pfx}-am)"/>')
    miss.append(f'<text x="{cx("tlb") - 40}" y="{box["tlb"][1] + bh + 66}" class="pg-ft miss">miss</text>')
    o.append(f'<g id="{pfx}-miss" class="h">{"".join(miss)}</g>')
    for n in ["cpu", "tlb", "data"] + pts:
        x, y = box[n]
        o.append(f'<g id="{pfx}-b-{n}"><rect x="{x:.0f}" y="{y}" width="{bw}" height="{bh}" rx="14" class="pg-box {n[:2]}"/>'
                 f'<text x="{x + bw / 2:.0f}" y="{y + 55}" class="pg-bt">{esc(lab[n])}</text></g>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- multilevel walk
def mini_table(pfx, title, rows, hl, hidden=True, kind="outer"):
    """one table of the walk: rows [(index, value)] with '⋮' rows between non-consecutive indexes; the row hl is
    highlighted (id {pfx}-hi). Ids: {pfx} the table."""
    o = [f'<div id="{pfx}" class="pg-mt {kind}{" h" if hidden else ""}"><div class="pg-mtt">{title}</div>']
    last = None
    for i, v in rows:
        if last is not None and i != last + 1:
            o.append('<div class="pg-mtr dots"><span>⋮</span></div>')
        hi = f'<i id="{pfx}-hi" class="pg-hi h"></i>' if i == hl else ""
        o.append(f'<div class="pg-mtr">{hi}<span class="ix">{i}</span><span>{v}</span></div>')
        last = i
    o.append("</div>")
    return "".join(o)


def arrow(id_, hidden=True, label=""):
    lab = f'<span class="pg-arl">{label}</span>' if label else ""
    return f'<div id="{id_}" class="pg-arrow{" h" if hidden else ""}">{lab}<span>➜</span></div>'


def box(id_, html_, hidden=True, cls=""):
    return f'<div id="{id_}" class="pg-boxh {cls}{" h" if hidden else ""}">{html_}</div>'


def chain(*parts):
    return f'<div class="pg-chain">{"".join(parts)}</div>'


# ---------------------------------------------------------------- CPU core + RAM + kernel (who does what)
def machine(pfx, cores=1, hidden=False):
    """a CPU (cores with MMU, TLB and PTBR), RAM with the page tables of A and B, and the kernel's PCBs.
    One core: the three units stacked; two cores: one row of units per core, PTBR at the right end.
    Ids: {pfx}-c<k> core k, {pfx}-mmu<k> / {pfx}-tlb<k> / {pfx}-ptbr<k>, {pfx}-ta / {pfx}-tb the tables,
    {pfx}-pa / {pfx}-pb the PCBs, {pfx}-a<k>A / {pfx}-a<k>B the PTBR arrow of core k to table A/B (hidden),
    {pfx}-sv the save arrow PTBR -> PCB A, {pfx}-ld the load arrow PCB B -> PTBR (hidden, core 0)."""
    assert cores in (1, 2)
    w, h = 1000, 640
    o = [f'<svg class="pg-mach{" h" if hidden else ""}" id="{pfx}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" direction="ltr">',
         f'<defs><marker id="{pfx}-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="#2dd4bf"/></marker>'
         f'<marker id="{pfx}-am" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="#fbbf24"/></marker></defs>']
    o.append('<rect x="10" y="10" width="430" height="330" rx="18" class="pg-cpu"/><text x="24" y="44" class="pg-mt2">CPU</text>')

    def unit(id_, x, y, wd, name, cls):
        o.append(f'<g id="{id_}"><rect x="{x}" y="{y}" width="{wd}" height="54" rx="10" class="pg-box {cls}"/>'
                 f'<text x="{x + wd / 2}" y="{y + 36}" class="pg-bt sm">{name}</text></g>')

    starts = []                                   # where each core's PTBR arrow leaves
    if cores == 1:
        x0, y0, wc = 26, 60, 388
        o.append(f'<g id="{pfx}-c0"><rect x="{x0}" y="{y0}" width="{wc}" height="230" rx="14" class="pg-core"/>'
                 f'<text x="{x0 + 12}" y="{y0 + 30}" class="pg-mt3">core</text></g>')
        for name, cls, dy in (("MMU", "mm", 44), ("TLB", "tl", 106), ("PTBR", "pr", 168)):
            unit(f"{pfx}-{name.lower()}0", x0 + 14, y0 + dy, wc - 28, name, cls)
        starts.append((x0 + wc - 14, y0 + 195))
        ptbr_bottom = (x0 + 14, y0 + 222, x0 + wc - 14)
    else:
        for k in range(2):
            x0, y0, wc = 26, 56 + k * 142, 398
            o.append(f'<g id="{pfx}-c{k}"><rect x="{x0}" y="{y0}" width="{wc}" height="128" rx="14" class="pg-core"/>'
                     f'<text x="{x0 + 12}" y="{y0 + 28}" class="pg-mt3">core {k + 1}</text></g>')
            for j, (name, cls) in enumerate((("MMU", "mm"), ("TLB", "tl"), ("PTBR", "pr"))):
                unit(f"{pfx}-{name.lower()}{k}", x0 + 12 + j * 126, y0 + 52, 116, name, cls)
            starts.append((x0 + 12 + 2 * 126 + 116, y0 + 79))
        ptbr_bottom = None
    o.append('<rect x="560" y="10" width="430" height="330" rx="18" class="pg-ram"/><text x="574" y="44" class="pg-mt2">RAM</text>')
    for nm, y in (("a", 70), ("b", 200)):
        o.append(f'<g id="{pfx}-t{nm}"><rect x="640" y="{y}" width="270" height="100" rx="12" class="pg-box pt"/>'
                 f'<text x="775" y="{y + 60}" class="pg-bt sm">page table {nm.upper()}</text></g>')
    o.append('<rect x="560" y="380" width="430" height="250" rx="18" class="pg-kern"/><text x="574" y="414" class="pg-mt2">kernel</text>')
    for nm, x in (("a", 590), ("b", 790)):
        o.append(f'<g id="{pfx}-p{nm}"><rect x="{x}" y="440" width="180" height="150" rx="12" class="pg-box pc"/>'
                 f'<text x="{x + 90}" y="490" class="pg-bt sm">PCB {nm.upper()}</text>'
                 f'<text x="{x + 90}" y="540" class="pg-bt xs">page table</text><text x="{x + 90}" y="572" class="pg-bt xs">address</text></g>')
    for k, (sx, sy) in enumerate(starts):
        for nm, ty in (("A", 120), ("B", 250)):
            o.append(f'<path id="{pfx}-a{k}{nm}" d="M{sx},{sy} C{sx + 110},{sy} {530},{ty} 636,{ty}" class="pg-ah h" '
                     f'marker-end="url(#{pfx}-ah)"/>')
    if ptbr_bottom:                               # context switch on the single core: save to PCB A, load from PCB B
        lx, by, rx = ptbr_bottom
        o.append(f'<path id="{pfx}-sv" d="M{lx + 60},{by + 4} C{lx + 60},{560} {400},{560} 584,{560}" class="pg-am h" '
                 f'marker-end="url(#{pfx}-am)"/>')
        o.append(f'<path id="{pfx}-ld" d="M880,436 C880,380 {rx - 40},{400} {rx - 60},{by + 8}" class="pg-am h" '
                 f'marker-end="url(#{pfx}-am)"/>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- whole pages: a request laid over its pages
def alloc(size, page_size):
    """(pages, allocated bytes, internal fragmentation) for a request of `size` bytes"""
    n = -(-size // page_size)
    assert (n - 1) * page_size < size <= n * page_size
    return n, n * page_size, n * page_size - size


def alloc_bar(pfx, size, page_size, w=1000, hidden=False, unit="bytes"):
    """the request as a bar over whole pages. Ids (hidden): {pfx}-p<i> page i, {pfx}-u the used part,
    {pfx}-w the wasted tail of the last page, {pfx}-wl its label, {pfx}-sl the request label.
    Returns (svg, (pages, allocated, waste))."""
    n, tot, waste = alloc(size, page_size)
    L, R = 10, 10
    X = lambda v: L + (w - L - R) * v / tot
    h = 210
    yb, hb = 70, 70
    o = [f'<svg class="pg-bar{" h" if hidden else ""}" id="{pfx}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" direction="ltr">']
    o.append(f'<rect id="{pfx}-u" x="{X(0):.1f}" y="{yb}" width="{X(size) - X(0):.1f}" height="{hb}" class="pg-used h"/>')
    o.append(f'<rect id="{pfx}-w" x="{X(size):.1f}" y="{yb}" width="{X(tot) - X(size):.1f}" height="{hb}" class="pg-waste h"/>')
    for i in range(n):
        x0, x1 = X(i * page_size), X((i + 1) * page_size)
        o.append(f'<g id="{pfx}-p{i}" class="h"><rect x="{x0 + 1:.1f}" y="{yb - 6}" width="{x1 - x0 - 2:.1f}" height="{hb + 12}" rx="8" '
                 f'class="pg-pgbox"/><text x="{(x0 + x1) / 2:.1f}" y="{yb - 18}" class="pg-pgl">{i}</text></g>')
    close = X(tot) - X(size) < 130                  # the two bottom labels would collide: pull the request label left
    o.append(f'<text id="{pfx}-sl" x="{X(size) - (8 if close else 0):.1f}" y="{yb + hb + 46}" class="pg-bl h"'
             f'{" style=" + chr(34) + "text-anchor:end" + chr(34) if close else ""}>{size}</text>')
    o.append(f'<text id="{pfx}-wl" x="{(X(size) + X(tot)) / 2:.1f}" y="{yb + hb / 2 + 11}" class="pg-wl h">{waste}</text>')
    o.append(f'<text x="{X(tot) - 4:.1f}" y="{yb + hb + 46}" class="pg-bl end">{tot}</text>')
    o.append("</svg>")
    return "".join(o), (n, tot, waste)
