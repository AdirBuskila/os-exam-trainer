# -*- coding: utf-8 -*-
"""P01 · דפים, מסגרות ופיצול הכתובת — video script (build: tools/video/vid.py P01).

Source: src/courses/paging.py level 1 (lesson + goal: cut an address into page number and offset; count pages and
frames with powers of two).
Exam part: an original question "בסגנון מבחן" (bank={}). The only free counting item of the bank, 2015B-6 (32-bit
address, 4KB pages, how many frames), is not used: its numbers are those of the level-1 quiz question "32 bits,
4 KB, page-number bits" (and the L4 lesson's 2^20). 2024A-7 (42 bits, 1 MB) is a quiz/boss item.
Avoided on purpose: every number of the P01 quiz (4 KB -> 12, 32 bits / 4 KB, 36 bits / 4 KB -> 2^24, 42 bits /
1 MB -> 2^22, 13000 with 4096-byte pages). Here: page sizes 1/2/8/16 KB, a 24-bit space with 2 KB pages and 20
physical bits, the address 11000 with 1 KB pages (16 bits), and the exam-style 40/30 bits with 8 KB pages.
Every split is computed with sims.split_address (through w_paging.split, which also checks the bit cut).
"""
from vid import P, Scene, Video, show, hide
import stage as st
import w_paging as w

# ---------------------------------------------------------------- numbers (verified)
SIZES = [(1024, "1KB"), (2048, "2KB"), (8192, "8KB"), (16384, "16KB")]
assert [w.log2(s) for s, _ in SIZES] == [10, 11, 13, 14]

V1, PS1, PH1 = 24, 2048, 20                     # counting example
K1 = w.log2(PS1)
assert (K1, V1 - K1, PH1 - K1) == (11, 13, 9)
assert 2 ** V1 // PS1 == 2 ** 13 and 2 ** PH1 // PS1 == 2 ** 9

A2, PS2, N2 = 11000, 1024, 16                    # split example
PG2, OF2 = w.split(A2, PS2)
assert (PG2, OF2) == (10, 760) and PG2 * PS2 == 10240 and A2 - 10240 == 760
S2, VALS2 = w.strip("sa", A2, [(N2 - 10, "דף", "page"), (10, "offset", "off")])
assert VALS2 == [PG2, OF2]
SR = w.strip("sr", A2, [(N2 - 10, "דף", "page"), (10, "offset", "off")], tint_hidden=False)[0].replace("pg-val h", "pg-val")

VX, PX, SX = 40, 30, 8192                        # exam-style
KX = w.log2(SX)
assert (KX, VX - KX, PX - KX) == (13, 27, 17)

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נלמד לחתוך כתובת וירטואלית לשני חלקים: מספר הדף, וה-offset בתוך הדף."),
    P("נראה איך סופרים ביטים, דפים ומסגרות, בעזרת חזקות של שתיים."),
    P("ובסוף נפתור שאלה בסגנון מבחן.", hold=0.4),
], stage='<div class="kicker">P01 · דפדוף ותרגום כתובות</div><h1>דפים, מסגרות ופיצול הכתובת</h1>'
         '<p>לחתוך כתובת למספר דף והיסט (offset), ולספור דפים ומסגרות לפי מספר הביטים.</p>', layout="title")

PAGES = "".join(f'<span class="pg-boxh">{i}</span>' for i in range(6))
FRAMES = "".join(f'<span class="pg-boxh fr">{i}</span>' for i in range(8))
idea = Scene("idea", "דפים ומסגרות", [
    P("כל תהליך רואה זיכרון משלו, רציף, שמתחיל בכתובת אפס. זה הזיכרון הווירטואלי."),
    P("מערכת ההפעלה חותכת אותו לבלוקים שווים, שנקראים **דפים**, ובאנגלית pages.", do=show("i-v")),
    P("גם הזיכרון הפיזי, ה-RAM, נחתך לבלוקים באותו גודל בדיוק. הם נקראים **מסגרות**, ובאנגלית frames.",
      do=show("i-p")),
    P("הגדלים שווים, ולכן כל דף יכול לשבת בכל מסגרת.", do=show("i-c1")),
    P("ולכן כתובת וירטואלית מורכבת משני חלקים: באיזה דף מדובר, ואיפה בתוך הדף.", do=show("i-f")),
    P("החלק השני נקרא offset, או בעברית היסט: המרחק מתחילת הדף, בבתים.", do=show("i-c2"), hold=0.4),
], stage=w.stack(f'<div id="i-v" class="h pg-stack" style="gap:10px"><div class="pg-row sm">דפים (וירטואלי)</div>'
                 f'<div class="pg-chain">{PAGES}</div></div>',
                 f'<div id="i-p" class="h pg-stack" style="gap:10px"><div class="pg-row sm">מסגרות (RAM)</div>'
                 f'<div class="pg-chain">{FRAMES}</div></div>',
                 w.big("i-f", r"\text{address} = [\ \text{page} \mid \text{offset}\ ]"), gap=40),
   panel=st.card("i-c1", "rule", "🔑 דף ומסגרת: <b>אותו גודל</b>")
         + st.card("i-c2", "rule", "🔑 offset: המקום בתוך הדף, בבתים"))

