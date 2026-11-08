# -*- coding: utf-8 -*-
"""V05 · יותר מסגרות, יותר שגיאות? האנומליה של Belady — video script (build: tools/video/vid.py V05).

Source: src/courses/vmem.py level 5 (lesson + goal: FIFO can fault more with more frames (Belady's anomaly); LRU and
OPT are stack algorithms: the pages held with n frames are always a subset of those held with n+1, so they are
immune).
Exam part: an original question "בסגנון מבחן" (bank={}): the bank's Belady item 2023A-8 is a level-5 and boss quiz
item, and no free item asks about the stack property.
Avoided on purpose: the classic Belady string 1 2 3 4 1 2 5 1 2 3 4 5 (all level-5 quiz items and the boss LRU item
use it, with its counts 9 / 10 / 8). An exhaustive search over 5 pages showed it is the ONLY 3-vs-4-frame FIFO
anomaly of length <= 12 (up to renaming), so this video uses a 13-reference one found by search:
2 6 1 5 2 5 6 3 2 6 1 4 3 (FIFO: 3 frames 9 faults, 4 frames 10; LRU: 11 and 8).
The exam-style claim (LRU 7 faults with 3 frames, 8 with 4) is answered from the stack property, no string.
Every count comes from sims.replace through w_vmem.run; the inclusion property is checked step by step below.
"""
from vid import P, Scene, Video, show, hide
import stage as st
import w_vmem as w

# ---------------------------------------------------------------- numbers (verified)
BS = [2, 6, 1, 5, 2, 5, 6, 3, 2, 6, 1, 4, 3]
F3 = w.rtable("a", BS, 3, "FIFO", cw=100, out=False, sm=True, label="FIFO, 3 מסגרות")
F4 = w.rtable("b", BS, 4, "FIFO", cw=100, out=False, sm=True, label="FIFO, 4 מסגרות")
assert (F3.faults, F4.faults) == (9, 10)
assert (w.faults(BS, 3, "LRU"), w.faults(BS, 4, "LRU")) == (11, 8)
# first 7 references: 6 faults with 3 frames, 4 with 4 frames
assert F3.nfaults_upto(6) == 6 and F4.nfaults_upto(6) == 4
# reference 8 (index 7, page 3): both fault; 3 frames evict 5, 4 frames evict 2 -> inclusion breaks here
assert F3.steps[7]["victim"] == 5 and F4.steps[7]["victim"] == 2
R3, R4 = w.resident(BS, 3, "FIFO"), w.resident(BS, 4, "FIFO")
assert [i for i in range(len(BS)) if not R3[i] <= R4[i]] == [7, 8, 11]
assert R3[7] == {2, 3, 6} and R4[7] == {1, 3, 5, 6}
assert not F3.steps[8]["fault"] and F4.steps[8]["fault"]                # page 2: hit with 3 frames, fault with 4
assert F3.nfaults_upto(7) == 7 and F4.nfaults_upto(7) == 5
assert [x["fault"] for x in F4.steps[8:]] == [True] * 5
assert [F4.steps[i]["victim"] for i in (8, 9)] == [BS[9], BS[10]]   # evicts exactly the next reference, twice
assert [x["fault"] for x in F3.steps[8:]] == [False, False, True, True, False]
# LRU: the n most recently used distinct pages -> inclusion holds at every step for 1..5 frames
for n in range(1, 5):
    a, b = w.resident(BS, n, "LRU"), w.resident(BS, n + 1, "LRU")
    assert all(a[i] <= b[i] for i in range(len(BS)))
    for i in range(len(BS)):              # the set is exactly the n most recent distinct pages
        rec = []
        for p in reversed(BS[:i + 1]):
            if p not in rec:
                rec.append(p)
        assert a[i] == set(rec[:n])
