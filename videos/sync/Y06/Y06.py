# -*- coding: utf-8 -*-
"""Y06 · מאפייה, TestAndSet והליבה — video script (build: tools/video/vid.py Y06).

Source: src/courses/sync.py level 6 (lesson + goal: the Bakery algorithm, ordering by (ticket, PID); a solution
without OS calls cannot put a process to sleep, so it busy-waits; TestAndSet spin-locks inside the kernel, which cannot
sleep).
Exam anchor: 2016A-6 (the Linux spin-lock suffers from busy waiting and also from ____: starvation); no guided quiz
uses it. Avoided on purpose: the level-6 quiz items (tickets PID 4 -> 2, PID 2 -> 2, PID 7 -> 1 = 2016B-6; 2021A-7,
2020B-7, 2023B-5, 2017SB-4; the choosing array 2017SA-7, so the choosing array is not discussed), and the bakery
items 2020B-8 / 2022A-5 (kept for the Y07 walkthrough / a twin of it).
Also not staged after review: "no OS calls -> necessarily busy waiting" (2020B-7), "the kernel cannot sleep ->
spin-lock" (2023B-5, 2017SB-4), "any number of processes, no system call" (2021A-7) and the smaller-PID tie rule
(2016B-6): the bakery example has no tie and the tie-breaker is only named, without its direction.
Worked examples: tickets PID 5 -> 3, PID 8 -> 2, PID 6 -> 4 (order 8, 5, 6; w_sync.bakery_order); a
TestAndSet spin-lock with three threads where T1 re-enters three times and T2, T3 never do (w_sync.tas_run, which
also asserts mutual exclusion at every step).
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_sync as w

# ---------------------------------------------------------------- bakery (verified)
TIX = {5: 3, 8: 2, 6: 4}
ORDER = w.bakery_order(TIX)
assert ORDER == [8, 5, 6] and len(set(TIX.values())) == len(TIX)       # no tie in this example

# ---------------------------------------------------------------- TestAndSet (verified)
SCHED = ["T1", "T2", "T3", "T1", "T1", "T2", "T1", "T1", "T3"]
TR, ENT = w.tas_run(SCHED, ["T1", "T2", "T3"])
assert ENT == {"T1": 3, "T2": 0, "T3": 0}
assert [r["res"] for r in TR] == ["in", "spin", "spin", "out", "in", "spin", "out", "in", "spin"]

Q = BANK["2016A-6"]
assert Q["section"] == "sync" and Q["answer_he"] == "הרעבה"

RES = {"in": '<span class="sy-ok">נכנס</span>', "spin": "מסתובב", "out": "יוצא ומשחרר"}
TAS_T = w.table("ts", ["#", "מי", "פעולה", "הוחזר", w.mono("lock"), "תוצאה"],
                [[str(i), w.ltr(r["t"]),
                  w.mono("TestAndSet") if r["act"] == "tas" else w.mono("lock = false"),
                  w.mono("—" if r["old"] is None else str(r["old"]).lower()), w.mono(str(r["lock"]).lower()),
                  RES[r["res"]]] for i, r in enumerate(TR, 1)],
                ids=[f"ts-r{i}" for i in range(1, len(TR) + 1)], cls="sm")

TICKETS = ('<div id="bk-t" class="sy-tix h">'
           + "".join(f'<div class="sy-tk"><span class="p">PID {p}</span><span class="n">{t}</span></div>'
                     for p, t in TIX.items()) + '</div>')

TAS_CODE = ('<pre id="tc-code" class="sy-code2 h"><span class="c">// one atomic CPU instruction</span>\n'
            '<span class="k">bool</span> TestAndSet(<span class="k">bool</span> *lock) {\n'
            '    <span class="k">bool</span> old = *lock;\n    *lock = true;\n    <span class="k">return</span> old;\n}\n\n'
            '<span class="k">while</span> (TestAndSet(&amp;lock))\n    ;                <span class="c">// spin</span>\n'
            '<span class="x">critical section</span>\nlock = false;</pre>')

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נפתור את בעיית הקטע הקריטי **בלי** סמפורים."),
    P("נכיר את אלגוריתם המאפייה ואת TestAndSet, ונראה איפה הליבה עצמה משתמשת בה."),
    P("ובסוף נפתור שאלה ממבחן על המחיר של הפתרון הזה.", hold=0.4),
], stage='<div class="kicker">Y06 · סנכרון: סמפורים וקיפאון</div><h1>מאפייה, TestAndSet והליבה</h1>'
         '<p>קטעים קריטיים בלי מערכת ההפעלה, ולמה הליבה מיוחדת.</p>', layout="title")


bakery = Scene("bakery", "אלגוריתם המאפייה", [
    P("הפתרון הראשון: אלגוריתם **Bakery**, המאפייה."),
    P("כמו בתור במאפייה: כל תהליך שרוצה להיכנס לוקח מספר, אחד יותר מהמספר הגבוה שהוא רואה אצל האחרים.",
      do=show("bk-t")),
    P("ונכנס מי שהמספר שלו הכי קטן.", do=show("bk-c1")),
    P("נסדר. המספר הקטן ביותר הוא שתיים, של PID שמונה. הוא ראשון.", do=show("bk-o1")),
    P("אחריו PID חמש, עם המספר שלוש.", do=show("bk-o2")),
    P("ואחרון PID שש, עם המספר ארבע.", do=show("bk-o3"), hold=0.3),
    P("ומה אם שני תהליכים בוחרים באותו רגע, ומקבלים אותו מספר? אז יש שובר שוויון קבוע, לפי ה-PID.",
      do=show("bk-c2")),
    P("ושימו לב: תהליך שמחכה לתור שלו לא ישן. הוא בודק בלולאה, שוב ושוב.", hold=0.4),
], stage='<div class="sy-stack">' + TICKETS
         + '<div class="sy-ord"><span id="bk-o1" class="h">' + w.ltr("PID 8") + '</span>'
         + '<span id="bk-o2" class="h"> ← ' + w.ltr("PID 5") + '</span>'
         + '<span id="bk-o3" class="h"> ← ' + w.ltr("PID 6") + '</span></div></div>',
   panel=st.card("bk-c1", "rule", "🔑 המספר הקטן ביותר נכנס")
         + st.card("bk-c2", "ex", "מספר שווה ← שובר שוויון לפי PID"))

tas = Scene("tas", "TestAndSet", [
    P("הפתרון השני נשען על החומרה: הפקודה **TestAndSet**.", do=show("tc-code")),
    P("זו פקודת מעבד אחת, אטומית. היא מחזירה את הערך הישן של המנעול, ובאותו צעד מציבה בו אמת.", do=show("tc-1")),
    P("הלולאה מסתובבת כל עוד חזר אמת, כלומר כל עוד מישהו אחר כבר בפנים.", do=show("tc-2")),
    P("כשחוזר שקר, המנעול היה פתוח, ועכשיו הוא כבר נעול בשבילנו. נכנסים.", hold=0.2),
    P("וביציאה פשוט מציבים שקר. זה נקרא **spin-lock**, מנעול מסתובב.", do=show("tc-3")),
    P("ו-Linux משתמשת במנעול כזה בתוך הליבה עצמה.", hold=0.4),
], stage=TAS_CODE,
   panel=st.card("tc-1", "rule", "🔑 מחזירה את הישן, ומציבה " + w.mono("true") + ", אטומית")
         + st.card("tc-2", "ex", "חזר " + w.mono("true") + ": מישהו בפנים, מסתובבים")
         + st.card("tc-3", "ex", "יציאה: " + w.mono("lock = false")))

spin = Scene("spin", "מריצים", [
    P("נריץ שלושה תהליכונים על ליבות שונות. T1 מריץ TestAndSet ראשון: חוזר שקר, והוא בפנים.", do=show("ts", "ts-r1")),
    P("T2 ו-T3 מנסים: חוזר אמת. הם מסתובבים, ושורפים מעבד.", do=show("ts-r2", "ts-r3")),
    P("T1 יוצא ומשחרר. ומיד חוזר לבקש שוב, ומריץ TestAndSet לפני כולם: שוב בפנים.", do=show("ts-r4", "ts-r5")),
    P("T2 בודק: נעול. T1 יוצא, ושוב תופס ראשון.", do=show("ts-r6", "ts-r7", "ts-r8")),
    P("ו-T3 בודק: נעול.", do=show("ts-r9"), hold=0.3),
    P("ההדדיות נשמרה בכל צעד: אף פעם לא היו שניים בפנים.", do=show("sp-c1")),
    P("אבל T1 נכנס שלוש פעמים, ו-T2 ו-T3 אפס. אין תור ואין סדר: מי שמגיע ראשון ל-TestAndSet, מנצח.",
      do=show("sp-c2")),
    P("שום דבר לא מבטיח ש-T2 ייכנס אי פעם.", hold=0.4),
], stage=TAS_T,
   panel=st.card("sp-c1", "ex", "הדדיות: ✓")
         + st.card("sp-c2", "trap", "⚠️ כניסות: " + w.ltr("T1 = 3, T2 = 0, T3 = 0")))


exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: פתרון ה-spin-lock של Linux סובל מבעיה של busy waiting, ובנוסף מאיזו בעיה?"),
    P("את הבעיה הראשונה ראינו: T2 ו-T3 הסתובבו ושרפו מעבד.", do=show("x-1")),
    P("והשנייה: T1 נכנס שוב ושוב, ו-T2 לא נכנס אף פעם. אין שום חסם על מספר העקיפות.", do=show("x-2")),
    P("כלומר אין המתנה חסומה, ולכן תהליכון יכול להידחות לנצח. זו **הרעבה**.", do=show("x-ans"), hold=0.3),
    P("המלכודת היא לענות קיפאון. אבל ראינו ש-T1 כן מתקדם. כשמישהו נכנס, זה לא קיפאון.", do=show("x-t1")),
    P("ההבדל ממאפייה ומסמפור: שם יש מספר בתור או תור של ממתינים, וזה מה שמבטיח שתורו של כל אחד יגיע.",
      do=show("x-t2"), hold=0.5),
], stage='<div class="sy-stack">'
         + st.card("x-1", "ex", "בעיה 1: מסתובבים ← " + w.ltr("busy waiting"))
         + st.card("x-2", "ex", "בעיה 2: T1 עוקף שוב ושוב, אין חסם")
         + st.card("x-t1", "trap", "⚠️ לא קיפאון: T1 מתקדם")
         + st.card("x-t2", "rule", "🔑 מאפייה וסמפור: יש תור ← אין הרעבה")
         + '</div>',
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         '<div id="x-ans" class="qans h"><span class="k">תשובה:</span> הרעבה (starvation)</div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום: במאפייה כל אחד לוקח מספר, והמספר הקטן נכנס.", do=show("s-1")),
    P("TestAndSet מחזירה את הערך הישן ונועלת, בפקודה אטומית אחת.", do=show("s-2")),
    P("ולולאה סביבה היא spin-lock, המנעול המסתובב.", do=show("s-3")),
    P("והמחיר שלו: המתנה פעילה, והרעבה. נתראה בשלב המבחן.", do=show("s-4"), hold=0.6),
], stage=TAS_CODE.replace(' h"', '"').replace('id="tc-code"', 'id="tc-code2"'),
   panel=st.card("s-1", "rule", "🔑 מאפייה: המספר הקטן נכנס")
         + st.card("s-2", "rule", "🔑 TestAndSet: מחזירה את הישן, ונועלת")
         + st.card("s-3", "rule", "🔑 לולאה סביבה = " + w.ltr("spin-lock"))
         + st.card("s-4", "trap", "⚠️ " + w.ltr("spin-lock") + ": המתנה פעילה + הרעבה"))

VIDEO = Video("Y06", "sync", "מאפייה, TestAndSet והליבה", [title, bakery, tas, spin, exam, recap],
              bank={"2016A-6": None})
