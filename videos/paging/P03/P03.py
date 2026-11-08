# -*- coding: utf-8 -*-
"""P03 · דפים שלמים ופיצול פנימי — video script (build: tools/video/vid.py P03).

Source: src/courses/paging.py level 3 (lesson + goal: memory is given in whole pages, so the last page is partly
wasted: internal fragmentation; shared memory comes in whole pages too).
Exam anchor: 2015B-10 (a write through a shared-memory pointer after shmdt, before IPC_RMID: segmentation fault),
a free memory item that no guided quiz cites. The quiz items 2022B-7 (a write into the unused tail of one's own
last page) and 2020B-9 (shared region = multiple of the page size) are neither posed nor answered as questions.
Avoided on purpose: the P03 quiz numbers (10,000 bytes with 4096-byte pages -> 2288; 4095 as the maximum for
4096-byte pages; 6K -> 8K; shmget of one int -> 4096). Their twins 2023B-7 and 2026A-7 (name of the waste) are
not used either. Here: 7000 bytes with 2048- and 512-byte pages, 6145 / 6144 bytes with 2048-byte pages, and a
5000-byte shared segment with 4096-byte pages.
Every count comes from w_paging.alloc (ceil division, asserted against the page bounds).
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_paging as w

# ---------------------------------------------------------------- numbers (verified)
B1, (N1, T1, W1) = w.alloc_bar("b1", 7000, 2048)
assert (N1, T1, W1) == (4, 8192, 1192) and 3 * 2048 == 6144 < 7000
B2, (N2, T2, W2) = w.alloc_bar("b2", 7000, 512)
assert (N2, T2, W2) == (14, 7168, 168) and 13 * 512 == 6656 < 7000
B3, (N3, T3, W3) = w.alloc_bar("b3", 6145, 2048)
assert (N3, T3, W3) == (4, 8192, 2047) == (4, 8192, 2048 - 1)
assert w.alloc(6144, 2048) == (3, 6144, 0)
# the worst case over every request size: one byte into the last page
assert max(w.alloc(s, 2048)[2] for s in range(1, 3 * 2048 + 1)) == 2047
SH = w.alloc(5000, 4096)
assert SH == (2, 8192, 3192)

Q = BANK["2015B-10"]
assert Q["answer_he"] == "SEGMENTATION FAULT" and Q["section"] == "memory"

# two processes share frame 9: A maps it at its page 4, B at its page 1
TA = {3: 2, 4: 9, 5: 7}
TB = {0: 4, 1: 9, 2: 11}
assert TA[4] == TB[1] == 9
TA_AFTER = {3: 2, 4: None, 5: 7}                               # after shmdt in A: the entry is gone

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("מערכת ההפעלה נותנת זיכרון רק בדפים שלמים. בסרטון הזה נראה כמה זה עולה."),
    P("נחשב את הבזבוז שנקרא פיצול פנימי, נדבר על זיכרון משותף, ונפתור שאלה ממבחן עם segmentation fault.",
      say="נחשב את הבזבוז שנקרא פיצול פנימי, נדבר על זיכרון משותף, ונפתור שאלה ממבחן עם סֶגְמֶנְטֵיישֶׁן פוֹלְט.",
      hold=0.4),
], stage='<div class="kicker">P03 · דפדוף ותרגום כתובות</div><h1>דפים שלמים ופיצול פנימי</h1>'
         '<p>הזיכרון ניתן בדפים שלמים, לכן הדף האחרון מבוזבז חלקית. וגם: למה זיכרון משותף הוא תמיד כפולה של דף.</p>',
   layout="title")

idea = Scene("idea", "בדפים שלמים", [
    P("טבלת הדפים ממפה דפים שלמים. אי אפשר למפות חצי דף."),
    P("לכן תהליך שמבקש זיכרון מקבל מספר שלם של דפים: מעגלים את הבקשה **כלפי מעלה**.", do=show("i-1")),
    P("החלק של הדף האחרון שלא נדרש פשוט לא מנוצל.", do=show("i-2")),
    P("הבזבוז הזה נמצא **בתוך** הזיכרון שהוקצה לתהליך, ולכן קוראים לו פיצול פנימי, internal fragmentation.",
      do=show("i-c1"), say="הבזבוז הזה נמצא בתוך הזיכרון שהוקצה לתהליך, ולכן קוראים לו פיצול פנימי, אִינְטֶרְנָל פְרָגְמֶנְטֵיישֶׁן."),
    P("ואין בדפדוף פיצול חיצוני: כל מסגרת פנויה מתאימה לכל דף, ולכן אין חורים שאי אפשר לנצל.", do=show("i-c2"),
      hold=0.4),
], stage=w.stack(w.big("i-1", r"\text{pages} = \left\lceil \frac{\text{size}}{\text{page size}} \right\rceil"),
                 w.big("i-2", r"\text{waste} = \text{pages} \cdot \text{page size} - \text{size}", cls="sm"), gap=50),
   panel=st.card("i-c1", "rule", "🔑 בזבוז בתוך ההקצאה = <b>פיצול פנימי</b>")
         + st.card("i-c2", "ex", "בדפדוף אין פיצול <b>חיצוני</b>: כל מסגרת מתאימה לכל דף"))

ex1 = Scene("ex1", "כמה מבוזבז", [
    P("דוגמה: תהליך צריך 7000 בתים, והדפים בגודל 2048.", do=show("e-a"),
      say="דוגמה: תהליך צריך שבעת אלפים בתים, והדפים בגודל אלפיים ארבעים ושמונה."),
    P("שלושה דפים הם 6144 בתים. זה לא מספיק.", do=show("b1-p0", "b1-p1", "b1-p2", "e-1"),
      say="שלושה דפים הם שש אלף מאה ארבעים וארבעה בתים. זה לא מספיק."),
    P("לכן צריך דף רביעי, ובסך הכול מקבלים 8192 בתים.", do=show("b1-p3", "b1-u", "b1-sl", "e-2"),
      say="לכן צריך דף רביעי, ובסך הכול מקבלים שמונת אלפים מאה תשעים ושניים בתים."),
    P("הבזבוז: 8192 פחות 7000, כלומר 1192 בתים בסוף הדף הרביעי.", do=show("b1-w", "b1-wl", "e-3"),
      say="הבזבוז: שמונת אלפים מאה תשעים ושתיים פחות שבעת אלפים, כלומר אלף מאה תשעים ושניים בתים בסוף הדף הרביעי."),
    P("ועם דפים קטנים יותר, של 512 בתים? צריך ארבעה עשר דפים.", do=show("e-b", *[f"b2-p{i}" for i in range(14)], "b2-u", "e-4"),
      say="ועם דפים קטנים יותר, של חמש מאות ושנים עשר בתים? צריך ארבעה עשר דפים."),
    P("הם 7168 בתים, והבזבוז יורד ל-168 בלבד.", do=show("b2-w", "b2-wl", "b2-sl", "e-5"),
      say="הם שבעת אלפים מאה שישים ושמונה בתים, והבזבוז יורד למאה שישים ושמונה בלבד."),
    P("דף קטן מבזבז פחות בסוף. אבל יש יותר דפים, ולכן טבלת הדפים גדלה. זו הפשרה.", do=show("e-c1"), hold=0.4),
], stage=w.stack(w.row("e-a", "דפים של 2048 בתים", cls="sm"), B1,
                 w.row("e-b", "דפים של 512 בתים", cls="sm"), B2, gap=10),
   panel=st.card("e-1", "ex", w.ltr("3 · 2048 = 6144 < 7000"))
         + st.card("e-2", "ex", "4 דפים = " + w.mono("8192"))
         + st.card("e-3", "ex", "בזבוז: " + w.ltr("8192 − 7000 = 1192"))
         + st.card("e-4", "ex", "דף 512: 14 דפים = " + w.mono("7168"))
         + st.card("e-5", "ex", "בזבוז: " + w.ltr("7168 − 7000 = 168"))
         + st.card("e-c1", "rule", "🔑 דף קטן: פחות בזבוז, טבלה גדולה יותר"))

worst = Scene("worst", "המקרה הגרוע", [
    P("מה הבזבוז הכי גדול שיכול להיות בדף אחד?"),
    P("הוא קורה כשהבקשה נכנסת לדף האחרון רק בבית אחד. למשל 6145 בתים, עם דפים של 2048.", do=show(
        "b3-p0", "b3-p1", "b3-p2", "b3-p3", "b3-u", "b3-sl"),
      say="הוא קורה כשהבקשה נכנסת לדף האחרון רק בבית אחד. למשל שש אלף מאה ארבעים וחמישה בתים, עם דפים של אלפיים ארבעים ושמונה."),
    P("הבית הבודד הזה דורש דף שלם, ושאר הדף, 2047 בתים, מבוזבז.", do=show("b3-w", "b3-wl", "w-1"),
      say="הבית הבודד הזה דורש דף שלם, ושאר הדף, אלפיים ארבעים ושבעה בתים, מבוזבז."),
    P("לכן הבזבוז המרבי בדף אחד הוא גודל הדף פחות בית אחד.", do=show("w-c1")),
    P("ולמה לא גודל הדף כולו? כי דף שלא נכנס אליו אף בית לא מוקצה בכלל.", do=show("w-2")),
    P("למשל 6144 בתים הם בדיוק שלושה דפים, והבזבוז הוא אפס.", do=show("w-3"), hold=0.4,
      say="למשל שש אלף מאה ארבעים וארבעה בתים הם בדיוק שלושה דפים, והבזבוז הוא אפס."),
], stage=w.stack(B3, gap=10),
   panel=st.card("w-1", "ex", "6145 בתים: 4 דפים, בזבוז " + w.mono("2047"))
         + st.card("w-c1", "rule", "🔑 בזבוז מרבי = גודל הדף − 1")
         + st.card("w-2", "trap", "⚠️ לא גודל הדף: דף ריק לא מוקצה")
         + st.card("w-3", "ex", "6144 בתים = 3 דפים בדיוק: בזבוז 0"))

shared = Scene("shared", "זיכרון משותף", [
    P("זיכרון משותף עובד דרך אותן טבלאות דפים.", do=show("s-a", "s-b")),
    P("שני תהליכים משתפים מסגרת: אצל תהליך אחד היא דף ארבע, ואצל השני היא דף מספר אחת.", do=show("ta-hi4", "tb-hi1", "s-f")),
    P("שתי הטבלאות מצביעות על אותה מסגרת, מסגרת תשע. מה שאחד כותב, השני רואה."),
    P("ובגלל שמשתפים דרך טבלת הדפים, גודל אזור משותף הוא תמיד כפולה של גודל הדף.", do=show("s-c1")),
    P("מבקשים 5000 בתים משותפים, עם דפים של 4096? מקבלים שני דפים, 8192 בתים.", do=show("s-c2"),
      say="מבקשים חמשת אלפים בתים משותפים, עם דפים של ארבעת אלפים תשעים ושש? מקבלים שני דפים, שמונת אלפים מאה תשעים ושניים בתים.",
      hold=0.4),

], stage=w.stack(f'<div class="pg-chain" style="gap:60px;align-items:flex-start">'
                 f'<div id="s-a" class="h pg-stack" style="gap:8px"><div class="pg-row sm">תהליך A</div>{w.page_table("ta", TA, valid_col=False)}</div>'
                 f'<div id="s-b" class="h pg-stack" style="gap:8px"><div class="pg-row sm">תהליך B</div>{w.page_table("tb", TB, valid_col=False)}</div></div>',
                 w.row("s-f", "שתיהן ← מסגרת " + w.mono("9")), gap=30),
   panel=st.card("s-c1", "rule", "🔑 אזור משותף = כפולה של גודל הדף")
         + st.card("s-c2", "ex", w.mono("5000") + " בתים ← 2 דפים = " + w.mono("8192")))

exam = Scene("exam", "שאלה ממבחן", [
    P("ועכשיו שאלה ממבחן: פִּי הוא מצביע לזיכרון משותף. התהליך עשה עליו shmdt."),
    P("אבל עוד לא מחק את האזור עם IPC_RMID. ואז הוא כותב אפס דרך המצביע. מה התוצאה?"),
    P("נתחיל במה שעושה shmdt: הוא מנתק את האזור המשותף מטבלת הדפים של התהליך.", do=show("x-1")),
    P("הכניסה של הדף הזה בטבלה כבר לא תקפה. אצל התהליך, הכתובת של פִּי לא ממופה יותר.", do=show("tx-hi4", "x-2")),
    P("לכן הגישה נתקעת ב-MMU, ומערכת ההפעלה רואה שהכתובת לא שייכת לתהליך.", do=show("x-3")),
    P("התוצאה: segmentation fault.", do=show("x-ans")),
    P("המלכודת: האזור עצמו עדיין קיים, כי לא קראו ל-IPC_RMID. אז אולי הכתיבה תצליח?", do=show("x-t")),
    P("לא. האזור קיים, אבל הוא לא ממופה אצל **התהליך הזה**.", hold=0.3),
    P("וזה הכלל: מה שקובע הוא אם הדף ממופה בטבלה של התהליך.", hold=0.5),
], stage=w.stack(st.card("x-1", "ex", "shmdt: מנתק את האזור מטבלת הדפים"),
                 f'<div class="pg-stack" style="gap:8px">{w.page_table("tx", TA_AFTER, head=("דף", "מסגרת", "valid"))}</div>',
                 st.card("x-2", "ex", "הדף של " + w.ltr("p") + ": valid = 0"),
                 st.card("x-3", "rule", "🔑 כתובת לא ממופה בתהליך ← שגיאה"),
                 st.card("x-t", "trap", "⚠️ האזור קיים, אבל לא ממופה <b>אצל התהליך</b>"), gap=16),
   panel=f'<div class="qstem pg-qsm"><span class="qid">{Q["id"]}</span>נניח כי ' + w.ltr("p") + ' הוא מצביע לזיכרון משותף, '
         'ותהליך ביצע ' + w.mono("*p=0") + ' לאחר שביצע עליו ' + w.mono("shmdt") + ', אבל עדיין לא בוצע</div>'
         + f'<pre class="qcode">shmctl(shmid, IPC_RMID, 0)</pre>'
         + '<div class="qstem pg-qsm">תוצאת הפנייה תהיה ______.</div>'
         + w.qans("x-ans", w.ltr("SEGMENTATION FAULT")))

recap = Scene("recap", "סיכום", [
    P("לסיכום: מספר הדפים הוא הבקשה חלקי גודל הדף, מעוגל כלפי מעלה.", do=show("r-1")),
    P("מה שנשאר בדף האחרון הוא פיצול פנימי, ולכל היותר גודל הדף פחות בית אחד.", do=show("r-2")),
    P("זיכרון משותף מגיע בדפים שלמים, וממופה דרך טבלת הדפים.", do=show("r-3")),
    P("ובלי מיפוי בטבלה, גישה גורמת ל-segmentation fault. נתראה ברמה הבאה.", do=show("r-4"), hold=0.6,
      say="ובלי מיפוי בטבלה, גישה גורמת לסֶגְמֶנְטֵיישֶׁן פוֹלְט. נתראה ברמה הבאה."),
], stage=w.stack(w.big("r-f", r"\text{pages} = \left\lceil \frac{\text{size}}{\text{page size}} \right\rceil", hidden=False), gap=20),
   panel=st.card("r-1", "rule", "🔑 דפים = עיגול כלפי מעלה")
         + st.card("r-2", "rule", "🔑 פיצול פנימי: לכל היותר גודל הדף − 1")
         + st.card("r-3", "rule", "🔑 זיכרון משותף: כפולה של דף")
         + st.card("r-4", "trap", "⚠️ לא ממופה ← segmentation fault"))

VIDEO = Video("P03", "paging", "דפים שלמים ופיצול פנימי", [title, idea, ex1, worst, shared, exam, recap],
              bank={"2015B-10": None})