for n in range(1, 4):                      # LRU never gets worse with one more frame
    assert w.faults(BS, n + 1, "LRU") <= w.faults(BS, n, "LRU")

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נשאל שאלה שנשמעת טיפשית: אם נוסיף זיכרון, האם יכולות להיות יותר שגיאות דף?"),
    P("נראה שב-FIFO התשובה היא כן, ונבין למה ב-LRU וב-OPT זה בלתי אפשרי.",
      say="נראה שבפִיפוֹ התשובה היא כן, ונבין למה באֶל אַר יוּ ובאוֹפְּט זה בלתי אפשרי."),
    P("ובסוף נבדוק טענה בסגנון מבחן.", hold=0.4),
], stage='<div class="kicker">V05 · דפדוף לפי דרישה והחלפת דפים</div><h1>יותר מסגרות, יותר שגיאות? האנומליה של Belady</h1>'
         '<p>מדוע רק FIFO יכול להחמיר כשנותנים לו יותר זיכרון.</p>', layout="title")

side = Scene("side", "3 מול 4 מסגרות", [
    P("האינטואיציה אומרת: יותר מסגרות, פחות שגיאות. או לפחות לא יותר."),
    P("נבדוק על מחרוזת משלנו, לא זו שבאפליקציה: שלוש עשרה הפניות, FIFO, פעם עם שלוש מסגרות ופעם עם ארבע."),
    P("שבע ההפניות הראשונות: עם שלוש מסגרות יש כבר שש שגיאות. עם ארבע, רק ארבע.",
      do=F3.cols(0, 6) + F4.cols(0, 6)),
    P("עד כאן הכול לפי האינטואיציה: ארבע מסגרות מחזיקות את כל ארבעת הדפים, ואין פינויים."),
    P("ההפניה הבאה, דף 3, היא שגיאה בשתי הטבלאות. אבל כל אחת מפנה דף אחר.",
      do=show("a-rr-7", "b-rr-7"), say="ההפניה הבאה, דף שלוש, היא שגיאה בשתי הטבלאות. אבל כל אחת מפנה דף אחר."),
    P("עם שלוש מסגרות, הוותיק הוא 5, והוא יוצא. עם ארבע, הוותיק הוא 2, שנטען ראשון.",
      do=show("a-vk-7", "b-vk-7") + F3.col(7) + F4.col(7),
      say="עם שלוש מסגרות, הוותיק הוא חמש, והוא יוצא. עם ארבע, הוותיק הוא שתיים, שנטען ראשון."),
    P("ושימו לב מה קרה: דף 2 נמצא בזיכרון הקטן, אבל **לא** בזיכרון הגדול.",
      say="ושימו לב מה קרה: דף שתיים נמצא בזיכרון הקטן, אבל לא בזיכרון הגדול."),
    P("ומיד מבקשים את דף 2. עם שלוש מסגרות זו פגיעה, ועם ארבע זו שגיאה.",
      do=hide("a-rr-7", "b-rr-7", "a-vk-7", "b-vk-7") + F3.col(8) + F4.col(8),
      say="ומיד מבקשים את דף שתיים. עם שלוש מסגרות זו פגיעה, ועם ארבע זו שגיאה."),
    P("מכאן הטבלה הגדולה נגררת: פעמיים ברצף היא מפנה בדיוק את הדף שמבקשים מיד אחר כך. שגיאה בכל חמש ההפניות האחרונות.", do=F4.cols(9, 12)),
    P("והקטנה? פגיעה, שתי שגיאות, ועוד פגיעה.", do=F3.cols(9, 12)),
    P("התוצאה: עם שלוש מסגרות **תשע** שגיאות, ועם ארבע **עשר**. יותר זיכרון, יותר שגיאות."),
    P("זו **האנומליה של Belady**. והיא לא באג בחישוב: זו תכונה של FIFO.", hold=0.4),
], stage=w.stack(F3.html, F4.html, gap=14),
   panel="", layout="full")

