# -*- coding: utf-8 -*-
"""Y04 · יצרן-צרכן וקוראים-כותבים — video script (build: tools/video/vid.py Y04).

Source: src/courses/sync.py level 4 (lesson + goal: the bounded buffer with mutex = 1, empty = N, full = 0 and what
their values mean; readers-writers: a writer alone, the last reader out lets the writer in, writers can starve).
Exam part: an original "שאלה בסגנון מבחן" (bank={}): the producer's two waits swapped (wait(mutex) before
wait(empty)) -> deadlock on a full buffer (the trap listed in the section lesson). No free bank item fits: 2023B-6
(readers-writers, the violated condition; official key "starvation") is a content twin of the level-4 quiz item
2015B-5, so it is not used. Avoided on purpose: the level-4 quiz scenarios (a consumer on an empty buffer with
full = 0; three consumers -> full = -3; 2019A-5, 2021B-7, 2022B-6) are not posed or solved.
Worked examples: a 2-slot buffer where a third put blocks the producer (empty = -1) until a consumer takes one; and
readers 1-3 overlapping while a writer waits. Every value comes from w_sync.pc_run / rw_run (each semaphore re-run
through sims.semaphore).
"""
from vid import P, Scene, Video, show, hide
import stage as st
import w_sync as w

PR, CO = "יצרן", "צרכן"
# ---------------------------------------------------------------- the bounded buffer (verified)
RW, S = w.pc_run(2, [(PR, "put"), (PR, "put"), (PR, "put"), (CO, "take"), (PR, "resume")])
assert [(r["empty"], r["full"], r["mutex"], r["items"]) for r in RW] == [(1, 1, 1, 1), (0, 2, 1, 2), (-1, 2, 1, 2),
                                                                          (0, 1, 1, 1), (0, 2, 1, 2)]
assert RW[2]["blocked"] == [PR] and RW[3]["woke"] == [PR] and not RW[4]["blocked"]

# the swapped producer (exam-style): wait(mutex) before wait(empty)
DW, DS = w.pc_run(2, [(PR, "put"), (PR, "put"), (PR, "put"), (CO, "take")], mutex_first=True)
assert DW[2]["mutex"] == 0 and DW[2]["blocked"] == [PR] and DW[2]["waiting_on"] == {PR: "empty"}
assert sorted(DW[3]["blocked"]) == sorted([PR, CO]) and DW[3]["waiting_on"] == {PR: "empty", CO: "mutex"}
assert DW[3]["items"] == 2                                   # the consumer never reached the buffer

# readers-writers
R1, R2, R3, WR = "קורא 1", "קורא 2", "קורא 3", "כותב"
RR = w.rw_run([(R1, "in"), (WR, "win"), (R2, "in"), (R1, "out"), (R3, "in"), (R2, "out"), (R3, "out")])
assert [r["rc"] for r in RR] == [1, 1, 2, 1, 2, 1, 0]
assert [r["wrt"] for r in RR] == [0, -1, -1, -1, -1, -1, 0]
assert all(WR in r["blocked"] for r in RR[1:6]) and RR[6]["woke"] == WR and RR[6]["inside"] == [WR]


def names(xs):
    return ", ".join(xs) if xs else '<span class="sy-mut">—</span>'


KIND = {"put": "מכניס", "take": "מוציא", "resume": "מתעורר וממשיך"}


def pc_table(pfx, rows, notes):
    body = [["", '<span class="sy-mut">התחלה</span>', w.val(2), w.val(0), w.val(1), "0", ""]]
    for r, n in zip(rows, notes):
        body.append([r["who"], KIND[r["kind"]], w.val(r["empty"]), w.val(r["full"]), w.val(r["mutex"]),
                     str(r["items"]), n])
    return w.table(pfx, ["מי", "פעולה", w.mono("empty"), w.mono("full"), w.mono("mutex"), "בחוצץ", "מה קרה"], body,
                   ids=[None] + [f"{pfx}-r{i}" for i in range(1, len(rows) + 1)])


