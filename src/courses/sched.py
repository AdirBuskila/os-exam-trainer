# -*- coding: utf-8 -*-
"""Course 1: CPU scheduling. Every number below is recomputed by tests/courses_check.py."""
from _kit import Q, Lv, Course


def tbl(procs, head=("Process", "Arrival", "Burst")):
    """Monospace table for a question. procs: [(arrival, burst)] for P1..Pn."""
    rows = [("%-9s%-9s%s" % head)]
    for i, (a, b) in enumerate(procs, 1):
        rows.append("%-9s%-9d%d" % ("P%d" % i, a, b))
    return "\n".join(rows)


def S(procs, algo, ask, q=None, want=None):
    d = dict(k="sched", procs=procs, algo=algo, q=q, ask=ask)
    if want is not None:
        d["want"] = want
    return d


# ------------------------------------------------------------------ level 1
L1_LESSON = (
    """
<p>Every CPU question uses the same three numbers per process: <b>arrival</b> (when it enters the ready queue), <b>burst</b> (how much CPU time it needs) and <b>completion</b> (when it finishes). Three clocks are built from them. They are different things, and the exam mixes them up on purpose.</p>
<table>
<tr><th>Metric</th><th>Formula</th><th>In words</th></tr>
<tr><td>Turnaround</td><td>completion &minus; arrival</td><td>the whole time in the system</td></tr>
<tr><td>Waiting</td><td>turnaround &minus; burst</td><td>time spent in the ready queue, not running</td></tr>
<tr><td>Response</td><td>first run &minus; arrival</td><td>time until it first gets the CPU</td></tr>
</table>
<p>So <b>waiting + running = turnaround</b>. The formula <code>waiting = turnaround &minus; burst</code> works for every algorithm, even when a process runs in pieces, so it is the one to memorise.</p>
<pre>P2 arrives at 2, burst 3, finishes at 8
turnaround = 8 - 2 = 6
waiting    = 6 - 3 = 3
</pre>
<p>A <b>CPU burst</b> is a stretch of pure computing between two I/O requests (adding two register values is a CPU burst). The average waiting time of a set is the sum of the waiting times divided by the number of processes.</p>
""",
    """
<p>בכל שאלת מעבד משתמשים באותם שלושה מספרים לכל תהליך: <b>הגעה</b> (מתי נכנס לתור המוכנים), <b>פרץ</b> (כמה זמן מעבד הוא צריך) ו<b>סיום</b> (מתי הוא מסתיים). מהם בונים שלושה מדדים. הם לא אותו דבר, והמבחן מערבב ביניהם בכוונה.</p>
<table>
<tr><th>מדד</th><th>נוסחה</th><th>במילים</th></tr>
<tr><td>זמן סבב (Turnaround)</td><td>סיום &minus; הגעה</td><td>כל הזמן שהתהליך במערכת</td></tr>
<tr><td>זמן המתנה (Waiting)</td><td>סבב &minus; פרץ</td><td>הזמן בתור המוכנים, בלי לרוץ</td></tr>
<tr><td>זמן תגובה (Response)</td><td>ריצה ראשונה &minus; הגעה</td><td>הזמן עד שהוא מקבל את המעבד בפעם הראשונה</td></tr>
</table>
<p>כלומר <b>המתנה + ריצה = סבב</b>. הנוסחה <code>waiting = turnaround &minus; burst</code> נכונה לכל האלגוריתמים, גם כשתהליך רץ בחתיכות, ולכן היא הנוסחה לשנן.</p>
<pre>P2 arrives at 2, burst 3, finishes at 8
turnaround = 8 - 2 = 6
waiting    = 6 - 3 = 3
</pre>
<p><b>פרץ חישוב (CPU burst)</b> הוא רצף של חישוב טהור בין שתי בקשות קלט/פלט (חיבור של שני אוגרים הוא פרץ חישוב). זמן ההמתנה הממוצע של קבוצה הוא סכום זמני ההמתנה חלקי מספר התהליכים.</p>
""",
)

L1 = Lv(
    ("Arrival, burst and the three clocks", "הגעה, פרץ ושלושת המדדים"),
    ("Turnaround, waiting and response from a single process.", "זמן סבב, המתנה ותגובה של תהליך בודד."),
    L1_LESSON,
    [
        Q(("A process arrives at time 2, needs 3 ms of CPU and finishes at time 8. What is its **turnaround time**?",
           "תהליך מגיע בזמן 2, צריך 3 מ״ש של מעבד ומסיים בזמן 8. מהו **זמן הסבב** שלו?"),
          ["6", "8", "3", "5"],
          ("Turnaround = completion − arrival = 8 − 2 = 6. The 8 is only the completion time.",
           "זמן סבב = סיום − הגעה = 8 − 2 = 6. המספר 8 הוא רק זמן הסיום."),
          ("Turnaround = completion − arrival.", "זמן סבב = סיום − הגעה."),
          check=dict(k="calc", v="8-2")),
        Q(("The same process (arrival 2, burst 3, completion 8). What is its **waiting time**?",
           "אותו תהליך (הגעה 2, פרץ 3, סיום 8). מהו **זמן ההמתנה** שלו?"),
          ["3", "6", "5", "8"],
          ("Waiting = turnaround − burst = (8 − 2) − 3 = 3. It sat in the ready queue for 3 ms.",
           "המתנה = סבב − פרץ = (8 − 2) − 3 = 3. הוא חיכה בתור המוכנים 3 מ״ש."),
          ("Waiting = turnaround − burst.", "המתנה = סבב − פרץ."),
          check=dict(k="calc", v="(8-2)-3")),
        Q(("Which metric is the total time a process spends in the ready queue, waiting for the CPU?",
           "איזה מדד הוא כל הזמן שתהליך מבלה בתור המוכנים, בהמתנה למעבד?"),
          [("Waiting time", "זמן המתנה"), ("Turnaround time", "זמן סבב"), ("Response time", "זמן תגובה"), ("Burst time", "זמן פרץ")],
          ("Waiting time is exactly the time in the ready queue. Turnaround also includes the running time.",
           "זמן המתנה הוא בדיוק הזמן בתור המוכנים. זמן סבב כולל גם את זמן הריצה."),
          ("Waiting = time in the ready queue.", "המתנה = הזמן בתור המוכנים."),
          exam="2023A-4", has="waiting"),
        Q(("In scheduling, waiting time + running time gives which metric?",
           "בתזמון, זמן המתנה + זמן ריצה נותנים איזה מדד?"),
          [("Turnaround time", "זמן סבב"), ("Response time", "זמן תגובה"), ("Throughput", "תפוקה"), ("Quantum", "קוונטום")],
          ("Turnaround = waiting + burst, from the formula waiting = turnaround − burst.",
           "סבב = המתנה + פרץ, מהנוסחה המתנה = סבב − פרץ."),
          ("Waiting + running = turnaround.", "המתנה + ריצה = סבב."),
          exam="2026A-4", has="turnaround"),
        Q(("FCFS finished three processes at the times in the table. What is the **average waiting time**?",
           "FCFS סיים שלושה תהליכים בזמנים שבטבלה. מהו **זמן ההמתנה הממוצע**?"),
          ["3", "9", "6.33", "4"],
          ("Waits: P1 (4−0)−4 = 0, P2 (8−1)−4 = 3, P3 (10−2)−2 = 6. Sum 9, divided by 3 = 3. The 6.33 is the average turnaround.",
           "המתנות: P1 (4−0)−4 = 0, P2 (8−1)−4 = 3, P3 (10−2)−2 = 6. סכום 9 חלקי 3 = 3. המספר 6.33 הוא הסבב הממוצע."),
          ("Average waiting = sum of (completion − arrival − burst) / n.", "המתנה ממוצעת = סכום (סיום − הגעה − פרץ) חלקי n."),
          code="Process  Arrival  Burst  Completion\nP1       0        4      4\nP2       1        4      8\nP3       2        2      10",
          check=[S([(0, 4), (1, 4), (2, 2)], "FCFS", "avg_wait")]),
    ],
    icon="⏱️",
)

