# -*- coding: utf-8 -*-
"""Y07 · בוס: מבחן סנכרון — video script (build: tools/video/vid.py Y07).

Boss walkthrough of three exam questions that no guided quiz (level or boss) uses:
  2017SB-5  binary vs counting semaphores: each can be implemented by the other (answer ג)
  2022B-5   the entry code's second job, after announcing the intent: check that no other process is inside
  2020B-8   when the Bakery algorithm compares PIDs: only when the tickets are equal
Avoided on purpose: the boss quiz items (2024A-10, 2023A-10, 2014B-9, 2017A-10, 2019B-4, 2023A-6) and every level
quiz item; 2022A-5 (a twin of 2020B-8) is not shown either.
Verified here: a counting semaphore rebuilt as an integer counter guarded by a binary semaphore gives exactly the
values and wake-ups of sims.semaphore (w_sync.sem_steps) on a test run (shown as one run, not a proof); the check-before-announce entry code lets two
threads in (small simulator below); the bakery order is w_sync.bakery_order.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import sims
import w_sync as w

# ---------------------------------------------------------------- Q1: a counting semaphore from binary ones
Q1 = BANK["2017SB-5"]
assert Q1["answer_he"].startswith("(ג)")


def counting_from_binary(n, ops):
    """the counter C (protected by a binary mutex, so every update below is one atomic step) and the processes asleep
    on a binary 'delay' semaphore, FIFO. Returns rows (who, op, C, sleeping list)."""
    c, sleeping, rows = n, [], []
    mutex = 1
    for tok in ops.split():
        op, who = tok.split(":")
        assert mutex == 1
        mutex = 0                                          # wait(mutex)
        if op == "P":
            c -= 1
            if c < 0:
                sleeping.append(who)                       # signal(mutex); wait(delay)
        else:
            c += 1
            if c <= 0:
                sleeping.pop(0)                            # signal(delay): one sleeper continues
        mutex = 1                                          # signal(mutex)
        rows.append((who, op, c, list(sleeping)))
    return rows


OPS1 = "P:P1 P:P2 P:P3 V:P1 P:P4 V:P2 V:P3"
CB = counting_from_binary(2, OPS1)
REF = w.sem_steps(2, OPS1)
assert [r[2] for r in CB] == [r["value"] for r in REF] and [r[3] for r in CB] == [r["queue"] for r in REF]
assert [r[2] for r in CB] == [1, 0, -1, 0, -1, 0, 1]
assert REF[-1]["value"] == sims.semaphore(2, OPS1)["value"]

CBT = w.table("cb", ["מי", "פעולה", w.mono("C"), "ישנים"],
              [[w.ltr(a), w.mono("wait" if o == "P" else "signal"), w.val(c), w.qhtml(q)] for a, o, c, q in CB],
              ids=[f"cb-r{i}" for i in range(1, len(CB) + 1)], cls="sm")


# ---------------------------------------------------------------- Q2: the entry code's two jobs
Q2 = BANK["2022B-5"]
assert "בדיקה" in Q2["answer_he"]


def entry_run(order, check_first):
    """two threads, entry code = announce (flag[me] = 1) and check (pass if flag[other] == 0), in the given order of
    steps; returns the set of threads that got in. A thread whose check fails stays out."""
    flag, step, inside = {"T1": 0, "T2": 0}, {"T1": 0, "T2": 0}, set()
    prog = ["check", "announce"] if check_first else ["announce", "check"]
    ok = {"T1": None, "T2": None}
    for t in order:
        other = "T2" if t == "T1" else "T1"
        act = prog[step[t]]
        step[t] += 1
        if act == "announce":
            flag[t] = 1
        else:
            ok[t] = flag[other] == 0
        if step[t] == 2 and ok[t]:
            inside.add(t)
    return inside


assert entry_run(["T1", "T2", "T1", "T2"], check_first=True) == {"T1", "T2"}   # both checked an empty room
assert len(entry_run(["T1", "T2", "T1", "T2"], check_first=False)) <= 1
assert len(entry_run(["T1", "T1", "T2", "T2"], check_first=False)) <= 1

# ---------------------------------------------------------------- Q3: when bakery compares PIDs
Q3 = BANK["2020B-8"]
assert "שווים" in Q3["answer_he"]
TIX = {12: 3, 5: 3, 9: 2}
assert w.bakery_order(TIX) == [9, 5, 12]

BAKE = ('<pre class="sy-code2" style="font-size:23px"><span class="c">// entry code of process i</span>\n'
        'choosing[i] = true;\n'
        '<span id="e-a">number[i] = 1 + max(number[0..n-1]);</span>   <span class="c">// 1</span>\n'
        'choosing[i] = false;\n'
        '<span class="k">for</span> (j = 0; j &lt; n; j++) {\n'
        '  <span class="k">while</span> (choosing[j]) ;\n'
        '  <span id="e-b"><span class="k">while</span> (number[j] != 0 &amp;&amp;\n'
        '         <span id="e-c">(number[j], j) &lt; (number[i], i)</span>) ;</span>  <span class="c">// 2</span>\n'
        '}\n<span class="x">critical section</span>\nnumber[i] = 0;</pre>')

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("זה שלב המבחן של קורס הסנכרון. נפתור יחד שלוש שאלות אמיתיות ממבחנים."),
    P("סמפור בינארי מול סמפור סופר, שני התפקידים של קוד הכניסה, ומתי אלגוריתם המאפייה משווה PID."),
    P("בכל שאלה ננמק כל צעד, ונראה את המלכודת.", hold=0.4),
], stage='<div class="kicker">Y07 · סנכרון: סמפורים וקיפאון</div><h1>בוס: מבחן סנכרון</h1>'
         '<p>שאלות מהמבחנים מכל הנושא, עם הנימוק המלא והמלכודת של כל אחת.</p>', layout="title")

q1 = Scene("q1", "שאלה 1", [
    P("שאלה ראשונה: יש סמפור בינארי, שערכו אפס או אחת, וסמפור סופר, שערכו כל מספר. את מי מהם אפשר לממש בעזרת השני?"),
    P("כיוון ראשון: סמפור בינארי הוא מקרה פרטי של סופר: סופר שמתחיל באחת ומשמש כמנעול נותן בדיוק את אותה התנהגות.",
      do=show("a-1")),
    P("כיוון שני: סופר בעזרת בינאריים. מחזיקים מונה רגיל, $C$, וסמפור בינארי שמגן עליו.", do=show("a-2"),
      say="כיוון שני: סופר בעזרת בינאריים. מחזיקים מונה רגיל, סִי, וסמפור בינארי שמגן עליו."),
    P("ב-wait מחסירים אחת מהמונה, ואם הוא שלילי, נרדמים על סמפור בינארי שני.", do=show("a-3")),
    P("וב-signal מוסיפים אחת, ואם המונה לא חיובי, מעירים ישן אחד."),
    P("נריץ את הבנייה הזאת. המונה מתחיל בשתיים.", do=show("cb", "cb-r1", "cb-r2")),
    P("P3 מוריד למינוס אחת ונרדם. P1 עושה signal, חוזרים לאפס, ו-P3 מתעורר.", do=show("cb-r3", "cb-r4")),
    P("P4 נרדם, P2 מעיר אותו, ו-P3 מחזיר לאחת. בהרצה הזאת קיבלנו אותם ערכים ואותם ישנים כמו בסמפור סופר.",
      do=show("cb-r5", "cb-r6", "cb-r7")),
    P("אז שני הכיוונים אפשריים, והתשובה היא ג.", do=show("q1-ans"), hold=0.3),
    P("המלכודת: לחשוב שבינארי חלש יותר, ולכן אפשר רק בכיוון אחד. מונה רגיל ועוד בינאריים משלימים את החסר.",
      do=show("a-t"), hold=0.5),
], stage='<div class="sy-stack" style="gap:12px">'
         + st.card("a-1", "ex", "בינארי ← סופר שמתחיל ב-1")
         + st.card("a-2", "ex", "סופר ← מונה " + w.mono("C") + " + בינארי שמגן עליו")
         + st.card("a-3", "ex", w.mono("C < 0") + ": ישנים · " + w.mono("C <= 0") + " ב-signal: מעירים")
         + CBT.replace('class="sy-tab sm"', 'class="sy-tab sm h"') + '</div>',
   panel=f'<div class="qstem" style="font-size:27px"><span class="qid">{Q1["id"]}</span>{Q1["he"]}</div>'
         + '<div id="q1-ans" class="qans h"><span class="k">תשובה:</span> (ג) כל אחד אפשר לממש בעזרת השני</div>'
         + st.card("a-t", "trap", "⚠️ לא רק בכיוון אחד: מונה + בינאריים = סופר"))

q2 = Scene("q2", "שאלה 2", [
    P("שאלה שנייה: בקוד הכניסה לקטע הקריטי חייבים לבצע שתי פעולות. אחת היא הודעה לכל העולם שאנחנו רוצים להיכנס. מהי השנייה?"),
    P("נסתכל על קוד הכניסה של המאפייה.", do=show("bk")),
    P("השורה שמסומנת אחת: לוקחים מספר. זו ההודעה: אני רוצה להיכנס, וזה המקום שלי בתור.", do=show("b-1")),
    P("הלולאה: עוברים על כל האחרים, ומחכים כל עוד מישהו מהם לפנינו. זו **הבדיקה** שאף אחד אחר לא בקטע הקריטי, או קודם לנו.",
      do=show("b-2")),
    P("למה צריך את שתיהן, ובסדר הזה? בקוד כללי עם דגלים, נניח שבודקים **לפני** שמודיעים.", do=show("b-3")),
    P("T1 בודק: אף אחד לא הודיע. T2 בודק: אף אחד לא הודיע. ועכשיו שניהם מודיעים, ושניהם נכנסים.",
      do=show("b-4")),
    P("ההדדיות נשברה. לכן קודם מודיעים, ורק אחר כך בודקים.", hold=0.3),
    P("התשובה: לבדוק שאין תהליך אחר בקטע הקריטי.", do=show("q2-ans"), hold=0.5),
], stage='<div class="sy-stack" style="gap:16px">' + BAKE.replace('<pre class="sy-code2"', '<pre id="bk" class="sy-code2 h"')
         + st.card("b-3", "trap", "⚠️ בודקים לפני שמודיעים?")
         + st.card("b-4", "ex", "שניהם ראו חדר ריק ← שניהם בפנים") + '</div>',
   panel=f'<div class="qstem" style="font-size:30px"><span class="qid">{Q2["id"]}</span>{Q2["he"]}</div>'
         + st.card("b-1", "ex", "1. הודעה: לוקחים מספר")
         + st.card("b-2", "rule", "🔑 2. בדיקה: אף אחד אחר לא בפנים או לפניי")
         + '<div id="q2-ans" class="qans h"><span class="k">תשובה:</span> בדיקה שאין תהליך אחר בקטע הקריטי</div>')

q3 = Scene("q3", "שאלה 3", [
    P("שאלה שלישית: מתי אלגוריתם המאפייה משווה את מספרי ה-PID של התהליכים?"),
    P("בקוד שלנו ההשוואה היא על **זוגות**: קודם המספר בתור, ורק אחר כך ה-PID.", do=show("e3")),
    P("השוואת זוגות מכריעה לפי האיבר הראשון. ה-PID נכנס לתמונה רק כשהמספרים **שווים**.", do=show("c-1")),
    P("דוגמה: ל-PID תשע המספר שתיים, ול-PID שתים עשרה ול-PID חמש המספר שלוש.", do=show("c-tix")),
    P("תשע ראשון, בלי שום השוואת PID, כי שתיים קטן משלוש.", do=show("c-o1")),
    P("בין שתים עשרה לחמש המספר שווה, ורק כאן משווים PID: חמש קטן יותר, ולכן הוא לפני שתים עשרה.", do=show("c-o2")),
    P("התשובה: כשמספרי הכרטיס שלהם שווים.", do=show("q3-ans"), hold=0.3),
    P("המלכודת: לחשוב שה-PID קובע תמיד. הוא רק שובר שוויון. מספר קטן יותר נכנס קודם, גם עם PID גדול.",
      do=show("c-t"), hold=0.5),
], stage='<div class="sy-stack">'
         + '<div id="e3" class="sy-big h" style="font-size:40px">(number[j], j) &lt; (number[i], i)</div>'
         + '<div id="c-tix" class="sy-tix h">' + "".join(
             f'<div class="sy-tk"><span class="p">PID {p}</span><span class="n">{t}</span></div>' for p, t in TIX.items())
         + '</div><div class="sy-ord"><span id="c-o1" class="h">' + w.ltr("PID 9") + '</span>'
         + '<span id="c-o2" class="h"> ← ' + w.ltr("PID 5") + ' ← ' + w.ltr("PID 12") + '</span></div>'
         + st.card("c-t", "trap", "⚠️ ה-PID רק שובר שוויון") + '</div>',
   panel=f'<div class="qstem"><span class="qid">{Q3["id"]}</span>{Q3["he"]}</div>'
         + st.card("c-1", "rule", "🔑 קודם המספר. PID רק כשהמספרים <b>שווים</b>")
         + '<div id="q3-ans" class="qans h"><span class="k">תשובה:</span> כשמספרי ה-' + w.ltr("ticket")
         + ' שלהם שווים</div>')

recap = Scene("recap", "סיכום הקורס", [
    P("לסיכום הקורס כולו: מצב תחרות הוא תוצאה שתלויה בסדר, ושלושת התנאים הם הדדיות, התקדמות והמתנה חסומה.",
      do=show("s-1")),
    P("סמפור הוא מספר ותור: ערך חיובי סופר פנויים, ושלילי סופר ממתינים.", do=show("s-2")),
    P("ב-Linux: semget יוצרת, semop מבצעת, ו-semctl מאתחלת ומוחקת.", do=show("s-3")),
    P("קיפאון דורש את ארבעת התנאים, ושוברים אותו בסדר גלובלי או בלקיחה אטומית.", do=show("s-4")),
    P("ובלי מערכת ההפעלה: המתנה פעילה. בהצלחה במבחן!", do=show("s-5"), hold=0.6),
], stage='<div class="sy-stack">'
         + st.card("s-1", "rule", "🔑 הדדיות · התקדמות · המתנה חסומה")
         + st.card("s-2", "rule", "🔑 סמפור = מספר + תור · שלילי = ממתינים")
         + st.card("s-3", "rule", "🔑 semget · semop · semctl")
         + st.card("s-4", "rule", "🔑 קיפאון: ארבעה תנאים · סדר גלובלי או הכול יחד")
         + st.card("s-5", "rule", "🔑 בלי מערכת ההפעלה: " + w.ltr("busy waiting"))
         + '</div>', layout="full")

VIDEO = Video("Y07", "sync", "בוס: מבחן סנכרון", [title, q1, q2, q3, recap],
              bank={"2017SB-5": None, "2022B-5": None, "2020B-8": None})
