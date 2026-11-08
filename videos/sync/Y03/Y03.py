# -*- coding: utf-8 -*-
"""Y03 · סמפורים ב-Linux: semget, semop, semctl — video script (build: tools/video/vid.py Y03).

Source: src/courses/sync.py level 3 (lesson + goal: the three system calls and what they really do; struct sembuf;
sem_op < 0 / > 0; filling sem_op does nothing until semop; wait on 0 sleeps; many operations in one atomic call).
Exam anchor: 2016B-10 (SETVAL zeroes semaphore #0, then semop with sem_op = -1: the following code runs only if
sops->sem_num != 0); no guided quiz uses it. Avoided on purpose: the level-3 quiz items (2026A-10, 2015A-9 with
sem_op = -10, 2022A-10 with 123 semaphores, 2024B-10, 2022B-10, 2023B-10), the boss items (2024A-10 five + five,
2023A-10, 2014B-9, 2017A-10 ipcrm 666) and the twins 2014A-9 (= 2026A-10), 2016A-10 (= 2023B-10), 2019A-10 (semget
decides the size, close to 2022A-10). Worked example: an array of 3, #1 set to 2, a wait of 1 then a wait of 2 (sleeps),
and one call with two waits that sleeps holding neither.
Every value comes from w_sync.linux_semop (the Linux all-or-nothing rule, asserted on hand-checked cases).
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_sync as w
from html import escape as esc

# ---------------------------------------------------------------- the worked example (verified)
V0 = [None, None, None]                                       # after semget: three semaphores, not initialised by us
V1 = [None, 2, None]                                          # semctl(semid, 1, SETVAL, arg) with arg.val = 2
V2, R2 = w.linux_semop([0, 2, 0], [(1, -1)])
assert (V2[1], R2) == (1, "ok")
V3, R3 = w.linux_semop(V2, [(1, -2)])
assert (V3, R3) == (V2, "sleep")                              # needs 2, has 1: sleeps, nothing changes
V4, R4 = w.linux_semop([0, 1, 0], [(1, -1), (2, -1)])        # two waits in ONE call; #2 is 0
assert (V4, R4) == ([0, 1, 0], "sleep")                       # #1 is not taken either
V5, R5 = w.linux_semop([0, 1, 1], [(1, -1), (2, -1)])
assert (V5, R5) == ([0, 0, 0], "ok")

# exam 2016B-10: SETVAL puts 0 in semaphore #0; the wait acts on sops->sem_num
Q = BANK["2016B-10"]
assert "SETVAL" in Q["code"] and "sem_num" in Q["answer_he"]
assert w.linux_semop([0, 1], [(0, -1)])[1] == "sleep"         # sem_num == 0: waits on the 0 -> sleeps
assert w.linux_semop([0, 1], [(1, -1)])[1] == "ok"            # another semaphore with a positive value: passes


def arr(pfx, vals, note=""):
    cells = "".join(f'<td>{"?" if v is None else v}</td>' for v in vals)
    return (f'<table id="{pfx}" class="sy-tab lg h" style="direction:ltr"><thead><tr><th></th><th>#0</th><th>#1</th><th>#2</th></tr></thead>'
            f'<tbody><tr><td class="sy-mut">value</td>{cells}</tr></tbody></table>')


CALLS = w.table("c", ["קריאה", "מה היא עושה"], [
    [w.mono("semget(key, n, flags)"), "יוצרת קבוצה, מחזירה מזהה"],
    [w.mono("semop(semid, sops, nsops)"), "מבצעת את הפעולות"],
    [w.mono("semctl(semid, num, cmd, ...)"), "קריאת הבקרה"],
], ids=["c-1", "c-2", "c-3"], cls="lg")

SEMBUF = ('<pre id="b-code" class="sy-code2 h"><span class="k">struct</span> sembuf {\n'
          '    <span class="k">short</span> sem_num;  <span class="c">// איזה סמפור במערך</span>\n'
          '    <span class="k">short</span> sem_op;   <span class="c">// כמה להחסיר או להוסיף</span>\n'
          '    <span class="k">short</span> sem_flg;\n};</pre>')

EX = ('<pre class="sy-code2">semid = semget(IPC_PRIVATE, 3, 0600);\n'
      '<span id="e-l2">arg.val = 2;  semctl(semid, 1, SETVAL, arg);</span>\n'
      '<span id="e-l3">sops[0].sem_num = 1;  sops[0].sem_op = -1;\n'
      'semop(semid, sops, 1);</span>\n'
      '<span id="e-l4">sops[0].sem_op = -2;\n'
      'semop(semid, sops, 1);</span></pre>')

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נעבור מהסמפור של התיאוריה לסמפורים האמיתיים של Linux."),
    P("נכיר את שלוש קריאות המערכת semget, semop ו-semctl, ונראה מה כל אחת באמת עושה."),
    P("ובסוף נפתור שאלת קוד ממבחן, עם מלכודת.", hold=0.4),
], stage='<div class="kicker">Y03 · סנכרון: סמפורים וקיפאון</div><h1>סמפורים ב-Linux: semget, semop, semctl</h1>'
         '<p>שלוש קריאות המערכת ומה הן באמת עושות: יצירה, פעולות, אתחול ומחיקה.</p>', layout="title")

calls = Scene("calls", "שלוש קריאות", [
    P("ב-Linux אין קריאת מערכת בשם wait, ואין בשם signal. יש שלוש קריאות אחרות."),
    P("semget יוצרת קבוצה של סמפורים, שממוספרים מאפס.", do=show("c-1")),
    P("היא מחזירה מזהה, semid, ודרכו פונים לקבוצה בכל שאר הקריאות.", do=show("k-1")),
    P("semop היא שמבצעת את הפעולות על הסמפורים. מה בדיוק, נראה עוד רגע במבנה שמעבירים לה.", do=show("c-2")),
    P("semctl היא קריאת הבקרה. איתה נותנים ערך התחלתי: SETVAL לסמפור אחד, או SETALL לכולם.", do=show("c-3")),
    P("ואיתה גם מסירים את הקבוצה בסוף, עם IPC_RMID.", do=show("k-3"), hold=0.4),
], stage=CALLS,
   panel=st.card("k-1", "ex", "semget מחזירה " + w.mono("semid"))
         + st.card("k-3", "ex", w.mono("SETVAL") + " / " + w.mono("SETALL") + ": אתחול · "
                   + w.mono("IPC_RMID") + ": מחיקה"))

sembuf = Scene("sembuf", "struct sembuf", [
    P("כל פעולה מתוארת במבנה בשם sembuf.", do=show("b-code")),
    P("sem_num אומר על **איזה** סמפור במערך פועלים. המספור מתחיל באפס."),
    P("ו-sem_op אומר מה עושים: מספר שלילי הוא wait. מינוס אחת מחסיר אחת, מינוס שתיים מחסיר שתיים.",
      do=show("b-1")),
    P("מספר חיובי הוא signal: הוא מוסיף לערך, ומעיר מי שמחכה.", do=show("b-2")),
    P("ואם אי אפשר להחסיר, כי הערך קטן מדי, התהליך **ישן** עד שאפשר. זו לא שגיאה.", do=show("b-3"), hold=0.4),
], stage=SEMBUF,
   panel=st.card("b-1", "rule", "🔑 " + w.mono("sem_op < 0") + ": wait, מחסירים")
         + st.card("b-2", "rule", "🔑 " + w.mono("sem_op > 0") + ": signal, מוסיפים")
         + st.card("b-3", "ex", "אי אפשר להחסיר ← ישנים, לא שגיאה"))

run = Scene("run", "מריצים קוד", [
    P("נריץ קוד קטן. semget יוצרת שלושה סמפורים, שמספריהם אפס, אחת ושתיים.", do=show("a0")),
    P("אנחנו לא סומכים על הערך שלהם. מאתחלים בעצמנו."),
    P("semctl עם SETVAL שמה שתיים בסמפור מספר אחת.", do=hide("a0") + show("a1", "e-h2")),
    P("עכשיו sem_num הוא אחת, ו-sem_op מינוס אחת."),
    P("הקריאה ל-semop מבצעת את ה-wait: משתיים לאחת. ממשיכים לרוץ.", do=hide("a1") + show("a2", "e-h3")),
    P("עכשיו sem_op מינוס שתיים, ו-semop שוב. צריך להחסיר שתיים, ויש רק אחת.", do=show("e-h4")),
    P("לכן התהליך **ישן**, והערך נשאר אחת. הוא יתעורר רק כשמישהו יוסיף מספיק.", do=show("r-s1")),
    P("שימו לב: זה שונה מהסמפור של התיאוריה. ב-Linux הערך לא יורד מתחת לאפס, והליבה סופרת את הישנים בנפרד.",
      do=show("r-c1"), hold=0.4),
], stage='<div class="sy-stack">'
         + EX.replace('<span id="e-l2">', '<span id="e-l2"><span id="e-h2" class="h">▶</span> ')
             .replace('<span id="e-l3">', '<span id="e-l3"><span id="e-h3" class="h">▶</span> ')
             .replace('<span id="e-l4">', '<span id="e-l4"><span id="e-h4" class="h">▶</span> ')
         + '<div class="swap" style="--swap-h:130px"><div>' + arr("a0", V0) + '</div><div>' + arr("a1", V1)
         + '</div><div>' + arr("a2", [None, V2[1], None]) + '</div></div></div>',
   panel=st.card("r-s1", "rule", "🔑 צריך $2$, יש $1$: ישן, והערך לא משתנה")
         + st.card("r-c1", "ex", "ב-Linux הערך לא שלילי. הישנים נספרים בנפרד"))

atom = Scene("atom", "הכול או כלום", [
    P("ועכשיו קריאת semop אחת עם שתי פעולות.", do=show("t-code")),
    P("נניח שסמפור מספר אחת שווה אחת, וסמפור מספר שתיים שווה אפס. ובקריאה אחת: wait על שניהם.", do=show("t-v")),
    P("מסמפור מספר אחת אפשר להחסיר, ומסמפור מספר שתיים לא. מה קורה?"),
    P("הקריאה כולה ישנה, ו**שום** פעולה לא מתבצעת. סמפור מספר אחת נשאר אחת: התהליך לא מחזיק אותו.",
      do=show("t-r1")),
    P("כשסמפור מספר שתיים יעלה לאחת, ואם סמפור מספר אחת עדיין אחת, שתי הפעולות יתבצעו יחד: שניהם יורדים לאפס.",
      do=show("t-r2")),
    P("הכול או כלום. נשתמש בזה בהמשך, כדי לפתור קיפאון של הפילוסופים הסועדים.", do=show("t-k"), hold=0.4),
], stage='<div class="sy-stack">'
         '<pre id="t-code" class="sy-code2 h">sops[0] = { 1, -1, 0 };    <span class="c">// wait על #1</span>\n'
         'sops[1] = { 2, -1, 0 };    <span class="c">// wait על #2</span>\n'
         'semop(semid, sops, 2);     <span class="c">// nsops = 2</span></pre>'
         + w.table("t-tab", ["", "#1", "#2", "מה קרה"], [
             ["לפני", "1", "0", ""],
             ["אחרי", str(V4[1]), str(V4[2]), "ישן, לא לקח כלום"],
             ["כש-#2 עולה ל-1", str(V5[1]), str(V5[2]), "שתי הפעולות יחד"]],
             ids=["t-v", "t-r1", "t-r2"], cls="lg") + '</div>',
   panel=st.card("t-k", "rule", "🔑 קריאה אחת = הכול או כלום"))

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן. כל המשתנים והסמפור הוגדרו כהלכה, והקוד הזה רץ. מתי יתבצעו הפקודות שאחריו?"),
    P("שורה ראשונה ושנייה: semctl עם SETVAL שמה אפס בסמפור. באיזה סמפור? הארגומנט השני: מספר אפס.",
      do=show("x-1")),
    P("אחר כך sem_op מינוס אחת, ו-semop. זה wait, אבל על **איזה** סמפור?", do=show("x-2")),
    P("לא על הסמפור שאתחלנו. על הסמפור ש-sem_num מצביע עליו, וה-sem_num לא מופיע בקוד בכלל.", do=show("x-3")),
    P("אם sem_num הוא אפס, הפעולה היא על הסמפור שאיפסנו הרגע, ואין ממה להחסיר. התהליך נתקע שם, והפקודות שאחריו לא מתבצעות.",
      do=show("x-4")),
    P("אז הפקודות שאחרי הקוד יתבצעו רק אם sem_num **שונה מאפס**: ה-wait פועל על סמפור אחר.", do=show("x-ans")),
    P("ולמען הדיוק: גם הסמפור האחר צריך ערך חיובי. השאלה מניחה שהכול הוגדר כהלכה.", do=show("x-5"), hold=0.3),
    P("המלכודת: לחשוב שה-wait פועל על הסמפור שאותחל בשורה למעלה. הוא פועל על sem_num, תמיד.", do=show("x-t"),
      hold=0.5),
], stage='<div class="sy-stack">'
         + st.card("x-1", "ex", w.mono("semctl(semid, 0, SETVAL, …)") + ": סמפור <b>#0</b> מקבל 0")
         + st.card("x-2", "ex", w.mono("sem_op = -1") + ": wait")
         + st.card("x-3", "rule", "🔑 ה-wait פועל על " + w.mono("sops->sem_num"))
         + st.card("x-4", "ex", "אם " + w.mono("sem_num == 0") + ": זה הסמפור שאיפסנו ← נתקעים")
         + st.card("x-5", "plain", "(והסמפור האחר צריך ערך חיובי)")
         + st.card("x-t", "trap", "⚠️ לא הסמפור שאותחל, אלא " + w.mono("sem_num"))
         + '</div>',
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         f'<pre class="qcode">{esc(Q["code"])}</pre>'
         '<div id="x-ans" class="qans h"><span class="k">תשובה:</span> ' + w.mono("sops->sem_num") + ' שונה מ-0</div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום: semget יוצרת את קבוצת הסמפורים, ומחזירה מזהה.", do=show("s-1")),
    P("semop מבצעת את הפעולות: sem_op שלילי מחסיר, וחיובי מוסיף. ובקריאה עם כמה פעולות: הכול או כלום.",
      do=show("s-2")),
    P("semctl היא קריאת הבקרה, עם SETVAL בהתחלה ו-IPC_RMID בסוף.", do=show("s-3")),
    P("והפעולה תמיד על הסמפור ש-sem_num בוחר. נתראה ברמה הבאה.", do=show("s-4"),
      hold=0.6),
], stage=CALLS.replace(' class="h"', ''),
   panel=st.card("s-1", "rule", "🔑 semget: יוצרת, מחזירה " + w.mono("semid"))
         + st.card("s-2", "rule", "🔑 semop: " + w.mono("sem_op") + " מחסיר או מוסיף")
         + st.card("s-3", "rule", "🔑 semctl: " + w.mono("SETVAL") + " · " + w.mono("IPC_RMID"))
         + st.card("s-4", "trap", "⚠️ הפעולה על הסמפור ש-" + w.mono("sem_num") + " בוחר"))

VIDEO = Video("Y03", "sync", "סמפורים ב-Linux: semget, semop, semctl", [title, calls, sembuf, run, atom, exam, recap],
              bank={"2016B-10": None})