# ------------------------------------------------------------------ level 2
L2_LESSON = (
    """
<p><b>FCFS</b> (First-Come First-Served) runs the processes in arrival order and never interrupts one: it is <b>non-preemptive</b>. To solve a question, draw the Gantt chart, read each completion time, then use <code>waiting = completion &minus; arrival &minus; burst</code>.</p>
<pre>P1 (arr 0, burst 7)   P2 (arr 1, burst 7)   P3 (arr 2, burst 7)
|-- P1 --|-- P2 --|-- P3 --|
0        7        14       21
waits: 0,  14-1-7 = 6,  21-2-7 = 12   -> average 6
</pre>
<p>If the CPU becomes free before the next process arrives it simply sits <b>idle</b>; the idle gap is not waiting for anyone. A process that arrives after the gap starts the moment it arrives and waits 0.</p>
<p>The weakness of FCFS is the <b>convoy effect</b>: one long process at the front makes all the short ones queue behind it, which inflates the average waiting time.</p>
""",
    """
<p><b>FCFS</b> (First-Come First-Served) מריץ את התהליכים לפי סדר ההגעה ולעולם לא מפסיק תהליך באמצע: הוא <b>לא נשלף</b> (non-preemptive). כדי לפתור שאלה: מציירים תרשים גאנט, קוראים את זמן הסיום של כל תהליך, ואז <code>waiting = completion &minus; arrival &minus; burst</code>.</p>
<pre>P1 (arr 0, burst 7)   P2 (arr 1, burst 7)   P3 (arr 2, burst 7)
|-- P1 --|-- P2 --|-- P3 --|
0        7        14       21
waits: 0,  14-1-7 = 6,  21-2-7 = 12   -> average 6
</pre>
<p>אם המעבד מתפנה לפני שהתהליך הבא הגיע, הוא פשוט <b>סרק</b>. זמן הסרק הוא לא המתנה של אף אחד. תהליך שמגיע אחרי הפער מתחיל לרוץ ברגע שהגיע וממתין 0.</p>
<p>החולשה של FCFS היא <b>אפקט השיירה (convoy effect)</b>: תהליך ארוך אחד בראש התור גורם לכל הקצרים לחכות מאחוריו, וזמן ההמתנה הממוצע מתנפח.</p>
""",
)

L2 = Lv(
    ("FCFS and the convoy effect", "FCFS ואפקט השיירה"),
    ("Draw the Gantt chart for first-come first-served.", "לצייר תרשים גאנט ל-FCFS."),
    L2_LESSON,
    [
        Q(("Under FCFS, which ready process gets the CPU next?", "ב-FCFS, איזה תהליך מוכן מקבל את המעבד הבא?"),
          [("The one that arrived first", "זה שהגיע ראשון"), ("The one with the shortest burst", "זה עם הפרץ הקצר ביותר"),
           ("The one that has waited the least", "זה שהמתין הכי מעט"), ("The one with the most work left", "זה שנשאר לו הכי הרבה עבודה")],
          ("FCFS is purely arrival order; burst lengths are ignored.", "FCFS הוא סדר הגעה בלבד; אורך הפרץ לא משנה."),
          ("FCFS = arrival order.", "FCFS = לפי סדר ההגעה.")),
        Q(("Compute the average waiting time under FCFS.", "חשבו את זמן ההמתנה הממוצע ב-FCFS."),
          ["4", "3", "6", "7"],
          ("Gantt: P1 0–7, P2 7–10, P3 10–32. Waits: 0, 7−1 = 6, 10−4 = 6. Average 12/3 = 4.",
           "גאנט: P1 0–7, P2 7–10, P3 10–32. המתנות: 0, 7−1 = 6, 10−4 = 6. ממוצע 12/3 = 4."),
          ("FCFS 7@0, 3@1, 22@4 gives 4 ms.", "FCFS עם 7@0, 3@1, 22@4 נותן 4 מ״ש."),
          code=tbl([(0, 7), (1, 3), (4, 22)]),
          check=S([(0, 7), (1, 3), (4, 22)], "FCFS", "avg_wait"), exam="2020A-6", has="4"),
        Q(("Which scheduling method is known for the **convoy effect** (short jobs stuck behind one long job)?",
           "איזו שיטת תזמון ידועה ב**אפקט השיירה** (עבודות קצרות תקועות מאחורי עבודה ארוכה אחת)?"),
          ["FCFS", "Round Robin", "SRTF", "Multilevel feedback"],
          ("The convoy effect belongs to FCFS: a long process in front cannot be preempted.",
           "אפקט השיירה שייך ל-FCFS: תהליך ארוך בראש התור לא ניתן להפסקה."),
          ("Convoy effect = FCFS.", "אפקט השיירה = FCFS."),
          exam="2016B-5", has="fcfs"),
        Q(("Compute the average waiting time under FCFS. P1 is long, P2 and P3 are short.",
           "חשבו את זמן ההמתנה הממוצע ב-FCFS. P1 ארוך, P2 ו-P3 קצרים."),
          ["6.33", "6", "19", "4.5"],
          ("Gantt: P1 0–10, P2 10–12, P3 12–14. Waits: 0, 10−1 = 9, 12−2 = 10. Sum 19, average 19/3 = 6.33.",
           "גאנט: P1 0–10, P2 10–12, P3 12–14. המתנות: 0, 10−1 = 9, 12−2 = 10. סכום 19, ממוצע 19/3 = 6.33."),
          ("Sum the waits, then divide by n.", "מסכמים את ההמתנות ומחלקים ב-n."),
          code=tbl([(0, 10), (1, 2), (2, 2)]),
          check=S([(0, 10), (1, 2), (2, 2)], "FCFS", "avg_wait")),
        Q(("The CPU is idle between time 2 and time 5. What is the **waiting time of P2**?",
           "המעבד סרק בין זמן 2 לזמן 5. מהו **זמן ההמתנה של P2**?"),
          ["0", "3", "2", "5"],
          ("P2 arrives at 5, the CPU is free, so it runs at once: 5–8. Waiting = (8−5)−3 = 0. The idle gap is not waiting.",
           "P2 מגיע ב-5, המעבד פנוי, ולכן הוא רץ מיד: 5–8. המתנה = (8−5)−3 = 0. הסרק אינו המתנה."),
          ("An idle CPU means the next arrival waits 0.", "מעבד סרק אומר שההגעה הבאה ממתינה 0."),
          code=tbl([(0, 2), (5, 3)]),
          check=S([(0, 2), (5, 3)], "FCFS", "wait:P2")),
    ],
    icon="🚶",
)