count = Scene("count", "סופרים ביטים", [
    P("כמה ביטים צריך ה-offset? מספיק ביטים כדי לציין כל בית בתוך הדף."),
    P("גודל דף הוא תמיד חזקה של שתיים. אם הדף הוא שתיים בחזקת קֵיי בתים, ה-offset תופס קֵיי ביטים.",
      do=show("c-k")),
    P("קילובייט הוא שתיים בחזקת עשר, ולכן דף של קילובייט אחד נותן offset של עשרה ביטים.", do=show("c-t", "c-r0")),
    P("כל הכפלה של הדף מוסיפה ביט אחד: דף של שני קילובייט נותן offset של אחד עשר ביטים.", do=show("c-r1")),
    P("דף של שמונה קילובייט נותן offset של 13 ביטים, ודף של שישה עשר קילובייט נותן 14.", do=show("c-r2", "c-r3"),
      say="דף של שמונה קילובייט נותן אוֹפְסֶט של שלושה עשר ביטים, ודף של שישה עשר קילובייט נותן ארבעה עשר."),
    P("ומה שנשאר מהכתובת, משמאל ל-offset, הוא מספר הדף.", do=show("c-f")),
    P("דוגמה: כתובת וירטואלית של 24 ביטים, ודפים של 2KB. ה-offset: אחד עשר ביטים.", do=show("c-e1"),
      say="דוגמה: כתובת וירטואלית של עשרים וארבעה ביטים, ודפים של שני קילובייט. האוֹפְסֶט: אחד עשר ביטים."),
    P("מספר הדף: עשרים וארבע פחות אחת עשרה, כלומר שלושה עשר ביטים.", do=show("c-e2")),
    P("ולכן יש $2^{13}$ דפים, ובטבלת דפים חד-שלבית יש כניסה אחת לכל דף.", do=show("c-e3"),
      say="ולכן יש שתיים בחזקת שלוש עשרה דפים, ובטבלת דפים חד שלבית יש כניסה אחת לכל דף."),
    P("ואם לכתובת הפיזית יש 20 ביטים, יש $2^{9}$ מסגרות: עשרים פחות אחת עשרה.", do=show("c-e4"),
      say="ואם לכתובת הפיזית יש עשרים ביטים, יש שתיים בחזקת תשע מסגרות: עשרים פחות אחת עשרה."),
    P("שימו לב: דפים סופרים לפי הכתובת **הווירטואלית**. וכשנתונים ביטים פיזיים, מסגרות סופרים לפי הכתובת **הפיזית**.",
      do=show("c-c1"), hold=0.4),
], stage=w.stack(w.big("c-k", r"\text{page} = 2^{k}\ \text{bytes} \;\Rightarrow\; \text{offset} = k\ \text{bits}", cls="sm"),
                 w.table("c-t", ["גודל דף", "בתים", "ביטי offset"],
                         [[w.ltr(lab), w.ltr(f"$2^{{{w.log2(s)}}}$"), str(w.log2(s))] for s, lab in SIZES],
                         ids=[f"c-r{i}" for i in range(4)]),
                 w.big("c-f", r"\text{page bits} = \text{address bits} - \text{offset bits}", cls="xs"), gap=30),
   panel=st.card("c-e1", "ex", "24 ביטים, דף 2KB: offset = 11")
         + st.card("c-e2", "ex", w.ltr("24 − 11 = 13") + " ביטים לדף")
         + st.card("c-e3", "ex", "$2^{13}$ דפים = $2^{13}$ כניסות בטבלה")
         + st.card("c-e4", "ex", "פיזי 20 ביט: $2^{20-11} = 2^{9}$ מסגרות")
         + st.card("c-c1", "rule", "🔑 דפים ← ביטים וירטואליים; נתונים ביטים פיזיים? מסגרות ← ביטים פיזיים"))

