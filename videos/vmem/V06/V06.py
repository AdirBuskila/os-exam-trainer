# -*- coding: utf-8 -*-
"""V06 · Clock, ביטי התייחסות, הקצאה מקומית ותזזית — video script (build: tools/video/vid.py V06).

Source: src/courses/vmem.py level 6 (lesson + goal: Clock (second chance) approximates LRU with a reference bit per
frame; the MMU sets the bit on an access, the OS clears it while sweeping; a bit 1 gets a second chance, a bit 0 is
the victim; local allocation evicts a page of the faulting process; thrashing; at process exit the frames are just
freed, dirty pages included).
Exam anchor: 2026A-9 (open: dirty pages at process exit), no guided quiz uses it. Its bank note says the official
key is "nothing, freed as usual (not written to disk)"; the video follows the note: write-back on the dirty bit is
for evicting a page of a live process.
Avoided on purpose: the level-6 quiz items (2019A-8, 2019B-5, 2017SB-6, 2021B-10, 2017A-8, 2021A-10) and the boss's
(2024A-8, 2024B-8) are not asked as questions; 2017SA-6 (who sets the dirty bit) is left out as a content twin of
2017SB-6, and 2022B-8 (thrashing, by name) as a twin of 2017A-8 / 2024A-8.
Clock run: frames 7 2 9 4 with bits 1 0 1 1, hand at frame 0, references 5 7 8 (our own); the run comes from
w_vmem.clock() (no Clock simulator in sims.py; it is asserted on a hand-checked case at import) and is asserted here.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_vmem as w

# ---------------------------------------------------------------- numbers (verified)
C = w.clock([5, 7, 8], [7, 2, 9, 4], [1, 0, 1, 1], 0)
ST = C["states"]
assert [s["kind"] for s in ST] == ["start", "clear", "load", "hit", "clear", "clear", "clear", "clear", "load"]
assert C["victims"] == [2, 9] and C["faults"] == 2
assert ST[2]["slots"] == [7, 5, 9, 4] and ST[2]["hand"] == 2 and ST[2]["bits"] == [0, 1, 1, 1]
assert ST[3]["bits"] == [1, 1, 1, 1]                    # the hit on 7 set its bit again; the hand did not move
assert [s["at"] for s in ST[4:8]] == [2, 3, 0, 1]       # second fault: the hand clears all four bits ...
assert ST[8]["at"] == 2 and ST[8]["slots"] == [7, 5, 8, 4] and ST[8]["hand"] == 3   # ... and takes frame 2 again
CLK = w.clock_svg("k", ST, size=560, names=["מסגרת 0", "מסגרת 1", "מסגרת 2", "מסגרת 3"])
# the idea scene draws the start state under its own prefix (an SVG marker id must be unique in the document)
CLK0 = w.clock_svg("ki", ST[:1], size=560, names=["מסגרת 0", "מסגרת 1", "מסגרת 2", "מסגרת 3"], hidden_first=True)

Q = BANK["2026A-9"]
assert Q["section"] == "replacement" and "dirty" in Q["he"] and "ישוחררו" in Q["answer_he"]
assert "TRICK" in Q["note"] and "EVICTING" in Q["note"]

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נכיר את האלגוריתם שמערכות אמיתיות באמת משתמשות בו: Clock."),
    P("נראה מי מדליק ומי מכבה את ביט ההתייחסות, ואחר כך מה זו הקצאה מקומית, ומה זו תזזית."),
    P("ובסוף שאלה ממבחן על דפים מלוכלכים של תהליך שמסתיים.", hold=0.4),
], stage='<div class="kicker">V06 · דפדוף לפי דרישה והחלפת דפים</div>'
         '<h1>Clock, ביטי התייחסות, הקצאה מקומית ותזזית</h1>'
         '<p>האלגוריתם המעשי ומה משתבש: הזדמנות שנייה, מי נוגע בביט, דף של מי מפנים, ומתי המערכת רק מחליפה דפים.</p>',
   layout="title")

idea = Scene("idea", "הרעיון", [
    P("ראינו ש-LRU מדויק יקר מדי: הוא דורש עבודה בכל גישה לזיכרון."),
    P("**Clock** מקרב אותו עם ביט אחד לכל מסגרת: ה-**reference bit**, ביט ההתייחסות.", do=show("i-1")),
    P("בכל גישה לדף, ה-MMU, כלומר החומרה, מדליק את הביט. בלי שום עבודה של מערכת ההפעלה.", do=show("i-2")),
    P("המסגרות מסודרות במעגל, ומחוג מצביע על אחת מהן.", do=show("ki-s-0")),
    P("כשצריך קורבן, מערכת ההפעלה בודקת את המסגרת שתחת המחוג."),
    P("ביט דלוק? הדף שימש לאחרונה. הוא מקבל **הזדמנות שנייה**: מערכת ההפעלה מכבה את הביט, והמחוג מתקדם.", do=show("i-3")),
    P("ביט כבוי? אף אחד לא נגע בדף מאז שהמחוג עבר עליו בפעם הקודמת. הוא הקורבן.", do=show("i-4"), hold=0.3),
], stage=CLK0,
   panel=st.card("i-1", "plain", "Clock = הזדמנות שנייה, ביט אחד לכל מסגרת")
         + st.card("i-2", "rule", "🔑 ה-<b>MMU</b> מדליק את הביט בכל גישה")
         + st.card("i-3", "rule", "🔑 ביט 1: מערכת ההפעלה <b>מכבה</b> וממשיכה")
         + st.card("i-4", "ex", "ביט 0: <b>קורבן</b>"))

run = Scene("run", "דוגמה", [
    P("ארבע מסגרות: הדפים 7, 2, 9 ו-4. הביטים: 1, 0, 1, 1. המחוג על מסגרת 0.",
      say="ארבע מסגרות: הדפים שבע, שתיים, תשע וארבע. הביטים: אחת, אפס, אחת, אחת. המחוג על מסגרת אפס."),
    P("מגיעה הפניה לדף 5. הוא לא בזיכרון: page fault, וצריך קורבן.", say="מגיעה הפניה לדף חמש. הוא לא בזיכרון: פֵּייג' פוֹלְט, וצריך קורבן."),
    P("תחת המחוג: דף 7, והביט של 7 דלוק. הזדמנות שנייה: מכבים את הביט, וזזים.", do=w.clock_step("k", 1) + show("c-1"),
      say="תחת המחוג: דף שבע, והביט של שבע דלוק. הזדמנות שנייה: מכבים את הביט, וזזים."),
    P("דף 2: הביט כבוי. הוא הקורבן. דף 5 נכנס למסגרת שלו.", do=w.clock_step("k", 2),
      say="דף שתיים: הביט כבוי. הוא הקורבן. דף חמש נכנס למסגרת שלו."),
    P("הביט של 5 דלוק, כי ההוראה רצה מחדש וניגשת אליו. והמחוג עובר למסגרת הבאה.",
      say="הביט של חמש דלוק, כי ההוראה רצה מחדש וניגשת אליו. והמחוג עובר למסגרת הבאה."),
    P("עכשיו גישה לדף 7: הוא בזיכרון. פגיעה, וה-MMU מדליק שוב את הביט של 7. המחוג לא זז.",
      do=w.clock_step("k", 3) + show("c-2"),
      say="עכשיו גישה לדף שבע: הוא בזיכרון. פגיעה, והאֶם אֶם יוּ מדליק שוב את הביט של שבע. המחוג לא זז."),
    P("ועכשיו דף 8: עוד page fault. ותראו מה קורה כשכל הביטים דלוקים.",
      say="ועכשיו דף שמונה: עוד פֵּייג' פוֹלְט. ותראו מה קורה כשכל הביטים דלוקים."),
    P("9: מכבים וזזים. 4: מכבים וזזים.", do=w.clock_step("k", 4) + w.clock_step("k", 5),
      say="תשע: מכבים וזזים. ארבע: מכבים וזזים."),
    P("7, שקיבל רגע קודם ביט חדש: מכבים וזזים. 5: מכבים וזזים.", do=w.clock_step("k", 6) + w.clock_step("k", 7),
      say="שבע, שקיבל רגע קודם ביט חדש: מכבים וזזים. חמש: מכבים וזזים."),
    P("המחוג השלים סיבוב שלם וחזר לדף 9. עכשיו הביט של 9 כבוי, אז 9 הוא הקורבן.", do=w.clock_step("k", 8) + show("c-3"),
      say="המחוג השלים סיבוב שלם וחזר לדף תשע. עכשיו הביט של תשע כבוי, אז תשע הוא הקורבן."),
    P("זה המקרה הגרוע: כשכל הביטים דלוקים, המחוג עובר על כל המסגרות לפני שהוא מוצא קורבן.", do=show("c-4")),
    P("ואז הביטים לא עזרו בכלל: הקורבן הוא פשוט הדף שהמחוג התחיל ממנו.", hold=0.4),
], stage=CLK,
   panel=st.card("c-1", "rule", "🔑 ביט 1 ← מכבים, זזים (הזדמנות שנייה)")
         + st.card("c-2", "ex", "פגיעה: ה-MMU מדליק, המחוג לא זז")
         + st.card("c-3", "plain", "כל הביטים 1: סיבוב שלם, ואז הקורבן")
         + st.card("c-4", "trap", "⚠️ המקרה הגרוע: המחוג עובר על <b>כל</b> המסגרות"))

alloc = Scene("alloc", "הקצאה ותזזית", [
    P("נושא נוסף: הקצאת מסגרות. נניח שתהליך A צריך מסגרת, וכל המסגרות תפוסות.", do=show("a-1"),
      say="נושא נוסף: הקצאת מסגרות. נניח שתהליך אֵיי צריך מסגרת, וכל המסגרות תפוסות."),
    P("בהקצאה **גלובלית**, הקורבן יכול להיות דף של כל תהליך במערכת.", do=show("a-2")),
    P("בהקצאה **מקומית**, לכל תהליך יש מכסה של מסגרות, והוא מפנה רק דפים **משלו**.", do=show("a-3")),
    P("ועכשיו הבעיה הגדולה: **thrashing**, תזזית. היא קורית כשהתהליכים צריכים יותר מסגרות ממה שיש.", do=show("a-4", "a-7")),
    P("בהקצאה גלובלית, כל תהליך מפנה דפים של אחרים. וכשמגיע תורו, הוא מגלה שהדפים של התהליך פונו מה-RAM.", do=show("a-5")),
    P("כולם מחכים לדיסק, והמעבד כמעט לא עובד: המערכת מבלה את רוב הזמן בהעברת דפים, במקום בריצה.", do=show("a-6")),
    P("הפתרון המקובל: להוריד את מספר התהליכים שרצים יחד.", do=show("a-8"), hold=0.4),
], stage=w.stack(st.card("a-1", "plain", "תהליך A צריך מסגרת, והכול תפוס"),
                 st.card("a-2", "ex", "גלובלית: דף של <b>כל</b> תהליך"),
                 st.card("a-3", "rule", "🔑 מקומית: רק דף של A עצמו"), gap=20),
   panel=st.card("a-4", "plain", "ביקוש למסגרות &gt; המסגרות שקיימות")
         + st.card("a-5", "plain", "בהקצאה גלובלית, כל תהליך מפנה דפים של אחרים")
         + st.card("a-6", "plain", "כולם מחכים לדיסק, המעבד מובטל")
         + st.card("a-7", "trap", "⚠️ <b>thrashing</b>: רוב הזמן על החלפת דפים")
         + st.card("a-8", "rule", "🔑 הפתרון: פחות תהליכים במקביל"))

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: תהליך הסתיים, ולחלק מהדפים שלו ה-dirty bit דלוק. מה יקרה לדפים האלה?"),
    P("האינסטינקט אומר: dirty, אז כותבים לדיסק. אבל למה בכלל כותבים דף מלוכלך?", do=show("x-1")),
    P("כותבים אותו כשמפנים דף של תהליך **חי**: הוא עוד יצטרך את הנתונים, ולכן הם חייבים להישמר.", do=show("x-2")),
    P("תהליך שהסתיים לא יקרא את הדפים האלה אף פעם. אין מה לשמור.", do=show("x-3")),
    P("לכן המסגרות פשוט משוחררות כרגיל, והתוכן לא נכתב לדיסק.", do=show("x-4")),
    P("וזו גם התשובה הרשמית: כלום. הדפים ישוחררו כרגיל, בלי כתיבה לדיסק.", do=show("x-a")),
    P("המלכודת: ה-dirty bit מחייב כתיבה רק ב**פינוי** דף מתהליך שעדיין רץ, לא בסיום.", do=show("x-t"), hold=0.5),
], stage=w.stack(w.row("x-1", "dirty ← כותבים לדיסק? רק כש..."),
                 st.card("x-2", "rule", "🔑 פינוי דף של תהליך <b>חי</b> ← כותבים, כי הוא עוד יצטרך אותו"),
                 st.card("x-3", "ex", "תהליך שהסתיים לא יקרא את הדפים יותר"),
                 w.row("x-4", "← המסגרות משוחררות, בלי כתיבה", cls="big"),
                 st.card("x-t", "trap", "⚠️ dirty בסיום תהליך: לא כותבים"), gap=20),
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         + w.qans("x-a", f'<span class="k">תשובה:</span> {Q["answer_he"]}'))

recap = Scene("recap", "סיכום", [
    P("לסיכום: Clock מקרב את LRU עם ביט אחד. ה-MMU מדליק אותו, ומערכת ההפעלה מכבה אותו בסריקה.", do=show("r-1")),
    P("ביט דלוק: הזדמנות שנייה. ביט כבוי: קורבן. ואם כולם דלוקים, המחוג עובר על כל המסגרות.", do=show("r-2")),
    P("הקצאה מקומית מפנה רק דפים של התהליך עצמו. ותזזית: מחסור במסגרות שגורם להחלפות דפים כל הזמן.", do=show("r-3")),
    P("וברמה הבאה, שלב הבוס: שאלות ממבחנים קודמים וסימולציה מלאה. בהצלחה.", do=show("r-4"), hold=0.6),
], stage=w.stack(w.row("r-0", "MMU מדליק · מערכת ההפעלה מכבה", hidden=False, cls="big")),
   panel=st.card("r-1", "rule", "🔑 Clock: ביט 1 ← הזדמנות שנייה")
         + st.card("r-2", "rule", "🔑 ביט 0 ← קורבן")
         + st.card("r-3", "trap", "⚠️ מקומית: רק דפים של התהליך; תזזית: מחסור במסגרות")
         + st.card("r-4", "ex", "הבא: שלב הבוס"))

VIDEO = Video("V06", "vmem", "Clock, ביטי התייחסות, הקצאה מקומית ותזזית", [title, idea, run, alloc, exam, recap],
              bank={"2026A-9": None})
