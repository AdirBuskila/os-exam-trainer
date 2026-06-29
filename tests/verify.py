# -*- coding: utf-8 -*-
"""
Verification engine for OS exam coaching.
- fork() process-tree simulator (handles forks in expressions, &&/||/?: short-circuit)
- scheduling calculator (FCFS / SJF-nonpreemptive / SRTF / RR)
- disk geometry & paging helpers
Each engine is validated against past-exam questions whose official answers are known.
"""
from collections import deque

# ---------------------------------------------------------------------------
# FORK SIMULATOR
# ---------------------------------------------------------------------------
# A "process" is one complete assignment of parent/child to every fork() call it
# makes, in encounter order. We enumerate all processes via BFS: run the program;
# the first fork whose outcome is not yet decided forks the enumeration into
# (parent, child) and the run is replayed. Completed runs == real processes.
# Parent forks return DISTINCT positive ints (so fork()==fork() compares correctly);
# child forks return 0. printf() increments that process's print count.

class _Branch(Exception):
    pass

def simulate_fork(prog):
    """prog(fork, printf) -> runs straight-line code. Returns (num_processes, total_prints)."""
    q = deque([[]])
    procs = 0
    prints = 0
    while q:
        decisions = q.popleft()
        st = {"i": 0, "pos": 0, "prints": 0, "branch": None}

        def fork():
            j = st["i"]; st["i"] += 1
            if j < len(decisions):
                if decisions[j]:
                    st["pos"] += 1
                    return st["pos"]          # distinct positive pid
                return 0                       # child
            st["branch"] = (decisions + [True], decisions + [False])
            raise _Branch()

        def printf(*_):
            st["prints"] += 1

        try:
            prog(fork, printf)
        except _Branch:
            q.append(st["branch"][0]); q.append(st["branch"][1])
            continue
        procs += 1
        prints += st["prints"]
    return procs, prints


# --- past-exam fork programs (faithful Python translations) ---
def p_2017b_q9(f, pr):            # for(i=0;i<3;i++) fork(); printf
    for _ in range(3): f()
    pr()
def p_2022a_q9(f, pr):            # a=b=c=fork(); printf
    a = b = c = f(); pr()
def p_2022b_q9(f, pr):           # if(fork()!=fork()) printf
    if f() != f(): pr()
def p_2019b_q9(f, pr):           # if(fork()==fork()) printf
    if f() == f(): pr()
def p_2023a_q9(f, pr):           # if(fork()+fork()==0){ fork(); printf }
    if f() + f() == 0:
        f(); pr()
def p_2023b_q9(f, pr):           # fork()?fork():fork(); printf
    (f() if f() else f()); pr()
def p_2024b_q9(f, pr):           # if(fork()-fork()==0) printf
    if f() - f() == 0: pr()
def p_2024a_q9(f, pr):           # if(fork()*fork()*fork()==0) printf
    if f() * f() * f() == 0: pr()
def p_2017a_q9(f, pr):           # printf("%d",(int)(1/(fork()+100)))  -> value not count
    val = int(1 / (f() + 100)); pr()  # we report the per-process value separately below

FORK_CASES = [
    ("2017B Q9  for 3x fork; printf            ", p_2017b_q9, "prints", 8),
    ("2022A Q9  a=b=c=fork(); printf HIT        ", p_2022a_q9, "prints", 2),
    ("2022B Q9  if(fork()!=fork()) HIT          ", p_2022b_q9, "prints", 3),
    ("2019B Q9  if(fork()==fork()) a            ", p_2019b_q9, "prints", None),
    ("2023A Q9  if(fork()+fork()==0){fork();..} ", p_2023a_q9, "prints", 2),
    ("2023B Q9  fork()?fork():fork(); printf    ", p_2023b_q9, "prints", 4),
    ("2024B Q9  if(fork()-fork()==0) fork       ", p_2024b_q9, "prints", 1),
    ("2024A Q9  if(fork()*fork()*fork()==0) fork", p_2024a_q9, "prints", "4? (notes flag)"),
]

# --- diagnostic fork program(s) ---
def diag_q3(f, pr):              # fork() && fork() && fork(); printf("x")  (unconditional printf)
    f() and f() and f()
    pr()

