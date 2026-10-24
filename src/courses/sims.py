# -*- coding: utf-8 -*-
"""Independent simulators used to machine-check every stored course answer.

Nothing here is shared with js/engines.js: the scheduler below is a unit-tick simulation, the
engine is event driven. tests/courses_check.py also cross-checks the two against each other.
`strict=True` makes an ambiguous decision (a tie the exam would have to specify) raise, so a
question can never rest on a tie-break rule the course did not teach.
"""
from collections import deque
import math


class Ambiguous(Exception):
    pass


# ---------------------------------------------------------------- scheduling
def schedule(procs, algo, quantum=None, strict=True):
    """procs: list of (arrival, burst) for P1..Pn. algo: FCFS | SJF | SRTF | RR.
    Returns dict(gantt=[(name,start,end)], finish, turn, wait, resp, avg_wait, avg_turn)."""
    n = len(procs)
    names = ["P%d" % (i + 1) for i in range(n)]
    arr = [p[0] for p in procs]
    bur = [p[1] for p in procs]
    rem = bur[:]
    finish = [None] * n
    first = [None] * n
    timeline = []  # name per tick or None for idle
    t = 0
    running = None
    rq = deque()
    queued = [False] * n
    rr_used = 0

    def admit(now):
        # arrivals at time `now` join the ready queue (in index order)
        for i in range(n):
            if arr[i] <= now and not queued[i] and rem[i] > 0:
                rq.append(i)
                queued[i] = True

    while any(r > 0 for r in rem):
        if algo == "RR":
            admit(t)
            if running is None:
                if not rq:
                    timeline.append(None)
                    t += 1
                    continue
                running = rq.popleft()
                rr_used = 0
            i = running
        else:
            ready = [i for i in range(n) if arr[i] <= t and rem[i] > 0]
            if not ready:
                timeline.append(None)
                t += 1
                continue
            if algo == "FCFS":
                if running is None or rem[running] == 0:
                    key = sorted((arr[i], i) for i in ready)
                    if strict and len(key) > 1 and key[0][0] == key[1][0]:
                        raise Ambiguous("FCFS tie at t=%d" % t)
                    running = key[0][1]
            elif algo == "SJF":
                if running is None or rem[running] == 0:
                    key = sorted((bur[i], i) for i in ready)
                    if strict and len(key) > 1 and key[0][0] == key[1][0]:
                        raise Ambiguous("SJF tie at t=%d" % t)
                    running = key[0][1]
            elif algo == "SRTF":
                key = sorted((rem[i], i) for i in ready)
                if strict and len(key) > 1 and key[0][0] == key[1][0]:
                    raise Ambiguous("SRTF tie at t=%d" % t)
                running = key[0][1]
            else:
                raise ValueError(algo)
            i = running
        if first[i] is None:
            first[i] = t
        timeline.append(names[i])
        rem[i] -= 1
        t += 1
        if algo == "RR":
            rr_used += 1
            if rem[i] == 0:
                finish[i] = t
                admit(t)
                running = None
            elif rr_used == quantum:
                admit(t)          # arrivals first, then the preempted job (the course's rule)
                rq.append(i)
                running = None
        else:
            if rem[i] == 0:
                finish[i] = t
                running = None if algo != "SRTF" else None
    gantt = []
    for tick, name in enumerate(timeline):
        if name is None:
            continue
        if gantt and gantt[-1][0] == name and gantt[-1][2] == tick:
            gantt[-1] = (name, gantt[-1][1], tick + 1)
        else:
            gantt.append((name, tick, tick + 1))
    turn = [finish[i] - arr[i] for i in range(n)]
    wait = [turn[i] - bur[i] for i in range(n)]
    resp = [first[i] - arr[i] for i in range(n)]
    return dict(names=names, gantt=gantt, finish=finish, turn=turn, wait=wait, resp=resp,
                avg_wait=sum(wait) / n, avg_turn=sum(turn) / n, avg_resp=sum(resp) / n,
                switches=len(gantt) - 1)