PCT = pc_table("pc", RW, ["", "החוצץ מלא", "נחסם על " + w.mono("empty"), "מעיר את היצרן", "מכניס את השלישי"])
DLT = pc_table("dl", DW, ["", "החוצץ מלא", "נחסם על " + w.mono("empty") + ", <b>מחזיק</b> " + w.mono("mutex"),
                          "נחסם על " + w.mono("mutex")])

RWK = {"in": "נכנס", "out": "יוצא", "win": "מבקש לכתוב"}
RWT = w.table("rw", ["מי", "פעולה", w.mono("readcount"), w.mono("wrt"), "בפנים", "ממתין"],
              [["", '<span class="sy-mut">התחלה</span>', "0", w.val(1), names([]), names([])]]
              + [[r["who"], RWK[r["kind"]], str(r["rc"]), w.val(r["wrt"]), names(r["inside"]), names(r["blocked"])]
                 for r in RR],
              ids=[None] + [f"rw-r{i}" for i in range(1, len(RR) + 1)], cls="sm")

CODE = ('<div class="sy-pair">'
        '<div><div class="sy-ph">יצרן</div><pre class="sy-code2">wait(empty);\nwait(mutex);\n  <span class="x">put(item);</span>\n'
        'signal(mutex);\nsignal(full);</pre></div>'
        '<div><div class="sy-ph">צרכן</div><pre class="sy-code2">wait(full);\nwait(mutex);\n  <span class="x">take(item);</span>\n'
        'signal(mutex);\nsignal(empty);</pre></div></div>')

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נראה שתי בעיות קלאסיות: יצרן-צרכן, וקוראים-כותבים."),
    P("ונלמד לקרוא את ערך הסמפור כמו סיפור: מי ממתין, ולמה."),
    P("ובסוף שאלה בסגנון מבחן: מה קורה כשמחליפים את סדר ה-wait.", hold=0.4),
], stage='<div class="kicker">Y04 · סנכרון: סמפורים וקיפאון</div><h1>יצרן-צרכן וקוראים-כותבים</h1>'
         '<p>קריאת ערך הסמפור כסיפור: מקומות פנויים, ממתינים, ומי מאותת למי.</p>', layout="title")

buf = Scene("buffer", "החוצץ החסום", [
    P("יצרן מכניס פריטים לחוצץ, וצרכן מוציא אותם. לחוצץ יש מקום ל-$N$ פריטים בלבד.",
      say="יצרן מכניס פריטים לחוצץ, וצרכן מוציא אותם. לחוצץ יש מקום לאֶן פריטים בלבד."),
    P("הפתרון משתמש בשלושה סמפורים.", do=show("b-code")),
    P("mutex מתחיל באחת: רק אחד נוגע בחוצץ בכל רגע.", do=show("b-1")),
    P("empty מתחיל ב-$N$: הוא סופר את המקומות **הפנויים**. היצרן עושה עליו wait לפני שהוא מכניס.",
      do=show("b-2"), say="אֶמְפְּטִי מתחיל באֶן: הוא סופר את המקומות הפנויים. היצרן עושה עליו ווֵייט לפני שהוא מכניס."),
    P("full מתחיל באפס: הוא סופר את המקומות **המלאים**. הצרכן עושה עליו wait לפני שהוא מוציא.",
      do=show("b-3")),
    P("ושימו לב לסדר: קודם wait על הספירה, ורק אחר כך wait על mutex.", do=show("b-4"), hold=0.4),
], stage=CODE.replace('class="sy-pair"', 'id="b-code" class="sy-pair h"'),
   panel=st.card("b-1", "ex", w.mono("mutex = 1") + ": הדדיות")
         + st.card("b-2", "ex", w.mono("empty = N") + ": מקומות פנויים")
         + st.card("b-3", "ex", w.mono("full = 0") + ": מקומות מלאים")
         + st.card("b-4", "rule", "🔑 קודם הספירה, אחר כך " + w.mono("mutex")))