# ------------------------------------------------------------------ level 3
L3_LESSON = (
    """
<p><b>SJF</b> (Shortest Job First) picks, whenever the CPU becomes free, the process with the <b>shortest burst among those that have already arrived</b>. It is <b>non-preemptive</b>: once a process starts it keeps the CPU until its burst ends, even if a shorter one arrives.</p>
<pre>P1 (arr 0, b 6)   P2 (arr 1, b 8)   P3 (arr 2, b 2)
|-- P1 --|P3|----- P2 -----|
0        6  8              16
at t=6 both P2 (8) and P3 (2) are waiting -> the shorter goes
waits: P1 0,  P2 (16-1)-8 = 7,  P3 (8-2)-2 = 4   -> average 3.67
</pre>
<p>Careful: a process that has <b>not arrived yet</b> is never a candidate, however short it is. SJF gives a smaller average waiting time than FCFS, but long processes can wait forever if short ones keep arriving (<b>starvation</b>).</p>
""",
    """
<p><b>SJF</b> (Shortest Job First) בוחר, בכל פעם שהמעבד מתפנה, את התהליך עם <b>הפרץ הקצר ביותר מבין אלה שכבר הגיעו</b>. הוא <b>לא נשלף</b>: תהליך שהתחיל ממשיך עד סוף הפרץ שלו, גם אם הגיע תהליך קצר ממנו.</p>
<pre>P1 (arr 0, b 6)   P2 (arr 1, b 8)   P3 (arr 2, b 2)
|-- P1 --|P3|----- P2 -----|
0        6  8              16
at t=6 both P2 (8) and P3 (2) are waiting -> the shorter goes
waits: P1 0,  P2 (16-1)-8 = 7,  P3 (8-2)-2 = 4   -> average 3.67
</pre>
<p>שימו לב: תהליך ש<b>עוד לא הגיע</b> אף פעם לא מועמד, גם אם הוא קצר מאוד. SJF נותן המתנה ממוצעת קטנה מ-FCFS, אבל תהליכים ארוכים עלולים לחכות לנצח אם כל הזמן מגיעים קצרים (<b>הרעבה</b>).</p>
""",
)

