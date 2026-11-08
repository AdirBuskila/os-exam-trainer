# -*- coding: utf-8 -*-
"""S02 · FCFS ואפקט השיירה — video script (build: tools/video/vid.py S02).

Source: src/courses/sched.py level 2 (lesson + goal: draw the Gantt chart for first-come first-served; idle gaps;
the convoy effect). Exam anchor: 2014A-5 (in which group of scheduling methods can an endless loop without I/O hang
the computer: non-preemptive), which no guided quiz cites.
Avoided on purpose: the level-2 quiz tables (7@0 3@1 22@4 = 2020A-6, 10@0 2@1 2@2, 2@0 3@5), the lesson's and the
boss's 7@0 7@1 7@2 (2021B-5), the boss's 7@0 4@2 1@4 4@5 (2017SB-3), and the quiz item 2016B-5 ("which method has the
convoy effect": the video explains the effect on numbers, it does not pose that question).
Here: 3@0 6@1 4@4 2@6 (average 3.5), an idle gap 3@0 4@6 2@7 (the zero wait after the gap is P2 arriving at 6, not the quiz's 2@0 3@5), and the convoy pair 12@0 1@1 2@2 against
1@0 2@1 12@2. Every number comes from sims.schedule (w_sched.run) and is asserted below.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_sched as w

# ---------------------------------------------------------------- numbers (verified)
A = [(0, 3), (1, 6), (4, 4), (6, 2)]
RA = w.run(A, "FCFS")
assert RA["gantt"] == [("P1", 0, 3), ("P2", 3, 9), ("P3", 9, 13), ("P4", 13, 15)]
assert RA["wait"] == [0, 2, 5, 7] and sum(RA["wait"]) == 14 and RA["avg_wait"] == 3.5
# non-preemptive: one piece each, so waiting = start - arrival as well
assert all(s - A[int(n[1]) - 1][0] == RA["wait"][int(n[1]) - 1] for n, s, e in RA["gantt"])

B = [(0, 3), (6, 4), (7, 2)]
RB = w.run(B, "FCFS")
assert RB["gantt"] == [("P1", 0, 3), ("P2", 6, 10), ("P3", 10, 12)] and RB["wait"] == [0, 0, 3]
assert RB["avg_wait"] == 1

C1 = [(0, 12), (1, 1), (2, 2)]
C2 = [(0, 1), (1, 2), (2, 12)]
RC1, RC2 = w.run(C1, "FCFS"), w.run(C2, "FCFS")
assert RC1["wait"] == [0, 11, 11] and abs(RC1["avg_wait"] - 22 / 3) < 1e-9
assert RC2["wait"] == [0, 0, 1] and abs(RC2["avg_wait"] - 1 / 3) < 1e-9
assert w.num(RC1["avg_wait"]) == "7.33" and w.num(RC2["avg_wait"]) == "0.33"
w.assert_fresh(A, B, C1, C2)

Q = BANK["2014A-5"]
assert Q["answer_he"].startswith("non-preemptive")

GA = w.gantt("ga", RA, width=1000)
TA = w.ptable("ta", RA, cols=("arr", "burst", "fin", "wait"), shown=("arr", "burst"),
              avg="ממוצע: " + w.ltr("(0 + 2 + 5 + 7) / 4 = 3.5"))
GB = w.gantt("gb", RB, width=1000)
TB = w.ptable("tb", RB, cols=("arr", "burst", "fin", "wait"), shown=("arr", "burst"), cls="sm")
GC1 = w.gantt("gc1", RC1, width=900, hidden=False, finishes=False)
GC2 = w.gantt("gc2", RC2, width=900, hidden=False, finishes=False)

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נבנה בעצמנו את תרשים הגאנט הראשון, באלגוריתם הפשוט ביותר: FCFS."),
    P("נראה מה קורה כשהמעבד מתפנה ואין מי שיחכה לו, ולמה תהליך ארוך אחד מעכב את כולם."),
    P("ובסוף שאלה ממבחן על לולאה אינסופית.", hold=0.4),
], stage='<div class="kicker">S02 · תזמון מעבד: תרשימי גאנט וזמני המתנה</div><h1>FCFS ואפקט השיירה</h1>'
         '<p>לצייר תרשים גאנט ל-FCFS: לפי סדר ההגעה, בלי להפסיק אף תהליך באמצע.</p>', layout="title")

idea = Scene("idea", "הכלל", [
    P("FCFS פירושו: מי שבא ראשון, מקבל ראשון. בדיוק כמו תור בקופה.", do=show("i-c1")),
    P("כשהמעבד מתפנה, הוא לוקח את התהליך שהגיע **הכי מוקדם** מבין אלה שמחכים.", do=show("i-c2")),
    P("והוא **לא נשלף**: תהליך שהתחיל לרוץ, רץ עד סוף הפרץ שלו. אף אחד לא מפסיק אותו.", do=show("i-c3")),
    P("השיטה לכל שאלה: מציירים גאנט, קוראים את זמני הסיום, ומחשבים המתנה.", do=show("i-c4"), hold=0.4),
], stage=w.stack(w.line("i-c1", "🧾 כל הקודם זוכה: לפי סדר ההגעה" ),
                 w.line("i-c2", "המעבד התפנה ← הוותיק ביותר בתור" ),
                 w.line("i-c3", "<b>לא נשלף</b>: רץ עד סוף הפרץ" ), gap=34),
   panel=st.card("i-c4", "rule", "🔑 גאנט ← סיום ← המתנה = סיום − הגעה − פרץ"))

ex = Scene("ex", "דוגמה", [
    P("ארבעה תהליכים. P1 מגיע בזמן 0, P2 בזמן 1, P3 בזמן 4, ו-P4 בזמן 6.",
      say="ארבעה תהליכים. פִּי אחת מגיע בזמן אפס, פִּי שתיים בזמן אחת, פִּי שלוש בזמן ארבע, ופִּי ארבע בזמן שש."),
    P("בזמן 0 רק P1 כאן. הוא רץ שלוש יחידות, ומסיים בזמן 3.", do=show("ga-s0", "ga-f-P1"),
      say="בזמן אפס רק פִּי אחת כאן. הוא רץ שלוש יחידות, ומסיים בזמן שלוש."),
    P("בזמן 3 מחכה רק P2. הוא רץ שש יחידות, עד זמן 9.", do=show("ga-s1", "ga-f-P2"),
      say="בזמן שלוש מחכה רק פִּי שתיים. הוא רץ שש יחידות, עד זמן תשע."),
    P("בזמן שהוא רץ מגיעים P3 ו-P4. אבל FCFS לא נשלף, אז הם עומדים בתור.", do=show("ex-c1"),
      say="בזמן שהוא רץ מגיעים פִּי שלוש ופִּי ארבע. אבל אֶף סִי אֶף אֶס לא נשלף, אז הם עומדים בתור."),
    P("בזמן 9: P3 הגיע לפני P4, אז הוא רץ עד 13. ואחריו P4, עד 15.",
      do=show("ga-s2", "ga-f-P3", "ga-s3", "ga-f-P4"),
      say="בזמן תשע: פִּי שלוש הגיע לפני פִּי ארבע, אז הוא רץ עד שלוש עשרה. ואחריו פִּי ארבע, עד חמש עשרה."),
    P("עכשיו הטבלה. זמני הסיום: שלוש, תשע, שלוש עשרה וחמש עשרה.",
      do=show("ta-P1-fin", "ta-P2-fin", "ta-P3-fin", "ta-P4-fin")),
    P("המתנה היא סיום פחות הגעה פחות פרץ. ל-P2: תשע פחות אחת פחות שש, כלומר שתיים.",
      do=show("ta-P1-wait", "ta-P2-wait", "ex-c2"),
      say="המתנה היא סיום פחות הגעה פחות פרץ. לפִּי שתיים: תשע, פחות אחת, פחות שש. כלומר שתיים."),
    P("ל-P3: שלוש עשרה פחות ארבע פחות ארבע, חמש. ול-P4: חמש עשרה פחות שש פחות שתיים, שבע.",
      do=show("ta-P3-wait", "ta-P4-wait"),
      say="לפִּי שלוש: שלוש עשרה, פחות ארבע, פחות ארבע. חמש. ולפִּי ארבע: חמש עשרה, פחות שש, פחות שתיים. שבע."),
    P("הסכום ארבע עשרה, חלקי ארבעה תהליכים: הממוצע הוא שלוש וחצי.", do=show("ta-avg")),
    P("קיצור דרך: ב-FCFS כל תהליך רץ בחתיכה אחת, אז ההמתנה היא פשוט רגע ההתחלה פחות ההגעה.",
      do=show("ex-c3"), hold=0.5),
], stage=w.stack(GA, TA, gap=24),
   panel=st.card("ex-c1", "trap", "⚠️ P3 ו-P4 הגיעו באמצע: P2 <b>לא</b> מופסק")
         + st.card("ex-c2", "rule", '🔑 המתנה = סיום − הגעה − פרץ<span class="sc-calc">P2: 9 − 1 − 6 = 2</span>')
         + st.card("ex-c3", "ex", "קיצור ל-FCFS: המתנה = התחלה − הגעה"))

idle = Scene("idle", "מעבד בסרק", [
    P("ומה אם המעבד מתפנה, ואף אחד עוד לא הגיע? כאן P1 מסיים בזמן 3, ו-P2 מגיע רק בזמן 6.",
      do=show("gb-s0", "gb-f-P1"),
      say="ומה אם המעבד מתפנה, ואף אחד עוד לא הגיע? כאן פִּי אחת מסיים בזמן שלוש, ופִּי שתיים מגיע רק בזמן שש."),
    P("משלוש עד שש המעבד **בסרק**. מציירים את הפער בתרשים, ולא משייכים אותו לאף תהליך.", do=show("gb-i0")),
    P("P2 מגיע בזמן 6, המעבד פנוי, והוא רץ מיד עד 10. ההמתנה שלו: אפס.",
      do=show("gb-s1", "gb-f-P2", "tb-P2-fin", "tb-P2-wait", "tb-P1-fin", "tb-P1-wait"),
      say="פִּי שתיים מגיע בזמן שש, המעבד פנוי, והוא רץ מיד עד עשר. ההמתנה שלו: אפס."),
    P("P3 הגיע בזמן 7, וחיכה ש-P2 יסיים. הוא רץ מעשר עד שתים עשרה, וההמתנה שלו שלוש.",
      do=show("gb-s2", "gb-f-P3", "tb-P3-fin", "tb-P3-wait"),
      say="פִּי שלוש הגיע בזמן שבע, וחיכה שפִּי שתיים יסיים. הוא רץ מעשר עד שתים עשרה, וההמתנה שלו שלוש."),
    P("המלכודת: לספור את שלוש יחידות הסרק כהמתנה של P2. הוא עוד לא היה בתור, אז אין לו מה לחכות.",
      do=show("id-c1"), say="המלכודת: לספור את שלוש יחידות הסרק כהמתנה של פִּי שתיים. הוא עוד לא היה בתור, אז אין לו מה לחכות."),
    P("והנוסחה מסתדרת לבד: עשר פחות שש פחות ארבע, אפס.", do=show("id-c2"), hold=0.4,
      say="והנוסחה מסתדרת לבד: עשר, פחות שש, פחות ארבע. אפס."),
], stage=w.stack(GB, TB, gap=26),
   panel=st.card("id-c1", "trap", "⚠️ סרק אינו המתנה של אף אחד")
         + st.card("id-c2", "rule", '🔑 הנוסחה לא משתנה<span class="sc-calc">P2: 10 − 6 − 4 = 0</span>'))

convoy = Scene("convoy", "אפקט השיירה", [
    P("עכשיו החולשה של FCFS. תהליך ארוך של שתים עשרה יחידות מגיע ראשון, ואחריו שני קצרים.",
      do=show("cv-1", "cv-1g")),
    P("שני הקצרים מחכים מאחוריו אחת עשרה יחידות כל אחד. ממוצע ההמתנה: בערך שבע ושליש.", do=show("cv-1a")),
    P("אותם שלושה תהליכים, אבל הארוך מגיע אחרון: עכשיו ההמתנות הן אפס, אפס ואחת.", do=show("cv-2", "cv-2g")),
    P("והממוצע: שליש בלבד. אותה עבודה בדיוק, רק סדר הגעה אחר.", do=show("cv-2a")),
    P("זה **אפקט השיירה**, convoy effect: כמו משאית איטית בכביש צר, וכל המכוניות בשיירה מאחוריה.",
      do=show("cv-c1")),
    P("FCFS לא נשלף, ולכן אין לו דרך לתת לקצרים לעקוף. האלגוריתמים בשלבים הבאים יתקנו את זה.",
      do=show("cv-c2"), hold=0.5),
], stage=w.stack(w.line("cv-1", "הארוך ראשון"), f'<div id="cv-1g" class="h">{GC1}</div>',
                 w.line("cv-1a", "המתנות 0, 11, 11 ← ממוצע " + w.ltr("7.33")),
                 w.line("cv-2", "הארוך אחרון", cls="sc-gapt"), f'<div id="cv-2g" class="h">{GC2}</div>',
                 w.line("cv-2a", "המתנות 0, 0, 1 ← ממוצע " + w.ltr("0.33")), gap=12),
   panel=st.card("cv-c1", "rule", "🔑 אפקט השיירה: ארוך אחד בראש התור מנפח את ההמתנה של כולם")
         + st.card("cv-c2", "trap", "⚠️ ב-FCFS אין עקיפה: הוא לא נשלף"))

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: באילו שיטות תזמון, לולאה אינסופית בלי קלט פלט יכולה לתקוע את המחשב? רוצים את שם הקבוצה."),
    P("במתזמן שלא נשלף, תהליך עוזב את המעבד רק בשני מקרים: כשהפרץ שלו נגמר, או כשהוא מבקש קלט פלט.", do=show("x-1")),
    P("לולאה אינסופית בלי קלט פלט לא עושה אף אחד מהם. זה פרץ שאורכו אינסוף.", do=show("x-2")),
    P("במתזמן שלא נשלף, כמו FCFS, אף אחד לא לוקח ממנו את המעבד. כל השאר בתור, לתמיד.", do=show("x-3")),
    P("זה דומה לאפקט השיירה, רק שכאן השיירה לא זזה לעולם."),
    P("במתזמן נשלף, פסיקת שעון לוקחת ממנו את המעבד בסוף פרוסת הזמן, ושאר התהליכים ממשיכים לרוץ.",
      do=show("x-4")),
    P("ולכן התשובה: השיטות הלא נשלפות, non-preemptive. בשיטות האלה אי אפשר לקחת מתהליך את המעבד בכוח.",
      do=show("x-ans"), hold=0.5),
], stage=w.stack(st.card("x-1", "ex", "יציאה מהמעבד: סוף הפרץ, או בקשת קלט/פלט"),
                 st.card("x-2", "trap", "⚠️ לולאה אינסופית בלי קלט/פלט: פרץ אינסופי"),
                 st.card("x-3", "rule", "🔑 לא נשלף: אין מי שיפסיק אותו ← המחשב תקוע"),
                 st.card("x-4", "ex", "נשלף: פסיקת שעון בסוף הפרוסה ← כולם ממשיכים"), gap=22),
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         f'<div id="x-ans" class="qans h"><span class="k">תשובה:</span> {Q["answer_he"]}</div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום: FCFS מריץ לפי סדר ההגעה, וכל תהליך רץ עד הסוף, בלי הפסקה.", do=show("r-1")),
    P("מציירים גאנט, קוראים זמני סיום, והמתנה היא סיום פחות הגעה פחות פרץ.", do=show("r-2")),
    P("פער שבו אף אחד לא הגיע הוא סרק, לא המתנה.", do=show("r-3")),
    P("ותהליך ארוך בראש התור מעכב את כולם: אפקט השיירה. ברמה הבאה נעקוף אותו. נתראה.", do=show("r-4"), hold=0.6),
], stage=w.gantt("gr", RA, width=1000, hidden=False),
   panel=st.card("r-1", "rule", "🔑 לפי סדר הגעה, לא נשלף")
         + st.card("r-2", "rule", "🔑 המתנה = סיום − הגעה − פרץ")
         + st.card("r-3", "trap", "⚠️ סרק ≠ המתנה")
         + st.card("r-4", "trap", "⚠️ אפקט השיירה: ארוך בראש התור"))

VIDEO = Video("S02", "sched", "FCFS ואפקט השיירה", [title, idea, ex, idle, convoy, exam, recap],
              bank={"2014A-5": None})