# ----------------------------------------------------------- page replacement
def replace(refs, frames, algo, strict=True):
    """Return dict(faults, hits, trace=[(page, 'hit'|'fault', frames_after, victim)]).
    OPT may face several pages that are never used again; they are equivalent for the fault count,
    so only strict callers (asking which page is evicted) treat that as ambiguous."""
    mem = []          # FIFO: load order; LRU: recency order (oldest first)
    faults = 0
    trace = []
    for idx, p in enumerate(refs):
        victim = None
        if p in mem:
            if algo == "LRU":
                mem.remove(p)
                mem.append(p)
            trace.append((p, "hit", list(mem), None))
            continue
        faults += 1
        if len(mem) >= frames:
            if algo in ("FIFO", "LRU"):
                victim = mem.pop(0)
            elif algo == "OPT":
                future = refs[idx + 1:]
                dist = {}
                for m in mem:
                    dist[m] = future.index(m) if m in future else math.inf
                far = max(dist.values())
                cands = [m for m in mem if dist[m] == far]
                if strict and len(cands) > 1:
                    raise Ambiguous("OPT tie at ref %d" % idx)
                victim = cands[0]
                mem.remove(victim)
            else:
                raise ValueError(algo)
        mem.append(p)
        trace.append((p, "fault", list(mem), victim))
    return dict(faults=faults, hits=len(refs) - faults, trace=trace)


# ------------------------------------------------------------------- paging
def split_address(vaddr, page_size):
    return vaddr // page_size, vaddr % page_size


def translate(vaddr, page_size, table):
    """table: {page: frame or None}. Returns int physical address or 'fault'."""
    page, off = split_address(vaddr, page_size)
    fr = table.get(page)
    if fr is None:
        return "fault"
    return fr * page_size + off


def eat(hit, mem_ns, levels, tlb_ns=0):
    """Effective access time: hit -> TLB + 1 access; miss -> TLB + levels walks + 1 access."""
    return hit * (tlb_ns + mem_ns) + (1 - hit) * (tlb_ns + (levels + 1) * mem_ns)


# --------------------------------------------------------------- semaphores
def semaphore(init, ops):
    """ops: 'P:A V:B ...' (space separated). Returns dict(value, queue(list), log)."""
    value = init
    queue = []
    log = []
    for tok in ops.split():
        op, who = tok.split(":")
        if op == "P":
            value -= 1
            if value < 0:
                queue.append(who)
                log.append("%s blocks" % who)
            else:
                log.append("%s passes" % who)
        elif op == "V":
            value += 1
            if value <= 0 and queue:
                woken = queue.pop(0)
                log.append("%s wakes %s" % (who, woken))
            else:
                log.append("%s signals" % who)
        else:
            raise ValueError(tok)
    return dict(value=value, queue=queue, log=log)


# ----------------------------------------------------------------- deadlock
def can_deadlock(procs, locks=None):
    """procs: list of lock sequences, e.g. [['A','B'],['B','A']]. A process takes its locks in
    order, holds all of them, finishes after the last, then releases everything. Exhaustive
    search over every interleaving; True if some reachable state has unfinished processes and
    nobody able to move."""
    n = len(procs)
    seen = set()
    stack = [(tuple([0] * n), frozenset())]
    while stack:
        pcs, held = stack.pop()
        if (pcs, held) in seen:
            continue
        seen.add((pcs, held))
        if all(pcs[i] == len(procs[i]) for i in range(n)):
            continue
        holders = {}
        for (lock, who) in held:
            holders[lock] = who
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
            nheld = set(held)
            nheld.add((lock, i))
            if npcs[i] == len(procs[i]):
                nheld = {h for h in nheld if h[1] != i}
            stack.append((tuple(npcs), frozenset(nheld)))
        if not moved:
            return True
    return False


def philosophers(n, ordered=False):
    seqs = []
    for i in range(n):
        a, b = i, (i + 1) % n
        if ordered and a > b:
            a, b = b, a
        seqs.append([a, b])
    return seqs


# ------------------------------------------------------------------ helpers
def fmt_num(x):
    if isinstance(x, str):
        return x
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return ("%.2f" % x).rstrip("0").rstrip(".")


def pow2(x):
    k = int(round(math.log2(x)))
    assert 2 ** k == x, x
    return "2^%d" % k
