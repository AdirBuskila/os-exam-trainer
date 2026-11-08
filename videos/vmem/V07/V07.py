# -*- coding: utf-8 -*-
"""V07 · בוס: מבחן החלפת דפים — boss walkthrough (build: tools/video/vid.py V07).

Source: src/courses/vmem.py level 7 (boss: past-exam items and a full simulation; OPT looks right, LRU left, FIFO at
load time; only FIFO has Belady; Clock: hardware sets, OS clears).
Exam parts: 2014A-7 (the interrupt on the first access to a code page: Page-Fault) and 2020B-10 (a page fault brings
the page from the disk into RAM), both open questions no guided quiz uses; and an original full simulation
"בסגנון מבחן" (bank={} for it): LRU and OPT on 2 4 2 1 5 2 1 3 4 1 5 4 with 3 frames (LRU 7, OPT 6).
Avoided on purpose: every boss-quiz item (2023A-8, 2019B-8, 2024A-8, 2024B-8, LRU on 1 2 3 4 1 2 5 1 2 3 4 5 with
4 frames, FIFO on the 20-reference string with 4 frames) and their twins (2022B-8, 2017SA-6); all course strings.
Both runs come from sims.replace(strict=True) through w_vmem.run; no OPT tie occurs.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_vmem as w

# ---------------------------------------------------------------- numbers (verified)
Q1, Q2 = BANK["2014A-7"], BANK["2020B-10"]
assert Q1["answer_he"] == "Page-Fault" and "בפעם הראשונה" in Q1["he"]
assert "RAM" in Q2["answer_he"] and "page fault" in Q2["he"]

Z = [2, 4, 2, 1, 5, 2, 1, 3, 4, 1, 5, 4]
LR = w.rtable("l", Z, 3, "LRU", cw=104, out=False, sm=True, label="LRU, 3 מסגרות")
OP = w.rtable("o", Z, 3, "OPT", cw=104, out=False, sm=True, label="OPT, 3 מסגרות")
assert (LR.faults, OP.faults) == (7, 6)
L, O = LR.steps, OP.steps
assert [x["fault"] for x in L[:7]] == [x["fault"] for x in O[:7]] == [True, True, False, True, True, False, False]
assert L[4]["victim"] == O[4]["victim"] == 4                        # the first eviction agrees
assert L[7]["victim"] == 5 and O[7]["victim"] == 2                  # page 3: LRU looks left, OPT right
assert L[8]["victim"] == 2 and O[8]["victim"] == 3                  # page 4
assert L[10]["fault"] and not O[10]["fault"]                         # page 5: LRU evicted it, OPT kept it
assert w.faults(Z, 3, "FIFO") == 9

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("זה שלב הבוס של הקורס: שאלות ממבחנים קודמים, ובסוף סימולציה מלאה."),
    P("שתי שאלות קצרות על page fault, ואחריהן מחרוזת אחת שמריצים עליה שני אלגוריתמים."),
    P("טיפ לפני שמתחילים: בכל שאלה, קודם מזהים מה בדיוק שואלים, ורק אחר כך עונים.", hold=0.4),
], stage='<div class="kicker">V07 · דפדוף לפי דרישה והחלפת דפים</div><h1>בוס: מבחן החלפת דפים</h1>'
         '<p>שאלות ממבחנים קודמים וסימולציה מלאה: לזהות מה המבחן שואל, ולהריץ את האלגוריתם בלי לטעות בכיוון.</p>',
   layout="title")

q1 = Scene("q1", "שאלה 1", [
    P("שאלה ראשונה: פונים לדף בתוך קוד התוכנית **בפעם הראשונה**. איזו פסיקה נוצרת?"),
    P("בדפדוף לפי דרישה, שום דף לא נטען מראש. אז בגישה הראשונה הדף עוד לא ב-RAM.", do=show("a-1")),
    P("ביט ה-valid שלו כבוי, וה-MMU לא יכול לתרגם את הכתובת.", do=show("a-2")),
    P("לכן הוא מעלה פסיקה: page fault. מערכת ההפעלה טוענת את הדף, וההוראה רצה שוב.", do=show("a-3")),
    P("התשובה: Page-Fault.", do=show("a-a")),
    P("המלכודת: segmentation fault. זו פסיקה על גישה **לא חוקית**, וכאן הגישה חוקית לגמרי.", do=show("a-t"), hold=0.4),
], stage=w.stack(w.row("a-1", "גישה ראשונה ← הדף עוד לא נטען"),
                 w.row("a-2", "valid = 0 ← ה-MMU לא מתרגם"),
                 w.row("a-3", "← <b>page fault</b>", cls="big"),
                 st.card("a-t", "trap", "⚠️ לא segmentation fault: הגישה חוקית"), gap=28),
   panel=f'<div class="qstem"><span class="qid">{Q1["id"]}</span>{Q1["he"]}</div>'
         + w.qans("a-a", f'<span class="k">תשובה:</span> <span class="vm-ltr">{Q1["answer_he"]}</span>'))

q2 = Scene("q2", "שאלה 2", [
    P("שאלה שנייה: כשמתרחש page fault, מערכת ההפעלה מביאה דף מהדיסק הקשיח אל... לאן?"),
    P("הבעיה ב-page fault היא שהדף לא נמצא בזיכרון הראשי. אז לשם צריך להביא אותו.", do=show("b-1")),
    P("מערכת ההפעלה מוצאת מסגרת ב-RAM, פנויה או של קורבן, וקוראת אליה את הדף.", do=show("b-2")),
    P("רק אחרי זה היא מעדכנת את טבלת הדפים, וההוראה רצה מחדש.", do=show("b-3")),
    P("התשובה: אל ה-RAM.", do=show("b-a")),
    P("המלכודת: ה-TLB שומר רק תרגומי כתובות, והמטמון עותקים קטנים של נתונים. הדף עצמו יושב במסגרת ב-RAM.",
      do=show("b-t"), hold=0.4),
], stage=w.stack(w.ltrflex("b-1", ["דיסק", "→", "<b>RAM</b>"], cls="q"),
                 w.row("b-2", "מסגרת פנויה, או של קורבן"),
                 w.row("b-3", "← מעדכנים את טבלת הדפים ← ההוראה רצה שוב"),
                 st.card("b-t", "trap", "⚠️ לא ה-TLB ולא המטמון"), gap=30),
   panel=f'<div class="qstem"><span class="qid">{Q2["id"]}</span>{Q2["he"]}</div>'
         + w.qans("b-a", f'<span class="k">תשובה:</span> {Q2["answer_he"]}'))

EXQ = ('<div class="qstem"><span class="qid">בסגנון מבחן</span>3 מסגרות, ריקות בהתחלה. כמה שגיאות דף יהיו '
       'באלגוריתם LRU, וכמה באלגוריתם האופטימלי?</div>' + w.qcode(3, Z))
q3 = Scene("q3", "שאלה 3", [
    P("ועכשיו השאלה הגדולה, בסגנון מבחן: שתים עשרה הפניות ושלוש מסגרות."),
    P("צריך לספור שגיאות פעמיים: פעם ב-LRU, ופעם באלגוריתם האופטימלי.", say="צריך לספור שגיאות פעמיים: פעם באֶל אַר יוּ, ופעם באלגוריתם האופטימלי."),
    P("הטיפ: מריצים את שתי הטבלאות זו מתחת לזו, וכך רואים בדיוק איפה הן נפרדות.", do=show("q-1")),
    P("ובכל שגיאה עם מסגרות מלאות, שואלים: שמאלה או ימינה?", do=show("q-2"), hold=0.3),
], stage=w.stack(st.card("q-1", "ex", "שתי טבלאות, זו מתחת לזו"),
                 st.card("q-2", "rule", "🔑 LRU: מסתכלים <b>שמאלה</b>. OPT: מסתכלים <b>ימינה</b>"), gap=30),
   panel=EXQ)

sim = Scene("sim", "סימולציה", [
    P("ההתחלה זהה: 2 ו-4 שגיאות, 2 פגיעה, 1 שגיאה.", do=LR.cols(0, 3) + OP.cols(0, 3),
      say="ההתחלה זהה: שתיים וארבע שגיאות, שתיים פגיעה, אחת שגיאה."),
    P("דף 5: מסגרות מלאות. LRU: ב-4 השתמשו הכי מזמן. OPT: 4 יידרש הכי מאוחר. שניהם מפנים את 4.",
      do=show("l-vk-4", "o-vk-4") + LR.col(4) + OP.col(4),
      say="דף חמש: מסגרות מלאות. אֶל אַר יוּ: בארבע השתמשו הכי מזמן. אוֹפְּט: ארבע יידרש הכי מאוחר. שניהם מפנים את ארבע."),
    P("2 ו-1: פגיעות בשתי הטבלאות.", do=hide("l-vk-4", "o-vk-4") + LR.cols(5, 6) + OP.cols(5, 6),
      say="שתיים ואחת: פגיעות בשתי הטבלאות."),
    P("ועכשיו דף 3, ופה הן נפרדות.", do=show("l-rr-7", "o-rr-7"), say="ועכשיו דף שלוש, ופה הן נפרדות."),
    P("LRU מסתכל שמאלה: ב-5 השתמשו לפני 2 ו-1. אז 5 יוצא.", do=show("l-vk-7") + LR.col(7),
      say="אֶל אַר יוּ מסתכל שמאלה: בחמש השתמשו לפני שתיים ואחת. אז חמש יוצא."),
    P("OPT מסתכל ימינה: 1 ו-5 עוד יידרשו, ו-2 לא יידרש אף פעם. אז 2 יוצא.", do=show("o-vk-7") + OP.col(7),
      say="אוֹפְּט מסתכל ימינה: אחת וחמש עוד יידרשו, ושתיים לא יידרש אף פעם. אז שתיים יוצא."),
    P("דף 4: שגיאה בשתיהן. LRU מפנה את 2, ו-OPT את 3, שלא יחזור.",
      do=hide("l-rr-7", "o-rr-7", "l-vk-7", "o-vk-7") + show("l-vk-8", "o-vk-8") + LR.col(8) + OP.col(8),
      say="דף ארבע: שגיאה בשתיהן. אֶל אַר יוּ מפנה את שתיים, ואוֹפְּט את שלוש, שלא יחזור."),
    P("דף 1: פגיעה בשתיהן.", do=hide("l-vk-8", "o-vk-8") + LR.col(9) + OP.col(9), say="דף אחת: פגיעה בשתיהן."),
    P("דף 5: ב-LRU הוא פונה קודם, אז שגיאה. ב-OPT הוא נשמר בדיוק בשבילו: פגיעה.",
      do=show("l-rr-10", "o-rr-10") + LR.col(10) + OP.col(10),
      say="דף חמש: באֶל אַר יוּ הוא פונה קודם, אז שגיאה. באוֹפְּט הוא נשמר בדיוק בשבילו: פגיעה."),
    P("ודף 4 אחרון: פגיעה בשתיהן.", do=hide("l-rr-10", "o-rr-10") + LR.col(11) + OP.col(11),
      say="ודף ארבע אחרון: פגיעה בשתיהן."),
    P("סך הכול: LRU שבע שגיאות, והאופטימלי שש.", hold=0.4, say="סך הכול: אֶל אַר יוּ שבע שגיאות, והאופטימלי שש."),
], stage=w.stack(LR.html, OP.html, gap=18), layout="full")

ans = Scene("ans", "תשובה", [
    P("התשובה: שבע שגיאות ב-LRU, ושש באופטימלי.", do=show("z-a"), say="התשובה: שבע שגיאות באֶל אַר יוּ, ושש באופטימלי."),
    P("בדיקת שפיות: האופטימלי לא יכול לקבל יותר מ-LRU. שש לא גדול משבע, אז זה מסתדר.", do=show("z-1")),
    P("ולמי שרוצה להשוות: FIFO על אותה מחרוזת נותן תשע.", do=show("z-2"),
      say="ולמי שרוצה להשוות: פִיפוֹ על אותה מחרוזת נותן תשע."),
    P("המלכודת הנפוצה: להפוך כיוונים. מי שמסתכל ימינה ב-LRU, מריץ בעצם את האופטימלי.", do=show("z-t"), hold=0.4),
], stage=w.stack(st.card("z-1", "rule", "🔑 בדיקה: OPT ≤ כל אלגוריתם אחר"),
                 st.card("z-2", "ex", "FIFO על אותה מחרוזת: 9"),
                 st.card("z-t", "trap", "⚠️ LRU = שמאלה (עבר), OPT = ימינה (עתיד)"), gap=26),
   panel=EXQ + w.qans("z-a", '<span class="k">תשובה:</span> LRU: 7 שגיאות דף; האופטימלי: 6'))

recap = Scene("recap", "סיכום", [
    P("לסיכום הקורס: גישה ראשונה לדף היא page fault, והדף מגיע מהדיסק אל ה-RAM.", do=show("r-1")),
    P("בסימולציה עובדים עמודה אחרי עמודה, ובכל פינוי בודקים לאן האלגוריתם מסתכל.", do=show("r-2")),
    P("וב-Clock, החומרה מדליקה את הביט, ומערכת ההפעלה מכבה אותו.", do=show("r-3")),
    P("עכשיו תורכם: שלב הבוס באפליקציה מחכה. בהצלחה!", do=show("r-4"), hold=0.6),
], stage=w.ltrflex("r-0", ["LRU: 7", "|", "OPT: 6"], hidden=False),
   panel=st.card("r-1", "rule", "🔑 גישה ראשונה ← page fault ← דיסק אל RAM")
         + st.card("r-2", "rule", "🔑 עמודה אחרי עמודה; בכל פינוי: לאן מסתכלים?")
         + st.card("r-3", "rule", "🔑 Clock: חומרה מדליקה, מערכת ההפעלה מכבה")
         + st.card("r-4", "ex", "🏆 לשלב הבוס"))

VIDEO = Video("V07", "vmem", "בוס: מבחן החלפת דפים", [title, q1, q2, q3, sim, ans, recap],
              bank={"2014A-7": None, "2020B-10": None})
