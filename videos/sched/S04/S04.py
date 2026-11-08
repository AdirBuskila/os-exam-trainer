# -*- coding: utf-8 -*-
"""S04 · SRTF: מפסיקים כשמישהו קצר יותר — video script (build: tools/video/vid.py S04).

Source: src/courses/sched.py level 4 (lesson + goal: SRTF is preemptive SJF; at every arrival compare the newcomer
with the time LEFT to the running process, not with its original burst; keep a "remaining" column).
Exam anchor: none fits (the free scheduling bank items are theory items), so the exam scene is an original
"שאלה בסגנון מבחן" (bank={}): SRTF on 7@1 7@2 6@5 1@6, average waiting 4.5 and the response time of P1.
Avoided on purpose: the level-4 quiz tables (9@0 7@1 4@2 = 2022A-4, 8@0 6@3, 8@0 4@1 2@2) and its preemptive item
2020B-5, the boss's SRTF table 7@0 3@1 22@4, and every other course table (w.assert_fresh).
Here: 7@0 4@2 1@3 3@5: two preemptions, then at t=5 a newcomer (3) shorter than P2's original burst (4) but not
shorter than what P2 has left (2): no preemption. Every chart, comparison and number comes from sims.schedule
(w_sched.run, strict: a tie would raise) and w_sched.srtf_events, asserted below.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_sched as w

# ---------------------------------------------------------------- numbers (verified)
A = [(0, 7), (2, 4), (3, 1), (5, 3)]
RA = w.run(A, "SRTF")
assert RA["gantt"] == [("P1", 0, 2), ("P2", 2, 3), ("P3", 3, 4), ("P2", 4, 7), ("P4", 7, 10), ("P1", 10, 15)]
EV = w.srtf_events(A, RA)
assert EV == [(2, "P2", 4, "P1", 5, True), (3, "P3", 1, "P2", 3, True), (5, "P4", 3, "P2", 2, False)]
assert A[1][1] == 4 and 3 < 4                      # the trap: 3 is below P2's ORIGINAL burst, above what is left
assert RA["finish"] == [15, 7, 4, 10] and RA["wait"] == [8, 1, 0, 2] and RA["avg_wait"] == 2.75
assert RA["resp"][0] == 0 and RA["wait"][0] == 8   # start - arrival would say 0 for P1: wrong for a split process

X = [(1, 7), (2, 7), (5, 6), (6, 1)]
RX = w.run(X, "SRTF")
assert RX["gantt"] == [("P1", 1, 6), ("P4", 6, 7), ("P1", 7, 9), ("P3", 9, 15), ("P2", 15, 22)]
EX = w.srtf_events(X, RX)
assert EX[1:] == [(2, "P2", 7, "P1", 6, False), (5, "P3", 6, "P1", 3, False), (6, "P4", 1, "P1", 2, True)]
assert RX["wait"] == [1, 13, 4, 0] and sum(RX["wait"]) == 18 and RX["avg_wait"] == 4.5 and RX["resp"][0] == 0
w.assert_fresh(A, X)

REM = {"P1": '7 <span id="ta-r1a" class="h">→ 5</span>',
       "P2": '4 <span id="ta-r2a" class="h">→ 3</span> <span id="ta-r2b" class="h">→ 2</span>'}
GA = w.gantt("ga", RA, width=1000, arrivals=True)
TA = w.ptable("ta", RA, cols=("arr", "burst", "rem", "fin", "wait"), shown=("arr", "burst"), cls="sm",
              extra={("P1", "rem"): REM["P1"], ("P2", "rem"): REM["P2"], ("P3", "rem"): "1", ("P4", "rem"): "3"},
              avg="ממוצע: " + w.ltr("(8 + 1 + 0 + 2) / 4 = 2.75"))
for nm in ("P1", "P2", "P3", "P4"):                 # the remaining column is visible from the start
    TA = TA.replace(f'id="ta-{nm}-rem" class="sc-v h"', f'id="ta-{nm}-rem" class="sc-v"')
GW = w.gantt("gw", RA, width=1000, finishes=False, hidden=False, bands=[("w0", 2, 10)])
GX = w.gantt("gx", RX, width=1000)
TX = w.ptable("tx", RX, cols=("arr", "burst", "fin", "wait", "resp"), shown=("arr", "burst"), cls="sm",
              avg="ממוצע: " + w.ltr("(1 + 13 + 4 + 0) / 4 = 4.5"))
QX = ("Process  Arrival  Burst\n" + "\n".join("P%d       %-9d%d" % (i + 1, a, b) for i, (a, b) in enumerate(X)))

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נלמד את SRTF: הגרסה של SJF שמותר לה להפסיק תהליך באמצע."),
    P("נראה מתי חדש שולף את מי שרץ, ואת ההשוואה שמכשילה הכי הרבה סטודנטים."),
    P("ובסוף נפתור שאלה בסגנון מבחן.", hold=0.4),
], stage='<div class="kicker">S04 · תזמון מעבד: תרשימי גאנט וזמני המתנה</div><h1>SRTF: מפסיקים כשמישהו קצר יותר</h1>'
         '<p>משווים את התהליך החדש למה <b>שנשאר</b> לתהליך הרץ, לא לפרץ המקורי שלו.</p>', layout="title")

idea = Scene("idea", "הכלל", [
    P("SRTF, כלומר Shortest Remaining Time First: הזמן **הנותר** הקצר ביותר רץ ראשון.",
      say="אֶס אַר טִי אֶף, כלומר שוֹרְטֶסְט רִימֵיינִינְג טַיים פֶרְסְט: הזמן הנותר הקצר ביותר רץ ראשון.", do=show("i-1")),
    P("זה SJF, אבל **נשלף**: המתזמן מחליט מחדש בכל פעם שמגיע תהליך, ולא רק כשהמעבד מתפנה.", do=show("i-2")),
    P("כשמגיע תהליך חדש, משווים את הפרץ שלו למה **שנשאר** לתהליך שרץ עכשיו.", do=show("i-3")),
    P("אם החדש קטן יותר, הוא שולף את הרץ. הרץ חוזר לתור המוכנים, עם מה שנשאר לו.", do=show("i-4")),
    P("ולכן מוסיפים לטבלה עמודה של **נשאר**, ומעדכנים אותה בכל הגעה.", do=show("i-c1"), hold=0.4),
], stage=w.stack(w.line("i-1", "בכל רגע: <b>הזמן הנותר</b> הקצר ביותר"),
                 w.line("i-2", "<b>נשלף</b>: מחליטים מחדש בכל הגעה"),
                 w.line("i-3", "חדש מול <b>מה שנשאר</b> לרץ"),
                 w.line("i-4", "חדש קטן יותר ← הרץ חוזר לתור"), gap=30),
   panel=st.card("i-c1", "rule", "🔑 עמודת <b>נשאר</b>, מתעדכנת בכל הגעה"))

ex = Scene("ex", "דוגמה", [
    P("P1 עם פרץ שבע מגיע בזמן 0, P2 עם פרץ ארבע בזמן 2, P3 עם פרץ אחת בזמן 3, ו-P4 עם פרץ שלוש בזמן 5.",
      do=show("ga-a-P1", "ga-a-P2", "ga-a-P3", "ga-a-P4"),
      say="פִּי אחת עם פרץ שבע מגיע בזמן אפס, פִּי שתיים עם פרץ ארבע בזמן שתיים, פִּי שלוש עם פרץ אחת בזמן שלוש, ופִּי ארבע עם פרץ שלוש בזמן חמש."),
    P("בזמן 0 רק P1 כאן, אז הוא מתחיל לרוץ.", do=show("ga-s0"),
      say="בזמן אפס רק פִּי אחת כאן, אז הוא מתחיל לרוץ."),
    P("בזמן 2 מגיע P2 עם ארבע. P1 כבר רץ שתיים, אז נשארו לו חמש. ארבע קטן מחמש: P2 שולף אותו.",
      do=show("ta-r1a", "e-1"),
      say="בזמן שתיים מגיע פִּי שתיים עם ארבע. פִּי אחת כבר רץ שתיים, אז נשארו לו חמש. ארבע קטן מחמש: פִּי שתיים שולף אותו."),
    P("בזמן 3 מגיע P3 עם אחת. ל-P2 נשארו שלוש, ואחת קטן משלוש: שוב שליפה.",
      do=show("ga-s1", "ta-r2a", "e-2"),
      say="בזמן שלוש מגיע פִּי שלוש עם אחת. לפִּי שתיים נשארו שלוש, ואחת קטן משלוש: שוב שליפה."),
    P("P3 רץ יחידה אחת ומסיים בזמן 4. עכשיו בוחרים מחדש: ל-P1 חמש, ל-P2 שלוש. P2 חוזר.",
      do=show("ga-s2", "ga-f-P3"),
      say="פִּי שלוש רץ יחידה אחת ומסיים בזמן ארבע. עכשיו בוחרים מחדש: לפִּי אחת חמש, לפִּי שתיים שלוש. פִּי שתיים חוזר."),
    P("בזמן 5 מגיע P4 עם שלוש. וזה הרגע של המלכודת.", do=show("ta-r2b"),
      say="בזמן חמש מגיע פִּי ארבע עם שלוש. וזה הרגע של המלכודת."),
    P("שלוש קטן מהפרץ המקורי של P2, ארבע. אבל P2 כבר רץ שתי יחידות, ונשארו לו רק שתיים.",
      say="שלוש קטן מהפרץ המקורי של פִּי שתיים, ארבע. אבל פִּי שתיים כבר רץ שתי יחידות, ונשארו לו רק שתיים."),
    P("שלוש לא קטן משתיים, ולכן **אין** שליפה. P2 ממשיך ומסיים בזמן 7.", do=show("e-3", "ga-s3", "ga-f-P2"),
      say="שלוש לא קטן משתיים, ולכן אין שליפה. פִּי שתיים ממשיך, ומסיים בזמן שבע."),
    P("בזמן 7: ל-P1 חמש, ל-P4 שלוש. P4 רץ עד 10, ו-P1 מסיים אחרון, בחמש עשרה.",
      do=show("ga-s4", "ga-f-P4", "ga-s5", "ga-f-P1"),
      say="בזמן שבע: לפִּי אחת חמש, לפִּי ארבע שלוש. פִּי ארבע רץ עד עשר, ופִּי אחת מסיים אחרון, בחמש עשרה."),
    P("ההמתנות, סיום פחות הגעה פחות פרץ: שמונה, אחת, אפס ושתיים.",
      do=show(*[f"ta-P{i}-{c}" for i in range(1, 5) for c in ("fin", "wait")])),
    P("הסכום אחת עשרה, חלקי ארבע: שתיים נקודה שבעים וחמש.", do=show("ta-avg"), hold=0.5),
], stage=w.stack(GA, TA, gap=16),
   panel=st.card("e-1", "ex", 'זמן 2: P2 מול P1<span class="sc-calc">4 &lt; 5 ?  ✓ שליפה</span>')
         + st.card("e-2", "ex", 'זמן 3: P3 מול P2<span class="sc-calc">1 &lt; 3 ?  ✓ שליפה</span>')
         + st.card("e-3", "trap", '⚠️ זמן 5: P4 מול P2<span class="sc-calc">3 &lt; 2 ?  ✗ אין שליפה</span>'))

split = Scene("split", "תהליך בחתיכות", [
    P("עוד מלכודת: ב-FCFS ההמתנה הייתה פשוט ההתחלה פחות ההגעה. כאן זה לא עובד.",
      say="עוד מלכודת: באֶף סִי אֶף אֶס ההמתנה הייתה פשוט ההתחלה פחות ההגעה. כאן זה לא עובד."),
    P("P1 התחיל לרוץ ברגע שהגיע, בזמן 0. לפי הקיצור הוא חיכה אפס.", do=show("gw-hl0", "sp-1"),
      say="פִּי אחת התחיל לרוץ ברגע שהגיע, בזמן אפס. לפי הקיצור הוא חיכה אפס."),
    P("אבל הוא נשלף בזמן 2, וחזר לרוץ רק בזמן 10: שמונה יחידות בתור.", do=show("gw-hl5", "gw-b-w0"),
      say="אבל הוא נשלף בזמן שתיים, וחזר לרוץ רק בזמן עשר: שמונה יחידות בתור."),
    P("הנוסחה האוניברסלית תופסת את זה: חמש עשרה פחות אפס פחות שבע, שמונה.", do=show("sp-2"),
      say="הנוסחה האוניברסלית תופסת את זה: חמש עשרה, פחות אפס, פחות שבע. שמונה."),
    P("ומה שהקיצור כן נותן, ההתחלה פחות ההגעה, זה זמן התגובה: אפס.", do=show("sp-3"), hold=0.4),
], stage=GW,
   panel=st.card("sp-1", "trap", '⚠️ התחלה − הגעה<span class="sc-calc">0 − 0 = 0 ✗</span>')
         + st.card("sp-2", "rule", '🔑 המתנה = סיום − הגעה − פרץ<span class="sc-calc">15 − 0 − 7 = 8 ✓</span>')
         + st.card("sp-3", "ex", "התחלה − הגעה = זמן <b>תגובה</b>, לא המתנה"))

exam = Scene("exam", "שאלה בסגנון מבחן", [
    P("שאלה בסגנון מבחן: חשבו את זמן ההמתנה הממוצע ב-SRTF, ואת זמן התגובה של P1.",
      say="שאלה בסגנון מבחן: חשבו את זמן ההמתנה הממוצע באֶס אַר טִי אֶף, ואת זמן התגובה של פִּי אחת."),
    P("עד זמן 1 אין אף אחד: סרק. אז מגיע P1 עם שבע, ומתחיל.", do=show("gx-i0", "gx-s0"),
      say="עד זמן אחת אין אף אחד: סרק. אז מגיע פִּי אחת עם שבע, ומתחיל."),
    P("בזמן 2 מגיע P2, גם הוא עם שבע. ל-P1 נשארו שש. שבע לא קטן משש: אין שליפה.", do=show("x-1"),
      say="בזמן שתיים מגיע פִּי שתיים, גם הוא עם שבע. לפִּי אחת נשארו שש. שבע לא קטן משש: אין שליפה."),
    P("בזמן 5 מגיע P3 עם שש. ל-P1 נשארו שלוש, אז שוב אין שליפה.", do=show("x-2"),
      say="בזמן חמש מגיע פִּי שלוש עם שש. לפִּי אחת נשארו שלוש, אז שוב אין שליפה."),
    P("בזמן 6 מגיע P4 עם אחת. ל-P1 נשארו שתיים, ואחת קטן משתיים: שליפה.",
      do=show("x-3"),
      say="בזמן שש מגיע פִּי ארבע עם אחת. לפִּי אחת נשארו שתיים, ואחת קטן משתיים: שליפה."),
    P("P4 רץ משש עד שבע. P1 חוזר ומסיים בתשע. אחריו P3 עד חמש עשרה, ו-P2 עד עשרים ושתיים.",
      do=show("gx-s1", "gx-f-P4", "gx-s2", "gx-f-P1", "gx-s3", "gx-f-P3", "gx-s4", "gx-f-P2"),
      say="פִּי ארבע רץ משש עד שבע. פִּי אחת חוזר, ומסיים בתשע. אחריו פִּי שלוש עד חמש עשרה, ופִּי שתיים עד עשרים ושתיים."),
    P("המתנות: P1 אחת, P2 שלוש עשרה, P3 ארבע, ו-P4 אפס. הסכום שמונה עשרה, חלקי ארבע: ארבע וחצי.",
      do=show(*[f"tx-P{i}-{c}" for i in range(1, 5) for c in ("fin", "wait")], "tx-avg"),
      say="המתנות: פִּי אחת אחת, פִּי שתיים שלוש עשרה, פִּי שלוש ארבע, ופִּי ארבע אפס. הסכום שמונה עשרה, חלקי ארבע: ארבע וחצי."),
    P("וזמן התגובה של P1: הוא רץ ברגע שהגיע, אז אפס. אבל ההמתנה שלו אחת, בגלל השליפה בזמן 6.",
      do=show("tx-P1-resp", "x-ans"), hold=0.5,
      say="וזמן התגובה של פִּי אחת: הוא רץ ברגע שהגיע, אז אפס. אבל ההמתנה שלו אחת, בגלל השליפה בזמן שש."),
], stage=w.stack(GX, TX, gap=16),
   panel='<div class="qstem"><span class="qid">בסגנון מבחן</span>חשבו את זמן ההמתנה הממוצע בשיטת SRTF, '
         'ואת זמן התגובה של P1.</div>'
         f'<pre class="qcode">{QX}</pre>'
         + '<div class="sc-evs"><span id="x-1" class="sc-calc h">t=2:  7 &lt; 6 ?  ✗</span>'
           '<span id="x-2" class="sc-calc h">t=5:  6 &lt; 3 ?  ✗</span>'
           '<span id="x-3" class="sc-calc h">t=6:  1 &lt; 2 ?  ✓</span></div>'
         + '<div id="x-ans" class="qans h"><span class="k">תשובה:</span> ממוצע 4.5 מ״ש; תגובת P1: 0</div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום: SRTF הוא SJF נשלף. בכל הגעה בודקים מחדש מי הכי קצר.", do=show("r-1")),
    P("משווים את החדש למה **שנשאר** לרץ, לא לפרץ המקורי שלו.", do=show("r-2")),
    P("תהליך שנשלף רץ בחתיכות, ולכן ההמתנה היא תמיד סיום פחות הגעה פחות פרץ.", do=show("r-3")),
    P("ברמה הבאה: Round Robin, שבו כל אחד מקבל פרוסת זמן קבועה. נתראה.", do=show("r-4"), hold=0.6),
], stage=w.gantt("gr", RA, width=1000, hidden=False),
   panel=st.card("r-1", "rule", "🔑 SRTF = SJF נשלף")
         + st.card("r-2", "trap", "⚠️ חדש מול <b>מה שנשאר</b>, לא מול הפרץ המקורי")
         + st.card("r-3", "rule", "🔑 המתנה = סיום − הגעה − פרץ")
         + st.card("r-4", "ex", "הבא בתור: Round Robin"))

VIDEO = Video("S04", "sched", "SRTF: מפסיקים כשמישהו קצר יותר", [title, idea, ex, split, exam, recap], bank={})
