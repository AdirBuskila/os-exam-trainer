# -*- coding: utf-8 -*-
"""P04 · טבלאות דפים רב-שלביות — video script (build: tools/video/vid.py P04).

Source: src/courses/paging.py level 4 (lesson + goal: the page number is split into several indexes, one per level;
only the used parts of the tree are kept; each level costs one more memory access on a TLB miss).
Exam anchor: 2022A-7 (the mechanism that cuts the slowness of reading one page table per level: the TLB), a free
memory item that no guided quiz cites.
Avoided on purpose: the P04 quiz numbers and items (3 levels -> 4 accesses = 2024B-7, 4 levels -> 5, 1024-byte
frames with 4 levels of 128 entries = 2017SA-8, 4 KB / 4-byte entries -> 1024, two levels of 1024 with 4 KB pages
-> 2^32) and the lesson's 10|10|12 split. The access count is shown only for the two-level walk (2 + 1 = 3,
which is also in the L5 lesson); the three-level machine below is used only to count levels.
Here: a toy machine with 20-bit addresses, 256-byte pages and 4-byte entries (6|6|8); the address 58824; the
memory saving for a process that uses three outer entries; and a 39-bit machine with 4 KB pages and 8-byte
entries (9|9|9|12) for the level count. Every number is asserted below.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_paging as w

# ---------------------------------------------------------------- numbers (verified)
VB, PS, ENT = 20, 256, 4                       # toy machine
K = w.log2(PS)
PER = PS // ENT                                # entries in one page-table page
IB = w.log2(PER)
assert (K, PER, IB) == (8, 64, 6) and VB - K == 2 * IB  # two levels of 6 bits each

VA = 58824
S1, F1 = w.strip("sa", VA, [(IB, "outer", "outer"), (IB, "inner", "inner"), (K, "offset", "off")])
assert F1 == [3, 37, 200] and VA == (3 << 14) | (37 << 8) | 200

OUTER = {0: 5, 3: 12, 63: 8}                   # outer index -> frame that holds that inner table
INNER3 = {36: 4, 37: 21, 38: None}             # the inner table in frame 12: inner index -> data frame
FR = INNER3[F1[1]]
PA = FR * PS + F1[2]
# the same translation through sims, with the two levels flattened into one page number
flat = {(o << IB) | i: f for o in OUTER for i, f in (INNER3.items() if o == 3 else [])}
assert w.translate(VA, PS, flat) == PA == 5576 and FR == 21
ACCESSES = 2 + 1                               # outer entry, inner entry, the data
assert ACCESSES == 3

SINGLE = 2 ** (VB - K) * ENT                   # one-level table: one entry per page
TREE = (1 + len(OUTER)) * PS                   # the outer table + one inner table per used outer entry
assert (SINGLE, TREE) == (16384, 1024) and SINGLE // TREE == 16

XB, XPS, XENT = 39, 4096, 8                    # 39-bit machine
XK, XPER = w.log2(XPS), XPS // XENT
XIB = w.log2(XPER)
LEVELS = -(-(XB - XK) // XIB)
assert (XK, XPER, XIB, XB - XK, LEVELS) == (12, 512, 9, 27, 3)
assert XPER ** LEVELS * XPS == 2 ** XB
ONE_LEVEL = 2 ** (XB - XK) * XENT
assert ONE_LEVEL == 2 ** 30                    # 1 GB of table for one process

Q = BANK["2022A-7"]
assert Q["answer_he"].startswith("TLB") and Q["section"] == "memory"

# walk figure
OUT_ROWS = [(0, "5"), (1, "—"), (2, "—"), (3, "12"), (63, "8")]
IN_ROWS = [(36, "4"), (37, "21"), (38, "—"), (63, "—")]
WALK = w.chain(
    w.box("k-ptbr", "PTBR", hidden=False, cls="ok"),
    w.arrow("k-a1"),
    w.mini_table("k-o", "outer", OUT_ROWS, 3),
    w.arrow("k-a2", label="frame 12"),
    w.mini_table("k-i", "inner", IN_ROWS, 37, kind="inner"),
    w.arrow("k-a3"),
    w.box("k-f", "frame 21", cls="fr"))

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("עד עכשיו לכל תהליך הייתה טבלת דפים אחת, עם שורה לכל דף."),
    P("בסרטון הזה נראה למה זה לא עובד במרחב כתובות גדול, ואיך טבלה רב-שלבית פותרת את זה. ומה המחיר.",
      hold=0.4),
], stage='<div class="kicker">P04 · דפדוף ותרגום כתובות</div><h1>טבלאות דפים רב-שלביות</h1>'
         '<p>מספר הדף מתפצל לכמה אינדקסים, שלב אחד לכל אינדקס. חוסכים זיכרון, ומשלמים בגישות.</p>', layout="title")

why = Scene("why", "הבעיה", [
    P("ניקח מחשב עם כתובות של 39 ביטים, דפים של 4KB, וכניסה בטבלה של שמונה בתים.",
      say="ניקח מחשב עם כתובות של שלושים ותשעה ביטים, דפים של ארבעה קילובייט, וכניסה בטבלה של שמונה בתים."),
    P("ה-offset תופס שנים עשר ביטים, ולכן מספר הדף הוא עשרים ושבעה ביטים.", do=show("y-1")),
    P("טבלה חד-שלבית צריכה שורה לכל דף: $2^{27}$ שורות, כל אחת שמונה בתים.", do=show("y-2"),
      say="טבלה חד שלבית צריכה שורה לכל דף: שתיים בחזקת עשרים ושבע שורות, כל אחת שמונה בתים."),
    P("זה $2^{30}$ בתים, גיגהבייט שלם, לכל תהליך!", do=show("y-3"),
      say="זה שתיים בחזקת שלושים בתים, גיגהבייט שלם, לכל תהליך!"),
    P("והרוב המוחלט של השורות ריק, כי תהליך רגיל משתמש בחלק זעיר מהמרחב.", do=show("y-c1")),
    P("הפתרון: לא לשמור שורות לאזורים שלא בשימוש. בשביל זה מפצלים את הטבלה לשלבים.", do=show("y-c2"), hold=0.4),
], stage=w.stack(w.big("y-1", r"39 - 12 = 27\ \text{page bits}", cls="sm"),
                 w.big("y-2", r"2^{27}\ \text{entries} \times 8\ \text{bytes}", cls="sm"),
                 w.big("y-3", r"= 2^{30}\ \text{bytes} = 1\,\text{GB}", cls="sm"), gap=40),
   panel=st.card("y-c1", "trap", "⚠️ טבלה ענקית, כמעט כולה ריקה")
         + st.card("y-c2", "rule", "🔑 שומרים טבלאות רק לאזורים שבשימוש"))

split = Scene("split", "מפצלים את מספר הדף", [
    P("נעבור למחשב קטן, כדי שנוכל לראות הכול: כתובת של עשרים ביטים, ודפים של 256 בתים.",
      do=show("s-a", "s-c0"), say="נעבור למחשב קטן, כדי שנוכל לראות הכול: כתובת של עשרים ביטים, ודפים של מאתיים חמישים ושישה בתים."),
    P("ה-offset: שמונה ביטים. נשארים שנים עשר ביטים למספר הדף.", do=show("sa-t2", "sa-l2")),
    P("נניח, כמו שמקובל, שכל טבלה בעץ תופסת בדיוק דף אחד. כניסה היא ארבעה בתים, ולכן בדף יש שישים וארבע כניסות.", do=show("s-c1")),
    P("שישים וארבע זה שתיים בחזקת שש, ולכן כל אינדקס הוא שישה ביטים.", do=show("s-c2")),
    P("מספר הדף מתפצל לשניים: ששת הביטים השמאליים הם האינדקס בטבלה החיצונית, outer.",
      do=show("sa-t0", "sa-l0")),
    P("ששת הביטים הבאים הם האינדקס בטבלה הפנימית, inner.", do=show("sa-t1", "sa-l1"),
      say="ששת הביטים הבאים הם האינדקס בטבלה הפנימית, אִינֶר."),
    P("הכתובת שלנו היא 58824. החלקים שלה: שלוש, שלושים ושבע, ומאתיים.", do=show("sa-v0", "sa-v1", "sa-v2"),
      say="הכתובת שלנו היא חמישים ושמונה אלף שמונה מאות עשרים וארבע. החלקים שלה: שלוש, שלושים ושבע, ומאתיים."),
], stage=w.stack(f'<div id="s-a" class="h">{S1}</div>', gap=20),
   panel=st.card("s-c0", "plain", "20 ביט, דף " + w.ltr("256") + " בתים, כניסה 4 בתים")
         + st.card("s-c1", "ex", w.ltr("256 / 4 = 64") + " כניסות בטבלה")
         + st.card("s-c2", "rule", "🔑 $64 = 2^{6}$ ← כל אינדקס 6 ביטים"))

walk = Scene("walk", "ההליכה בעץ", [
    P("עכשיו נלך בעץ. ה-PTBR מצביע על הטבלה החיצונית של התהליך.", do=show("k-a1", "k-o")),
    P("גישה ראשונה לזיכרון: כניסה שלוש בטבלה החיצונית. היא אומרת שהטבלה הפנימית יושבת במסגרת שתים עשרה.",
      do=show("k-o-hi", "k-a2", "w-1")),
    P("גישה שנייה: כניסה שלושים ושבע בטבלה הפנימית. היא אומרת שהנתון במסגרת עשרים ואחת.",
      do=show("k-i", "k-i-hi", "k-a3", "k-f", "w-2")),
    P("ואז מצמידים את ה-offset, כמו תמיד: עשרים ואחת כפול 256, ועוד מאתיים. יוצא 5576.", do=show("w-3"),
      say="ואז מצמידים את האוֹפְסֶט, כמו תמיד: עשרים ואחת כפול מאתיים חמישים ושש, ועוד מאתיים. יוצא חמשת אלפים חמש מאות שבעים ושש."),
    P("גישה שלישית: הנתון עצמו.", do=show("w-4")),
    P("כלומר, אם ה-TLB לא עוזר, תרגום בשני שלבים עולה שלוש גישות לזיכרון: אחת לכל שלב, ועוד הנתון.",
      do=show("w-c1")),
    P("זה המחיר של הטבלה הרב-שלבית: כל שלב מוסיף גישה.", hold=0.4),
], stage=w.stack(WALK, w.row("w-1", "גישה 1: outer[3] ← הטבלה הפנימית במסגרת 12", cls="sm"),
                 w.row("w-2", "גישה 2: inner[37] ← מסגרת 21", cls="sm"),
                 w.big("w-3", r"21 \cdot 256 + 200 = 5576", cls="xs"),
                 w.row("w-4", "גישה 3: הנתון בכתובת " + w.mono("5576"), cls="sm"), gap=16),
   panel=st.card("w-c0", "plain", "outer = 3, inner = 37, offset = 200")
         + st.card("w-c1", "rule", "🔑 בלי TLB: שלבים + 1 גישות<br>כאן: " + w.ltr("2 + 1 = 3")))
walk.phrases[0].do += show("w-c0")

save = Scene("save", "מה חסכנו", [
    P("נניח שהתהליך משתמש רק בשלושה אזורים: שלוש כניסות תקפות בטבלה החיצונית.",
      do=show("v-1")),
    P("הוא צריך את הטבלה החיצונית, ועוד שלוש טבלאות פנימיות. ארבע טבלאות של 256 בתים: קילובייט אחד.", do=show("v-2"),
      say="הוא צריך את הטבלה החיצונית, ועוד שלוש טבלאות פנימיות. ארבע טבלאות של מאתיים חמישים ושישה בתים: קילובייט אחד."),
    P("טבלה חד-שלבית הייתה צריכה כניסה לכל אחד מ-4096 הדפים: שישה עשר קילובייט.", do=show("v-3"),
      say="טבלה חד שלבית הייתה צריכה כניסה לכל אחד מארבעת אלפים תשעים ושישה הדפים: שישה עשר קילובייט."),
    P("פי שישה עשר פחות זיכרון. כשהכניסה בטבלה החיצונית לא תקפה, הטבלה הפנימית שלה בכלל לא קיימת.", do=show("v-c1"),
      hold=0.4),
], stage=w.stack(w.row("v-1", "3 כניסות תקפות ב-outer", cls="sm"),
                 w.big("v-2", r"(1 + 3) \cdot 256 = 1024\ \text{bytes}", cls="sm"),
                 w.big("v-3", r"2^{12} \cdot 4 = 16384\ \text{bytes}", cls="sm"), gap=40),
   panel=st.card("v-c1", "rule", "🔑 כניסה לא תקפה ב-outer: אין טבלה פנימית"))

levels = Scene("levels", "כמה שלבים", [
    P("ובחזרה למחשב של 39 הביטים: כמה שלבים הוא צריך?", say="ובחזרה למחשב של שלושים ותשעה הביטים: כמה שלבים הוא צריך?"),
    P("טבלה תופסת דף, כלומר ארבעה קילובייט, וכל כניסה היא שמונה בתים. אז בטבלה יש חמש מאות ושתים עשרה כניסות.",
      do=show("l-1")),
    P("חמש מאות ושתים עשרה זה שתיים בחזקת תשע, ולכן כל שלב מכסה תשעה ביטים.", do=show("l-2")),
    P("מספר הדף הוא עשרים ושבעה ביטים, ועשרים ושבע חלקי תשע זה שלוש. כלומר שלושה שלבים.", do=show("l-3", "lx-t0", "lx-t1", "lx-t2", "lx-l0", "lx-l1", "lx-l2")),
    P("ובדיקה: שלוש פעמים תשעה ביטים, ועוד שנים עשר של offset, נותנים בדיוק שלושים ותשעה ביטים.",
      do=show("lx-t3", "lx-l3", "l-c1")),
    P("ואם החלוקה לא יוצאת שלמה, מעגלים כלפי מעלה: גם כמה ביטים עודפים צריכים שלב משלהם.", do=show("l-c2"),
      hold=0.4),
], stage=w.stack(w.big("l-1", r"4096 / 8 = 512 = 2^{9}", cls="sm"),
                 w.big("l-2", r"\text{9 bits per level}", cls="xs"),
                 w.big("l-3", r"27 / 9 = 3\ \text{levels}", cls="sm"),
                 w.strip("lx", 1, [(9, "L1", "outer"), (9, "L2", "inner"), (9, "L3", "page"), (12, "offset", "off")],
                         vals=False, digits=False)[0], gap=26),
   panel=st.card("l-c1", "ex", w.ltr("9 + 9 + 9 + 12 = 39"))
         + st.card("l-c2", "rule", "🔑 שלבים = ביטי הדף חלקי ביטים לשלב, מעוגל למעלה"))

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: דפדוף סובל מאיטיות, כי צריך לגשת לטבלת דפים ב-RAM בכל אחד מהשלבים."),
    P("איך נקרא המנגנון שמצמצם משמעותית את הבעיה?"),
    P("ראינו את הבעיה בעצמנו: בשני שלבים, כל גישה לנתון הפכה לשלוש גישות לזיכרון.", do=show("x-1")),
    P("התשובה: TLB. זה מטמון קטן בתוך המעבד, ששומר תרגומים אחרונים של דף למסגרת.", do=show("x-ans", "x-2")),
    P("כשהתרגום נמצא ב-TLB, מדלגים על כל ההליכה בעץ. נשארת רק הגישה לנתון.", do=show("x-3")),
    P("המלכודת: לענות טבלה רב-שלבית. היא לא מקצרת את הזמן, היא בדיוק הסיבה לגישות הנוספות.", do=show("x-t")),
    P("את ה-TLB נפגוש מקרוב בסרטון הבא.", hold=0.5),
], stage=w.stack(w.row("x-1", "בלי TLB: " + w.ltr("2 + 1 = 3") + " גישות"),
                 w.row("x-2", "TLB: מטמון של תרגומי דף ← מסגרת"),
                 w.row("x-3", "פגיעה ב-TLB: גישה <b>אחת</b>, לנתון"),
                 st.card("x-t", "trap", "⚠️ לא ״רב-שלבית״: היא <b>מוסיפה</b> גישות"), gap=30),
   panel=f'<div class="qstem pg-qsm"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         + w.qans("x-ans", "TLB"))

recap = Scene("recap", "סיכום", [
    P("לסיכום: טבלה רב-שלבית מפצלת את מספר הדף לכמה אינדקסים.", do=show("r-1")),
    P("ביטים לכל שלב: לוג בבסיס שתיים של מספר הכניסות שנכנסות בדף אחד.", do=show("r-2")),
    P("היא חוסכת זיכרון, כי חלקים לא בשימוש לא נשמרים.", do=show("r-3")),
    P("ומחירה: בלי TLB, גישה אחת לכל שלב ועוד הנתון. נתראה ברמה הבאה.", do=show("r-4"), hold=0.6),
], stage=w.stack(w.strip("sr", VA, [(IB, "outer", "outer"), (IB, "inner", "inner"), (K, "offset", "off")],
                         tint_hidden=False)[0], gap=20),
   panel=st.card("r-1", "rule", "🔑 מספר הדף = [ outer | inner ]")
         + st.card("r-2", "rule", "🔑 ביטים לשלב = $\\log_2$ (כניסות בדף)")
         + st.card("r-3", "rule", "🔑 טבלאות רק לאזורים שבשימוש")
         + st.card("r-4", "trap", "⚠️ בלי TLB: שלבים + 1 גישות"))

VIDEO = Video("P04", "paging", "טבלאות דפים רב-שלביות", [title, why, split, walk, save, levels, exam, recap],
              bank={"2022A-7": None})
