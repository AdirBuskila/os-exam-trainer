# -*- coding: utf-8 -*-
"""V01 · דפדוף לפי דרישה ושגיאות דף — video script (build: tools/video/vid.py V01).

Source: src/courses/vmem.py level 1 (lesson + goal: a page comes into RAM only when it is first touched; the page
fault in three steps: valid bit off -> MMU raises a page fault, the OS loads the page into a free frame, marks the
entry valid and the faulting instruction runs again; the dirty bit; Copy-on-Write; swap).
Exam anchor: 2021B-9 (open question: under demand paging a page is not loaded until ...), no guided quiz uses it.
Avoided on purpose: the level-1 quiz items (2016B-7, 2019B-7, 2019B-6, 2016A-8, 2015A-7, 2020A-10) are never asked
or answered as questions here; the page-fault items 2014A-7 and 2020B-10 are left for the V07 boss walkthrough, and
the address-translation items (2022A-8, TLB) for the paging course.
Worked example: our own reference string 3 0 3 3 5 0 3 with 4 free frames (no quiz uses it); its fault count comes
from sims.replace (through w_vmem.run) and is asserted to equal the number of distinct pages.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_vmem as w

# ---------------------------------------------------------------- numbers (verified)
REFS = [3, 0, 3, 3, 5, 0, 3]
TAB = w.rtable("t", REFS, 4, "FIFO", cw=96)
assert TAB.faults == len(set(REFS)) == 3                 # enough frames: one fault per distinct page, no eviction
assert all(s["victim"] is None for s in TAB.steps)
assert [s["fault"] for s in TAB.steps] == [True, True, False, False, True, False, False]
assert TAB.sim["hits"] == len(REFS) - 3 == 4

# the page-table walk of scene "fault": page 2 -> frame 0, page 4 -> frame 1, then page 2 again (a hit)
WALK = w.run([2, 4, 2], 4, "FIFO")["steps"]
assert [(s["page"], s["fault"], s["slot"]) for s in WALK] == [(2, True, 0), (4, True, 1), (2, False, None)]
PT = w.ptable("pt", 6, 4)
PT0 = w.ptable("pi", 6, 4).replace('class="vm-ptw"', 'class="vm-ptw h"', 1)

Q = BANK["2021B-9"]
assert Q["section"] == "memory" and "demand paging" in Q["he"] and "מבקשים" in Q["answer_he"]

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נראה איך דף מגיע ל-RAM רק ברגע שצריך אותו."),
    P("נעקוב אחרי page fault צעד אחרי צעד, ונספור שגיאות דף על מחרוזת הפניות."),
    P("ובסוף נפתור שאלה ממבחן על demand paging.", hold=0.4),
], stage='<div class="kicker">V01 · דפדוף לפי דרישה והחלפת דפים</div><h1>דפדוף לפי דרישה ושגיאות דף</h1>'
         '<p>דפים נכנסים ל-RAM רק כשניגשים אליהם: מה זו שגיאת דף, מה המערכת עושה בה, ולאן התהליך חוזר.</p>',
   layout="title")

idea = Scene("idea", "הרעיון", [
    P("תוכנית מחולקת לדפים, וכל הדפים שלה שמורים בדיסק."),
    P("ב-**demand paging**, דפדוף לפי דרישה, לא טוענים את כל התוכנית ל-RAM מראש.", do=show("i-c1")),
    P("דף מובא מהדיסק רק כשהתוכנית **ניגשת** אליו בפעם הראשונה.", do=show("i-c2")),
    P("חלקים שהתוכנית אף פעם לא נוגעת בהם, למשל קוד של טיפול בשגיאות נדירות, פשוט לא נטענים."),
    P("לכן תהליך חדש מתחיל כשאף דף שלו עוד לא ב-RAM.", do=show("pi")),
    P("בטבלת הדפים, ליד כל דף יש ביט **valid**. כרגע הוא כבוי בכל הכניסות.", do=show("i-c3")),
    P("ה-RAM מחולק למסגרות באותו גודל של דף. בדוגמה שלנו יש ארבע מסגרות, וכולן פנויות.", hold=0.3),
], stage=PT0,
   panel=st.card("i-c1", "plain", "לא טוענים את כל התוכנית מראש")
         + st.card("i-c2", "rule", "🔑 דף נטען רק בגישה <b>הראשונה</b> אליו")
         + st.card("i-c3", "ex", "תהליך חדש: כל ביטי ה-valid כבויים"))

fault = Scene("fault", "שגיאת דף", [
    P("עכשיו התוכנית ניגשת לכתובת שנמצאת בדף 2.", do=show("pt-hl-2")),
    P("ה-MMU, החומרה שמתרגמת כתובות, מסתכל בשורה של דף 2. ביט ה-valid כבוי.", do=show("f-1")),
    P("אז ה-MMU לא יכול לתרגם, והוא מעלה פסיקה: **page fault**, שגיאת דף.", do=show("f-2")),
    P("מערכת ההפעלה מקבלת את הפסיקה, ומוצאת מסגרת פנויה: מסגרת 0.", do=show("pt-fl-0")),
    P("היא קוראת את דף 2 מהדיסק אל המסגרת הזו. זו הפעולה האיטית: גישה לדיסק.", do=show("pt-ram-0-2", "f-3")),
    P("אחר כך היא מעדכנת את הטבלה: דף 2 נמצא במסגרת 0, וביט ה-valid נדלק.",
      do=show("pt-v1-2", "pt-f-2-0") + hide("pt-v0-2", "pt-fl-0")),
    P("ועכשיו הצעד שקל לשכוח: התהליך חוזר **לאותה הוראה** שגרמה לשגיאה, ומריץ אותה מחדש.", do=show("f-4")),
    P("למה? כי הגישה לזיכרון לא הושלמה. הפעם הדף כבר שם, והתרגום מצליח.", hold=0.3),
    P("ניגשים לדף 4: שוב valid כבוי, שוב page fault, והדף נטען למסגרת 1.",
      do=hide("pt-hl-2") + show("pt-hl-4", "pt-ram-1-4", "pt-v1-4", "pt-f-4-1") + hide("pt-v0-4")),
    P("ועכשיו שוב לדף 2. הפעם הביט דלוק, ה-MMU מתרגם מיד, ואין שום שגיאה.",
      do=hide("pt-hl-4") + show("pt-hl-2", "f-5"), hold=0.4),
], stage=PT,
   panel=st.card("f-1", "plain", "1. ה-MMU רואה valid = 0")
         + st.card("f-2", "trap", "2. פסיקה: <b>page fault</b>")
         + st.card("f-3", "plain", "3. המערכת קוראת את הדף מהדיסק למסגרת פנויה ומדליקה את valid")
         + st.card("f-4", "rule", "🔑 4. חוזרים <b>לאותה הוראה</b> ומריצים אותה שוב")
         + st.card("f-5", "ex", "גישה שנייה לאותו דף: אין שגיאה"))

count = Scene("count", "ספירת שגיאות", [
    P("את רצף הדפים שהתוכנית ניגשת אליהם קוראים **מחרוזת הפניות**. כאן: 3, 0, 3, 3, 5, 0, 3.",
      say="את רצף הדפים שהתוכנית ניגשת אליהם קוראים מחרוזת הפניות. כאן: שלוש, אפס, שלוש, שלוש, חמש, אפס, שלוש."),
    P("יש ארבע מסגרות פנויות. בכל עמודה נרשום מה יש במסגרות אחרי ההפניה.", do=show("c-c0")),
    P("דף 3: עוד לא ב-RAM. שגיאה ראשונה, והוא נכנס למסגרת הראשונה.", do=TAB.col(0)),
    P("דף 0: גם הוא חדש. שגיאה שנייה.", do=TAB.col(1)),
    P("שוב דף 3: הוא כבר במסגרת. זו **פגיעה**, hit, ואין שגיאה.", do=TAB.col(2),
      say="שוב דף שלוש: הוא כבר במסגרת. זו פגיעה, הִיט, ואין שגיאה."),
    P("ועוד פעם דף 3: שוב פגיעה.", do=TAB.col(3)),
    P("דף 5: חדש. שגיאה שלישית.", do=TAB.col(4)),
    P("דף 0 ודף 3: שניהם כבר בפנים. שתי פגיעות.", do=TAB.col(5, 6)),
    P("סך הכול שלוש שגיאות דף, וארבע פגיעות. שבע הפניות בסך הכול.", do=show("c-c1")),
    P("שימו לב: כשיש מספיק מסגרות, מספר השגיאות הוא פשוט מספר הדפים **השונים**.", do=show("c-c2")),
    P("כל דף גורם לשגיאה אחת, בגישה הראשונה שלו. כל גישה חוזרת היא פגיעה."),
    P("הבעיה מתחילה כשהמסגרות נגמרות. אז צריך לפנות דף, ועל זה שאר הקורס.", hold=0.4),
], stage=TAB.html,
   panel=st.card("c-c0", "plain", "F = שגיאת דף, ✓ = פגיעה")
         + st.card("c-c1", "ex", "3 שגיאות + 4 פגיעות = 7 הפניות")
         + st.card("c-c2", "rule", "🔑 מספיק מסגרות: שגיאות = מספר הדפים <b>השונים</b>"))

bits = Scene("bits", "dirty ו-swap", [
    P("לכל דף יש עוד ביט חשוב: ה-**dirty bit**.", do=show("b-1")),
    P("ה-MMU מדליק אותו כשכותבים לדף. הוא אומר: הדף השתנה מאז שנטען מהדיסק.", do=show("b-1a")),
    P("כשמפנים דף שה-dirty שלו דלוק, צריך קודם לכתוב אותו חזרה לדיסק. אחרת השינוי ילך לאיבוד.", do=show("b-1b")),
    P("ודף נקי? העותק בדיסק עדיין נכון, אז אפשר פשוט לדרוס את המסגרת. זה חוסך כתיבה."),
    P("ב-Linux, דפים שמפנים מה-RAM נשמרים באזור מיוחד בדיסק, שנקרא **swap partition**.", do=show("b-2")),
    P("ועוד מנגנון שחוסך העתקות הוא **Copy-on-Write**.", do=show("b-3")),
    P("תהליך בן חולק עם האב את המסגרות, ומקבל רק עותק של טבלאות הדפים.", do=show("b-3a")),
    P("דף מועתק רק כשמישהו **כותב** אליו, ורק הדף הזה.", do=show("b-3b"), hold=0.4),
], stage=w.stack(st.card("b-1", "rule", "🔑 <b>dirty bit</b>: הדף השתנה מאז שנטען")
                 + w.row("b-1a", "ה-MMU מדליק אותו בכתיבה")
                 + w.row("b-1b", "פינוי של דף dirty ← קודם כותבים אותו לדיסק"), gap=18),
   panel=st.card("b-2", "ex", "Linux: דפים שפונו נשמרים ב-<b>swap partition</b>")
         + st.card("b-3", "rule", "🔑 <b>Copy-on-Write</b>")
         + st.card("b-3a", "plain", "הבן חולק את המסגרות של האב")
         + st.card("b-3b", "plain", "כתיבה ראשונה לדף ← מעתיקים רק אותו"))

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: במערכת שעובדת לפי demand paging, דף לא נטען מהדיסק לזיכרון עד ש... מה?"),
    P("נחזור למה שראינו: הדף נטען בתוך הטיפול ב-page fault.", do=show("x-1")),
    P("ו-page fault קורה כשהתוכנית ניגשת לכתובת בדף, וביט ה-valid של הדף כבוי.", do=show("x-2")),
    P("כלומר, הדף נטען רק כשמבקשים ממנו נתון כלשהו. קריאה, כתיבה, או הבאת הוראה מהקוד.", do=show("x-3")),
    P("המלכודת: לא כשהתהליך מתחיל, ולא כשיש מסגרת פנויה. מסגרת פנויה לבד לא מביאה שום דף.", do=show("x-t")),
    P("התשובה הרשמית: עד שמבקשים נתון כלשהו מהדף.", do=show("x-a"), hold=0.5),
], stage=w.stack(w.row("x-1", "הדף נטען בטיפול ב-<b>page fault</b>"),
                 w.row("x-2", "page fault = גישה לדף עם valid = 0"),
                 w.row("x-3", "← נטען רק כשמבקשים ממנו נתון", cls="big"),
                 st.card("x-t", "trap", "⚠️ לא בתחילת התהליך, ולא כי יש מסגרת פנויה"), gap=26),
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         + w.qans("x-a", f'<span class="k">תשובה:</span> {Q["answer_he"]}'))

recap = Scene("recap", "סיכום", [
    P("לסיכום: דף נטען ל-RAM רק בגישה הראשונה אליו. תהליך חדש מתחיל בלי אף דף תקף.", do=show("r-1")),
    P("גישה לדף עם valid כבוי: ה-MMU מעלה page fault, והמערכת טוענת את הדף למסגרת.", do=show("r-2")),
    P("אחרי הטיפול חוזרים לאותה הוראה ומריצים אותה מחדש.", do=show("r-3")),
    P("ו-dirty אומר שצריך לכתוב את הדף חזרה לפני פינוי. ברמה הבאה: מה עושים כשהמסגרות נגמרות.",
      do=show("r-4"), hold=0.6),
], stage=w.stack(w.row("r-0", "גישה ← valid? ← page fault ← טעינה ← <b>אותה הוראה שוב</b>", hidden=False, cls="big")),
   panel=st.card("r-1", "rule", "🔑 נטען רק בגישה הראשונה")
         + st.card("r-2", "rule", "🔑 valid = 0 ← page fault")
         + st.card("r-3", "rule", "🔑 חוזרים להוראה <b>שגרמה</b> לשגיאה")
         + st.card("r-4", "trap", "⚠️ dirty ← כותבים לדיסק לפני פינוי"))

VIDEO = Video("V01", "vmem", "דפדוף לפי דרישה ושגיאות דף", [title, idea, fault, count, bits, exam, recap],
              bank={"2021B-9": None})
