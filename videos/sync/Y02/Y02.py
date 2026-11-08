# -*- coding: utf-8 -*-
"""Y02 · סמפורים: wait, signal והערך — video script (build: tools/video/vid.py Y02).

Source: src/courses/sync.py level 2 (lesson + goal: a semaphore is an integer + a queue in the kernel; wait / signal;
what a positive, zero and negative value mean; starting values 1, 0 and N).
Exam anchor: 2017B-6 (signal on a semaphore whose value is not positive: what does the kernel do to the queue?
dequeue the head to Ready); no guided quiz uses it. Avoided on purpose: the level-2 quiz scenarios (start 1 with
three waits -> -2; the same plus a signal -> -1), its exam items 2017SB-9, 2017SA-10, 2015A-5, 2017A-6, and the
twin 2014B-5 (= 2017SB-9). Worked examples: a counting semaphore that starts at 2 with four processes (P1..P4 wait,
then all four signal), and a three-stage chain T1 -> T2 -> T3 on two semaphores that start at 0 (not the
quiz pair "F of A before G of B"), run in the worst order.
Every value, queue and wake-up comes from w_sync.sem_steps, asserted against sims.semaphore.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_sync as w

# ---------------------------------------------------------------- traces (verified)
OPS = "P:P1 P:P2 P:P3 P:P4 V:P1 V:P2 V:P3 V:P4"
TAB, R = w.sem_table("t", 2, OPS)
assert [r["value"] for r in R] == [1, 0, -1, -2, -1, 0, 1, 2]
assert [r["queue"] for r in R][:6] == [[], [], ["P3"], ["P3", "P4"], ["P4"], []]
assert R[4]["woken"] == "P3" and R[5]["woken"] == "P4"           # FIFO: the first to sleep wakes first
assert R[6]["ev"] == "sig" and R[7]["ev"] == "sig"                 # nobody left in the queue

# a three-stage chain T1 -> T2 -> T3 with two semaphores S1, S2 (both 0), run in the worst order: T3, T2, T1
CH = w.Sems(S1=0, S2=0)
CHROWS = []
for who, op, sem in [("T3", "P", "S2"), ("T2", "P", "S1"), ("T1", "V", "S1"), ("T2", "V", "S2")]:
    res = CH.P(who, sem) if op == "P" else CH.V(who, sem)
    CHROWS.append((who, op, sem, CH.v["S1"], CH.v["S2"], res))
CH.check()
assert [(r[3], r[4], r[5]) for r in CHROWS] == [(0, -1, "block"), (-1, -1, "block"), (0, -1, "T2"), (0, 0, "T3")]
CHT = w.table("ch", ["מי", "פעולה", w.mono("S1"), w.mono("S2"), "מה קרה"],
              [["", '<span class="sy-mut">התחלה</span>', w.val(0), w.val(0), ""]]
              + [[w.ltr(a), w.mono(("wait" if o == "P" else "signal") + f"({s})"), w.val(x), w.val(y),
                  "נחסם" if r == "block" else "מעיר את " + w.ltr(r)] for a, o, s, x, y, r in CHROWS],
              ids=[None] + [f"ch-r{i}" for i in range(1, 5)], cls="sm")

Q = BANK["2017B-6"]
assert Q["section"] == "sync" and "Dequeue" in Q["answer_he"]

OPCODE = ('<div class="sy-pair">'
          '<div><div class="sy-ph">wait</div><pre class="sy-code2">S.value--;\n<span class="k">if</span> (S.value &lt; 0)\n'
          '    <span class="x">sleep in S.queue</span>;</pre></div>'
          '<div><div class="sy-ph">signal</div><pre class="sy-code2">S.value++;\n<span class="k">if</span> (S.value &lt;= 0)\n'
          '    <span class="x">wake head of S.queue</span>;</pre></div></div>')

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נפתח את הסמפור, ונבין מה המספר שבתוכו אומר."),
    P("נריץ wait ו-signal צעד אחר צעד, ונקרא את הערך כמו סיפור: כמה פנויים, וכמה ממתינים."),
    P("ובסוף נפתור שאלה ממבחן על מה שהליבה עושה ב-signal.", hold=0.4),
], stage='<div class="kicker">Y02 · סנכרון: סמפורים וקיפאון</div><h1>סמפורים: wait, signal והערך</h1>'
         '<p>מה המספר בתוך סמפור אומר: ערך חיובי, אפס ושלילי, ולאיזה ערך מאתחלים.</p>', layout="title")

idea = Scene("idea", "מה יש בסמפור", [
    P("**semaphore**, סמפור, הוא אובייקט שמערכת ההפעלה מחזיקה בזיכרון הליבה.", do=show("i-c1")),
    P("יש בו שני דברים: מספר שלם, ו**תור** של תהליכים שממתינים.", do=show("i-c2")),
    P("ויש עליו שתי פעולות. הראשונה, wait: מחסירים אחת מהערך.", do=show("i-code")),
    P("אם הערך נעשה **שלילי**, התהליך נכנס לתור והולך לישון. הוא לא רץ ולא שורף מעבד."),
    P("השנייה, signal: מוסיפים אחת לערך."),
    P("ואם הערך עדיין **לא חיובי**, סימן שמישהו ממתין. תהליך אחד יוצא מראש התור ומתעורר.", hold=0.3),
    P("ושתי הפעולות **אטומיות**: אף אחד לא יכול להיכנס באמצע של wait או של signal.", do=show("i-c3"),
      hold=0.4),
], stage=OPCODE.replace('class="sy-pair"', 'id="i-code" class="sy-pair h"'),
   panel=st.card("i-c1", "plain", "סמפור: אובייקט בזיכרון הליבה")
         + st.card("i-c2", "rule", "🔑 סמפור = <b>מספר שלם</b> + <b>תור</b> ממתינים")
         + st.card("i-c3", "rule", "🔑 wait ו-signal אטומיות"))

trace = Scene("trace", "מריצים", [
    P("נריץ. יש שתי מדפסות זהות, ולכן הסמפור מתחיל ב**שתיים**: שתי יחידות פנויות.", do=show("t")),
    P("P1 עושה wait: שתיים פחות אחת, אחת. הערך לא שלילי, אז P1 עובר ומקבל מדפסת.", do=show("t-r1")),
    P("P2 עושה wait: אפס. עדיין לא שלילי, ו-P2 עובר. שתי המדפסות תפוסות.", do=show("t-r2")),
    P("P3 עושה wait: מינוס אחת. הערך שלילי, ולכן P3 נכנס לתור והולך לישון.", do=show("t-r3")),
    P("P4 עושה wait: מינוס שתיים. גם P4 נכנס לתור, אחרי P3.", do=show("t-r4"), hold=0.3),
    P("עכשיו P1 מסיים ועושה signal: מינוס אחת. הערך עדיין לא חיובי, אז ראש התור, P3, מתעורר.",
      do=show("t-r5")),
    P("P3 מקבל את המדפסת ש-P1 שחרר.", hold=0.2),
    P("P2 עושה signal: אפס. גם אפס הוא לא חיובי, ולכן P4 מתעורר. התור ריק.", do=show("t-r6")),
    P("P3 עושה signal: אחת. הפעם הערך חיובי, ואין את מי להעיר.", do=show("t-r7")),
    P("ו-P4 עושה signal: חוזרים לשתיים, כמו בהתחלה.", do=show("t-r8"), hold=0.4),
], stage=TAB, layout="full")

read = Scene("read", "קוראים את הערך", [
    P("עכשיו נקרא את הערך כמו סיפור. יש שלושה מקרים.", do=show("t2")),
    P("ערך **חיובי**: זה מספר היחידות הפנויות. בשורה מספר אחת, הערך אחת: מדפסת אחת פנויה.", do=show("rd-1")),
    P("ערך **אפס**: אין יחידה פנויה, וגם אף אחד לא ממתין. מי שיעשה עכשיו wait, יירדם.", do=show("rd-2")),
    P("ערך **שלילי**: הגודל שלו הוא מספר הממתינים. מינוס שתיים, ובתור באמת שניים: P3 ו-P4.", do=show("rd-3")),
    P("שימו לב: הממתינים לא מבקשים שוב ושוב. הם ישנים בתור, עד ש-signal מעיר אותם.", do=show("rd-4"),
      hold=0.4),
], stage=TAB.replace('id="t"', 'id="t2"').replace('class="h"', 'class=""').replace('id="t-r', 'id="t2-r'),
   panel=st.card("rd-1", "ex", "ערך חיובי: מספר היחידות <b>הפנויות</b>")
         + st.card("rd-2", "ex", "אפס: אין פנוי, ואין ממתין")
         + st.card("rd-3", "rule", "🔑 ערך שלילי: הגודל = מספר <b>הממתינים</b>")
         + st.card("rd-4", "trap", "⚠️ ממתין = ישן בתור, לא בודק בלולאה"))

init = Scene("init", "ערך התחלתי", [
    P("הערך ההתחלתי קובע למה הסמפור משמש. שלושה ערכים חשובים.", do=show("n-1")),
    P("**אחת**: הדדיות. רק תהליך אחד עובר את ה-wait, וכל השאר ממתינים עד ה-signal שלו.", do=show("n-2")),
    P("**$N$**: $N$ יחידות זהות, כמו שתי המדפסות שלנו. זה סמפור סופר.", do=show("n-3"),
      say="אֶן: אֶן יחידות זהות, כמו שתי המדפסות שלנו. זה סמפור סופר."),
    P("ועוד שימוש: שרשרת. T1 טוען נתונים, T2 מעבד אותם, ו-T3 שומר את התוצאה. בדיוק בסדר הזה.", do=show("n-code")),
    P("שני סמפורים, S1 ו-S2, ושניהם מתחילים באפס: אין שום יחידה פנויה, עד שמישהו מאותת.", do=show("n-4"),
      say="שני סמפורים, אֶס אחת ואֶס שתיים, ושניהם מתחילים באפס: אין שום יחידה פנויה, עד שמישהו מאותת."),
    P("נריץ בסדר הכי גרוע: T3 מגיע ראשון, ועושה wait על S2. מינוס אחת, והוא נרדם.", do=show("ch", "ch-r1"),
      say="נריץ בסדר הכי גרוע: טִי שלוש מגיע ראשון, ועושה ווֵייט על אֶס שתיים. מינוס אחת, והוא נרדם."),
    P("T2 מגיע, ועושה wait על S1. גם הוא נרדם.", do=show("ch-r2"),
      say="טִי שתיים מגיע, ועושה ווֵייט על אֶס אחת. גם הוא נרדם."),
    P("T1 מסיים לטעון ועושה signal על S1: חוזר לאפס, ו-T2 מתעורר ומעבד.", do=show("ch-r3"),
      say="טִי אחת מסיים לטעון ועושה סִיגְנָל על אֶס אחת: חוזר לאפס, וטִי שתיים מתעורר ומעבד."),
    P("T2 מסיים ועושה signal על S2, ו-T3 מתעורר ושומר. כל שלב חיכה לשלב שלפניו.", do=show("ch-r4"),
      say="טִי שתיים מסיים ועושה סִיגְנָל על אֶס שתיים, וטִי שלוש מתעורר ושומר. כל שלב חיכה לשלב שלפניו.", hold=0.4),
], stage='<div class="sy-stack">'
         '<pre id="n-code" class="sy-code2 h">T1:  load();  signal(S1);\nT2:  wait(S1);  process();  signal(S2);\nT3:  wait(S2);  save();</pre>'
         + CHT.replace('class="sy-tab sm"', 'class="sy-tab sm h"') + '</div>',
   panel=st.card("n-1", "plain", "הערך ההתחלתי קובע את התפקיד:")
         + st.card("n-2", "rule", "🔑 $1$: הדדיות")
         + st.card("n-3", "rule", "🔑 $N$: $N$ יחידות זהות")
         + st.card("n-4", "rule", "🔑 $0$: אף אחד לא עובר עד שמאותתים"))

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: תהליך מבקש לעשות signal, והליבה רואה שערך הסמפור **איננו חיובי**. מה היא עושה לתור?"),
    P("ערך לא חיובי אחרי ההוספה אומר שלפניה הוא היה שלילי. כלומר יש ממתינים בתור.", do=show("x-1")),
    P("ראינו את זה בטבלה: ה-signal של P1 העלה את הערך ממינוס שתיים למינוס אחת, ו-P3 התעורר.", do=show("x-tr")),
    P("אז הליבה מוציאה תהליך אחד **מראש** התור. מי שנרדם ראשון, מתעורר ראשון.", do=show("x-2")),
    P("והתהליך שהתעורר עובר למצב **Ready**: הוא מוכן לרוץ, וממתין שהמתזמן יבחר בו.", do=show("x-3")),
    P("התשובה: הוצאה מהתור, dequeue, של התהליך שבראש התור, אל Ready.", do=show("x-ans"),
      say="התשובה: הוצאה מהתור, דִי קְיוּ, של התהליך שבראש התור, אל רֶדִי.", hold=0.3),
    P("המלכודת: הליבה לא מעירה את **כל** התור, ולא מאפסת את הערך. רק תהליך אחד, כי נוספה רק יחידה אחת.",
      do=show("x-t"), hold=0.5),
], stage='<div class="sy-stack">'
         + w.table("x-tr", ["#", "מי", "פעולה", "ערך", "תור", "מה קרה"],
                   [["5", w.ltr("P1"), w.mono("signal"), w.val(-1), w.qhtml(["P4"]), "מעיר את " + w.ltr("P3")]],
                   hidden=True)
         + st.card("x-1", "ex", "לא חיובי <b>אחרי</b> ההוספה ← היה שלילי ← יש ממתינים")
         + st.card("x-2", "rule", "🔑 מוציאים <b>אחד</b> מראש התור")
         + st.card("x-3", "rule", "🔑 הוא עובר ל-<b>Ready</b>, לא רץ מיד")
         + st.card("x-t", "trap", "⚠️ לא את כל התור, ולא איפוס של הערך")
         + '</div>',
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         '<div id="x-ans" class="qans h"><span class="k">תשובה:</span> '
         + w.ltr("Dequeue") + ': מוציא תהליך מראש התור ל-' + w.ltr("Ready") + '</div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום: סמפור הוא מספר שלם ותור, בזיכרון הליבה.", do=show("s-1")),
    P("wait מחסיר אחת, ואם הערך שלילי, נרדמים בתור. signal מוסיף אחת, ואם הערך לא חיובי, מעירים את ראש התור.",
      do=show("s-2")),
    P("ערך חיובי הוא מספר הפנויים, וערך שלילי הוא מספר הממתינים.", do=show("s-3")),
    P("ומתחילים באחת להדדיות, באפס לסדר, וב-$N$ ליחידות זהות. נתראה ברמה הבאה.", do=show("s-4"), hold=0.6,
      say="ומתחילים באחת להדדיות, באפס לסדר, ובאֶן ליחידות זהות. נתראה ברמה הבאה."),
], stage=OPCODE,
   panel=st.card("s-1", "rule", "🔑 סמפור = מספר שלם + תור")
         + st.card("s-2", "rule", "🔑 שלילי ב-wait: נרדמים · לא חיובי ב-signal: מעירים אחד")
         + st.card("s-3", "rule", "🔑 חיובי = פנויים · שלילי = ממתינים")
         + st.card("s-4", "trap", "⚠️ $1$ הדדיות · $0$ סדר · $N$ יחידות"))

VIDEO = Video("Y02", "sync", "סמפורים: wait, signal והערך", [title, idea, trace, read, init, exam, recap],
              bank={"2017B-6": None})