trace = Scene("trace", "מריצים", [
    P("נריץ עם חוצץ של שני מקומות. empty מתחיל בשתיים, full באפס, ו-mutex באחת.", do=show("pc")),
    P("היצרן מכניס פריט: empty יורד לאחת, ו-full עולה לאחת.", do=show("pc-r1")),
    P("עוד פריט: empty אפס, full שתיים. החוצץ מלא.", do=show("pc-r2")),
    P("היצרן מנסה פריט שלישי: wait על empty מוריד אותו למינוס אחת. היצרן נרדם.", do=show("pc-r3")),
    P("הוא נרדם **לפני** ה-wait על mutex, ולכן הוא לא מחזיק אותו. mutex נשאר אחת.", hold=0.3),
    P("הצרכן מוציא פריט. בסוף הוא עושה signal על empty: ממינוס אחת לאפס, והיצרן מתעורר.", do=show("pc-r4")),
    P("היצרן ממשיך מאיפה שעצר, ומכניס את הפריט השלישי. full חוזר לשתיים.", do=show("pc-r5"), hold=0.4),
], stage=PCT, layout="full")

read = Scene("read", "קוראים את הערכים", [
    P("עכשיו נקרא את הערכים.", do=show("pc2")),
    P("בשורה מספר שלוש, empty הוא מינוס אחת. ערך שלילי סופר את מי שממתין על הסמפור: יצרן אחד ישן.",
      do=show("d-2")),
    P("ובשורה מספר ארבע הוא חוזר לאפס: ה-signal של הצרכן העיר את היצרן, ואין יותר ממתינים.", do=show("d-1"),
      hold=0.4),
], stage=PCT.replace('id="pc"', 'id="pc2"').replace('id="pc-r', 'id="pc2-r').replace(' class="h"', ''),
   panel=st.card("d-2", "rule", "🔑 ערך שלילי = מספר הממתינים על הסמפור")
         + st.card("d-1", "ex", "חזר לאפס: אין ממתינים"))

rw = Scene("rw", "קוראים-כותבים", [
    P("הבעיה השנייה: קוראים וכותבים. הרבה קוראים יכולים לקרוא יחד, אבל כותב צריך את הנתונים **לבד**."),
    P("סמפור wrt שומר על הכתיבה, ומונה readcount סופר כמה קוראים בפנים.",
      do=show("rw"), say="סמפור ווּ אַר טִי שומר על הכתיבה, ומונה רִיד קָאוּנְט סופר כמה קוראים בפנים."),
    P("קורא 1 נכנס. הוא הראשון, ולכן wrt יורד לאפס.", do=show("rw-r1"),
      say="קורא אחת נכנס. הוא הראשון, ולכן ווּ אַר טִי יורד לאפס."),
    P("הכותב מבקש לכתוב: wrt יורד למינוס אחת, והוא נרדם, כי קורא בפנים.", do=show("rw-r2"),
      say="הכותב מבקש לכתוב: ווּ אַר טִי יורד למינוס אחת, והוא נרדם, כי קורא בפנים."),
    P("קורא 2 נכנס. הוא לא הראשון, אז הוא לא נוגע ב-wrt, ונכנס מיד.", do=show("rw-r3"),
      say="קורא שתיים נכנס. הוא לא הראשון, אז הוא לא נוגע בווּ אַר טִי, ונכנס מיד."),
    P("קורא 1 יוצא, אבל קורא 2 עדיין בפנים. readcount יורד לאחת, ו-wrt לא משתנה.", do=show("rw-r4"),
      say="קורא אחת יוצא, אבל קורא שתיים עדיין בפנים. רִיד קָאוּנְט יורד לאחת, ווּ אַר טִי לא משתנה."),
    P("קורא 3 נכנס, וקורא 2 יוצא. עדיין נשאר קורא בפנים, והכותב ממתין.", do=show("rw-r5", "rw-r6"),
      say="קורא שלוש נכנס, וקורא שתיים יוצא. עדיין נשאר קורא בפנים, והכותב ממתין."),
    P("קורא 3 יוצא. readcount מגיע לאפס, ויש signal על wrt, שמעיר את הכותב.", do=show("rw-r7", "rw-c1"),
      say="קורא שלוש יוצא. רִיד קָאוּנְט מגיע לאפס, ויש סִיגְנָל על ווּ אַר טִי, שמעיר את הכותב."),
    P("ומה אם קוראים חדשים ממשיכים להיכנס לפני שהאחרונים יוצאים? readcount לא מגיע לאפס, והכותב ממשיך לחכות.",
      do=show("rw-c2"), hold=0.5),
], stage=RWT, panel=st.card("rw-c1", "rule", "🔑 " + w.mono("readcount = 0") + " ← signal על " + w.mono("wrt"))
                    + st.card("rw-c2", "trap", "⚠️ קוראים חופפים: " + w.mono("readcount") + " לא מתאפס"))