SPLIT_TEX = r"11000 = 10 \cdot 1024 + 760"
split = Scene("split", "חותכים כתובת", [
    P("עכשיו נחתוך כתובת אמיתית. כתובת של 16 ביטים, ודפים של 1KB, כלומר offset של עשרה ביטים.", do=show("s-a"),
      say="עכשיו נחתוך כתובת אמיתית. כתובת של שישה עשר ביטים, ודפים של קילובייט אחד, כלומר אוֹפְסֶט של עשרה ביטים."),
    P("הכתובת היא 11000. כך היא נראית בבינארי.", say="הכתובת היא אחת עשרה אלף. כך היא נראית בבינארי."),
    P("עשרת הביטים הימניים הם ה-offset.", do=show("sa-t1", "sa-l1")),
    P("ששת הביטים שנשארו משמאל הם מספר הדף.", do=show("sa-t0", "sa-l0")),
    P("נקרא כל חלק כמספר: הדף הוא 10, וה-offset הוא 760.", do=show("sa-v0", "sa-v1", "s-c1"),
      say="נקרא כל חלק כמספר: הדף הוא עשר, והאוֹפְסֶט הוא שבע מאות שישים."),
    P("ובלי בינארי? מחלקים בגודל הדף. המנה היא מספר הדף, והשארית היא ה-offset.", do=show("s-d")),
    P("עשר פעמים 1024 זה 10240, והשארית עד 11000 היא 760.", do=show("s-c2"),
      say="עשר פעמים אלף עשרים וארבע זה עשרת אלפים מאתיים ארבעים, והשארית עד אחת עשרה אלף היא שבע מאות שישים."),
    P("אותה תשובה בדיוק. כשגודל הדף הוא חזקה של שתיים, חלוקה בו היא פשוט חיתוך הביטים.", do=show("s-c3"), hold=0.4),
    P("וזו המלכודת: ה-offset תמיד קטן מגודל הדף. אם יצא לכם offset של 1024 ומעלה, טעיתם בחלוקה.",
      do=show("s-c4"),
      say="וזו המלכודת: האוֹפְסֶט תמיד קטן מגודל הדף. אם יצא לכם אוֹפְסֶט של אלף עשרים וארבע ומעלה, טעיתם בחלוקה."),
], stage=w.stack(f'<div id="s-a" class="h">{S2}</div>', w.big("s-d", SPLIT_TEX), gap=40),
   panel=st.card("s-c0", "plain", "כתובת " + w.mono("11000") + ", דף " + w.ltr("1KB"))
         + st.card("s-c1", "ex", "דף = <b>10</b>, offset = <b>760</b>")
         + st.card("s-c2", "ex", "מנה = דף, שארית = offset")
         + st.card("s-c3", "rule", "🔑 חלוקה בגודל הדף = חיתוך הביטים")
         + st.card("s-c4", "trap", "⚠️ offset &lt; גודל הדף, תמיד"))
split.phrases[0].do += show("s-c0")

