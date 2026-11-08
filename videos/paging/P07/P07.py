# -*- coding: utf-8 -*-
"""P07 · בוס: מבחן זיכרון — video script (build: tools/video/vid.py P07). Boss level: a walkthrough of exam items.

Source: src/courses/paging.py level 7 (boss: past-exam items on paging and translation).
Exam anchors (free memory items, none cited by any guided quiz, none in the boss quiz):
  part 1: 2014A-10 (the Linux call that attaches a shared-memory segment to the page tables: shmat) together with
          its pair 2014B-10 (the call that detaches it: shmdt);
  part 2: 2016A-7 (Linux divides a process's memory in two levels: pages below, segments above);
  part 3: 2020A-9 (the cache of the page table: TLB), with a TLB lookup worked on our own data.
Avoided on purpose: every boss-quiz item (2024A-7, 2024B-7, 2026A-8, 2017SA-8, 2021A-8, 2023A-7) and their
numbers; 2015B-6 (its numbers are those of a level-1 quiz question). The TLB lookups below use 1 KB pages and a
TLB of our own; each verdict and address is computed with sims.split_address / sims.translate.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_paging as w

# ---------------------------------------------------------------- numbers (verified)
Q1, Q2, Q3, Q4 = BANK["2014A-10"], BANK["2014B-10"], BANK["2016A-7"], BANK["2020A-9"]
assert (Q1["answer_he"], Q2["answer_he"], Q3["answer_he"], Q4["answer_he"]) == ("shmat", "shmdt", "Segments", "TLB")
assert all(q["section"] == "memory" for q in (Q1, Q2, Q3, Q4))

# part 1: the segment lives in frames 9 and 10; shmat maps it at the process's pages 4 and 5
BEFORE = {2: 7, 3: 1, 4: None, 5: None}
AFTER = {2: 7, 3: 1, 4: 9, 5: 10}
DETACHED = dict(BEFORE)
assert [p for p in AFTER if BEFORE[p] != AFTER[p]] == [4, 5] and DETACHED == BEFORE

# part 3: a TLB with three entries, the full table behind it, 1 KB pages
PS = 1024
TLB = {6: 13, 2: 3, 9: 0}
TABLE = {0: 8, 1: None, 2: 3, 3: 11, 6: 13, 9: 0}
assert all(TABLE[p] == f for p, f in TLB.items())               # the TLB only copies rows of the table
LOOK = []
for va in (6500, 9300, 3100):
    pg, of = w.split(va, PS)
    hit = pg in TLB
    pa = w.translate(va, PS, TABLE)
    assert pa != "fault" and pa == TABLE[pg] * PS + of
    LOOK.append((va, pg, of, hit, pa))
assert [(l[1], l[3]) for l in LOOK] == [(6, True), (9, True), (3, False)]
assert [l[4] for l in LOOK] == [13668, 84, 11292]

TLB_TAB = w.table("t-tlb", ["דף", "מסגרת"], [[str(p), str(f)] for p, f in TLB.items()], hidden=False,
                  ids=None, cls="")
LOOK_TAB = w.table("t-look", ["כתובת", "דף", "TLB", "פיזית"],
                   [[w.mono(va), str(pg), '<b class="pg-ok">hit</b>' if hit else '<b class="pg-bad">miss</b>', w.mono(pa)]
                    for va, pg, of, hit, pa in LOOK], hidden=False, ids=["t-l0", "t-l1", "t-l2"])

SEGS = [("stack", "#fb7185", 3), ("heap", "#fbbf24", 2), ("data", "#c084fc", 2), ("code", "#2dd4bf", 3)]


def seg_fig():
    """a process's address space, top = high addresses: four segments, each a run of pages (ids g-<name>)"""
    rows = []
    for name, col, n in SEGS:
        pages = "".join('<i class="pg-segp"></i>' for _ in range(n))
        rows.append(f'<div id="g-{name}" class="pg-seg h" style="border-color:{col}">'
                    f'<span class="pg-segn" style="color:{col}">{name}</span><span class="pg-segps">{pages}</span></div>')
        if name == "stack":
            rows.append('<div class="pg-seggap">⋮</div>')
    return f'<div class="pg-segs">{"".join(rows)}</div>'


# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("זה שלב הבוס של קורס הדפדוף. נפתור יחד שלוש שאלות ממבחנים קודמים."),
    P("זיכרון משותף וטבלאות הדפים, שתי הרמות של הזיכרון בלינוקס, וה-TLB. בכל אחת נראה למה התשובה נכונה.",
      hold=0.4),
], stage='<div class="kicker">P07 · דפדוף ותרגום כתובות</div><h1>בוס: מבחן זיכרון</h1>'
         '<p>שאלות מהמבחנים על דפדוף ותרגום: זיכרון משותף, סגמנטים ודפים, וה-TLB.</p>', layout="title")

shm = Scene("shm", "שאלה 1: זיכרון משותף", [
    P("שאלה ראשונה: מהי הפונקציה בלינוקס שמחברת סגמנט של זיכרון משותף לטבלאות הדפים של התהליך?"),
    P("נזכור איך זיכרון משותף עובד: הסגמנט יושב במסגרות ב-RAM, כאן מסגרות תשע ועשר.", do=show("h-0")),
    P("כדי שהתהליך יוכל לגשת אליו, צריך להוסיף לטבלת הדפים שלו שורות שמצביעות על המסגרות האלה.",
      do=show("h-a", "ha-hi4", "ha-hi5")),
    P("את זה עושה shmat, קיצור של attach: היא מחברת את הסגמנט, ומחזירה לתהליך את הכתובת הווירטואלית שלו.",
      do=show("x1-ans"), say="את זה עושה שֶׁם אַט, קיצור של אַטַאץ': היא מחברת את הסגמנט, ומחזירה לתהליך את הכתובת הווירטואלית שלו."),
    P("ואם שני תהליכים קוראים ל-shmat, אצל כל אחד מהם נוספות שורות שמצביעות על אותן מסגרות, ולא בהכרח באותם מספרי דפים.",
      say="ואם שני תהליכים קוראים לשֶׁם אַט, אצל כל אחד מהם נוספות שורות שמצביעות על אותן מסגרות, ולא בהכרח באותם מספרי דפים."),
    P("ובמבחן אחר נשאלה השאלה ההפוכה: איזו פונקציה **מנתקת** את הסגמנט מטבלאות הדפים?", do=show("x2-q")),
    P("זו shmdt, קיצור של detach. השורות נמחקות מהטבלה של התהליך.", do=show("h-d", "x2-ans"),
      say="זו שֶׁם דִי טִי, קיצור של דִיטַאץ'. השורות נמחקות מהטבלה של התהליך."),
    P("המלכודת: לחשוב ש-shmdt מוחקת את הסגמנט. היא רק מנתקת אותו מהתהליך הזה. המחיקה היא shmctl עם IPC_RMID.",
      do=show("h-t"), hold=0.4, say="המלכודת: לחשוב ששֶׁם דִי טִי מוחקת את הסגמנט. היא רק מנתקת אותו מהתהליך הזה. המחיקה היא שֶׁם קוֹנְטְרוֹל עם אַיי פִּי סִי רֶם אַיי דִי."),
], stage=w.stack(w.row("h-0", "הסגמנט: מסגרות " + w.mono("9, 10"), cls="sm"),
                 f'<div class="pg-chain" style="gap:50px;align-items:flex-start">'
                 f'<div class="pg-stack" style="gap:8px"><div class="pg-row sm">לפני</div>{w.page_table("hb", BEFORE)}</div>'
                 f'<div id="h-a" class="h pg-stack" style="gap:8px"><div class="pg-row sm">אחרי shmat</div>{w.page_table("ha", AFTER)}</div>'
                 f'<div id="h-d" class="h pg-stack" style="gap:8px"><div class="pg-row sm">אחרי shmdt</div>{w.page_table("hd", DETACHED)}</div></div>',
                 st.card("h-t", "trap", "⚠️ shmdt רק מנתק. מחיקה: " + w.mono("shmctl(…, IPC_RMID, …)")), gap=24),
   panel=f'<div class="qstem pg-qsm"><span class="qid">{Q1["id"]}</span>{Q1["he"]}</div>'
         + w.qans("x1-ans", w.mono("shmat"))
         + f'<div id="x2-q" class="qstem pg-qsm h"><span class="qid">{Q2["id"]}</span>{Q2["he"]}</div>'
         + w.qans("x2-ans", w.mono("shmdt")))

