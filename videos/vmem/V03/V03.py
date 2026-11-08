# -*- coding: utf-8 -*-
"""V03 · החלפת דפים LRU — video script (build: tools/video/vid.py V03).

Source: src/courses/vmem.py level 3 (lesson + goal: LRU evicts the page whose last use is the oldest; a hit refreshes
the page; exact LRU must be updated on every memory reference, so real systems approximate it).
Exam anchor: 2015B-7 (open question: name an algorithm we learned whose cost per memory reference is O(log n);
official answer LFU, pages kept in a heap), no guided quiz uses it.
Avoided on purpose: the level-3 quiz strings (1 2 3 1 4 2; the classic 20-reference string;
2 3 2 1 5 2 4 5 3 2 5 2) and every other string of the course; the quiz's "why is exact LRU rare" is only taught.
Here: the V02 string 2 6 4 6 2 5 2 3 5 4 with 3 frames again (LRU 6 faults vs FIFO 7), so the two runs can be
compared at the reference where they part (page 5: FIFO evicts 2, LRU evicts 4).
Every column, victim and count comes from sims.replace through w_vmem.run.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_vmem as w

# ---------------------------------------------------------------- numbers (verified)
S = [2, 6, 4, 6, 2, 5, 2, 3, 5, 4]
T = w.rtable("t", S, 3, "LRU", cw=82, order=True)
L = T.steps
assert T.faults == 6 and w.faults(S, 3, "FIFO") == 7
assert [x["fault"] for x in L] == [True, True, True, False, False, True, False, True, False, True]
assert L[3]["mem"] == [2, 4, 6] and L[4]["mem"] == [4, 6, 2]          # every hit moves the page to the right end
assert L[5]["victim"] == 4 and w.run(S, 3, "FIFO")["steps"][5]["victim"] == 2
# the LRU victim at reference 5 = the resident page whose last use (looking left) is the oldest
last = {p: max(i for i in range(5) if S[i] == p) for p in L[4]["mem"]}
assert last == {2: 4, 6: 3, 4: 2} and min(last, key=last.get) == 4
assert not L[6]["fault"]                                                # LRU kept 2: the next reference hits
assert L[7]["victim"] == 6 and L[9]["victim"] == 2

Q = BANK["2015B-7"]
assert Q["section"] == "replacement" and "LFU" in Q["answer_he"]

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נכיר את LRU: האלגוריתם שמסתכל על העבר."),
    P("נריץ אותו על אותה מחרוזת מהסרטון הקודם, ונראה בדיוק איפה הוא נפרד מ-FIFO."),
    P("ובסוף נפתור שאלה ממבחן על המחיר של אלגוריתמים כאלה.", hold=0.4),
], stage='<div class="kicker">V03 · דפדוף לפי דרישה והחלפת דפים</div><h1>החלפת דפים LRU</h1>'
         '<p>מפנים את הדף שלא השתמשו בו הכי הרבה זמן. כאן פגיעה כן משנה: היא מרעננת את הדף.</p>',
   layout="title")

idea = Scene("idea", "הרעיון", [
    P("**LRU** הם ראשי התיבות של Least Recently Used: הדף שהשתמשו בו הכי מזמן.", do=show("i-1"),
      say="אֶל אַר יוּ הם ראשי התיבות של לִיסְט רִיסֶנְטְלִי יוּזְד: הדף שהשתמשו בו הכי מזמן."),
    P("ההנחה: דף שהשתמשו בו לאחרונה כנראה ישמש שוב בקרוב. אז שומרים אותו."),
    P("וזה ההבדל מ-FIFO. שם הקובע הוא מתי הדף **נטען**. כאן, מתי **השתמשו** בו בפעם האחרונה.", do=show("i-2")),
    P("גם כאן מחזיקים רשימה: הישן משמאל, הטרי מימין. והקורבן הוא השמאלי.", do=show("i-3")),
    P("אבל עכשיו **פגיעה מרעננת**: דף שפגענו בו עובר לקצה הימני, כאילו הוא חדש.", do=show("i-4", "i-trap"), hold=0.3),
], stage=w.stack(w.queue("i-3", [2, 4, 6], left="ישן", right="טרי"),
                 w.queue("i-4", [2, 6, 4], left="ישן", right="טרי", head="פגיעה ב-4:"), gap=40),
   panel=st.card("i-1", "rule", "🔑 LRU מפנה את הדף ש<b>השימוש האחרון</b> בו הכי ותיק")
         + st.card("i-2", "ex", "FIFO: זמן <b>טעינה</b>. LRU: זמן <b>שימוש</b>")
         + st.card("i-trap", "trap", "⚠️ פגיעה מזיזה את הדף לסוף הרשימה"))

run = Scene("run", "דוגמה", [
    P("אותה מחרוזת: 2, 6, 4, 6, 2, 5, 2, 3, 5, 4, ושלוש מסגרות. ב-FIFO יצאו שבע שגיאות.",
      say="אותה מחרוזת: שתיים, שש, ארבע, שש, שתיים, חמש, שתיים, שלוש, חמש, ארבע, ושלוש מסגרות. בפִיפוֹ יצאו שבע שגיאות."),
    P("2, 6 ו-4 נכנסים. שלוש שגיאות.", do=T.cols(0, 2), say="שתיים, שש וארבע נכנסים. שלוש שגיאות."),
    P("דף 6: פגיעה. והפעם הוא עובר לסוף הרשימה: 2, 4, 6.", do=T.col(3),
      say="דף שש: פגיעה. והפעם הוא עובר לסוף הרשימה: שתיים, ארבע, שש."),
    P("דף 2: פגיעה, וגם הוא עובר לסוף: 4, 6, 2.", do=T.col(4), say="דף שתיים: פגיעה, וגם הוא עובר לסוף: ארבע, שש, שתיים."),
    P("ועכשיו דף 5, המקום שבו FIFO פינה את 2. מה LRU עושה?", do=show("t-hl-5")),
    P("מסתכלים **שמאלה**, אל העבר. ב-2 השתמשו לפני הפניה אחת, ב-6 לפני שתיים, וב-4 לפני שלוש.",
      do=show("t-rr-4", "t-rr-3", "t-rr-2", "r-c3"),
      say="מסתכלים שמאלה, אל העבר. בשתיים השתמשו לפני הפניה אחת, בשש לפני שתיים, ובארבע לפני שלוש."),
    P("השימוש האחרון ב-4 הוא הוותיק ביותר. לכן 4 הוא הקורבן. וזה גם בדיוק השמאלי ברשימה.",
      do=show("t-vk-5") + T.col(5), say="השימוש האחרון בארבע הוא הוותיק ביותר. לכן ארבע הוא הקורבן. וזה גם בדיוק השמאלי ברשימה."),
    P("והתמורה מגיעה מיד: דף 2 שוב. ב-FIFO זו הייתה שגיאה, וכאן זו פגיעה.",
      do=hide("t-rr-4", "t-rr-3", "t-rr-2", "t-hl-5", "t-vk-5") + T.col(6) + show("r-c1"),
      say="והתמורה מגיעה מיד: דף שתיים שוב. בפִיפוֹ זו הייתה שגיאה, וכאן זו פגיעה."),
    P("דף 3: שגיאה. השמאלי ברשימה הוא 6, ובו השתמשו הכי מזמן. 6 יוצא.", do=T.col(7),
      say="דף שלוש: שגיאה. השמאלי ברשימה הוא שש, ובו השתמשו הכי מזמן. שש יוצא."),
    P("דף 5: פגיעה, והוא עובר לסוף.", do=T.col(8), say="דף חמש: פגיעה, והוא עובר לסוף."),
    P("ודף 4: שגיאה. השמאלי עכשיו הוא 2, אז 2 יוצא.", do=T.col(9), say="ודף ארבע: שגיאה. השמאלי עכשיו הוא שתיים, אז שתיים יוצא."),
    P("סך הכול שש שגיאות. אחת פחות מ-FIFO על אותה מחרוזת.", do=show("r-c2")),
    P("אבל זה לא כלל: יש מחרוזות שבהן LRU דווקא מקבל יותר שגיאות. כאן ההנחה על העבר פשוט עבדה.", hold=0.4),
], stage=T.html,
   panel=st.card("r-c1", "ex", "הפניה 5: FIFO מפנה 2, LRU מפנה 4")
         + st.card("r-c2", "rule", "🔑 LRU: <b>6</b> שגיאות, FIFO: 7")
         + st.card("r-c3", "plain", "מסתכלים <b>שמאלה</b>: השימוש האחרון הוותיק ביותר"))

cost = Scene("cost", "המחיר", [
    P("LRU מדויק דורש לעדכן את הרשימה ב**כל** גישה לזיכרון. לא רק בשגיאה, גם בכל פגיעה.", do=show("c-1")),
    P("ומעבד ניגש לזיכרון מיליוני פעמים בשנייה, ולכן עבודה נוספת בכל גישה יקרה מדי.", do=show("c-2")),
    P("לכן מערכות אמיתיות רק **מקרבות** את LRU, בעזרת ביט אחד לכל דף. זה אלגוריתם Clock, שנראה ברמה שש.",
      do=show("c-3"), hold=0.4),
], stage=w.stack(w.row("c-1", "LRU מדויק: עדכון ב<b>כל</b> גישה לזיכרון", cls="big"),
                 w.row("c-2", "פגיעה = גם עבודה"),
                 st.card("c-3", "rule", "🔑 בפועל: קירוב עם <b>reference bit</b> (Clock)"), gap=36))

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: ציינו אלגוריתם החלפת דפים שלמדנו, שהסיבוכיות שלו בכל פנייה לזיכרון היא $O(\\log n)$.",
      say="שאלה ממבחן: ציינו אלגוריתם החלפת דפים שלמדנו, שהסיבוכיות שלו בכל פנייה לזיכרון היא סדר גודל של לוג אֶן."),
    P("שימו לב למילים: **בכל פנייה לזיכרון**. כלומר אלגוריתם שעושה עבודה גם בפגיעה, כמו LRU.", do=show("x-1")),
    P("LRU נשמע מתאים, אבל התשובה שהמבחן מצפה לה היא LFU, כי אצלו הלוג בא ממבנה נתונים מוכר: ערימה.",
      say="אֶל אַר יוּ נשמע מתאים, אבל התשובה שהמבחן מצפה לה היא אֶל אֶף יוּ, כי אצלו הלוג בא ממבנה נתונים מוכר: ערימה."),
    P("LFU הם ראשי התיבות של Least Frequently Used. הוא מפנה את הדף שהשתמשו בו **הכי מעט פעמים**.",
      do=show("x-2"),
      say="אֶל אֶף יוּ הם ראשי התיבות של לִיסְט פְרִיקְוֶנְטְלִי יוּזְד. הוא מפנה את הדף שהשתמשו בו הכי מעט פעמים."),
    P("לכל דף יש מונה שימושים. בכל גישה המונה של הדף עולה באחת.", do=show("x-3")),
    P("הדפים שמורים בערימת מינימום לפי המונה, כך שהקורבן, המונה הקטן ביותר, תמיד בראש.", do=show("x-4")),
    P("כשמונה עולה, הדף מחלחל בערימה למקום החדש שלו. זה גובה הערימה: לוג אֶן.", do=show("x-5"),
      say="כשמונה עולה, הדף מחלחל בערימה למקום החדש שלו. זה גובה הערימה: סדר גודל של לוג אֶן."),
    P("והמלכודת: לא לבלבל עם Clock. שם מחפשים קורבן רק בשגיאה, ובמקרה הגרוע עוברים על כל המסגרות.",
      do=show("x-t")),
    P("התשובה: LFU, כי הדפים מסודרים בערימה.", do=show("x-a"), hold=0.5,
      say="התשובה: אֶל אֶף יוּ, כי הדפים מסודרים בערימה."),
], stage=w.stack(w.row("x-1", "עבודה ב<b>כל</b> פנייה לזיכרון"),
                 st.card("x-2", "rule", "🔑 LFU: מפנים את הדף עם <b>הכי מעט</b> שימושים"),
                 w.row("x-3", "גישה ← המונה של הדף עולה ב-1"),
                 w.row("x-4", "ערימת מינימום לפי המונה: הקורבן בראש"),
                 w.row("x-5", "עדכון בערימה: $O(\\log n)$", cls="big"),
                 st.card("x-t", "trap", "⚠️ לא Clock: הוא עובד רק בשגיאה"), gap=20),
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         + w.qans("x-a", f'<span class="k">תשובה:</span> {Q["answer_he"]}'))

recap = Scene("recap", "סיכום", [
    P("לסיכום: LRU מפנה את הדף שהשימוש האחרון בו הכי ותיק. מסתכלים שמאלה, אל העבר.", do=show("r-1")),
    P("פגיעה מרעננת את הדף ומעבירה אותו לסוף הרשימה. זה ההבדל מ-FIFO.", do=show("r-2")),
    P("LRU מדויק דורש עדכון בכל גישה, ולכן בפועל מקרבים אותו.", do=show("r-3")),
    P("ברמה הבאה: אלגוריתם שמסתכל ימינה, אל העתיד. נתראה.", do=show("r-4"), hold=0.6),
], stage=w.stack(w.queue("r-0", [". . ."], left="ישן", right="טרי", hidden=False),
                 w.row("r-00", "פגיעה: הדף עובר לימין. קורבן: השמאלי", hidden=False)),
   panel=st.card("r-1", "rule", "🔑 LRU = השימוש האחרון הוותיק ביותר")
         + st.card("r-2", "trap", "⚠️ פגיעה מרעננת (לא כמו FIFO)")
         + st.card("r-3", "rule", "🔑 מדויק = עדכון בכל גישה")
         + st.card("r-4", "ex", "הבא: האלגוריתם האופטימלי"))

VIDEO = Video("V03", "vmem", "החלפת דפים LRU", [title, idea, run, cost, exam, recap], bank={"2015B-7": None})