# ---------------------------------------------------------------------------
# SCHEDULING
# ---------------------------------------------------------------------------
def schedule(procs, algo, quantum=None):
    """procs: list of (name, arrival, burst). Returns (avg_wait, gantt, per)."""
    n = len(procs)
    rem = {p[0]: p[2] for p in procs}
    arr = {p[0]: p[1] for p in procs}
    burst = {p[0]: p[2] for p in procs}
    finish = {}
    t = 0
    done = 0
    gantt = []
    if algo in ("FCFS", "SJF", "SRTF"):
        while done < n:
            avail = [p for p in procs if arr[p[0]] <= t and rem[p[0]] > 0]
            if not avail:
                t = min(arr[p[0]] for p in procs if rem[p[0]] > 0)
                continue
            if algo == "FCFS":
                cur = min(avail, key=lambda p: (arr[p[0]], procs.index(p)))
                run = rem[cur[0]]
            elif algo == "SJF":   # non-preemptive
                cur = min(avail, key=lambda p: (burst[p[0]], arr[p[0]], procs.index(p)))
                run = rem[cur[0]]
            else:                 # SRTF preemptive: run 1 tick (or until next arrival)
                cur = min(avail, key=lambda p: (rem[p[0]], arr[p[0]], procs.index(p)))
                future = [arr[p[0]] for p in procs if arr[p[0]] > t and rem[p[0]] > 0]
                step = 1
                run = 1
                # advance until completion or a new arrival could preempt
                nxt = min(future) if future else None
                run = (nxt - t) if nxt is not None else rem[cur[0]]
                run = min(run, rem[cur[0]])
            if gantt and gantt[-1][0] == cur[0]:
                gantt[-1] = (cur[0], gantt[-1][1], t + run)
            else:
                gantt.append((cur[0], t, t + run))
            rem[cur[0]] -= run
            t += run
            if rem[cur[0]] == 0:
                finish[cur[0]] = t
                done += 1
    elif algo == "RR":
        order = sorted(procs, key=lambda p: (arr[p[0]], procs.index(p)))
        rq = deque()
        i = 0
        # seed
        t = order[0][1]
        pending = sorted(procs, key=lambda p: (arr[p[0]], procs.index(p)))
        idx = 0
        while idx < n and arr[pending[idx][0]] <= t:
            rq.append(pending[idx][0]); idx += 1
        while rq:
            name = rq.popleft()
            run = min(quantum, rem[name])
            if gantt and gantt[-1][0] == name:
                gantt[-1] = (name, gantt[-1][1], t + run)
            else:
                gantt.append((name, t, t + run))
            t += run
            rem[name] -= run
            # add arrivals that came during this slice
            while idx < n and arr[pending[idx][0]] <= t:
                rq.append(pending[idx][0]); idx += 1
            if rem[name] > 0:
                rq.append(name)
            else:
                finish[name] = t
            if not rq and idx < n:  # gap until next arrival
                t = arr[pending[idx][0]]
                while idx < n and arr[pending[idx][0]] <= t:
                    rq.append(pending[idx][0]); idx += 1
    per = {}
    for p in procs:
        nm = p[0]
        ta = finish[nm] - arr[nm]
        w = ta - burst[nm]
        per[nm] = (ta, w)
    avg = sum(per[nm][1] for nm in per) / n
    return avg, gantt, per


SCHED_CASES = [
    ("2020A Q6 FCFS  [7@0,3@1,22@4]", "FCFS", None,
     [("P1",0,7),("P2",1,3),("P3",4,22)], 4),
    ("2020B Q6 SJF   [7@0,3@1,22@4]", "SJF", None,
     [("P1",0,7),("P2",1,3),("P3",4,22)], 4),       # true non-preemptive SJF
    ("2020B Q6 SRTF  [7@0,3@1,22@4]", "SRTF", None,
     [("P1",0,7),("P2",1,3),("P3",4,22)], 3),       # what the official key (3) matches
    ("2022A Q4 SRTF  [9@0,7@1,4@2]",  "SRTF", None,
     [("P1",0,9),("P2",1,7),("P3",2,4)], 5),
    ("2019A Q4 RR4   [9,3,7,1 @0]",   "RR", 4,
     [("P1",0,9),("P2",0,3),("P3",0,7),("P4",0,1)], 9.5),
    ("2021A Q5 RR4   [7,7,7 @0]",     "RR", 4,
     [("P1",0,7),("P2",0,7),("P3",0,7)], 11),
    ("2021B Q5 FCFS  [7@0,7@1,7@2]",  "FCFS", None,
     [("P1",0,7),("P2",1,7),("P3",2,7)], 6),
    ("2022B Q4 RR4   [9@0,7@1,4@3]",  "RR", 4,
     [("P1",0,9),("P2",1,7),("P3",3,4)], 9),
    ("2017SB Q3 FCFS [7@0,4@2,1@4,4@5]", "FCFS", None,
     [("P1",0,7),("P2",2,4),("P3",4,1),("P4",5,4)], 4.75),
]