segs = Scene("segs", "שאלה 2: סגמנטים ודפים", [
    P("שאלה שנייה: בלינוקס יש שתי רמות בחלוקת הזיכרון של תהליך. הרמה הנמוכה היא דפים. מהי הרמה הגבוהה?"),
    P("נסתכל על מרחב הכתובות של תהליך. הוא לא גוש אחד: יש בו אזורים עם תפקידים שונים.", do=show("g-code")),
    P("הקוד, הנתונים, הערימה שגדלה עם הקצאות, והמחסנית.", do=show("g-data", "g-heap", "g-stack")),
    P("כל אזור כזה נקרא **סגמנט**, ולכל סגמנט הרשאות משלו. למשל את הקוד אפשר לקרוא ולהריץ, אבל לא לכתוב.",
      do=show("y-c1")),
    P("וכל סגמנט בנוי מדפים שלמים, שממופים בטבלת הדפים כמו שראינו כל הקורס.", do=show("y-c2")),
    P("לכן התשובה היא segments: סגמנטים למעלה, ודפים מתחתם.", do=show("x3-ans"),
      say="לכן התשובה היא סֶגְמֶנְטְס: סגמנטים למעלה, ודפים מתחתם."),
    P("וזה גם מסביר את השאלה מסרטון שלוש: גישה לכתובת שלא שייכת לאף סגמנט גורמת ל-segmentation fault.",
      do=show("y-c3"), hold=0.4, say="וזה גם מסביר את השאלה מסרטון שלוש: גישה לכתובת שלא שייכת לאף סגמנט גורמת לסֶגְמֶנְטֵיישֶׁן פוֹלְט."),
], stage=w.stack(seg_fig(), gap=10),
   panel=f'<div class="qstem pg-qsm"><span class="qid">{Q3["id"]}</span>{Q3["he"]}</div>'
         + w.qans("x3-ans", w.ltr("Segments") + " (סגמנטים)")
         + st.card("y-c1", "ex", "סגמנט: אזור עם תפקיד והרשאות")
         + st.card("y-c2", "rule", "🔑 סגמנט = רצף של דפים")
         + st.card("y-c3", "trap", "⚠️ מחוץ לכל סגמנט ← segmentation fault"))

