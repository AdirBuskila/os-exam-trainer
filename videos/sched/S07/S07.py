# -*- coding: utf-8 -*-
"""S07 · בוס: מבחן תזמון — video script (build: tools/video/vid.py S07). Boss level: a walkthrough of exam questions.

Source: src/courses/sched.py level 7 (boss: real exam items on FCFS, SRTF and Round Robin; the lesson's four-step
recipe). Exam anchors: none. Every free scheduling bank item is either a theory item already used in S01/S02/S06
(2017A-5, 2014A-5, 2014B-4) or a content twin of a quiz item (2016A-5, 2017B-5, 2017A-4, 2017B-4), and the boss quiz
itself uses 2019A-4, 2021B-5, 2022B-4, 2017SB-3, 2024B-4 and the SRTF table 7@0 3@1 22@4. So the walkthrough is two
original "שאלה בסגנון מבחן" questions (bank={}), three parts:
  1. Round Robin, quantum 3, on 1@2 5@3 3@4 4@5 (idle start; two arrivals during one slice go before the preempted
     process): average waiting 3.5.
  2. The same table 6@0 1@1 3@2 5@6 under (a) SJF: 3.5, and (b) SRTF: 2 (with a no-preemption arrival at t=6:
     5 against the 4 that P1 has left).
Every chart, queue and number comes from sims.schedule (w_sched.run, strict), w_sched.rr_steps and
w_sched.srtf_events, asserted below; w.assert_fresh refuses any course table.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_sched as w

# ---------------------------------------------------------------- numbers (verified)
A = [(2, 1), (3, 5), (4, 3), (5, 4)]
RA = w.run(A, "RR", 3)
SA = w.rr_steps(A, 3)
assert [(s["start"], s["end"], s["run"], s["queue"]) for s in SA] == [
    (0, 2, None, ["P1"]), (2, 3, "P1", ["P2"]), (3, 6, "P2", ["P3", "P4", "P2"]), (6, 9, "P3", ["P4", "P2"]),
    (9, 12, "P4", ["P2", "P4"]), (12, 14, "P2", ["P4"]), (14, 15, "P4", [])]
assert RA["finish"] == [3, 14, 9, 15] and RA["wait"] == [0, 6, 2, 6] and RA["avg_wait"] == 3.5

B = [(0, 6), (1, 1), (2, 3), (6, 5)]
RJ = w.run(B, "SJF")
assert RJ["gantt"] == [("P1", 0, 6), ("P2", 6, 7), ("P3", 7, 10), ("P4", 10, 15)]
assert RJ["wait"] == [0, 5, 5, 4] and RJ["avg_wait"] == 3.5
RS = w.run(B, "SRTF")
assert RS["gantt"] == [("P1", 0, 1), ("P2", 1, 2), ("P3", 2, 5), ("P1", 5, 10), ("P4", 10, 15)]
assert w.srtf_events(B, RS) == [(1, "P2", 1, "P1", 5, True), (2, "P3", 3, None, None, True),
                                (6, "P4", 5, "P1", 4, False)]
assert RS["wait"] == [4, 0, 0, 4] and RS["avg_wait"] == 2
w.assert_fresh(A, B)


def code(procs):
    return "Process  Arrival  Burst\n" + "\n".join("P%d       %-9d%d" % (i + 1, a, b) for i, (a, b) in enumerate(procs))


GA = w.gantt("ga", RA, slices=w.rr_slices(SA), width=1000)
QA = w.rrq("qa", SA)
SLI = {}                                    # step index -> slice index in the chart (the idle step has none)
k = 0
for i, s in enumerate(SA):
    if s["run"]:
        SLI[i] = k
        k += 1


def rr_step(i):
    s = SA[i]
    ids = [f"qa-r{i}"]
    if s["run"] is None:
        ids.append("ga-i0")
    else:
        ids.append(f"ga-s{SLI[i]}")
        if s["done"]:
            ids.append(f"ga-f-{s['run']}")
    return show(*ids)


GJ = w.gantt("gj", RJ, width=1000, arrivals=True)
TJ = w.ptable("tj", RJ, cols=("arr", "burst", "fin", "wait"), shown=("arr", "burst"), cls="sm",
              avg="SJF: " + w.ltr("(0 + 5 + 5 + 4) / 4 = 3.5"))
GS = w.gantt("gs", RS, width=1000, arrivals=True)
TS = w.ptable("ts", RS, cols=("arr", "burst", "fin", "wait"), shown=("arr", "burst"), cls="sm",
              avg="SRTF: " + w.ltr("(4 + 0 + 0 + 4) / 4 = 2"))

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("זה שלב הבוס של תזמון המעבד. אין תאוריה חדשה, רק שאלות בנוסח של המבחן."),
    P("נפתור שתי שאלות: Round Robin עם הגעות מדורגות, ואותה טבלה גם ב-SJF וגם ב-SRTF.",
      say="נפתור שתי שאלות: רָאוּנְד רוֹבִּין עם הגעות מדורגות, ואותה טבלה גם באֶס גֵ'יי אֶף וגם באֶס אַר טִי אֶף."),
    P("עצרו את הסרטון אחרי כל שאלה, ונסו לפתור לבד לפני שממשיכים.", hold=0.4),
], stage='<div class="kicker">S07 · תזמון מעבד: תרשימי גאנט וזמני המתנה</div><h1>בוס: מבחן תזמון</h1>'
         '<p>שאלות בנוסח המבחנים על Round Robin, SJF ו-SRTF, צעד אחר צעד.</p>', layout="title")

recipe = Scene("recipe", "המתכון", [
    P("לפני שמתחילים, המתכון. אחד: בונים טבלה של הגעה ופרץ.", do=show("c-1")),
    P("שתיים: מציירים גאנט לפי הכלל של האלגוריתם, ובודקים מחדש בכל הגעה ובכל סיום.", do=show("c-2")),
    P("שלוש: קוראים את זמני הסיום, והמתנה היא סיום פחות הגעה פחות פרץ.", do=show("c-3")),
    P("וארבע: הממוצע הוא הסכום חלקי מספר התהליכים. זה הכול.", do=show("c-4"), hold=0.4),
], stage=w.stack(st.card("c-1", "ex", "1. טבלה: הגעה, פרץ"),
                 st.card("c-2", "ex", "2. גאנט לפי הכלל, בודקים בכל הגעה וסיום"),
                 st.card("c-3", "rule", "🔑 3. המתנה = סיום − הגעה − פרץ"),
                 st.card("c-4", "ex", "4. ממוצע = סכום חלקי מספר התהליכים"), gap=22),
   panel=st.card("c-t1", "trap", "⚠️ Round Robin: מי שהגיע במהלך הפרוסה, לפני הנשלף").replace(" h\"", "\"", 1)
         + st.card("c-t2", "trap", "⚠️ SRTF: חדש מול מה <b>שנשאר</b>").replace(" h\"", "\"", 1))

q1 = Scene("q1", "שאלה 1: Round Robin", [
    P("שאלה ראשונה: Round Robin עם קוונטום 3. חשבו את זמן ההמתנה הממוצע.",
      say="שאלה ראשונה: רָאוּנְד רוֹבִּין עם קְוַונְטוּם שלוש. חשבו את זמן ההמתנה הממוצע."),
    P("הראשון מגיע רק בזמן 2, אז מאפס עד שתיים המעבד בסרק.", do=rr_step(0),
      say="הראשון מגיע רק בזמן שתיים, אז מאפס עד שתיים המעבד בסרק."),
    P("P1 צריך יחידה אחת, ומסיים בזמן 3. בדיוק אז מגיע P2, והוא לבד בתור.", do=rr_step(1),
      say="פִּי אחת צריך יחידה אחת, ומסיים בזמן שלוש. בדיוק אז מגיע פִּי שתיים, והוא לבד בתור."),
    P("P2 רץ משלוש עד שש. בזמן הזה הגיעו P3 ו-P4. הם קודם, ו-P2, שנשלף, אחריהם.", do=rr_step(2),
      say="פִּי שתיים רץ משלוש עד שש. בזמן הזה הגיעו פִּי שלוש ופִּי ארבע. הם קודם, ופִּי שתיים, שנשלף, אחריהם."),
    P("P3 רץ שלוש יחידות בדיוק, ומסיים בזמן 9.", do=rr_step(3),
      say="פִּי שלוש רץ שלוש יחידות בדיוק, ומסיים בזמן תשע."),
    P("P4 רץ מתשע עד שתים עשרה, ונשארה לו יחידה. הוא עובר לסוף, אחרי P2.", do=rr_step(4),
      say="פִּי ארבע רץ מתשע עד שתים עשרה, ונשארה לו יחידה. הוא עובר לסוף, אחרי פִּי שתיים."),
    P("P2 גומר את השתיים שנשארו לו, עד ארבע עשרה, ו-P4 מסיים בחמש עשרה.", do=rr_step(5) + rr_step(6),
      say="פִּי שתיים גומר את השתיים שנשארו לו, עד ארבע עשרה, ופִּי ארבע מסיים בחמש עשרה."),
    P("המתנות: P1 שלוש פחות שתיים פחות אחת, אפס. P2 ארבע עשרה פחות שלוש פחות חמש, שש.", do=show("q1-w1", "q1-w1b"),
      say="המתנות: פִּי אחת, שלוש, פחות שתיים, פחות אחת. אפס. פִּי שתיים, ארבע עשרה, פחות שלוש, פחות חמש. שש."),
    P("P3 תשע פחות ארבע פחות שלוש, שתיים. P4 חמש עשרה פחות חמש פחות ארבע, שש.", do=show("q1-w2", "q1-w2b"),
      say="פִּי שלוש, תשע, פחות ארבע, פחות שלוש. שתיים. פִּי ארבע, חמש עשרה, פחות חמש, פחות ארבע. שש."),
    P("הסכום ארבע עשרה, חלקי ארבע: שלוש וחצי. והסרק בהתחלה לא נכנס לאף אחד.", do=show("q1-ans"), hold=0.5,
      say="הסכום ארבע עשרה, חלקי ארבע: שלוש וחצי. והסרק בהתחלה לא נכנס לאף אחד."),
], stage=w.stack(GA, QA, gap=14),
   panel='<div class="qstem"><span class="qid">בסגנון מבחן · 1</span>Round Robin עם קוונטום 3. '
         'חשבו את זמן ההמתנה הממוצע.</div>'
         f'<pre class="qcode">{code(A)}</pre>'
         '<div class="sc-evs"><span id="q1-w1" class="sc-calc h">P1: 3 − 2 − 1 = 0</span>'
         '<span id="q1-w1b" class="sc-calc h">P2: 14 − 3 − 5 = 6</span>'
         '<span id="q1-w2" class="sc-calc h">P3: 9 − 4 − 3 = 2</span>'
         '<span id="q1-w2b" class="sc-calc h">P4: 15 − 5 − 4 = 6</span></div>'
         '<div id="q1-ans" class="qans h"><span class="k">תשובה:</span> '
         '<span class="sc-ltr">(0 + 6 + 2 + 6) / 4 = 3.5</span> מ״ש</div>')

q2a = Scene("q2a", "שאלה 2 א: SJF", [
    P("שאלה שנייה, על טבלה אחת. סעיף א: חשבו את זמן ההמתנה הממוצע ב-SJF.",
      say="שאלה שנייה, על טבלה אחת. סעיף א: חשבו את זמן ההמתנה הממוצע באֶס גֵ'יי אֶף.",
      do=show("gj-a-P1", "gj-a-P2", "gj-a-P3", "gj-a-P4")),
    P("בזמן 0 רק P1 כאן. הוא מתחיל, ו-SJF לא מפסיק אותו: הוא רץ את כל השש, עד זמן 6.",
      do=show("gj-s0", "gj-f-P1"),
      say="בזמן אפס רק פִּי אחת כאן. הוא מתחיל, ואֶס גֵ'יי אֶף לא מפסיק אותו: הוא רץ את כל השש, עד זמן שש."),
    P("בזמן 6 מחכים P2 עם אחת, P3 עם שלוש, ו-P4 שהגיע עכשיו, עם חמש. מהקצר לארוך.",
      do=show("gj-s1", "gj-f-P2", "gj-s2", "gj-f-P3", "gj-s3", "gj-f-P4"),
      say="בזמן שש מחכים פִּי שתיים עם אחת, פִּי שלוש עם שלוש, ופִּי ארבע שהגיע עכשיו, עם חמש. מהקצר לארוך."),
    P("סיומים: שש, שבע, עשר וחמש עשרה. המתנות: אפס, חמש, חמש וארבע.",
      do=show(*[f"tj-P{i}-{c}" for i in range(1, 5) for c in ("fin", "wait")])),
    P("הסכום ארבע עשרה, חלקי ארבע: שלוש וחצי.", do=show("tj-avg", "q2a-ans"), hold=0.5),
], stage=w.stack(GJ, TJ, gap=16),
   panel='<div class="qstem"><span class="qid">בסגנון מבחן · 2</span>חשבו את זמן ההמתנה הממוצע: '
         '(א) בשיטת SJF; (ב) בשיטת SRTF.</div>'
         f'<pre class="qcode">{code(B)}</pre>'
         '<div id="q2a-ans" class="qans h"><span class="k">א:</span> ב-SJF הממוצע 3.5 מ״ש</div>')

q2b = Scene("q2b", "שאלה 2 ב: SRTF", [
    P("סעיף ב: אותה טבלה, הפעם ב-SRTF. עכשיו בודקים מחדש בכל הגעה.",
      say="סעיף ב: אותה טבלה, הפעם באֶס אַר טִי אֶף. עכשיו בודקים מחדש בכל הגעה.",
      do=show("gs-a-P1", "gs-a-P2", "gs-a-P3", "gs-a-P4")),
    P("בזמן 1 מגיע P2 עם אחת. ל-P1 נשארו חמש. אחת קטן מחמש: שליפה.", do=show("gs-s0", "b-1"),
      say="בזמן אחת מגיע פִּי שתיים עם אחת. לפִּי אחת נשארו חמש. אחת קטן מחמש: שליפה."),
    P("P2 מסיים בזמן 2, ובדיוק אז מגיע P3 עם שלוש. הוא קצר מהחמש של P1, אז P3 רץ עד 5.",
      do=show("gs-s1", "gs-f-P2", "gs-s2", "gs-f-P3", "b-2"),
      say="פִּי שתיים מסיים בזמן שתיים, ובדיוק אז מגיע פִּי שלוש עם שלוש. הוא קצר מהחמש של פִּי אחת, אז פִּי שלוש רץ עד חמש."),
    P("P1 חוזר בזמן 5. בזמן 6 מגיע P4 עם חמש, ול-P1 נשארו ארבע. חמש לא קטן מארבע: אין שליפה.",
      do=show("gs-s3", "b-3"),
      say="פִּי אחת חוזר בזמן חמש. בזמן שש מגיע פִּי ארבע עם חמש, ולפִּי אחת נשארו ארבע. חמש לא קטן מארבע: אין שליפה."),
    P("P1 מסיים בעשר, ו-P4 בחמש עשרה.", do=show("gs-f-P1", "gs-s4", "gs-f-P4"),
      say="פִּי אחת מסיים בעשר, ופִּי ארבע בחמש עשרה."),
    P("המתנות: ארבע, אפס, אפס וארבע. הסכום שמונה, חלקי ארבע: שתיים.",
      do=show(*[f"ts-P{i}-{c}" for i in range(1, 5) for c in ("fin", "wait")], "ts-avg", "q2b-ans")),
    P("שימו לב: אותה טבלה, וב-SRTF הממוצע ירד משלוש וחצי לשתיים. השליפה נתנה לקצרים לעקוף את P1.", hold=0.5,
      say="שימו לב: אותה טבלה, ובאֶס אַר טִי אֶף הממוצע ירד משלוש וחצי לשתיים. השליפה נתנה לקצרים לעקוף את פִּי אחת."),
], stage=w.stack(GS, TS, gap=16),
   panel='<div class="qstem"><span class="qid">בסגנון מבחן · 2</span>(ב) אותה טבלה, בשיטת SRTF.</div>'
         '<div class="sc-evs"><span id="b-1" class="sc-calc h">t=1:  1 &lt; 5 ?  ✓</span>'
         '<span id="b-2" class="sc-calc h">t=2:  3 &lt; 5 ?  ✓</span>'
         '<span id="b-3" class="sc-calc h">t=6:  5 &lt; 4 ?  ✗</span></div>'
         '<div class="qans"><span class="k">א:</span> ב-SJF הממוצע 3.5 מ״ש</div>'
         '<div id="q2b-ans" class="qans h"><span class="k">ב:</span> ב-SRTF הממוצע 2 מ״ש</div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום הקורס: כל שאלת חישוב היא אותו מתכון. גאנט, זמני סיום, המתנה, ממוצע.", do=show("r-1")),
    P("ב-Round Robin, מי שהגיע במהלך הפרוסה נכנס לפני הנשלף.", do=show("r-2"),
      say="ברָאוּנְד רוֹבִּין, מי שהגיע במהלך הפרוסה נכנס לפני הנשלף."),
    P("ב-SRTF משווים למה שנשאר. וסרק הוא לא המתנה של אף אחד.", do=show("r-3"),
      say="באֶס אַר טִי אֶף משווים למה שנשאר. וסרק הוא לא המתנה של אף אחד."),
    P("עכשיו תורכם: שלב הבוס באפליקציה מחכה. בהצלחה!", do=show("r-4"), hold=0.6),
], stage=w.gantt("gr", RS, width=1000, hidden=False),
   panel=st.card("r-1", "rule", "🔑 גאנט ← סיום ← המתנה ← ממוצע")
         + st.card("r-2", "trap", "⚠️ Round Robin: מי שהגיע לפני הנשלף")
         + st.card("r-3", "trap", "⚠️ SRTF: מול מה שנשאר · סרק ≠ המתנה")
         + st.card("r-4", "ex", "🏆 עכשיו: שלב הבוס באפליקציה"))

VIDEO = Video("S07", "sched", "בוס: מבחן תזמון", [title, recipe, q1, q2a, q2b, recap], bank={})