L3 = Lv(
    ("SJF: shortest job first", "SJF: העבודה הקצרה ראשונה"),
    ("Pick the shortest burst among the processes that have arrived.", "לבחור את הפרץ הקצר ביותר מבין התהליכים שהגיעו."),
    L3_LESSON,
    [
        Q(("Under SJF, P1 finishes at time 6. Who runs next?", "ב-SJF, P1 מסיים בזמן 6. מי רץ אחריו?"),
          ["P3", "P2", "Whoever arrived first", "The idle process"],
          ("At t=6 both P2 (burst 8) and P3 (burst 2) are waiting. SJF takes the shorter one, P3.",
           "בזמן 6 גם P2 (פרץ 8) וגם P3 (פרץ 2) מחכים. SJF לוקח את הקצר, P3."),
          ("SJF: shortest burst among arrived.", "SJF: הפרץ הקצר מבין אלה שהגיעו."),
          code=tbl([(0, 6), (1, 8), (2, 2)]),
          check=S([(0, 6), (1, 8), (2, 2)], "SJF", "slice:1")),
        Q(("What is the average waiting time under SJF for the same table?", "מהו זמן ההמתנה הממוצע ב-SJF לאותה טבלה?"),
          ["3.67", "5.67", "4", "3"],
          ("Order P1, P3, P2. Waits: 0, (8−2)−2 = 4, (16−1)−8 = 7. Sum 11, average 3.67. FCFS would give 5.67.",
           "הסדר P1, P3, P2. המתנות: 0, (8−2)−2 = 4, (16−1)−8 = 7. סכום 11, ממוצע 3.67. FCFS היה נותן 5.67."),
          ("SJF waits: 0, 4, 7.", "המתנות ב-SJF: 0, 4, 7."),
          code=tbl([(0, 6), (1, 8), (2, 2)]),
          check=S([(0, 6), (1, 8), (2, 2)], "SJF", "avg_wait")),
        Q(("Under SJF, in what order do the processes run?", "ב-SJF, באיזה סדר רצים התהליכים?"),
          ["P1, P2, P3", "P1, P3, P2", "P3, P1, P2", "P2, P1, P3"],
          ("At t=5 only P2 has arrived (P3 arrives at 6), so P2 runs 5–8 although P3 is shorter. Then P3.",
           "בזמן 5 רק P2 הגיע (P3 מגיע ב-6), לכן P2 רץ 5–8 למרות ש-P3 קצר יותר. אחר כך P3."),
          ("A process that has not arrived is not a candidate.", "תהליך שעוד לא הגיע אינו מועמד."),
          code=tbl([(0, 5), (1, 3), (6, 1)]),
          check=S([(0, 5), (1, 3), (6, 1)], "SJF", "order")),
        Q(("P1 (burst 10) is running under SJF when P2 (burst 1) arrives at time 1. When does P2 start?",
           "P1 (פרץ 10) רץ ב-SJF כש-P2 (פרץ 1) מגיע בזמן 1. מתי P2 מתחיל?"),
          ["10", "1", "2", "11"],
          ("SJF is non-preemptive: P1 keeps the CPU until time 10, then P2 runs.",
           "SJF לא נשלף: P1 שומר על המעבד עד זמן 10, ואז P2 רץ."),
          ("SJF never interrupts a running process.", "SJF אף פעם לא מפסיק תהליך שרץ."),
          code=tbl([(0, 10), (1, 1)]),
          check=S([(0, 10), (1, 1)], "SJF", "start:P2")),
        Q(("Which processes can starve under SJF?", "אילו תהליכים עלולים להיות מורעבים ב-SJF?"),
          [("Long ones, when short processes keep arriving", "ארוכים, כשמגיעים כל הזמן תהליכים קצרים"),
           ("Short ones", "קצרים"), ("The first to arrive", "הראשון שהגיע"), ("None, SJF is always fair", "אף אחד, SJF תמיד הוגן")],
          ("A long job is always passed over while shorter jobs keep showing up.",
           "עבודה ארוכה נדחית שוב ושוב כל עוד מגיעות עבודות קצרות יותר."),
          ("SJF can starve long jobs.", "SJF יכול להרעיב עבודות ארוכות.")),
    ],
    icon="🥇",
)

# ------------------------------------------------------------------ level 4
L4_LESSON = (
    """
<p><b>SRTF</b> (Shortest Remaining Time First) is the <b>preemptive</b> version of SJF. At every moment the CPU runs the process with the <b>least time remaining</b>. When a new process arrives, compare its burst with what is <b>left</b> of the running one (not with the running one's original burst). If the newcomer is smaller, the running process goes back to ready.</p>
<pre>P1 (arr 0, b 9)   P2 (arr 1, b 7)   P3 (arr 2, b 4)
t=1: P2 arrives, P1 has 8 left, 7 &lt; 8  -> preempt
t=2: P3 arrives, P2 has 6 left, 4 &lt; 6  -> preempt
|P1|P2|--- P3 ---|----- P2 -----|------- P1 -------|
0  1  2          6              12                 20
waits: P1 20-0-9 = 11, P2 12-1-7 = 4, P3 6-2-4 = 0  -> average 5
</pre>
<p>Keep a "remaining" column in your table and update it at every arrival. SRTF gives the smallest average waiting time of any algorithm when the bursts are known, and like SJF it can starve long processes.</p>
""",
    """
<p><b>SRTF</b> (Shortest Remaining Time First) הוא הגרסה ה<b>נשלפת</b> של SJF. בכל רגע המעבד מריץ את התהליך עם <b>הזמן הנותר הקטן ביותר</b>. כשמגיע תהליך חדש, משווים את הפרץ שלו למה ש<b>נשאר</b> לתהליך הרץ (לא לפרץ המקורי שלו). אם החדש קטן יותר, הרץ חוזר למצב מוכן.</p>
<pre>P1 (arr 0, b 9)   P2 (arr 1, b 7)   P3 (arr 2, b 4)
t=1: P2 arrives, P1 has 8 left, 7 &lt; 8  -> preempt
t=2: P3 arrives, P2 has 6 left, 4 &lt; 6  -> preempt
|P1|P2|--- P3 ---|----- P2 -----|------- P1 -------|
0  1  2          6              12                 20
waits: P1 20-0-9 = 11, P2 12-1-7 = 4, P3 6-2-4 = 0  -> average 5
</pre>
<p>מוסיפים לטבלה עמודת &quot;נשאר&quot; ומעדכנים אותה בכל הגעה. SRTF נותן את זמן ההמתנה הממוצע הקטן ביותר מבין כל האלגוריתמים כשהפרצים ידועים, וכמו SJF הוא יכול להרעיב תהליכים ארוכים.</p>
""",
)