stackp = Scene("stack", "אלגוריתם מחסנית", [
    P("אז מה בדיוק השתבש? הקבוצות."),
    P("נגדיר: אלגוריתם הוא **אלגוריתם מחסנית** אם בכל רגע, הדפים בזיכרון עם $n$ מסגרות מוכלים בדפים שבזיכרון עם $n+1$ מסגרות.",
      do=show("k-2")),
    P("למה זה מספיק? כל פגיעה עם $n$ מסגרות היא גם פגיעה עם $n+1$: הדף בקבוצה הקטנה, ולכן גם בגדולה.",
      do=show("k-3")),
    P("אז עם יותר מסגרות יש לפחות אותן פגיעות, ולכן לכל היותר אותן שגיאות.", do=show("k-4")),
    P("FIFO נכשל בדיוק בזה: ראינו את דף 2 בזיכרון של שלוש, ולא בזיכרון של ארבע.", do=show("k-1", "k-5"),
      say="פִיפוֹ נכשל בדיוק בזה: ראינו את דף שתיים בזיכרון של שלוש, ולא בזיכרון של ארבע."),
    P("הסיבה: ב-FIFO התוכן תלוי בזמני הטעינה, והם שונים בין שתי הריצות.", hold=0.3),
    P("ו-LRU? עם $n$ מסגרות הוא מחזיק בדיוק את $n$ הדפים השונים שהשתמשו בהם לאחרונה.", do=show("k-6"),
      say="ואֶל אַר יוּ? עם אֶן מסגרות הוא מחזיק בדיוק את אֶן הדפים השונים שהשתמשו בהם לאחרונה."),
    P("$n$ האחרונים תמיד מוכלים ב-$n+1$ האחרונים. לכן LRU הוא אלגוריתם מחסנית.", do=show("k-7"),
      say="ואֶן האחרונים תמיד מוכלים באֶן ועוד אחת האחרונים. לכן אֶל אַר יוּ הוא אלגוריתם מחסנית."),
    P("על אותה מחרוזת, LRU עובר מאחת עשרה שגיאות עם שלוש מסגרות, לשמונה עם ארבע.", do=show("k-8"),
      say="על אותה מחרוזת, אֶל אַר יוּ עובר מאחת עשרה שגיאות עם שלוש מסגרות, לשמונה עם ארבע."),
    P("גם OPT הוא אלגוריתם מחסנית. את ההוכחה שלו לא נביא כאן, אבל המסקנה זהה: אין לו אנומליה.", do=show("k-9"),
      say="גם אוֹפְּט הוא אלגוריתם מחסנית. את ההוכחה שלו לא נביא כאן, אבל המסקנה זהה: אין לו אנומליה.",
      hold=0.4),
], stage=w.stack(w.row("k-1", "הדפים בזיכרון אחרי הפניה 8:", cls=""),
                 w.row("k-5", "3 מסגרות: " + w.ltr("{2, 3, 6}") + "&nbsp;&nbsp;&nbsp; 4 מסגרות: " + w.ltr("{1, 3, 5, 6}"),
                       cls="big"),
                 st.card("k-2", "rule", "🔑 אלגוריתם מחסנית: זיכרון($n$) ⊆ זיכרון($n+1$) בכל רגע"),
                 w.row("k-3", "פגיעה עם $n$ ← פגיעה עם $n+1$"),
                 w.row("k-4", "← שגיאות($n+1$) ≤ שגיאות($n$)", cls="big"), gap=24),
   panel=st.card("k-6", "ex", "LRU מחזיק את $n$ הדפים <b>האחרונים</b> בשימוש")
         + st.card("k-7", "rule", "🔑 $n$ האחרונים ⊆ $n+1$ האחרונים")
         + st.card("k-8", "plain", "LRU: 11 שגיאות ← 8 שגיאות")
         + st.card("k-9", "rule", "🔑 גם OPT: אין אנומליה. רק FIFO"))

EXQ = ('<div class="qstem"><span class="qid">בסגנון מבחן</span>על מחרוזת הפניות מסוימת, LRU עם 3 מסגרות גורם ל-7 '
       'שגיאות דף. סטודנט טוען שעל אותה מחרוזת, LRU עם 4 מסגרות גרם ל-8 שגיאות. האם זה ייתכן? נמקו.</div>')