# diagnostic scheduling
DIAG_SCHED = ("DIAG Q2 SRTF [7@0,2@2,4@4]", "SRTF", None,
              [("P1",0,7),("P2",2,2),("P3",4,4)], 2)

# ---------------------------------------------------------------------------
# DISK GEOMETRY  (total_sectors = cylinders * surfaces * sectors_per_track)
# ---------------------------------------------------------------------------
def disk_unknown(capacity, sector, cylinders=None, surfaces=None, spt=None):
    total_sectors = capacity // sector
    if cylinders is None:
        return total_sectors // (surfaces * spt), "cylinders"
    if surfaces is None:
        return total_sectors // (cylinders * spt), "surfaces (=> platters/2)"
    if spt is None:
        return total_sectors // (cylinders * surfaces), "sectors_per_track"
    return total_sectors, "total_sectors"

K=1024; M=K*K; G=K*M; T=K*G
DISK_CASES = [
    ("2020A Q2 sectors total 1000cyl,8surf,50spt", lambda: 1000*8*50, 400000),
    ("2022A Q2 cylinders 1TB,4surf,2K spt,4KB",    lambda: disk_unknown(T, 4*K, surfaces=4, spt=2*K)[0], 32*K),
    ("2022B Q2 surfaces 0.5TB,8Kcyl,2Kspt,4KB",    lambda: disk_unknown(T//2, 4*K, cylinders=8*K, spt=2*K)[0], 8),
    ("2023B Q2 surfaces 1TB,8Kcyl,8Kspt,8KB",      lambda: disk_unknown(T, 8*K, cylinders=8*K, spt=8*K)[0], 2),
]
# diagnostic Q1: 2TB, 8 surfaces, 16K spt, 8KB sector -> cylinders?
DIAG_DISK = ("DIAG Q1 cyl 2TB,8surf,16Kspt,8KB", lambda: disk_unknown(2*T, 8*K, surfaces=8, spt=16*K)[0])

# ---------------------------------------------------------------------------
# RUN ALL
# ---------------------------------------------------------------------------
print("="*72); print("FORK SIMULATOR — validation vs known official answers"); print("="*72)
for label, prog, kind, expected in FORK_CASES:
    procs, prints = simulate_fork(prog)
    got = prints
    ok = "" if expected in (None,) or isinstance(expected,str) else ("  OK" if got==expected else "  <-- MISMATCH")
    print(f"{label} | processes={procs:2d} prints={prints:2d} | official={expected}{ok}")
# 2017A Q9 value check
vals=[]
def collect(f,pr):
    v=int(1/(f()+100)); vals.append(v)
simulate_fork(collect)
print(f"2017A Q9  printf 1/(fork()+100)            | per-process values={vals} -> output '{''.join(map(str,vals))}' (official '00')")

print("\nDIAGNOSTIC Q3  fork()&&fork()&&fork(); printf(\"x\")")
procs,prints = simulate_fork(diag_q3)
print(f"   -> processes={procs}  prints={prints}")

print("\n"+"="*72); print("SCHEDULER — validation vs known official answers"); print("="*72)
for label, algo, q, procs, expected in SCHED_CASES:
    avg, gantt, per = schedule(procs, algo, q)
    g = " ".join(f"{a}[{s}-{e}]" for a,s,e in gantt)
    ok = "OK" if abs(avg-expected)<1e-9 else "<-- MISMATCH"
    print(f"{label:32s} avg_wait={avg:5.2f} official={expected:<5} {ok}")
    print(f"      gantt: {g}")

print("\nDIAGNOSTIC Q2 (SRTF):")
label, algo, q, procs, expected = DIAG_SCHED
avg, gantt, per = schedule(procs, algo, q)
g = " ".join(f"{a}[{s}-{e}]" for a,s,e in gantt)
print(f"   {label}  avg_wait={avg:.2f}  gantt: {g}  per(turn,wait)={per}")

print("\n"+"="*72); print("DISK GEOMETRY — validation"); print("="*72)
for label, fn, expected in DISK_CASES:
    got = fn()
    ok = "OK" if got==expected else "<-- MISMATCH"
    print(f"{label:42s} got={got:<8} official={expected:<8} {ok}")
print(f"\nDIAGNOSTIC Q1: {DIAG_DISK[0]} -> cylinders={DIAG_DISK[1]()} (= {DIAG_DISK[1]()//1024}K)")

print("\n"+"="*72); print("PAGING — diagnostic Q9"); print("="*72)
print("Q9: 36-bit virtual addr, page=4KB(2^12). offset=12 bits, page-number=24 bits")
print(f"    single-level page table entries = 2^(36-12) = 2^24 = {2**24}")