L4 = Lv(
    ("SRTF: preempt when someone is shorter", "SRTF: מפסיקים כשמישהו קצר יותר"),
    ("Compare the newcomer with the time LEFT, not the original burst.", "משווים את החדש למה שנשאר, לא לפרץ המקורי."),
    L4_LESSON,
    [
        Q(("Compute the average waiting time under SRTF.", "חשבו את זמן ההמתנה הממוצע ב-SRTF."),
          ["5", "6", "11", "4"],
          ("P2 preempts P1 at t=1 (7 < 8) and P3 preempts P2 at t=2 (4 < 6). Waits 11, 4, 0 give 15/3 = 5.",
           "P2 שולף את P1 בזמן 1 (7 < 8) ו-P3 שולף את P2 בזמן 2 (4 < 6). המתנות 11, 4, 0 נותנות 15/3 = 5."),
          ("SRTF 9@0, 7@1, 4@2 gives 5 ms.", "SRTF עם 9@0, 7@1, 4@2 נותן 5 מ״ש."),
          code=tbl([(0, 9), (1, 7), (2, 4)]),
          check=S([(0, 9), (1, 7), (2, 4)], "SRTF", "avg_wait"), exam="2022A-4", has="5"),
        Q(("P1 (burst 8) is running. At time 3 P2 arrives with burst 6. Does SRTF preempt P1?",
           "P1 (פרץ 8) רץ. בזמן 3 מגיע P2 עם פרץ 6. האם SRTF שולף את P1?"),
          [("No: P1 has 5 left, less than 6", "לא: ל-P1 נשארו 5, פחות מ-6"),
           ("Yes: 6 is less than 8", "כן: 6 קטן מ-8"),
           ("Yes: SRTF always preempts on an arrival", "כן: SRTF תמיד שולף בהגעה"),
           ("No: SRTF never preempts", "לא: SRTF אף פעם לא שולף")],
          ("Compare with the REMAINING time: P1 ran 3 ms, so 5 are left, and 5 < 6. P1 continues.",
           "משווים לזמן הנותר: P1 רץ 3 מ״ש ונשארו לו 5, ו-5 < 6. P1 ממשיך."),
          ("Compare against the remaining time.", "משווים לזמן הנותר."),
          code=tbl([(0, 8), (3, 6)]),
          check=S([(0, 8), (3, 6)], "SRTF", "order", want="P1, P2")),
        Q(("Compute the average waiting time under SRTF.", "חשבו את זמן ההמתנה הממוצע ב-SRTF."),
          ["2.67", "3.33", "2", "4"],
          ("Gantt: P1 0–1, P2 1–2, P3 2–4, P2 4–7, P1 7–14. Waits: P1 6, P2 2, P3 0. Sum 8, average 2.67.",
           "גאנט: P1 0–1, P2 1–2, P3 2–4, P2 4–7, P1 7–14. המתנות: P1 6, P2 2, P3 0. סכום 8, ממוצע 2.67."),
          ("Update the remaining time at every arrival.", "מעדכנים את הזמן הנותר בכל הגעה."),
          code=tbl([(0, 8), (1, 4), (2, 2)]),
          check=S([(0, 8), (1, 4), (2, 2)], "SRTF", "avg_wait")),
        Q(("Which of these is a **preemptive** algorithm?", "איזה מאלה הוא אלגוריתם **נשלף**?"),
          ["SRTF", "FCFS", "SJF", "None of them"],
          ("SRTF can move a running process back to ready; FCFS and SJF never do.",
           "SRTF יכול להחזיר תהליך רץ למצב מוכן; FCFS ו-SJF אף פעם לא."),
          ("SRTF and Round Robin are preemptive.", "SRTF ו-Round Robin הם נשלפים."),
          exam="2020B-5", has="srtf"),
        Q(("Compute the **response time** of P2 under SRTF (time from arrival to its first run).",
           "חשבו את **זמן התגובה** של P2 ב-SRTF (מההגעה עד הריצה הראשונה)."),
          ["0", "3", "1", "5"],
          ("P2 arrives at 1 and preempts P1 immediately, so it first runs at 1: response 1 − 1 = 0.",
           "P2 מגיע בזמן 1 ושולף את P1 מיד, לכן הוא רץ לראשונה ב-1: תגובה 1 − 1 = 0."),
          ("Response = first run − arrival.", "תגובה = ריצה ראשונה − הגעה."),
          code=tbl([(0, 8), (1, 4), (2, 2)]),
          check=S([(0, 8), (1, 4), (2, 2)], "SRTF", "resp:P2")),
    ],
    icon="✂️",
)

# ------------------------------------------------------------------ level 5
L5_LESSON = (
    """
<p><b>Round Robin</b> gives each process a fixed <b>quantum</b> of CPU time, then moves it to the back of the ready queue. A process that needs less than a quantum simply finishes early.</p>
<p>The ordering rule that decides most exam questions: when a slice ends, put the processes that <b>arrived during that slice first</b>, and the process that was just preempted <b>behind them</b>.</p>
<pre>q = 4:  P1 (arr 0, b 9)  P2 (arr 1, b 7)  P3 (arr 3, b 4)
0-4   P1 runs (5 left).  P2 and P3 arrived  -> queue [P2, P3, P1]
4-8   P2 (3 left)                           -> queue [P3, P1, P2]
8-12  P3 done at 12                          -> queue [P1, P2]
12-16 P1 (1 left)  16-19 P2 done  19-20 P1 done
waits: P1 20-9 = 11, P2 19-1-7 = 11, P3 12-3-4 = 5  -> average 9
</pre>
<p>Two identities to remember: RR with an <b>infinite quantum</b> is FCFS, and when the quantum is <b>very small</b> most of the CPU time is wasted on context switching. RR never starves anyone.</p>
""",
    """
<p><b>Round Robin</b> נותן לכל תהליך <b>קוונטום</b> קבוע של זמן מעבד, ואז מעביר אותו לסוף תור המוכנים. תהליך שצריך פחות מקוונטום פשוט מסיים מוקדם.</p>
<p>כלל הסדר שמכריע את רוב שאלות המבחן: כשפרוסה מסתיימת, מכניסים לתור קודם את התהליכים ש<b>הגיעו במהלך הפרוסה</b>, ואת התהליך שזה עתה הופסק <b>מאחוריהם</b>.</p>
<pre>q = 4:  P1 (arr 0, b 9)  P2 (arr 1, b 7)  P3 (arr 3, b 4)
0-4   P1 runs (5 left).  P2 and P3 arrived  -> queue [P2, P3, P1]
4-8   P2 (3 left)                           -> queue [P3, P1, P2]
8-12  P3 done at 12                          -> queue [P1, P2]
12-16 P1 (1 left)  16-19 P2 done  19-20 P1 done
waits: P1 20-9 = 11, P2 19-1-7 = 11, P3 12-3-4 = 5  -> average 9
</pre>
<p>שני זהויות לזכור: RR עם <b>קוונטום אינסופי</b> הוא FCFS, וכשהקוונטום <b>קטן מאוד</b> רוב זמן המעבד מבוזבז על החלפות הקשר. RR לא מרעיב אף אחד.</p>
""",
)

