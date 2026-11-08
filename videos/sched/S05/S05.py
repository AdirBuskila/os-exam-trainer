# -*- coding: utf-8 -*-
"""S05 · Round Robin וכלל התור — video script (build: tools/video/vid.py S05).

Source: src/courses/sched.py level 5 (lesson + goal: fixed time slices, and who goes behind whom: when a slice ends,
the processes that arrived DURING it enter the queue first, the preempted process behind them).
Exam anchor: none fits (the free scheduling bank items are theory items), so the exam scene is an original
"שאלה בסגנון מבחן" (bank={}): Round Robin, quantum 2, on 3@0 5@1 4@3, average waiting 4.
Avoided on purpose: the level-5 quiz tables (three 7 ms jobs = 2021A-5, 5@0 3@1 1@2 with q=2, 9@0 7@1 4@3 = the
lesson's and 2022B-4's table) and its two theory items (2023B-4 infinite quantum, 2017SA-5 tiny quantum), the boss's
9 3 7 1 (2019A-4); every course table is refused by w.assert_fresh.
Here: quantum 3 on 7@0 1@1 4@2 1@6 (the rule decides the queue at t=3 and at t=7), the same set with the wrong order
(the preempted process first) for the trap, and the exam set. The queue after every slice comes from w.rr_steps, an
event replay of the course rule whose Gantt chart is asserted equal to sims.schedule's; arrivals at the exact instant
of a preemption (which the lesson does not order) are refused there.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_sched as w

# ---------------------------------------------------------------- numbers (verified)
A = [(0, 7), (1, 1), (2, 4), (6, 1)]
RA = w.run(A, "RR", 3)
SA = w.rr_steps(A, 3)
assert [(s["start"], s["end"], s["run"], s["queue"]) for s in SA] == [
    (0, 3, "P1", ["P2", "P3", "P1"]), (3, 4, "P2", ["P3", "P1"]), (4, 7, "P3", ["P1", "P4", "P3"]),
    (7, 10, "P1", ["P4", "P3", "P1"]), (10, 11, "P4", ["P3", "P1"]), (11, 12, "P3", ["P1"]), (12, 13, "P1", [])]
assert RA["finish"] == [13, 4, 12, 11] and RA["wait"] == [6, 2, 6, 4] and RA["avg_wait"] == 4.5


def wrong_rr(procs, q):
    """the same replay with the WRONG order (the preempted process before the arrivals), only for the trap"""
    names = ["P%d" % (i + 1) for i in range(len(procs))]
    arr = {n: procs[i][0] for i, n in enumerate(names)}
    rem = {n: procs[i][1] for i, n in enumerate(names)}
    t, queue = 0, [n for n in names if arr[n] <= 0]
    adm, sl, fin = set(queue), [], {}
    while any(rem.values()):
        if not queue:
            t = min(arr[n] for n in names if n not in adm)
            new = [n for n in names if arr[n] == t]
            queue += new
            adm |= set(new)
            continue
        p = queue.pop(0)
        d = min(q, rem[p])
        s, e = t, t + d
        rem[p] -= d
        new = [n for n in names if n not in adm and s < arr[n] <= e]
        if rem[p] > 0:
            queue.append(p)
        else:
            fin[p] = e
        queue += new
        adm |= set(new)
        sl.append((p, s, e))
        t = e
    wait = [fin[n] - arr[n] - procs[i][1] for i, n in enumerate(names)]
    return sl, wait


WSL, WW = wrong_rr(A, 3)
assert WSL[:3] == [("P1", 0, 3), ("P1", 3, 6), ("P2", 6, 7)] and WW == [4, 5, 7, 5] and sum(WW) / 4 == 5.25
assert sum(WW) / 4 != RA["avg_wait"]

X = [(0, 3), (1, 5), (3, 4)]
RX = w.run(X, "RR", 2)
SX = w.rr_steps(X, 2)
assert [(s["start"], s["end"], s["run"], s["queue"]) for s in SX] == [
    (0, 2, "P1", ["P2", "P1"]), (2, 4, "P2", ["P1", "P3", "P2"]), (4, 5, "P1", ["P3", "P2"]),
    (5, 7, "P3", ["P2", "P3"]), (7, 9, "P2", ["P3", "P2"]), (9, 11, "P3", ["P2"]), (11, 12, "P2", [])]
assert RX["finish"] == [5, 12, 11] and RX["wait"] == [2, 6, 4] and RX["avg_wait"] == 4
w.assert_fresh(A, X)

GA = w.gantt("ga", RA, slices=w.rr_slices(SA), width=1000)
QA = w.rrq("qa", SA)
TA = w.ptable("ta", RA, cols=("arr", "burst", "fin", "turn", "wait"), shown=("arr", "burst", "fin"),
              avg="ממוצע: " + w.ltr("(6 + 2 + 6 + 4) / 4 = 4.5"))
GT = w.gantt("gt", RA, slices=w.rr_slices(SA), width=1000, hidden=False, finishes=False)
GW = w.gantt("gw", RA, slices=WSL[:3], width=1000, unit=(1000 - 60) / 13, finishes=False, hidden=False)
assert all(s["run"] for s in SA + SX)          # no idle step: slice i of the chart = step i of the queue strip
GX = w.gantt("gx", RX, slices=w.rr_slices(SX), width=1000)
QXS = w.rrq("qx", SX)
QX = ("Process  Arrival  Burst\n" + "\n".join("P%d       %-9d%d" % (i + 1, a, b) for i, (a, b) in enumerate(X)))


def step_show(pfx, gp, i, steps):
    """ids for one Round Robin step: the queue row, the slice, and the completion mark if it finished"""
    s = steps[i]
    ids = [f"{pfx}-r{i}", f"{gp}-s{i}"]
    if s["done"]:
        ids.append(f"{gp}-f-{s['run']}")
    return show(*ids)


# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נלמד את Round Robin: כל תהליך מקבל פרוסת זמן קבועה, ועובר לסוף התור."),
    P("ונלמד את הכלל שמכריע כמעט כל שאלת מבחן: מי עומד מאחורי מי."),
    P("ובסוף נפתור שאלה בסגנון מבחן.", hold=0.4),
], stage='<div class="kicker">S05 · תזמון מעבד: תרשימי גאנט וזמני המתנה</div><h1>Round Robin וכלל התור</h1>'
         '<p>פרוסות זמן קבועות, ומי עומד מאחורי מי.</p>', layout="title")

idea = Scene("idea", "הכלל", [
    P("ב-Round Robin יש תור מוכנים אחד, ופרוסת זמן קבועה שנקראת **קוונטום**.", do=show("i-1"),
      say="ברָאוּנְד רוֹבִּין יש תור מוכנים אחד, ופרוסת זמן קבועה שנקראת קְוַונְטוּם."),
    P("התהליך שבראש התור רץ לכל היותר קוונטום אחד.", do=show("i-2"), say="התהליך שבראש התור רץ לכל היותר קְוַונְטוּם אחד."),
    P("אם הוא צריך פחות, הוא פשוט מסיים מוקדם, והבא בתור עולה מיד.", do=show("i-3")),
    P("ואם הקוונטום נגמר והוא עוד לא סיים, הוא נשלף ועובר **לסוף** התור.", do=show("i-4"),
      say="ואם הקְוַונְטוּם נגמר והוא עוד לא סיים, הוא נשלף ועובר לסוף התור."),
    P("והכלל החשוב: מי שהגיע **במהלך** הפרוסה נכנס לתור קודם. ואת התהליך שנשלף מכניסים **אחריהם**.",
      do=show("i-c1")),
    P("בשרטוט נסמן את מי שהגיע זה עתה בטורקיז, ואת מי שנשלף בצהוב.", do=show("i-c2"), hold=0.4),
], stage=w.stack(w.line("i-1", "תור אחד, <b>קוונטום</b> קבוע"),
                 w.line("i-2", "ראש התור רץ <b>לכל היותר</b> קוונטום"),
                 w.line("i-3", "סיים מוקדם ← הבא עולה מיד"),
                 w.line("i-4", "הקוונטום נגמר ← <b>לסוף</b> התור"), gap=30),
   panel=st.card("i-c1", "rule", "🔑 קודם מי שהגיע במהלך הפרוסה, ואחריו מי שנשלף")
         + st.card("i-c2", "ex", f'{w.chip("P2", "sc-new")} הגיע זה עתה &nbsp; {w.chip("P1", "sc-back")} נשלף'))

ex = Scene("ex", "דוגמה", [
    P("קוונטום 3. P1 עם פרץ שבע מגיע בזמן 0, P2 עם פרץ אחת בזמן 1, P3 עם פרץ ארבע בזמן 2, ו-P4 עם פרץ אחת בזמן 6.",
      say="קְוַונְטוּם שלוש. פִּי אחת עם פרץ שבע מגיע בזמן אפס, פִּי שתיים עם פרץ אחת בזמן אחת, פִּי שלוש עם פרץ ארבע בזמן שתיים, ופִּי ארבע עם פרץ אחת בזמן שש."),
    P("P1 רץ מאפס עד שלוש. בזמן הזה הגיעו P2 ו-P3. הם נכנסים לתור קודם, ו-P1 אחריהם.",
      do=step_show("qa", "ga", 0, SA) + show("ex-c1"),
      say="פִּי אחת רץ מאפס עד שלוש. בזמן הזה הגיעו פִּי שתיים ופִּי שלוש. הם נכנסים לתור קודם, ופִּי אחת אחריהם."),
    P("P2 צריך רק יחידה אחת. הוא מסיים בזמן 4, לפני שהקוונטום נגמר.",
      do=step_show("qa", "ga", 1, SA) + show("ex-c2"),
      say="פִּי שתיים צריך רק יחידה אחת. הוא מסיים בזמן ארבע, לפני שהקְוַונְטוּם נגמר."),
    P("P3 רץ מארבע עד שבע. באמצע, בזמן 6, הגיע P4. אז P4 נכנס לפני P3, שנשלף.",
      do=step_show("qa", "ga", 2, SA),
      say="פִּי שלוש רץ מארבע עד שבע. באמצע, בזמן שש, הגיע פִּי ארבע. אז פִּי ארבע נכנס לפני פִּי שלוש, שנשלף."),
    P("P1 חוזר לעוד קוונטום, משבע עד עשר, ועובר שוב לסוף התור.", do=step_show("qa", "ga", 3, SA),
      say="פִּי אחת חוזר לעוד קְוַונְטוּם, משבע עד עשר, ועובר שוב לסוף התור."),
    P("P4 רץ יחידה אחת ומסיים בזמן 11. P3 צריך עוד יחידה, ומסיים ב-12.",
      do=step_show("qa", "ga", 4, SA) + step_show("qa", "ga", 5, SA),
      say="פִּי ארבע רץ יחידה אחת, ומסיים בזמן אחת עשרה. פִּי שלוש צריך עוד יחידה, ומסיים בשתים עשרה."),
    P("ו-P1, שרץ כבר שש, צריך עוד אחת. הוא מסיים אחרון, בזמן 13.", do=step_show("qa", "ga", 6, SA), hold=0.4,
      say="ופִּי אחת, שרץ כבר שש, צריך עוד אחת. הוא מסיים אחרון, בזמן שלוש עשרה."),
], stage=w.stack(GA, QA, gap=14),
   panel=st.card("ex-c1", "rule", "🔑 בסוף כל פרוסה: קודם מי שהגיע, אחר כך מי שנשלף")
         + st.card("ex-c2", "ex", "מי שסיים לפני סוף הקוונטום ← הבא עולה מיד"))

res = Scene("res", "זמני ההמתנה", [
    P("עכשיו הטבלה. זמני הסיום כבר בתרשים: שלוש עשרה, ארבע, שתים עשרה ואחת עשרה.", do=show("res-g")),
    P("סבב הוא סיום פחות הגעה: שלוש עשרה, שלוש, עשר וחמש.",
      do=show(*[f"ta-P{i}-turn" for i in range(1, 5)])),
    P("והמתנה היא סבב פחות פרץ: שש, שתיים, שש וארבע.", do=show(*[f"ta-P{i}-wait" for i in range(1, 5)])),
    P("שימו לב ל-P1: הוא רץ בשלוש חתיכות, ובכל זאת הנוסחה נותנת שש, בלי לספור חורים.", do=show("res-c1"),
      say="שימו לב לפִּי אחת: הוא רץ בשלוש חתיכות, ובכל זאת הנוסחה נותנת שש, בלי לספור חורים."),
    P("הסכום שמונה עשרה, חלקי ארבע: ארבע וחצי.", do=show("ta-avg"), hold=0.4),
], stage=w.stack(f'<div id="res-g" class="h">{w.gantt("gs", RA, slices=w.rr_slices(SA), width=1000, hidden=False)}</div>',
                 TA, gap=16),
   panel=st.card("res-c1", "rule", '🔑 P1 בשלוש חתיכות<span class="sc-calc">13 − 0 − 7 = 6</span>'))

trap = Scene("trap", "הסדר ההפוך", [
    P("ומה אם מחזירים את הנשלף לתור **לפני** מי שהגיע? זו הטעות הנפוצה.", do=show("tr-1")),
    P("בזמן 3, P1 היה נכנס ראשון. הוא היה רץ שוב, משלוש עד שש.", do=show("tr-g"),
      say="בזמן שלוש, פִּי אחת היה נכנס ראשון. הוא היה רץ שוב, משלוש עד שש."),
    P("ו-P2, שצריך יחידה אחת בלבד, היה מחכה עד זמן 6.", do=show("tr-2"),
      say="ופִּי שתיים, שצריך יחידה אחת בלבד, היה מחכה עד זמן שש."),
    P("בסוף החישוב יוצא ממוצע חמש ורבע, במקום ארבע וחצי. תשובה שגויה, אחרי עבודה מלאה.", do=show("tr-3")),
    P("אז בכל סוף פרוסה עוצרים ושואלים: מי הגיע בזמן שהיא רצה? הם קודם.", do=show("tr-c"), hold=0.5),
], stage=w.stack(w.line("tr-1", "הסדר ה<b>הפוך</b>: הנשלף לפני מי שהגיע ✗"),
                 f'<div id="tr-g" class="h">{GW}</div>',
                 w.line("tr-2", "P2 מחכה עד זמן 6"),
                 w.line("tr-3", "ממוצע " + w.ltr("5.25") + " במקום " + w.ltr("4.5") + " ✗"), gap=28),
   panel=st.card("tr-c", "trap", "⚠️ בסוף פרוסה: מי הגיע במהלכה? הם לפני הנשלף"))

exam = Scene("exam", "שאלה בסגנון מבחן", [
    P("שאלה בסגנון מבחן: Round Robin עם קוונטום 2. חשבו את זמן ההמתנה הממוצע.",
      say="שאלה בסגנון מבחן: רָאוּנְד רוֹבִּין עם קְוַונְטוּם שתיים. חשבו את זמן ההמתנה הממוצע."),
    P("P1 רץ מאפס עד שתיים. P2 הגיע בזמן 1, אז הוא לפני P1.", do=step_show("qx", "gx", 0, SX),
      say="פִּי אחת רץ מאפס עד שתיים. פִּי שתיים הגיע בזמן אחת, אז הוא לפני פִּי אחת."),
    P("P2 רץ משתיים עד ארבע. בזמן 3 הגיע P3: הוא נכנס אחרי P1, אבל לפני P2.", do=step_show("qx", "gx", 1, SX),
      say="פִּי שתיים רץ משתיים עד ארבע. בזמן שלוש הגיע פִּי שלוש: הוא נכנס אחרי פִּי אחת, אבל לפני פִּי שתיים."),
    P("P1 צריך עוד יחידה אחת, ומסיים בזמן 5.", do=step_show("qx", "gx", 2, SX),
      say="פִּי אחת צריך עוד יחידה אחת, ומסיים בזמן חמש."),
    P("משם התור מתחלף בין P3 ל-P2: P3 מסיים באחת עשרה, ו-P2 בשתים עשרה.",
      do=step_show("qx", "gx", 3, SX) + step_show("qx", "gx", 4, SX) + step_show("qx", "gx", 5, SX)
      + step_show("qx", "gx", 6, SX),
      say="משם התור מתחלף בין פִּי שלוש לפִּי שתיים: פִּי שלוש מסיים באחת עשרה, ופִּי שתיים בשתים עשרה."),
    P("המתנות: P1 חמש פחות שלוש, שתיים. P2 שתים עשרה פחות אחת פחות חמש, שש.", do=show("x-w1", "x-w1b"),
      say="המתנות: פִּי אחת, חמש פחות שלוש, שתיים. פִּי שתיים, שתים עשרה, פחות אחת, פחות חמש. שש."),
    P("ו-P3: אחת עשרה פחות שלוש פחות ארבע, ארבע. הסכום שתים עשרה, חלקי שלוש: ארבע.", do=show("x-w2", "x-w2b", "x-ans"),
      hold=0.5, say="ופִּי שלוש: אחת עשרה, פחות שלוש, פחות ארבע. ארבע. הסכום שתים עשרה, חלקי שלוש: ארבע."),
], stage=w.stack(GX, QXS, gap=14),
   panel='<div class="qstem"><span class="qid">בסגנון מבחן</span>Round Robin עם קוונטום 2. חשבו את זמן ההמתנה '
         'הממוצע.</div>'
         f'<pre class="qcode">{QX}</pre>'
         '<div class="sc-evs"><span id="x-w1" class="sc-calc h">P1: 5 − 0 − 3 = 2</span>'
         '<span id="x-w1b" class="sc-calc h">P2: 12 − 1 − 5 = 6</span>'
         '<span id="x-w2" class="sc-calc h">P3: 11 − 3 − 4 = 4</span>'
         '<span id="x-w2b" class="sc-calc h">(2 + 6 + 4) / 3 = 4</span></div>'
         '<div id="x-ans" class="qans h"><span class="k">תשובה:</span> ממוצע ההמתנה 4 מ״ש</div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום: ב-Round Robin כל אחד רץ לכל היותר קוונטום, ואם לא סיים, עובר לסוף התור.", do=show("r-1"),
      say="לסיכום: ברָאוּנְד רוֹבִּין כל אחד רץ לכל היותר קְוַונְטוּם, ואם לא סיים, עובר לסוף התור."),
    P("מי שצריך פחות מקוונטום מסיים מוקדם, והבא עולה מיד.", do=show("r-2"),
      say="מי שצריך פחות מקְוַונְטוּם מסיים מוקדם, והבא עולה מיד."),
    P("בסוף כל פרוסה: קודם מי שהגיע במהלכה, ורק אחריהם מי שנשלף.", do=show("r-3")),
    P("וההמתנה, כמו תמיד, היא סיום פחות הגעה פחות פרץ. נתראה ברמה הבאה.", do=show("r-4"), hold=0.6),
], stage=GT,
   panel=st.card("r-1", "rule", "🔑 לכל היותר קוונטום, ואז לסוף התור")
         + st.card("r-2", "ex", "פחות מקוונטום: מסיים מוקדם")
         + st.card("r-3", "trap", "⚠️ מי שהגיע במהלך הפרוסה ← לפני הנשלף")
         + st.card("r-4", "rule", "🔑 המתנה = סיום − הגעה − פרץ"))

VIDEO = Video("S05", "sched", "Round Robin וכלל התור", [title, idea, ex, res, trap, exam, recap], bank={})