exam = Scene("exam", "שאלה בסגנון מבחן", [
    P("שאלה בסגנון מבחן: כתובת וירטואלית של 40 ביטים, כתובת פיזית של 30 ביטים, ודפים של 8KB.",
      say="שאלה בסגנון מבחן: כתובת וירטואלית של ארבעים ביטים, כתובת פיזית של שלושים ביטים, ודפים של שמונה קילובייט."),
    P("שלושה סעיפים: כמה ביטים ל-offset, כמה כניסות בטבלת דפים חד-שלבית, וכמה מסגרות יש."),
    P("סעיף ראשון: שמונה קילובייט הם שתיים בחזקת שלוש עשרה, ולכן ה-offset תופס שלושה עשר ביטים.", do=show("x-1")),
    P("סעיף שני: כניסה אחת לכל דף. ביטי הדף הם ארבעים פחות שלוש עשרה, עשרים ושבעה.", do=show("x-2")),
    P("ולכן בטבלה יש $2^{27}$ כניסות.", do=show("x-2b"), say="ולכן בטבלה יש שתיים בחזקת עשרים ושבע כניסות."),
    P("סעיף שלישי: המסגרות נמצאות בזיכרון הפיזי, ולכן סופרים לפי שלושים הביטים הפיזיים.", do=show("x-3")),
    P("שלושים פחות שלוש עשרה זה שבע עשרה, כלומר $2^{17}$ מסגרות.", do=show("x-3b", "x-ans"),
      say="שלושים פחות שלוש עשרה זה שבע עשרה, כלומר שתיים בחזקת שבע עשרה מסגרות."),
    P("המלכודת: כאן נתונים ביטים פיזיים, ולכן לא סופרים מסגרות לפי ארבעים הביטים הווירטואליים. זה מספר הדפים.",
      do=show("x-t")),
    P("כאן יש יותר דפים ממסגרות, ולכן לא כל הדפים יכולים לשבת ב-RAM באותו זמן."),
    P("ואם השאלה נותנת רק כתובת וירטואלית, ושואלת על מספר המסגרות המקסימלי או הפוטנציאלי, המבחנים סופרים לפי הביטים שניתנו.",
      do=show("x-g"), hold=0.5),
], stage=w.stack(w.big("x-1", r"8\,\text{KB} = 2^{13} \;\Rightarrow\; \text{offset} = 13", cls="sm"),
                 w.big("x-2", r"40 - 13 = 27\ \text{page bits}", cls="sm"),
                 w.big("x-2b", r"2^{27}\ \text{entries}", cls="sm"),
                 w.big("x-3", r"30 - 13 = 17\ \text{frame bits}", cls="sm"),
                 w.big("x-3b", r"2^{17}\ \text{frames}", cls="sm"),
                 st.card("x-t", "trap", "⚠️ אם נתונים ביטים פיזיים: מסגרות סופרים לפי הכתובת <b>הפיזית</b>"),
                 st.card("x-g", "rule", "🔑 רק כתובת וירטואלית? מסגרות ״פוטנציאליות״ לפי הביטים שניתנו"), gap=18),
   panel='<div class="qstem"><span class="qid">שאלה בסגנון מבחן</span>כתובת וירטואלית של 40 ביט, כתובת פיזית של 30 ביט, '
         'גודל דף ' + w.ltr("8KB") + '.<br>(א) כמה ביטים ל-offset?<br>(ב) כמה כניסות בטבלת דפים חד-שלבית?<br>'
         '(ג) כמה מסגרות יש בזיכרון הפיזי?</div>'
         + w.qans("x-ans", "(א) 13 &nbsp; (ב) $2^{27}$ &nbsp; (ג) $2^{17}$"))

recap = Scene("recap", "סיכום", [
    P("לסיכום: דף ומסגרת באותו גודל, וכתובת היא מספר דף ואחריו offset.", do=show("r-1")),
    P("דף של שתיים בחזקת קֵיי בתים נותן offset של קֵיי ביטים, והשאר הוא מספר הדף.", do=show("r-2")),
    P("פיצול של כתובת עשרונית: המנה היא הדף, והשארית היא ה-offset.", do=show("r-3")),
    P("ודפים סופרים לפי הכתובת הווירטואלית, ומסגרות לפי הפיזית כשהיא נתונה. נתראה ברמה הבאה.", do=show("r-4"), hold=0.6),
], stage=w.stack(SR, gap=20),
   panel=st.card("r-1", "rule", "🔑 כתובת = [ דף | offset ]")
         + st.card("r-2", "rule", "🔑 דף $2^{k}$ בתים ← offset של $k$ ביטים")
         + st.card("r-3", "rule", "🔑 דף = מנה, offset = שארית")
         + st.card("r-4", "trap", "⚠️ נתונים ביטים פיזיים? מסגרות ← ביטים פיזיים"))

VIDEO = Video("P01", "paging", "דפים, מסגרות ופיצול הכתובת", [title, idea, count, split, exam, recap], bank={})