L5 = Lv(
    ("Round Robin and the queue rule", "Round Robin וכלל התור"),
    ("Fixed time slices, and who goes behind whom.", "פרוסות זמן קבועות, ומי עומד מאחורי מי."),
    L5_LESSON,
    [
        Q(("Round Robin, quantum 4. Three processes of 7 ms arrive at time 0. What is the average waiting time?",
           "Round Robin, קוונטום 4. שלושה תהליכים של 7 מ״ש מגיעים בזמן 0. מהו זמן ההמתנה הממוצע?"),
          ["11", "7", "14", "8"],
          ("Slices P1, P2, P3, P1, P2, P3 end at 15, 18, 21. Waits are 15−7 = 8, 18−7 = 11, 21−7 = 14. Average 11.",
           "הפרוסות P1, P2, P3, P1, P2, P3 מסתיימות ב-15, 18, 21. המתנות: 15−7 = 8, 18−7 = 11, 21−7 = 14. ממוצע 11."),
          ("Three 7 ms jobs with q=4 give 11 ms.", "שלושה תהליכי 7 מ״ש עם q=4 נותנים 11 מ״ש."),
          code=tbl([(0, 7), (0, 7), (0, 7)]),
          check=S([(0, 7), (0, 7), (0, 7)], "RR", "avg_wait", q=4), exam="2021A-5", has="11"),
        Q(("Round Robin, quantum 2. What is the average waiting time?", "Round Robin, קוונטום 2. מהו זמן ההמתנה הממוצע?"),
          ["3.33", "4.33", "2.67", "3"],
          ("Slices: P1 0–2, P2 2–4, P3 4–5, P1 5–7, P2 7–8, P1 8–9. Waits: P1 4, P2 4, P3 2. Sum 10, average 3.33.",
           "פרוסות: P1 0–2, P2 2–4, P3 4–5, P1 5–7, P2 7–8, P1 8–9. המתנות: P1 4, P2 4, P3 2. סכום 10, ממוצע 3.33."),
          ("Turnaround − burst for each, then average.", "סבב פחות פרץ לכל אחד, ואז ממוצע."),
          code=tbl([(0, 5), (1, 3), (2, 1)]),
          check=S([(0, 5), (1, 3), (2, 1)], "RR", "avg_wait", q=2)),
        Q(("Round Robin, quantum 4. In what order do the slices run?", "Round Robin, קוונטום 4. באיזה סדר רצות הפרוסות?"),
          ["P1, P2, P3, P1, P2, P1", "P1, P3, P2, P1, P2, P1", "P1, P2, P1, P3, P2, P1", "P1, P2, P3, P2, P1"],
          ("P2 and P3 arrived during P1's slice, so they queue before the preempted P1: [P2, P3, P1].",
           "P2 ו-P3 הגיעו במהלך הפרוסה של P1, ולכן הם בתור לפני P1 שהופסק: [P2, P3, P1]."),
          ("Arrivals during the slice go before the preempted job.", "מי שהגיע בפרוסה נכנס לפני התהליך שהופסק."),
          code=tbl([(0, 9), (1, 7), (3, 4)]),
          check=S([(0, 9), (1, 7), (3, 4)], "RR", "order", q=4)),
        Q(("Round Robin with an **infinite quantum** is equivalent to which algorithm?",
           "Round Robin עם **קוונטום אינסופי** שקול לאיזה אלגוריתם?"),
          ["FCFS", "SJF", "SRTF", "Priority"],
          ("Nobody is ever preempted, so processes simply run in arrival order: FCFS.",
           "אף אחד לא מופסק, והתהליכים פשוט רצים לפי סדר הגעה: FCFS."),
          ("RR with q = infinity is FCFS.", "RR עם q = אינסוף הוא FCFS."),
          exam="2023B-4", has="fcfs"),
        Q(("When the quantum is very small, most CPU time is wasted on ____.",
           "כשהקוונטום קטן מאוד, רוב זמן המעבד מבוזבז על ____."),
          [("context switching", "החלפות הקשר"), ("busy waiting", "המתנה פעילה"),
           ("starvation", "הרעבה"), ("page faults", "החטאות דפים")],
          ("Every tiny slice costs a context switch, which does no useful work.",
           "כל פרוסה זעירה עולה החלפת הקשר, שאינה עבודה מועילה."),
          ("Tiny quantum = mostly context-switch overhead.", "קוונטום זעיר = בעיקר עלות החלפות הקשר."),
          exam="2017SA-5", has="context"),
    ],
    icon="🔄",
)

# ------------------------------------------------------------------ level 6
L6_LESSON = (
    """
<p>The theory questions of the exam are short and exact. Learn these as pairs.</p>
<table>
<tr><th>Term</th><th>Meaning</th></tr>
<tr><td>Preemptive</td><td>the scheduler can move a running process back to ready (SRTF, Round Robin). FCFS and SJF are non-preemptive.</td></tr>
<tr><td>CPU burst</td><td>a stretch of computing with no I/O between two I/O requests.</td></tr>
<tr><td>Starvation</td><td>a process never gets the CPU (low priority, or long jobs under SJF/SRTF). The cure is <b>aging</b>: raise the priority of a process the longer it waits.</td></tr>
<tr><td>Windows</td><td>the process that owns the <b>focus window</b> gets a quantum <b>three times</b> as long.</td></tr>
<tr><td>Linux</td><td>one full round in which every process that wants CPU time is served is an <b>epoch</b>. The course answer for Linux's approach is <b>Multilevel Queue</b>.</td></tr>
</table>
""",
    """
<p>שאלות התאוריה במבחן קצרות ומדויקות. לומדים אותן בזוגות.</p>
<table>
<tr><th>מושג</th><th>משמעות</th></tr>
<tr><td>נשלף (Preemptive)</td><td>המתזמן יכול להחזיר תהליך רץ למצב מוכן (SRTF, Round Robin). FCFS ו-SJF אינם נשלפים.</td></tr>
<tr><td>פרץ חישוב (CPU burst)</td><td>רצף חישוב בלי קלט/פלט בין שתי בקשות קלט/פלט.</td></tr>
<tr><td>הרעבה (Starvation)</td><td>תהליך לא מקבל מעבד לעולם (עדיפות נמוכה, או תהליכים ארוכים ב-SJF/SRTF). התרופה היא <b>הזדקנות (aging)</b>: מעלים עדיפות לתהליך ככל שהוא ממתין יותר.</td></tr>
<tr><td>Windows</td><td>התהליך ששייך ל<b>חלון הפוקוס</b> מקבל קוונטום ארוך <b>פי שלושה</b>.</td></tr>
<tr><td>Linux</td><td>סבב מלא שבו מטופלים כל התהליכים שרוצים מעבד נקרא <b>epoch</b>. התשובה בקורס לגישת התזמון של Linux היא <b>Multilevel Queue</b>.</td></tr>
</table>
""",
)