tlb = Scene("tlb", "שאלה 3: המטמון", [
    P("שאלה שלישית, קצרה: כיצד נקרא המטמון של טבלת הדפים?"),
    P("התשובה: TLB.", do=show("x4-ans")),
    P("אבל בואו נוודא שאנחנו מבינים מה יש בו. זה TLB עם שלוש שורות, והדפים בגודל קילובייט.", do=show("t-a")),
    P("כתובת 6500: דף שש. הוא ב-TLB, פגיעה. מסגרת שלוש עשרה, והכתובת הפיזית 13668.", do=show("t-l0"),
      say="כתובת שש אלף וחמש מאות: דף שש. הוא בטִי אֶל בִּי, פגיעה. מסגרת שלוש עשרה, והכתובת הפיזית שלושה עשר אלף שש מאות שישים ושמונה."),
    P("כתובת 9300: דף תשע, גם הוא ב-TLB. מסגרת אפס, ולכן הכתובת הפיזית היא פשוט ה-offset, 84.", do=show("t-l1"),
      say="כתובת תשעת אלפים ושלוש מאות: דף תשע, גם הוא בטִי אֶל בִּי. מסגרת אפס, ולכן הכתובת הפיזית היא פשוט האוֹפְסֶט, שמונים וארבע."),
    P("כתובת 3100: דף שלוש. הוא **לא** ב-TLB: החטאה. הולכים לטבלת הדפים ב-RAM, ושם הוא במסגרת אחת עשרה.",
      do=show("t-l2"), say="כתובת שלושת אלפים ומאה: דף שלוש. הוא לא בטִי אֶל בִּי: החטאה. הולכים לטבלת הדפים ברַאם, ושם הוא במסגרת אחת עשרה."),
    P("החטאה היא לא page fault! הדף בזיכרון, רק התרגום שלו לא היה במטמון.", do=show("t-t")),
    P("page fault קורה רק כשגם בטבלת הדפים ביט ה-valid כבוי.", hold=0.4),
], stage=w.stack(f'<div id="t-a" class="h pg-stack" style="gap:8px"><div class="pg-row sm">TLB</div>{TLB_TAB}</div>',
                 LOOK_TAB,
                 st.card("t-t", "trap", "⚠️ החטאת " + w.ltr("TLB") + " ≠ " + w.ltr("page fault")), gap=24),
   panel=f'<div class="qstem"><span class="qid">{Q4["id"]}</span>{Q4["he"]}</div>'
         + w.qans("x4-ans", "TLB"))

recap = Scene("recap", "סיכום הקורס", [
    P("וזה סוף הקורס. נעבור על כל מה שלמדנו, בשורה אחת לכל רמה."),
    P("כתובת היא מספר דף ו-offset, והביטים נספרים בחזקות של שתיים.", do=show("r-1")),
    P("טבלת הדפים מחליפה דף במסגרת, וה-offset נשאר. ביט valid כבוי: page fault.", do=show("r-2")),
    P("זיכרון ניתן בדפים שלמים, והבזבוז בדף האחרון הוא פיצול פנימי.", do=show("r-3")),
    P("טבלה רב-שלבית חוסכת זיכרון, ובהחטאה עולה גישה לכל שלב ועוד אחת.", do=show("r-4")),
    P("בפגיעת TLB התרגום מגיע מהמטמון, והזמן הממוצע הוא ממוצע משוקלל.", do=show("r-5")),
    P("וה-MMU מתרגם בחומרה, עם PTBR אחד לכל ליבה. בהצלחה במבחן!", do=show("r-6"), hold=0.6),
], stage=w.stack(w.big("r-f", r"\text{physical} = \text{frame} \cdot \text{page size} + \text{offset}", hidden=False, cls="sm"),
                 w.big("r-g", r"EAT = h \cdot \text{hit} + (1 - h) \cdot \text{miss}", hidden=False, cls="sm"), gap=50),
   panel=st.card("r-1", "rule", "🔑 כתובת = [ דף | offset ]")
         + st.card("r-2", "rule", "🔑 דף ← מסגרת, offset נשאר")
         + st.card("r-3", "rule", "🔑 דפים שלמים: פיצול פנימי")
         + st.card("r-4", "rule", "🔑 רב-שלבית: שלבים + 1")
         + st.card("r-5", "rule", "🔑 TLB ו-EAT")
         + st.card("r-6", "rule", "🔑 MMU, PTBR לכל ליבה"))

VIDEO = Video("P07", "paging", "בוס: מבחן זיכרון", [title, shm, segs, tlb, recap],
              bank={"2014A-10": None, "2014B-10": None, "2016A-7": None, "2020A-9": None})
