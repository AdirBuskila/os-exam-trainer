# -*- coding: utf-8 -*-
"""P02 · תרגום כתובת בעזרת טבלת דפים — video script (build: tools/video/vid.py P02).

Source: src/courses/paging.py level 2 (lesson + goal: page number -> frame number through the page table, the
offset copied unchanged; an invalid entry raises a page fault).
Exam anchor: 2015A-6 (the name of the table that maps a virtual page number to a physical frame: Page Table), a
free memory item that no guided quiz cites.
Avoided on purpose: the P02 quiz table {0:5, 1:2, 2:7, 3:invalid} with 1024-byte pages and its addresses 2100,
1030, 3500 (and the lesson's 2100 -> 7220); 2017B-8 (valid-invalid bit) and 2023A-7 / 2022A-8 (valid bit off ->
page fault: a quiz item and its twin) are not shown as exam questions.
Here: 2048-byte pages, 14-bit virtual and 15-bit physical addresses, the table below, addresses 5000, 14500, 2500.
Every translation comes from sims.translate (w_paging.translate also checks frame bits glued to the offset bits).
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_paging as w

# ---------------------------------------------------------------- numbers (verified)
PS = 2048
K = w.log2(PS)
T = {0: 6, 1: None, 2: 3, 3: 0, 4: 5, 5: None, 6: None, 7: 1}
VB, PB = 14, 15
assert 2 ** VB // PS == len(T)                                  # 8 pages: the table has a row for each

A1 = 5000
P1_, O1 = w.split(A1, PS)
R1 = w.translate(A1, PS, T)
assert (P1_, O1, T[P1_], R1) == (2, 904, 3, 7048) and 3 * 2048 == 6144
SV, VV = w.strip("sv", A1, [(VB - K, "דף", "page"), (K, "offset", "off")])
SP, VP = w.strip("sp", R1, [(PB - K, "מסגרת", "frame"), (K, "offset", "off")], tint_hidden=False)
assert VV == [2, 904] and VP == [3, 904]
assert w.bits(A1, VB)[-K:] == w.bits(R1, PB)[-K:]              # the offset bits are copied as they are

A2 = 14500
P2_, O2 = w.split(A2, PS)
R2 = w.translate(A2, PS, T)
assert (P2_, O2, T[P2_], R2) == (7, 164, 1, 2212) and 7 * 2048 == 14336
WRONG2 = T[P2_] + O2                                           # frame + offset, without multiplying
assert WRONG2 == 165

A3 = 2500
P3_, O3 = w.split(A3, PS)
assert P3_ == 1 and T[1] is None and w.translate(A3, PS, T) == "fault"

Q = BANK["2015A-6"]
assert Q["answer_he"] == "Page Table" and Q["section"] == "memory"

PT = w.page_table("pe", T)

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הקודם חתכנו כתובת לדף ול-offset. עכשיו נתרגם אותה לכתובת פיזית."),
    P("נכיר את טבלת הדפים, את ביט ה-valid, ומה קורה כשהדף בכלל לא בזיכרון."),
    P("ובסוף שאלה ממבחן.", hold=0.4),
], stage='<div class="kicker">P02 · דפדוף ותרגום כתובות</div><h1>תרגום כתובת בעזרת טבלת דפים</h1>'
         '<p>ממספר דף למספר מסגרת, וה-offset נשאר כמו שהוא. ואם הכניסה לא תקפה: page fault.</p>', layout="title")

idea = Scene("idea", "טבלת הדפים", [
    P("לכל תהליך יש **טבלת דפים**, ובאנגלית page table.", do=show("pt")),
    P("יש בה שורה לכל דף וירטואלי. השורה אומרת באיזו מסגרת ב-RAM הדף יושב.", do=show("i-c1")),
    P("בטבלה הזאת הדפים בגודל 2KB, ויש שמונה דפים, מאפס עד שבע.",
      say="בטבלה הזאת הדפים בגודל שני קילובייט, ויש שמונה דפים, מאפס עד שבע."),
    P("שימו לב: הדפים לא יושבים לפי הסדר. דף אפס במסגרת שש, ודף שלוש במסגרת אפס.", do=show("pt-hi0", "pt-hi3")),
    P("וזה בסדר גמור: כל דף יכול לשבת בכל מסגרת פנויה.", do=hide("pt-hi0", "pt-hi3")),
    P("התרגום מחליף **רק** את מספר הדף במספר המסגרת. ה-offset לא משתנה אף פעם.", do=show("i-f", "i-c2")),
    P("למה? כי דף ומסגרת באותו גודל, והנתון נמצא באותו מרחק מתחילת הבלוק, בשניהם.", hold=0.4),
], stage=w.stack(w.big("i-f", r"\text{physical} = \text{frame} \cdot \text{page size} + \text{offset}", cls="sm"),
                 st.card("i-c1", "plain", "שורה לכל דף: דף ← מסגרת"),
                 st.card("i-c2", "rule", "🔑 ה-offset <b>לא משתנה</b> בתרגום"), gap=40),
   panel=f'<div class="pg-stack">{w.page_table("pt", T, hidden=True)}</div>')

ex1 = Scene("ex1", "תרגום ראשון", [
    P("נתרגם את הכתובת הווירטואלית 5000.", do=show("e-v"), say="נתרגם את הכתובת הווירטואלית חמשת אלפים."),
    P("צעד ראשון: מפצלים. חמשת אלפים חלקי 2048: המנה היא 2, והשארית 904.", do=show("sv-t0", "sv-l0", "sv-t1", "sv-l1", "sv-v0", "sv-v1"),
      say="צעד ראשון: מפצלים. חמשת אלפים חלקי אלפיים ארבעים ושמונה: המנה היא שתיים, והשארית תשע מאות וארבע."),
    P("כלומר דף 2, ו-offset של 904.", do=show("e-c1"), say="כלומר דף שתיים, ואוֹפְסֶט של תשע מאות וארבע."),
    P("צעד שני: מחפשים בטבלה את השורה של דף 2. היא תקפה, והמסגרת היא 3.", do=show("pe-hi2", "e-c2"),
      say="צעד שני: מחפשים בטבלה את השורה של דף שתיים. היא תקפה, והמסגרת היא שלוש."),
    P("צעד שלישי: מחליפים את ביטי הדף בביטי המסגרת, ומעתיקים את ה-offset כמו שהוא.", do=show("e-p")),
    P("ביטי ה-offset זהים למעלה ולמטה. רק החלק השמאלי השתנה.", do=show("sp-v0", "sp-v1")),
    P("ובחשבון: שלוש כפול 2048 זה 6144, ועוד 904, יוצא 7048.", do=show("e-c3"),
      say="ובחשבון: שלוש כפול אלפיים ארבעים ושמונה זה שש אלף מאה ארבעים וארבע, ועוד תשע מאות וארבע, יוצא שבעת אלפים ארבעים ושמונה."),
    P("הכתובת הפיזית היא 7048.", do=show("e-c4"), hold=0.4, say="הכתובת הפיזית היא שבעת אלפים ארבעים ושמונה."),
], stage=w.stack(f'<div id="e-v" class="h">{SV}</div>',
                 f'<div id="e-p" class="h">{SP}</div>',
                 st.card("e-c3", "ex", w.ltr("3 · 2048 + 904 = 7048")),
                 st.card("e-c4", "rule", "🔑 הכתובת הפיזית: " + w.mono("7048")),
                 gap=24),
   panel=f'<div class="pg-stack" style="gap:16px">{PT}'
         + st.card("e-c1", "ex", "דף 2, offset 904")
         + st.card("e-c2", "ex", "דף 2 ← מסגרת 3")
         + "</div>")

ex2 = Scene("ex2", "תרגום שני", [
    P("עוד אחת, הפעם רק בחשבון: הכתובת 14500.", do=show("f-a"), say="עוד אחת, הפעם רק בחשבון: הכתובת ארבעה עשר אלף וחמש מאות."),
    P("שבע פעמים 2048 זה 14336. לכן הדף הוא 7, וה-offset הוא 164.", do=show("f-1"),
      say="שבע פעמים אלפיים ארבעים ושמונה זה ארבעה עשר אלף שלוש מאות שלושים ושש. לכן הדף הוא שבע, והאוֹפְסֶט הוא מאה שישים וארבע."),
    P("בטבלה, דף 7 נמצא במסגרת מספר 1.", do=show("pu-hi7"), say="בטבלה, דף שבע נמצא במסגרת מספר אחת."),
    P("ולכן הכתובת הפיזית היא 2048 ועוד 164: 2212.", do=show("f-2"),
      say="ולכן הכתובת הפיזית היא אלפיים ארבעים ושמונה ועוד מאה שישים וארבע: אלפיים מאתיים ושתים עשרה."),
    P("הכתובת הפיזית יצאה קטנה בהרבה מהווירטואלית. זה תקין: אין שום קשר בין הסדר של הדפים לסדר של המסגרות.",
      do=show("f-c1")),
    P("והמלכודת: לחבר את מספר המסגרת ישר ל-offset, ולקבל 165. שוכחים להכפיל בגודל הדף.", do=show("f-t"),
      say="והמלכודת: לחבר את מספר המסגרת ישר לאוֹפְסֶט, ולקבל מאה שישים וחמש. שוכחים להכפיל בגודל הדף."),
    P("מספר המסגרת אומר **איזו** מסגרת. כדי להגיע לתחילתה, מכפילים בגודל.", hold=0.4),
], stage=w.stack(w.row("f-a", w.mono("14500"), cls="ltr"),
                 w.big("f-1", r"14500 = 7 \cdot 2048 + 164", cls="sm"),
                 w.big("f-2", r"1 \cdot 2048 + 164 = 2212", cls="sm"),
                 st.card("f-t", "trap", "⚠️ לא " + w.ltr("1 + 164") + ": מכפילים את המסגרת בגודל הדף"), gap=30),
   panel=f'<div class="pg-stack" style="gap:16px">{w.page_table("pu", T)}'
         + st.card("f-c1", "rule", "🔑 סדר המסגרות לא קשור לסדר הדפים") + "</div>")

fault = Scene("fault", "page fault", [
    P("ומה עם הכתובת 2500? מפצלים: דף מספר 1, כי 2500 נמצא בין 2048 ל-4096.", do=show("g-a"),
      say="ומה עם הכתובת אלפיים וחמש מאות? מפצלים: דף מספר אחת, כי אלפיים וחמש מאות נמצא בין אלפיים ארבעים ושמונה לארבעת אלפים תשעים ושש."),
    P("בשורה של דף מספר 1, ביט ה-valid הוא אפס, ואין מסגרת.", do=show("pw-hi1", "g-c1"),
      say="בשורה של דף מספר אחת, ביט הוָלִיד הוא אפס, ואין מסגרת."),
    P("ביט ה-valid אומר אם הדף נמצא עכשיו ב-RAM. כאן הוא לא שם."),
    P("לכן ה-MMU לא מפיק כתובת. הוא קורא למערכת ההפעלה, וזה נקרא **page fault**.", do=show("g-c2")),
    P("מערכת ההפעלה היא שמחליטה מה לעשות: מביאה את הדף מהדיסק, או עוצרת את התהליך אם הגישה לא חוקית.",
      do=show("g-c3")),
    P("את הפרטים של הבאת הדף נראה בקורס של דפדוף לפי דרישה.", hold=0.4),
], stage=w.stack(w.row("g-a", w.mono("2500") + " ← דף 1", cls=""),
                 st.card("g-c1", "ex", "דף 1: valid = 0, אין מסגרת"),
                 st.card("g-c2", "trap", "⚠️ valid = 0 ← אין כתובת פיזית: <b>page fault</b>"),
                 st.card("g-c3", "rule", "🔑 ה-MMU רק מתריע. מערכת ההפעלה מטפלת"), gap=30),
   panel=f'<div class="pg-stack">{w.page_table("pw", T)}</div>')

exam = Scene("exam", "שאלה ממבחן", [
    P("ועכשיו שאלה ממבחן: כיצד נקראת הטבלה שלפיה מתרגמים מספר דף וירטואלי למספר מסגרת פיזית?"),
    P("זה בדיוק מה שעשינו כל הסרטון: מספר דף נכנס, מספר מסגרת יוצא.", do=show("x-1")),
    P("התשובה: טבלת הדפים, page table.", do=show("x-ans")),
    P("המלכודת: לענות TLB. ה-TLB הוא רק מטמון קטן של חלק מהשורות של הטבלה.", do=show("x-t")),
    P("הטבלה המלאה, עם שורה לכל דף, היא טבלת הדפים. ואת ה-TLB נפגוש בהמשך הקורס.", hold=0.5),
], stage=w.stack(w.row("x-1", "מספר דף ← <b>טבלה</b> ← מספר מסגרת"),
                 st.card("x-t", "trap", "⚠️ לא TLB: הוא רק מטמון של חלק מהטבלה"), gap=40),
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         + w.qans("x-ans", w.ltr("Page Table") + " (טבלת הדפים)"))

recap = Scene("recap", "סיכום", [
    P("לסיכום: מפצלים את הכתובת לדף ול-offset.", do=show("r-1")),
    P("מחפשים את הדף בטבלת הדפים ומקבלים מסגרת.", do=show("r-2")),
    P("הכתובת הפיזית היא המסגרת כפול גודל הדף, ועוד אותו offset.", do=show("r-3")),
    P("ואם ביט ה-valid כבוי: page fault, ומערכת ההפעלה מטפלת. נתראה ברמה הבאה.", do=show("r-4"), hold=0.6),
], stage=w.stack(w.big("r-f", r"\text{physical} = \text{frame} \cdot \text{page size} + \text{offset}", hidden=False, cls="sm"), gap=20),
   panel=st.card("r-1", "rule", "🔑 כתובת ← (דף, offset)")
         + st.card("r-2", "rule", "🔑 טבלת הדפים: דף ← מסגרת")
         + st.card("r-3", "rule", "🔑 offset לא משתנה")
         + st.card("r-4", "trap", "⚠️ valid = 0 ← page fault"))

VIDEO = Video("P02", "paging", "תרגום כתובת בעזרת טבלת דפים", [title, idea, ex1, ex2, fault, exam, recap],
              bank={"2015A-6": None})