L6 = Lv(
    ("The theory words", "מילות התאוריה"),
    ("Preemptive, starvation, aging, epoch and the OS quirks.", "נשלף, הרעבה, aging, epoch והמוזרויות של מערכות ההפעלה."),
    L6_LESSON,
    [
        Q(("What are schedulers that can move a process from running to ready called?",
           "איך קוראים למתזמנים שיכולים להעביר תהליך ממצב רץ למצב מוכן?"),
          [("Preemptive", "נשלפים (preemptive)"), ("Non-preemptive", "לא נשלפים"), ("Cooperative-only", "שיתופיים בלבד"), ("Batch-only", "אצווה בלבד")],
          ("A scheduler that can take the CPU away from a running process is preemptive.",
           "מתזמן שיכול לקחת את המעבד מתהליך רץ הוא נשלף."),
          ("Running → ready by the scheduler = preemptive.", "רץ → מוכן בידי המתזמן = נשלף."),
          exam="2020A-4", has="preempt"),
        Q(("Low-priority processes never get to run under priority scheduling. What is this problem called, and how is it fixed?",
           "תהליכים בעדיפות נמוכה אף פעם לא רצים בתזמון עדיפויות. איך קוראים לבעיה ואיך פותרים אותה?"),
          [("Starvation, fixed by aging", "הרעבה, נפתרת ב-aging"), ("Convoy effect, fixed by a bigger quantum", "אפקט שיירה, נפתר בקוונטום גדול יותר"),
           ("Thrashing, fixed by more RAM", "תזזית, נפתרת ביותר זיכרון"), ("Deadlock, fixed by a reboot", "קיפאון, נפתר באתחול")],
          ("Starvation is cured by aging: the longer a process waits, the higher its priority becomes.",
           "הרעבה נפתרת ב-aging: ככל שתהליך ממתין יותר, העדיפות שלו עולה."),
          ("Starvation → aging.", "הרעבה → aging."),
          exam="2021A-4", has="starvation"),
        Q(("Which single process does Windows give a **triple-length** time slice, as a personal-computing OS?",
           "לאיזה תהליך Windows נותנת פרוסת זמן **פי שלושה**, כמערכת למחשב אישי?"),
          [("The process of the focus window", "תהליך חלון הפוקוס"), ("The first process started", "התהליך הראשון שהופעל"),
           ("The process with the most threads", "התהליך עם הכי הרבה תהליכונים"), ("The kernel", "הליבה")],
          ("Windows favours the window the user is looking at: its process gets a 3× longer quantum.",
           "Windows מעדיפה את החלון שהמשתמש מסתכל עליו: התהליך שלו מקבל קוונטום ארוך פי 3."),
          ("Focus window = 3× quantum.", "חלון פוקוס = קוונטום ×3."),
          exam="2023A-5", has="focus"),
        Q(("In the Linux scheduler, one round over all processes that request CPU time is called ____.",
           "בתזמון של Linux, סבב אחד על כל התהליכים שמבקשים זמן מעבד נקרא ____."),
          ["an epoch", "a quantum", "a burst", "a convoy"],
          ("The word is epoch: one round in which every runnable process gets its share.",
           "המילה היא epoch: סבב אחד שבו כל תהליך ריץ מקבל את חלקו."),
          ("Linux round = epoch.", "סבב של Linux = epoch."),
          exam="2020A-7", has="epoch"),
        Q(("Which scheduling approach does Linux use, according to the course?", "באיזו גישת תזמון Linux משתמשת, לפי הקורס?"),
          ["Multilevel Queue", "Pure FCFS", "Shortest Job First", "Pure Round Robin"],
          ("The course answer is Multilevel Queue.", "התשובה בקורס היא Multilevel Queue."),
          ("Linux = Multilevel Queue (with epochs).", "Linux = Multilevel Queue (עם epochs)."),
          exam="2024A-5", has="multilevel"),
        Q(("During which kind of burst does a process add two register values together?",
           "באיזה סוג פרץ תהליך מחבר שני ערכי אוגרים?"),
          [("CPU burst", "פרץ חישוב (CPU burst)"), ("I/O burst", "פרץ קלט/פלט"), ("Memory burst", "פרץ זיכרון"), ("Wait burst", "פרץ המתנה")],
          ("Adding registers is pure computation with no I/O: a CPU burst.", "חיבור אוגרים הוא חישוב טהור בלי קלט/פלט: פרץ חישוב."),
          ("Pure computing = CPU burst.", "חישוב טהור = פרץ חישוב."),
          exam="2020B-4", has="cpu burst"),
    ],
    icon="📖",
)

# ------------------------------------------------------------------ level 7 (boss)
L7_LESSON = (
    """
<p>This is the exam level. No new theory, only the real question types. Before you start:</p>
<ol>
<li>Build the table (arrival, burst) and draw the Gantt chart for the algorithm named in the question.</li>
<li>Read each completion time, then <code>waiting = completion &minus; arrival &minus; burst</code>.</li>
<li>Average = sum / number of processes.</li>
<li>Round Robin: arrivals during a slice queue <b>before</b> the preempted process. SRTF: compare with the time <b>left</b>.</li>
</ol>
<p>Each question is a past-exam item or built the same way. You need 80% to pass.</p>
""",
    """
<p>זה שלב המבחן. אין תאוריה חדשה, רק סוגי השאלות האמיתיים. לפני שמתחילים:</p>
<ol>
<li>בונים טבלה (הגעה, פרץ) ומציירים גאנט לאלגוריתם שנזכר בשאלה.</li>
<li>קוראים את זמן הסיום של כל תהליך, ואז <code>waiting = completion &minus; arrival &minus; burst</code>.</li>
<li>ממוצע = סכום חלקי מספר התהליכים.</li>
<li>Round Robin: מי שהגיע במהלך פרוסה נכנס לתור <b>לפני</b> התהליך שהופסק. SRTF: משווים לזמן שנשאר.</li>
</ol>
<p>כל שאלה היא פריט ממבחן קודם או בנויה באותו אופן. צריך 80% כדי לעבור.</p>
""",
)