exam = Scene("exam", "שאלה בסגנון מבחן", [
    P("שאלה בסגנון מבחן: מתכנת החליף אצל היצרן את סדר שתי הפעולות. קודם wait על mutex, ואז wait על empty."),
    P("מה יכול לקרות? נריץ את אותו תרחיש: חוצץ של שני מקומות.", do=show("dl")),
    P("שני הפריטים הראשונים נכנסים כרגיל, והחוצץ מלא.", do=show("dl-r1", "dl-r2")),
    P("היצרן מנסה פריט שלישי. הפעם הוא קודם תופס את mutex: אחת לאפס. ואז wait על empty, והוא נרדם.",
      do=show("dl-r3")),
    P("הוא ישן, **ומחזיק** את mutex.", do=show("x-1"), hold=0.3),
    P("הצרכן מגיע להוציא פריט. wait על full עובר, אבל wait על mutex: מינוס אחת. גם הוא נרדם.", do=show("dl-r4")),
    P("היצרן מחכה למקום פנוי, שרק הצרכן יכול לפנות. והצרכן מחכה ל-mutex, שהיצרן מחזיק.", do=show("x-2")),
    P("כל אחד מחכה לשני, ואף אחד לא יעיר אף אחד. זה **קיפאון**.", do=show("x-ans"), hold=0.3),
    P("המלכודת: לחשוב שסדר ה-wait לא משנה. לא נרדמים כשמחזיקים את mutex: קודם הספירה, אחר כך המנעול.",
      do=show("x-t"), hold=0.5),
], stage=DLT,
   panel='<div class="qstem"><span class="qid">בסגנון מבחן</span>ביצרן הוחלף הסדר: <span class="sy-mono">'
         'wait(mutex)</span> ואז <span class="sy-mono">wait(empty)</span>. מה עלול לקרות?</div>'
         + st.card("x-1", "ex", "היצרן ישן ומחזיק " + w.mono("mutex"))
         + st.card("x-2", "ex", "יצרן ← מחכה ל-" + w.mono("empty") + " · צרכן ← מחכה ל-" + w.mono("mutex"))
         + '<div id="x-ans" class="qans h"><span class="k">תשובה:</span> קיפאון, כשהחוצץ מלא</div>'
         + st.card("x-t", "trap", "⚠️ קודם הספירה, אחר כך " + w.mono("mutex")),
   layout="split")

recap = Scene("recap", "סיכום", [
    P("לסיכום: בחוצץ החסום, mutex באחת, empty ב-$N$, ו-full באפס.", do=show("s-1"),
      say="לסיכום: בחוצץ החסום, מְיוּטֶקְס באחת, אֶמְפְּטִי באֶן, ופוּל באפס."),
    P("וערך שלילי של סמפור סופר את מי שממתין עליו.", do=show("s-2")),
    P("בקוראים-כותבים, הכותב צריך את הנתונים לבד, ונכנס רק כש-readcount חוזר לאפס.", do=show("s-3")),
    P("ו-wait על הספירה תמיד לפני wait על mutex, אחרת קיפאון. נתראה ברמה הבאה.", do=show("s-4"), hold=0.6),
], stage=CODE,
   panel=st.card("s-1", "rule", "🔑 " + w.mono("mutex=1, empty=N, full=0"))
         + st.card("s-2", "rule", "🔑 שלילי = ממתינים")
         + st.card("s-3", "rule", "🔑 כותב לבד · נכנס כש-" + w.mono("readcount = 0"))
         + st.card("s-4", "trap", "⚠️ קודם הספירה, אחר כך " + w.mono("mutex")))

VIDEO = Video("Y04", "sync", "יצרן-צרכן וקוראים-כותבים", [title, buf, trace, read, rw, exam, recap], bank={})
