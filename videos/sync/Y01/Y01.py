# -*- coding: utf-8 -*-
"""Y01 · מצבי תחרות וקטע קריטי — video script (build: tools/video/vid.py Y01).

Source: src/courses/sync.py level 1 (lesson + goal: race condition, critical section, the three conditions, and the
related words busy waiting / starvation / deadlock).
Exam anchor: 2026A-5 (a solution without bounded waiting: what problem may occur? starvation); no guided quiz uses
it. Avoided on purpose: the six level-1 quiz items (2024B-5, 2021A-6, 2020A-8, 2021B-6, 2015A-3, 2015A-4) are not
posed or solved as questions; 2015B-4 (no process enters at all = deadlock) is kept for Y05.
Worked example: two threads incrementing a shared counter that starts at 5 (w_sync.interleave): the order
T1,T2,T1,T2,T1,T2 ends at 6, the serial order at 7 (asserted).
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_sync as w

# ---------------------------------------------------------------- the race (verified)
PROGS = {"T1": [("ld", "r1", "count"), ("add", "r1", 1), ("st", "count", "r1")],
         "T2": [("ld", "r2", "count"), ("add", "r2", 1), ("st", "count", "r2")]}
ORDER = ["T1", "T2", "T1", "T2", "T1", "T2"]
IL, STATES = w.il_view("il", PROGS, ORDER, {"count": 5}, titles={"T1": "T1", "T2": "T2"})
assert [s[1]["T1"].get("r1") for s in STATES] == [None, 5, 5, 6, 6, 6, 6]
assert [s[1]["T2"].get("r2") for s in STATES] == [None, None, 5, 5, 6, 6, 6]
assert [s[0]["count"] for s in STATES] == [5, 5, 5, 5, 5, 6, 6]
SERIAL = w.interleave(PROGS, ["T1"] * 3 + ["T2"] * 3, {"count": 5})[-1][0]["count"]
assert SERIAL == 7 and STATES[-1][0]["count"] == 6          # two increments, one lost

Q = BANK["2026A-5"]
assert Q["section"] == "sync" and "starvation" in Q["answer_he"]

CS_CODE = ('<pre class="sy-code2"><span class="k">while</span> (1) {\n'
           '    <span id="cs-1" class="x">entry section</span>      <span class="c">// מבקשים להיכנס</span>\n'
           '    <span id="cs-2" class="x">critical section</span>   <span class="c">// count++</span>\n'
           '    <span id="cs-3" class="x">exit section</span>       <span class="c">// מודיעים שיצאנו</span>\n'
           '    remainder section\n}</pre>')

COND = w.table("cd", ["תנאי", "מה הוא דורש"], [
    ["<b>Mutual exclusion</b><br>הדדיות", "לכל היותר תהליך אחד בפנים"],
    ["<b>Progress</b><br>התקדמות", "הקטע פנוי ויש מי שרוצה: מישהו נכנס"],
    ["<b>Bounded waiting</b><br>המתנה חסומה", "חסם על מספר העקיפות של ממתין"],
], ids=["cd-1", "cd-2", "cd-3"], cls="lg")

WORDS_T = w.table("wd", ["מושג", "מה קורה", "מי נכנס"], [
    ["<b>busy waiting</b>", "בודקים שוב ושוב בלולאה, ושורפים מעבד", "בסוף נכנסים"],
    ["<b>starvation</b> · הרעבה", "תהליך אחד נעקף שוב ושוב", "אחרים כן"],
    ["<b>deadlock</b> · קיפאון", "כולם מחכים זה לזה", "אף אחד"],
], ids=["wd-1", "wd-2", "wd-3"], cls="lg")

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נראה מה קורה כששני תהליכונים נוגעים באותו משתנה בדיוק באותו זמן."),
    P("נבין מהו מצב תחרות, מהו הקטע הקריטי, ומהם שלושת התנאים שכל פתרון חייב לקיים."),
    P("ובסוף נפתור שאלה ממבחן.", hold=0.4),
], stage='<div class="kicker">Y01 · סנכרון: סמפורים וקיפאון</div><h1>מצבי תחרות וקטע קריטי</h1>'
         '<p>שלושת התנאים שכל פתרון לבעיית הקטע הקריטי חייב לעמוד בהם, ומה קורה כשאחד מהם חסר.</p>',
   layout="title")

race = Scene("race", "מצב תחרות", [
    P("שני תהליכונים, T1 ו-T2. כל אחד מהם מגדיל באחת מונה משותף. המונה מתחיל בחמש.", do=show("il")),
    P("בקוד זו שורה אחת, count++. אבל המעבד מבצע אותה בשלוש פקודות.", do=show("r-c0"),
      say="בקוד זו שורה אחת, קָאוּנְט פלוס פלוס. אבל המעבד מבצע אותה בשלוש פקודות."),
    P("קוראים את המונה לרגיסטר, מוסיפים אחת ברגיסטר, וכותבים בחזרה."),
    P("T1 קורא את המונה לרגיסטר שלו: חמש.", do=w.il_do("il", PROGS, 1)),
    P("עכשיו מערכת ההפעלה מחליפה ל-T2, והוא קורא גם הוא: חמש.", do=w.il_do("il", PROGS, 2)),
    P("T1 חוזר ומוסיף אחת: שש. אבל רק ברגיסטר שלו.", do=w.il_do("il", PROGS, 3)),
    P("T2 מוסיף אחת: גם אצלו שש.", do=w.il_do("il", PROGS, 4)),
    P("T1 כותב שש למונה.", do=w.il_do("il", PROGS, 5)),
    P("ו-T2 כותב את השש שלו. המונה נשאר שש.", do=w.il_do("il", PROGS, 6), hold=0.4),
    P("שתי הגדלות, והמונה עלה רק באחת. הגדלה אחת **אבדה**.", do=show("r-c1") + w.il_clear("il", 6)),
    P("אם T1 היה מסיים את שלוש הפקודות לפני ש-T2 מתחיל, היינו מקבלים שבע.", do=show("r-c2")),
    P("כלומר התוצאה תלויה בסדר שבו התהליכונים רצו. זה **race condition**, מצב תחרות.", do=show("r-c3"),
      hold=0.4),
], stage=IL,
   panel=st.card("r-c0", "plain", "<span class=\"sy-mono\">count++</span> = שלוש פקודות: קריאה, חיבור, כתיבה")
         + st.card("r-c1", "trap", "⚠️ שתי הגדלות, ו-$5 \\to 6$ בלבד")
         + st.card("r-c2", "ex", "בלי שזירה: $5 \\to 7$")
         + st.card("r-c3", "rule", "🔑 תוצאה שתלויה בסדר הריצה: <b>race condition</b>"))

cs = Scene("cs", "הקטע הקריטי", [
    P("הקוד שנוגע בנתון המשותף נקרא **critical section**, הקטע הקריטי. אצלנו: שלוש הפקודות של ההגדלה.",
      do=show("cs-2")),
    P("הרעיון של כל פתרון: לעטוף את הקטע הקריטי בקוד כניסה ובקוד יציאה."),
    P("בקוד הכניסה תהליך מבקש רשות להיכנס.", do=show("cs-1")),
    P("ובקוד היציאה הוא מודיע שיצא, כדי שמישהו אחר יוכל להיכנס.", do=show("cs-3")),
    P("כל השאר, הקוד שלא נוגע בנתון המשותף, רץ בלי שום הגבלה.", do=show("cs-c1")),
    P("ומה הופך את קוד הכניסה והיציאה לפתרון **טוב**? יש לזה שלושה תנאים.", hold=0.4),
], stage=CS_CODE.replace('id="cs-1" class="x"', 'id="cs-1" class="x h"')
                .replace('id="cs-2" class="x"', 'id="cs-2" class="x h"')
                .replace('id="cs-3" class="x"', 'id="cs-3" class="x h"'),
   panel=st.card("cs-c1", "rule", "🔑 הקטע הקריטי = הקוד שנוגע בנתון <b>המשותף</b>"))

cond = Scene("cond", "שלושה תנאים", [
    P("התנאי הראשון: **Mutual exclusion**, הדדיות. לכל היותר תהליך אחד בתוך הקטע הקריטי, בכל רגע.",
      do=show("cd-1")),
    P("זה בדיוק מה שנשבר במונה: שני התהליכונים היו באמצע ההגדלה בו זמנית.", do=show("c-c1")),
    P("התנאי השני: **Progress**, התקדמות. אם הקטע פנוי ויש מי שרוצה להיכנס, מישהו מהם נכנס.",
      do=show("cd-2")),
    P("דוגמה לפתרון שנכשל כאן: תור קבוע. משתנה אומר שעכשיו התור של T2, ורק הוא רשאי להיכנס.",
      do=show("c-c2")),
    P("אבל T2 עסוק בדברים אחרים ולא רוצה להיכנס. T1 רוצה, הקטע ריק, ו-T1 בכל זאת מחכה."),
    P("הקטע ריק, ומי שרוצה להיכנס לא נכנס: ההתקדמות נשברה. במקרה הקיצוני אף אחד לא נכנס, וזה קיפאון.", do=show("c-c3"), hold=0.3),
    P("התנאי השלישי: **Bounded waiting**, המתנה חסומה. יש חסם על כמה פעמים אחרים נכנסים לפני תהליך שממתין.",
      do=show("cd-3")),
    P("נניח ש-T2 ממתין, ו-T1 יוצא ומיד נכנס שוב, שוב ושוב. הקטע לא תקוע: T1 מתקדם.", do=show("c-c4")),
    P("ההתקדמות נשמרת, אבל T2 עלול לחכות לנצח. זו **הרעבה**, starvation.", do=show("c-c5"), hold=0.4),
], stage=COND,
   panel=st.card("c-c1", "trap", "⚠️ בלי הדדיות: הגדלה אבדה")
         + st.card("c-c2", "ex", "תור קבוע: רק T2 רשאי, ו-T2 לא מעוניין")
         + st.card("c-c3", "rule", "🔑 בלי התקדמות: קיפאון")
         + st.card("c-c4", "ex", "T1 נכנס שוב ושוב, T2 ממתין")
         + st.card("c-c5", "rule", "🔑 בלי המתנה חסומה: הרעבה"))

words = Scene("words", "שלושה מושגים", [
    P("שלושה מושגים שמתבלבלים ביניהם במבחן. נשים אותם זה לצד זה."),
    P("**busy waiting**, המתנה פעילה: התהליך בודק שוב ושוב בלולאה אם מותר לו להיכנס.", do=show("wd-1")),
    P("הוא לא ישן. הוא רץ על המעבד ושורף זמן על בדיקות, אבל בסוף הוא כן נכנס."),
    P("**starvation**, הרעבה: אחרים נכנסים, ותהליך אחד נעקף שוב ושוב ולא נכנס לעולם.", do=show("wd-2")),
    P("**deadlock**, קיפאון: כולם מחכים זה לזה, ו**אף אחד** לא נכנס.", do=show("wd-3"), hold=0.3),
    P("ההבדל: בהרעבה כולם חוץ מאחד נכנסים, ובקיפאון אף אחד. המתנה פעילה היא לא תוצאה, אלא **איך** מחכים.",
      do=show("w-c1"), hold=0.4),
], stage='<div class="sy-stack">' + WORDS_T
         + st.card("w-c1", "rule", "🔑 הרעבה: כולם חוץ מאחד · קיפאון: אף אחד · המתנה פעילה: <b>איך</b> מחכים") + '</div>',
   layout="full")

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: פתרון מסוים לבעיית הקטע הקריטי לא כולל bounded waiting. איזו בעיה עלולה להתרחש?"),
    P("נחזור להגדרה: המתנה חסומה היא חסם על מספר הפעמים שאחרים עוקפים תהליך שממתין.", do=show("x-1")),
    P("אם אין חסם, שום דבר לא מונע מהאחרים לעקוף אותו פעם אחרי פעם, בלי סוף.", do=show("x-2")),
    P("האחרים נכנסים ויוצאים, אז אין כאן קיפאון. אבל התהליך הזה לא נכנס לעולם.", do=show("x-3")),
    P("ולכן התשובה: **הרעבה**, starvation.", do=show("x-ans"), hold=0.3),
    P("המלכודת היא לענות קיפאון. קיפאון הוא כשאף אחד לא נכנס, וזה מה שהתקדמות מונעת, לא המתנה חסומה.",
      do=show("x-t1")),
    P("וגם לא המתנה פעילה: היא מתארת **איך** מחכים, לא **אם** בסוף נכנסים.", do=show("x-t2"), hold=0.5),
], stage=(
    '<div class="sy-stack">'
    + st.card("x-1", "ex", "המתנה חסומה = חסם על מספר העקיפות")
    + st.card("x-2", "ex", "אין חסם ← עוקפים את הממתין בלי סוף")
    + st.card("x-3", "rule", "🔑 האחרים מתקדמים, הוא לא נכנס לעולם: הרעבה")
    + st.card("x-t1", "trap", "⚠️ לא קיפאון: את זה מונעת <b>התקדמות</b>")
    + st.card("x-t2", "trap", "⚠️ לא המתנה פעילה: זה <b>איך</b> מחכים")
    + '</div>'),
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         f'<div id="x-ans" class="qans h"><span class="k">תשובה:</span> הרעבה (starvation)</div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום: כשהתוצאה תלויה בסדר הריצה, זה מצב תחרות.", do=show("s-1")),
    P("הקטע הקריטי הוא הקוד שנוגע בנתון המשותף, ועוטפים אותו בקוד כניסה ויציאה.", do=show("s-2")),
    P("שלושה תנאים: הדדיות, התקדמות, והמתנה חסומה.", do=show("s-3")),
    P("בלי התקדמות מקבלים קיפאון, ובלי המתנה חסומה מקבלים הרעבה. נתראה ברמה הבאה.", do=show("s-4"), hold=0.6),
], stage='<div class="sy-stack"><div class="sy-big">count++ = load · add · store</div></div>',
   panel=st.card("s-1", "rule", "🔑 תלוי בסדר = <b>race condition</b>")
         + st.card("s-2", "rule", "🔑 כניסה · קטע קריטי · יציאה")
         + st.card("s-3", "rule", "🔑 הדדיות · התקדמות · המתנה חסומה")
         + st.card("s-4", "trap", "⚠️ בלי התקדמות: קיפאון · בלי המתנה חסומה: הרעבה"))

VIDEO = Video("Y01", "sync", "מצבי תחרות וקטע קריטי", [title, race, cs, cond, words, exam, recap],
              bank={"2026A-5": None})