L7 = Lv(
    ("Boss: scheduling exam", "בוס: מבחן תזמון"),
    ("Real exam items on FCFS, SRTF and Round Robin.", "שאלות מהמבחנים על FCFS, SRTF ו-Round Robin."),
    L7_LESSON,
    [
        Q(("Compute the average waiting time under Round Robin, quantum 4.", "חשבו את זמן ההמתנה הממוצע ב-Round Robin עם קוונטום 4."),
          ["9.5", "9", "11", "10"],
          ("Slices: P1 0–4, P2 4–7, P3 7–11, P4 11–12, P1 12–16, P3 16–19, P1 19–20. Waits 11, 4, 12, 11 give 38/4 = 9.5.",
           "פרוסות: P1 0–4, P2 4–7, P3 7–11, P4 11–12, P1 12–16, P3 16–19, P1 19–20. המתנות 11, 4, 12, 11 נותנות 38/4 = 9.5."),
          ("RR q=4 on 9, 3, 7, 1 gives 9.5.", "RR עם q=4 על 9, 3, 7, 1 נותן 9.5."),
          code=tbl([(0, 9), (0, 3), (0, 7), (0, 1)]),
          check=S([(0, 9), (0, 3), (0, 7), (0, 1)], "RR", "avg_wait", q=4), exam="2019A-4", has="9.5"),
        Q(("Compute the average waiting time under FCFS.", "חשבו את זמן ההמתנה הממוצע ב-FCFS."),
          ["6", "7", "12", "14"],
          ("Gantt: 0–7, 7–14, 14–21. Waits 0, 14−1−7 = 6, 21−2−7 = 12. Average 18/3 = 6.",
           "גאנט: 0–7, 7–14, 14–21. המתנות 0, 14−1−7 = 6, 21−2−7 = 12. ממוצע 18/3 = 6."),
          ("Waits 0, 6, 12.", "המתנות 0, 6, 12."),
          code=tbl([(0, 7), (1, 7), (2, 7)]),
          check=S([(0, 7), (1, 7), (2, 7)], "FCFS", "avg_wait"), exam="2021B-5", has="6"),
        Q(("Compute the average waiting time under Round Robin, quantum 4 (staggered arrivals).",
           "חשבו את זמן ההמתנה הממוצע ב-Round Robin עם קוונטום 4 (הגעות מדורגות)."),
          ["9", "10", "7", "11"],
          ("P1 0–4, P2 4–8, P3 8–12, P1 12–16, P2 16–19, P1 19–20. Waits P1 11, P2 11, P3 5. Sum 27, average 9.",
           "P1 0–4, P2 4–8, P3 8–12, P1 12–16, P2 16–19, P1 19–20. המתנות P1 11, P2 11, P3 5. סכום 27, ממוצע 9."),
          ("Arrivals during a slice queue before the preempted job.", "מי שהגיע בפרוסה נכנס לפני התהליך שהופסק."),
          code=tbl([(0, 9), (1, 7), (3, 4)]),
          check=S([(0, 9), (1, 7), (3, 4)], "RR", "avg_wait", q=4), exam="2022B-4", has="9"),
        Q(("Compute the average waiting time under SRTF.", "חשבו את זמן ההמתנה הממוצע ב-SRTF."),
          ["3", "4", "5.33", "2"],
          ("P1 0–1, P2 1–4, P1 4–10, P3 10–32. Waits: P1 (10−0)−7 = 3, P2 0, P3 10−4 = 6. Sum 9, average 9/3 = 3.",
           "P1 0–1, P2 1–4, P1 4–10, P3 10–32. המתנות: P1 3, P2 0, P3 10−4 = 6. ממוצע (3+0+6)/3 = 3."),
          ("SRTF on 7@0, 3@1, 22@4 gives 3.", "SRTF על 7@0, 3@1, 22@4 נותן 3."),
          code=tbl([(0, 7), (1, 3), (4, 22)]),
          check=S([(0, 7), (1, 3), (4, 22)], "SRTF", "avg_wait")),
        Q(("Compute the average waiting time under FCFS (four processes).", "חשבו את זמן ההמתנה הממוצע ב-FCFS (ארבעה תהליכים)."),
          ["4.75", "5", "4", "19"],
          ("Gantt: 0–7, 7–11, 11–12, 12–16. Waits 0, 5, 7, 7 give 19/4 = 4.75.",
           "גאנט: 0–7, 7–11, 11–12, 12–16. המתנות 0, 5, 7, 7 נותנות 19/4 = 4.75."),
          ("Sum 19 over 4 processes.", "סכום 19 על 4 תהליכים."),
          code=tbl([(0, 7), (2, 4), (4, 1), (5, 4)]),
          check=S([(0, 7), (2, 4), (4, 1), (5, 4)], "FCFS", "avg_wait"), exam="2017SB-3", has="4.75"),
        Q(("When does Round Robin preempt a running process?", "מתי Round Robin מפסיק תהליך רץ?"),
          [("When its quantum expires", "כשהקוונטום שלו נגמר"), ("When a shorter process arrives", "כשמגיע תהליך קצר יותר"),
           ("When it starts an I/O burst", "כשהוא מתחיל פרץ קלט/פלט"), ("Never, it is non-preemptive", "אף פעם, הוא לא נשלף")],
          ("RR cuts a process off only when its quantum is used up.", "RR מפסיק תהליך רק כשהקוונטום שלו נוצל."),
          ("RR preempts on quantum expiry.", "RR מפסיק בתום הקוונטום."),
          exam="2024B-4", has="quantum"),
    ],
    icon="🏆",
    boss=True,
)

COURSE = Course(
    "sched", "🕒",
    ("CPU scheduling: Gantt charts and waiting time", "תזמון מעבד: תרשימי גאנט וזמני המתנה"),
    ("Scheduling is the guaranteed-points topic: about half theory words and half Gantt arithmetic. This course goes from one process and three formulas up to the exam's Round Robin and SRTF tables. Each level has a short lesson, then questions. Every level is open; 80% passes.",
     "תזמון הוא הנושא של הנקודות המובטחות: בערך חצי מילות תאוריה וחצי חשבון עם תרשימי גאנט. הקורס עובר מתהליך אחד ושלוש נוסחאות ועד טבלאות ה-Round Robin וה-SRTF של המבחן. בכל שלב שיעור קצר ואחריו שאלות. כל השלבים פתוחים; 80% עובר."),
    "scheduling",
    [L1, L2, L3, L4, L5, L6, L7],
)
