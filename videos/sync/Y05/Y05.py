# -*- coding: utf-8 -*-
"""Y05 · קיפאון והפילוסופים הסועדים — video script (build: tools/video/vid.py Y05).

Source: src/courses/sync.py level 5 (lesson + goal: deadlock = everybody waits for something another holds; locks
taken in conflicting order; dining philosophers; fixes: a global order, or taking both chopsticks atomically, not
shown: 2017SA-9) and the four Coffman conditions of the section lesson.
Exam anchor: 2015B-4 (a state in which no process manages to enter the critical section at all: deadlock); no
guided quiz uses it. Avoided on purpose: the level-5 quiz scenarios (two semaphores A/B in opposite order and the
"minimum is 2" items 2023A-6, 2017SB-8; the same-order pair; three philosophers numbered 0-2; 2022A-6, 2017SA-9).
Worked examples: three processes on S1, S2, S3 in a ring (P1: S1 then S2, P2: S2 then S3, P3: S3 then S1), fixed by
a global order (P3 takes S1 before S3); five philosophers, fixed by numbering the chopsticks.
Every verdict, path and cycle comes from w_sync.deadlock_path, asserted against sims.can_deadlock.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import sims
import w_sync as w

# ---------------------------------------------------------------- three processes in a ring (verified)
RING = [["S1", "S2"], ["S2", "S3"], ["S3", "S1"]]
D = w.deadlock_path(RING)
assert D["path"] == [(0, "S1"), (1, "S2"), (2, "S3")]
assert D["held"] == {"S1": 0, "S2": 1, "S3": 2} and D["waits"] == {0: "S2", 1: "S3", 2: "S1"}
assert D["cycle"] == [0, "S2", 1, "S3", 2, "S1"]
FIX = [["S1", "S2"], ["S2", "S3"], ["S1", "S3"]]
assert w.deadlock_path(FIX) is None and not sims.can_deadlock(FIX)

POS = w.ring(["P1", "S2", "P2", "S3", "P3", "S1"], 330, 300, 225)
KIND = {n: ("p" if n[0] == "P" else "r") for n in POS}
EDGES = [("h1", "S1", "P1", "hold"), ("h2", "S2", "P2", "hold"), ("h3", "S3", "P3", "hold"),
         ("w1", "P1", "S2", "wait"), ("w2", "P2", "S3", "wait"), ("w3", "P3", "S1", "wait")]
G = w.graph("g", POS, KIND, EDGES, w=660, h=600, cycle=[e[0] for e in EDGES])

# ---------------------------------------------------------------- five philosophers (verified)
PH = sims.philosophers(5)
DP = w.deadlock_path(PH)
assert DP["path"] == [(i, i) for i in range(5)] and DP["waits"] == {i: (i + 1) % 5 for i in range(5)}
assert len(DP["cycle"]) == 10                                      # all five philosophers are on the cycle
PHO = sims.philosophers(5, ordered=True)
assert PHO[4] == [0, 4] and w.deadlock_path(PHO) is None and not sims.can_deadlock(PHO)
assert sims.can_deadlock(PH)

names = []
for i in range(5):
    names += [f"c{i}", f"F{i}"]
FPOS = w.ring(names, 330, 310, 245)
FKIND = {n: ("p" if n[0] == "F" else "r") for n in FPOS}
FLAB = {**{f"F{i}": f"P{i + 1}" for i in range(5)}, **{f"c{i}": str(i + 1) for i in range(5)}}
FEDGES = ([(f"h{i}", f"c{i}", f"F{i}", "hold") for i in range(5)]
          + [(f"w{i}", f"F{i}", f"c{(i + 1) % 5}", "wait") for i in range(5)])
FG = w.graph("f", FPOS, FKIND, FEDGES, w=660, h=620, labels=FLAB, cycle=[e[0] for e in FEDGES])

Q = BANK["2015B-4"]
assert Q["section"] == "sync" and Q["answer_he"].lower() == "deadlock"

COF = w.table("cf", ["תנאי", "פירוש"], [[f"<b>{a}</b>", b] for a, b in w.COFFMAN],
              ids=[f"cf-{i}" for i in range(1, 5)], cls="lg")

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נראה איך תהליכים נתקעים לתמיד, כשכל אחד מחכה למשאב שאחר מחזיק."),
    P("נבנה מעגל המתנה צעד אחר צעד, נכיר את הפילוסופים הסועדים, ונראה איך שוברים את המעגל."),
    P("ובסוף נפתור שאלה ממבחן.", hold=0.4),
], stage='<div class="kicker">Y05 · סנכרון: סמפורים וקיפאון</div><h1>קיפאון והפילוסופים הסועדים</h1>'
         '<p>כשכולם מחכים למישהו אחר: ארבעת התנאים, מעגל ההמתנה, ואיך שוברים אותו.</p>', layout="title")

coff = Scene("coffman", "ארבעה תנאים", [
    P("**deadlock**, קיפאון, הוא מצב שבו קבוצת תהליכים תקועה: כל אחד מחכה למשאב שמישהו אחר בקבוצה מחזיק."),
    P("קיפאון יכול לקרות רק כשמתקיימים ארבעה תנאים, **כולם** יחד. הם נקראים תנאי Coffman.", do=show("cf")),
    P("אחד: הדדיות. משאב מוחזק בידי תהליך אחד בלבד, כמו סמפור בינארי.", do=show("cf-1")),
    P("שתיים: החזק והמתן. תהליך מחזיק משאב אחד, ובאותו זמן מחכה למשאב נוסף.", do=show("cf-2")),
    P("שלוש: אין הפקעה. אי אפשר לקחת ממנו את המשאב בכוח. הוא משחרר רק כשהוא רוצה.", do=show("cf-3")),
    P("וארבע: המתנה מעגלית. יש מעגל, שבו כל תהליך מחכה למשאב של הבא אחריו.", do=show("cf-4")),
    P("מספיק לשבור תנאי **אחד**, וקיפאון כבר לא יכול לקרות.", do=show("cf-k"), hold=0.4),
], stage='<div class="sy-stack">' + COF.replace('id="cf" class="sy-tab lg"', 'id="cf" class="sy-tab lg h"')
         + st.card("cf-k", "rule", "🔑 קיפאון דורש את <b>ארבעתם</b>. שוברים אחד, והוא לא יקרה") + '</div>',
   layout="full")

cycle = Scene("cycle", "מעגל המתנה", [
    P("שלושה תהליכים ושלושה סמפורים בינאריים. כל תהליך לוקח שני סמפורים, אחד אחרי השני.", do=show("cy-code")),
    P("P1 לוקח את S1 ואז את S2. P2 לוקח את S2 ואז את S3. ו-P3 לוקח את S3 ואז את S1.",
      say="פִּי אחת לוקח את אֶס אחת ואז את אֶס שתיים. פִּי שתיים לוקח את אֶס שתיים ואז את אֶס שלוש. ופִּי שלוש לוקח את אֶס שלוש ואז את אֶס אחת."),
    P("נריץ סדר רע. P1 תופס את S1.", do=show("g-e-h1"), say="נריץ סדר רע. פִּי אחת תופס את אֶס אחת."),
    P("החלפה, ו-P2 תופס את S2.", do=show("g-e-h2"), say="החלפה, ופִּי שתיים תופס את אֶס שתיים."),
    P("החלפה, ו-P3 תופס את S3.", do=show("g-e-h3"), say="החלפה, ופִּי שלוש תופס את אֶס שלוש."),
    P("עכשיו P1 רוצה את S2, אבל P2 מחזיק אותו. P1 נרדם.", do=show("g-e-w1"),
      say="עכשיו פִּי אחת רוצה את אֶס שתיים, אבל פִּי שתיים מחזיק אותו. פִּי אחת נרדם."),
    P("P2 רוצה את S3, ש-P3 מחזיק. גם הוא נרדם.", do=show("g-e-w2"),
      say="פִּי שתיים רוצה את אֶס שלוש, שפִּי שלוש מחזיק. גם הוא נרדם."),
    P("ו-P3 רוצה את S1, ש-P1 מחזיק. נרדם.", do=show("g-e-w3"),
      say="ופִּי שלוש רוצה את אֶס אחת, שפִּי אחת מחזיק. נרדם.", hold=0.3),
    P("הנה המעגל: כל אחד מחכה לבא אחריו, ואף אחד לא ישחרר כלום. זה קיפאון.", do=show("g-cy", "cy-c1")),
    P("ארבעת התנאים כאן: סמפור בינארי, כל אחד מחזיק ומחכה, אין הפקעה, והמעגל עצמו. ארבעתם מתקיימים.",
      do=show("cy-c2"), hold=0.3),
    P("ושימו לב: זה סדר **אחד** אפשרי. אם P1 היה לוקח את שני הסמפורים ומסיים לפני האחרים, הכול היה עובר.",
      do=show("cy-c3"),
      say="ושימו לב: זה סדר אחד אפשרי. אם פִּי אחת היה לוקח את שני הסמפורים ומסיים לפני האחרים, הכול היה עובר."),
    P("קיפאון הוא **אפשרות**: מספיק שיש סדר ריצה אחד שמוביל אליו.", hold=0.4),
], stage='<div class="sy-stack" style="gap:10px">' + G + w.legend() + '</div>',
   panel='<pre id="cy-code" class="sy-code2 h">P1: wait(S1); wait(S2);\nP2: wait(S2); wait(S3);\nP3: wait(S3); wait(S1);</pre>'
         + st.card("cy-c1", "rule", "🔑 מחכה ל: " + w.ltr("P1 → P2 → P3 → P1"))
         + st.card("cy-c2", "ex", "ארבעת התנאים מתקיימים")
         + st.card("cy-c3", "trap", "⚠️ קיפאון <b>אפשרי</b>, לא ודאי"))

fix = Scene("fix", "שוברים את המעגל", [
    P("איך מתקנים? שוברים את ההמתנה המעגלית: נותנים לסמפורים מספרים, וכולם לוקחים **מהקטן לגדול**.",
      do=show("fx-code")),
    P("P1 ו-P2 כבר עושים את זה. רק P3 משתנה: קודם S1, ואחר כך S3.", do=show("fx-1"),
      say="פִּי אחת ופִּי שתיים כבר עושים את זה. רק פִּי שלוש משתנה: קודם אֶס אחת, ואחר כך אֶס שלוש."),
    P("עכשיו P1 ו-P3 שניהם מתחילים ב-S1, ומתחרים עליו. מי שמפסיד, נרדם בלי להחזיק כלום.", do=show("fx-2"),
      say="עכשיו פִּי אחת ופִּי שלוש שניהם מתחילים באֶס אחת, ומתחרים עליו. מי שמפסיד, נרדם בלי להחזיק כלום."),
    P("ובאופן כללי: מי שמחזיק את הסמפור **הגבוה** ביותר מבין כולם, מבקש רק סמפורים גבוהים ממנו.",
      do=show("fx-3")),
    P("ואף אחד לא מחזיק סמפור גבוה משלו, אז מה שהוא מבקש פנוי. הוא מסיים ומשחרר, ואין מעגל."),
    P("בדקנו את כל סדרי הריצה האפשריים: עם הסדר הזה, אין אף סדר שמוביל לקיפאון.", do=show("fx-k"), hold=0.4),
], stage='<pre id="fx-code" class="sy-code2 h" style="font-size:34px">P1: wait(S1); wait(S2);\nP2: wait(S2); wait(S3);\n'
         'P3: <span class="x">wait(S1); wait(S3);</span></pre>',
   panel=st.card("fx-1", "ex", "רק P3 משתנה: " + w.mono("S1") + " ואז " + w.mono("S3"))
         + st.card("fx-2", "ex", "התחרות על " + w.mono("S1") + ": המפסיד לא מחזיק כלום")
         + st.card("fx-3", "rule", "🔑 מחזיק הגבוה ביותר לא מחכה לאף אחד")
         + st.card("fx-k", "rule", "🔑 סדר גלובלי = אין המתנה מעגלית"))

philo = Scene("philo", "הפילוסופים הסועדים", [
    P("ועכשיו הדוגמה הקלאסית: חמישה פילוסופים סביב שולחן עגול, ומקל אחד בין כל שניים.", do=show("f")),
    P("כדי לאכול, פילוסוף צריך שני מקלות: הוא לוקח את המקל שמשמאלו, ואחר כך את המקל שמימינו."),
    P("בגרף: מצב שהחיפוש שלנו מצא. כל פילוסוף מחזיק מקל אחד, ומחכה למקל שהשכן מחזיק.",
      do=show(*[f"f-e-h{i}" for i in range(5)], *[f"f-e-w{i}" for i in range(5)])),
    P("זה אותו מעגל שראינו קודם, רק עם חמישה.", do=show("f-cy", "f-c1"), hold=0.3),
    P("והתיקון הוא אותו תיקון: סדר גלובלי. ממספרים את המקלות, וכל אחד מבקש אותם לפי הסדר.", do=show("f-c2")),
    P("ל-P1 עד P4 זה לא משנה כלום. אבל P5, שיושב בין מקל חמש למקל אחת, לוקח עכשיו קודם את מקל אחת.",
      say="לפִּי אחת עד פִּי ארבע זה לא משנה כלום. אבל פִּי חמש, שיושב בין מקל חמש למקל אחת, לוקח עכשיו קודם את מקל אחת."),
    P("הוא מתחרה עם P1 על אותו מקל ראשון, והמעגל נשבר. בדקנו: אין סדר שמוביל לקיפאון.", do=show("f-c3"),
      say="הוא מתחרה עם פִּי אחת על אותו מקל ראשון, והמעגל נשבר. בדקנו: אין סדר שמוביל לקיפאון.", hold=0.4),
], stage='<div class="sy-stack" style="gap:8px">' + FG.replace('class="sy-g" id="f"', 'class="sy-g h" id="f"')
         + w.legend() + '</div>',
   panel=st.card("f-c1", "trap", "⚠️ אותו מעגל, עם חמישה")
         + st.card("f-c2", "rule", "🔑 סדר גלובלי על המקלות")
         + st.card("f-c3", "ex", "P5 מבקש את 1 לפני 5: המעגל נשבר"))

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: איך נקרא מצב שבו **אף** תהליך לא מצליח להיכנס לקטע הקריטי, בכלל?"),
    P("אם אף אחד לא נכנס, זה לא שמישהו מקופח. כולם תקועים, וכל אחד מחכה למשהו שאחר מחזיק.", do=show("x-1")),
    P("זה בדיוק מה שראינו במעגל: התשובה היא **deadlock**, קיפאון.", do=show("x-ans"), hold=0.3),
    P("המלכודת היא לענות הרעבה. בהרעבה האחרים **כן** נכנסים, ורק תהליך אחד נעקף שוב ושוב.", do=show("x-t1")),
    P("ההבדל: בקיפאון אף אחד, בהרעבה כולם חוץ ממישהו.", do=show("x-t2"), hold=0.5),
], stage='<div class="sy-stack">'
         + st.card("x-1", "ex", "אף אחד לא נכנס ← כולם מחכים זה לזה")
         + st.card("x-t1", "trap", "⚠️ לא הרעבה: שם האחרים <b>כן</b> נכנסים")
         + st.card("x-t2", "rule", "🔑 קיפאון: אף אחד · הרעבה: כולם חוץ ממישהו")
         + '</div>',
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         '<div id="x-ans" class="qans h"><span class="k">תשובה:</span> ' + w.ltr("Deadlock") + ' (קיפאון)</div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום: קיפאון דורש את ארבעת התנאים יחד: הדדיות, החזק והמתן, אין הפקעה, והמתנה מעגלית.",
      do=show("s-1")),
    P("מספיק סדר ריצה אחד רע, והתהליכים נתקעים במעגל.", do=show("s-2")),
    P("שוברים את המעגל בסדר גלובלי: כולם לוקחים מהמספר הקטן לגדול.", do=show("s-3")),
    P("ובפילוסופים הסועדים: אותו מעגל, ואותו תיקון. נתראה ברמה הבאה.", do=show("s-4"), hold=0.6),
], stage=G.replace('id="g', 'id="rg').replace('url(#g-', 'url(#rg-').replace(' h"', '"').replace('class="h"', ''),
   panel=st.card("s-1", "rule", "🔑 קיפאון = ארבעת התנאים יחד")
         + st.card("s-2", "trap", "⚠️ קיפאון אפשרי = יש סדר ריצה אחד רע")
         + st.card("s-3", "rule", "🔑 סדר גלובלי שובר את המעגל")
         + st.card("s-4", "rule", "🔑 פילוסופים: אותו מעגל, אותו תיקון"))

VIDEO = Video("Y05", "sync", "קיפאון והפילוסופים הסועדים", [title, coff, cycle, fix, philo, exam, recap],
              bank={"2015B-4": None})