exam = Scene("exam", "שאלה בסגנון מבחן", [
    P("שאלה בסגנון מבחן: LRU עם שלוש מסגרות נותן שבע שגיאות. עם ארבע, סטודנט קיבל שמונה. ייתכן?",
      say="שאלה בסגנון מבחן: אֶל אַר יוּ עם שלוש מסגרות נותן שבע שגיאות. עם ארבע, סטודנט קיבל שמונה. ייתכן?"),
    P("אין כאן מחרוזת, ולא צריך אותה. מספיקה התכונה שהוכחנו.", do=show("x-1")),
    P("LRU הוא אלגוריתם מחסנית: עם ארבע מסגרות הזיכרון תמיד מכיל את מה שיש עם שלוש.", do=show("x-2"),
      say="אֶל אַר יוּ הוא אלגוריתם מחסנית: עם ארבע מסגרות הזיכרון תמיד מכיל את מה שיש עם שלוש."),
    P("לכן כל פגיעה עם שלוש היא פגיעה גם עם ארבע, ומספר השגיאות עם ארבע הוא לכל היותר שבע.", do=show("x-3")),
    P("שמונה גדול משבע. אז הטענה בלתי אפשרית, והסטודנט טעה בסימולציה.", do=show("x-a")),
    P("המלכודת: לענות ״כן, זו האנומליה של Belady״. האנומליה שייכת ל-FIFO בלבד.", do=show("x-t"), hold=0.5,
      say="המלכודת: לענות כן, זו האנומליה של בֵּלָדִי. האנומליה שייכת לפִיפוֹ בלבד."),
], stage=w.stack(w.row("x-1", "לא צריך לסמלץ: מספיקה תכונת המחסנית"),
                 w.row("x-2", "זיכרון(3) ⊆ זיכרון(4)", cls="big"),
                 w.row("x-3", "← שגיאות(4) ≤ שגיאות(3) = 7", cls="big"),
                 st.card("x-t", "trap", "⚠️ Belady = FIFO בלבד"), gap=30),
   panel=EXQ + w.qans("x-a", '<span class="k">תשובה:</span> לא ייתכן. LRU הוא אלגוריתם מחסנית, ולכן עם 4 מסגרות '
                             'יהיו לכל היותר 7 שגיאות.'))

recap = Scene("recap", "סיכום", [
    P("לסיכום: ב-FIFO יותר מסגרות יכולות לתת יותר שגיאות. זו האנומליה של Belady.", do=show("r-1")),
    P("היא קורית כי הזיכרון הגדול לא תמיד מכיל את הקטן.", do=show("r-2")),
    P("LRU ו-OPT הם אלגוריתמי מחסנית: הקטן תמיד מוכל בגדול, ולכן יותר מסגרות לעולם לא מזיקות.", do=show("r-3"),
      say="אֶל אַר יוּ ואוֹפְּט הם אלגוריתמי מחסנית: הקטן תמיד מוכל בגדול, ולכן יותר מסגרות לעולם לא מזיקות."),
    P("ברמה הבאה: האלגוריתם שמערכות אמיתיות באמת משתמשות בו. נתראה.", do=show("r-4"), hold=0.6),
], stage=w.stack(w.row("r-0", "FIFO, 3 מסגרות: 9 &nbsp;&nbsp;|&nbsp;&nbsp; 4 מסגרות: 10", hidden=False, cls="big")),
   panel=st.card("r-1", "trap", "⚠️ Belady: יותר מסגרות, יותר שגיאות. רק FIFO")
         + st.card("r-2", "plain", "הסיבה: זיכרון(3) ⊄ זיכרון(4)")
         + st.card("r-3", "rule", "🔑 LRU, OPT: אלגוריתמי מחסנית, חסינים")
         + st.card("r-4", "ex", "הבא: Clock"))

VIDEO = Video("V05", "vmem", "יותר מסגרות, יותר שגיאות? האנומליה של Belady", [title, side, stackp, exam, recap], bank={})
