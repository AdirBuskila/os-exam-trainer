# -*- coding: utf-8 -*-
"""P06 · מי עושה מה: MMU, TLB, PTBR, PCB — video script (build: tools/video/vid.py P06).

Source: src/courses/paging.py level 6 (lesson + goal: the hardware and kernel pieces of address translation: the
MMU translates on every access, the TLB caches translations, the PTBR points to the running process's page table,
one per core, and changes on a context switch; the PCB keeps the table's address while the process is not running;
a valid bit that is off makes the MMU trap to the OS).
Exam anchor: 2017A-7 (translation is done by the MMU and not by the OS because the MMU ____). The official answer
("היא חומרה שלא תלויה במעבד") is loose; the bank note gives the real reason (the MMU runs on every memory access,
far faster than trapping to the OS each time). The video shows the official answer and says so.
Avoided on purpose: the P06 quiz items (2019A-6, 2017SB-1, 2021A-9, 2019B-2, 2023A-7, 2017SB-7) are not shown as
exam questions; 2022A-8 (a twin of 2023A-7) is not used.
The one translation shown (page 6 -> frame 13, 1 KB pages, address 6500) is computed with sims.translate.
"""
import re
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_paging as w

# ---------------------------------------------------------------- numbers (verified)
PS = 1024
TA = {5: 2, 6: 13, 7: None}
VA = 6500
PG, OF = w.split(VA, PS)
PA = w.translate(VA, PS, TA)
assert (PG, OF, PA) == (6, 356, 13 * 1024 + 356) and PA == 13668
assert w.translate(7300, PS, TA) == "fault" and w.split(7300, PS)[0] == 7

Q = BANK["2017A-7"]
assert Q["answer_he"] == "היא חומרה שלא תלויה במעבד" and "every memory access" in Q["note"]


# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בתרגום כתובת משתתפים כמה רכיבים. חלקם חומרה, וחלקם מבנים של מערכת ההפעלה."),
    P("בסרטון הזה נעשה סדר: מה עושים ה-MMU, ה-TLB, ה-PTBR וה-PCB, ומתי כל אחד נכנס לפעולה.", hold=0.4),
], stage='<div class="kicker">P06 · דפדוף ותרגום כתובות</div><h1>מי עושה מה: MMU, TLB, PTBR, PCB</h1>'
         '<p>רכיבי החומרה והליבה בתרגום כתובות, ומה משתנה בהחלפת הקשר.</p>', layout="title")

pieces = Scene("pieces", "הרכיבים", [
    P("נתחיל במפה. משמאל המעבד, עם ליבה אחת. מימין למעלה ה-RAM, ולמטה מבנים של הקרנל.", do=show("m")),
    P("ה-MMU: החומרה שמתרגמת כתובת וירטואלית לפיזית, בכל גישה לזיכרון.", do=show("c-1")),
    P("ה-TLB: מטמון של תרגומים. כשיש בו פגיעה, מתרגמים בלי לגשת לזיכרון בכלל.", do=show("c-2")),
    P("ה-PTBR: אוגר שמצביע על טבלת הדפים של התהליך שרץ עכשיו.", do=show("m-a0A", "c-3")),
    P("טבלאות הדפים עצמן יושבות ב-RAM. לכל תהליך טבלה משלו.", do=show("c-4")),
    P("וה-PCB: המבנה שבו הקרנל שומר כל מה שצריך כדי להמשיך תהליך, כולל הכתובת של טבלת הדפים שלו.",
      do=show("c-5"), hold=0.4),
], stage=w.machine("m", hidden=True),
   panel=st.card("c-1", "ex", "<b>MMU</b>: מתרגם, בכל גישה")
         + st.card("c-2", "ex", "<b>TLB</b>: מטמון תרגומים")
         + st.card("c-3", "ex", "<b>PTBR</b>: מצביע לטבלה של התהליך הרץ")
         + st.card("c-4", "ex", "<b>page table</b>: ב-RAM, אחת לכל תהליך")
         + st.card("c-5", "ex", "<b>PCB</b>: שומר את כתובת הטבלה"))

access = Scene("access", "גישה אחת", [
    P("נעקוב אחרי גישה אחת. התהליך ניגש לכתובת וירטואלית 6500, והדפים בגודל קילובייט.", do=show("a-0"),
      say="נעקוב אחרי גישה אחת. התהליך ניגש לכתובת וירטואלית שש אלף וחמש מאות, והדפים בגודל קילובייט."),
    P("ה-MMU מפצל: דף שש, offset שלוש מאות חמישים ושש. ובודק קודם ב-TLB.", do=show("a-1")),
    P("נניח שהחטאנו. ה-MMU לוקח מה-PTBR את כתובת הטבלה, וקורא ממנה את השורה של דף שש.", do=show("a-2")),
    P("השורה תקפה: מסגרת שלוש עשרה. הכתובת הפיזית היא 13668, וה-TLB שומר את התרגום לפעם הבאה.", do=show("a-3"),
      say="השורה תקפה: מסגרת שלוש עשרה. הכתובת הפיזית היא שלושה עשר אלף שש מאות שישים ושמונה, והטִי אֶל בִּי שומר את התרגום לפעם הבאה."),
    P("כל זה קרה בחומרה. מערכת ההפעלה בכלל לא ידעה שהייתה גישה.", do=show("a-c1")),
    P("ואם השורה לא תקפה? למשל דף שבע. אז ה-MMU לא יכול להמשיך לבד.", do=show("a-4")),
    P("הוא רק מפסיק, וקורא למערכת ההפעלה: page fault.", do=show("a-c2"),
      hold=0.4),
], stage=w.stack(w.page_table("at", TA), w.row("a-0", "כתובת " + w.mono("6500") + ", דף " + w.ltr("1KB")),
                 w.row("a-1", "דף 6, " + w.ltr("offset 356") + ". בודקים ב-TLB", cls="sm"),
                 w.row("a-2", "החטאה ← PTBR ← השורה של דף 6", cls="sm"),
                 w.row("a-3", w.ltr("13 · 1024 + 356 = 13668"), cls="sm"),
                 w.row("a-4", "דף 7: " + w.ltr("valid = 0") + " ← " + w.ltr("page fault"), cls="sm"), gap=18),
   panel=st.card("a-c1", "rule", "🔑 התרגום נעשה <b>בחומרה</b>, בלי מערכת ההפעלה")
         + st.card("a-c2", "rule", "🔑 valid כבוי: ה-MMU רק קורא למערכת ההפעלה"))
access.phrases[2].do += show("at-hi6")
access.phrases[5].do += hide("at-hi6") + show("at-hi7")

switch = Scene("switch", "החלפת הקשר", [
    P("עכשיו החלפת הקשר: הליבה מפסיקה להריץ את תהליך A, ועוברת לתהליך B.", do=show("s")),
    P("ה-PTBR מצביע עכשיו על הטבלה של A. מערכת ההפעלה שומרת את הערך הזה ב-PCB של A.",
      do=show("s-a0A", "s-sv", "w-1")),
    P("אחר כך היא טוענת ל-PTBR את הכתובת ששמורה ב-PCB של B.", do=show("s-ld", "w-2")),
    P("ומעכשיו ה-PTBR מצביע על הטבלה של B. כל כתובת של B תתורגם לפי הטבלה שלו.",
      do=hide("s-a0A", "s-sv", "s-ld") + show("s-a0B", "w-3")),
    P("והתרגומים שב-TLB? הם שייכים ל-A, ולכן בדרך כלל מרוקנים אותו בהחלפת הקשר.", do=show("w-4")),
    P("כלומר ה-PTBR משתנה בהחלפת הקשר.", do=show("w-c1"), hold=0.4),
], stage=w.machine("s", hidden=True),
   panel=st.card("w-1", "ex", "1. PTBR ← נשמר ב-PCB של A")
         + st.card("w-2", "ex", "2. PCB של B ← נטען ל-PTBR")
         + st.card("w-3", "ex", "3. התרגום לפי הטבלה של B")
         + st.card("w-4", "ex", "4. ה-TLB בדרך כלל מתרוקן")
         + st.card("w-c1", "rule", "🔑 PTBR משתנה <b>בהחלפת הקשר</b>"))

cores = Scene("cores", "PTBR לכל ליבה", [
    P("ומה במעבד עם שתי ליבות? כל ליבה מריצה תהליך אחר באותו רגע.", do=show("n")),
    P("לכן לכל ליבה יש MMU, TLB ו-PTBR משלה.", do=show("k-1")),
    P("ה-PTBR של הליבה הראשונה מצביע על הטבלה של A, וזה של השנייה על הטבלה של B.", do=show("n-a0A", "n-a1B")),
    P("ליבה מריצה תהליך אחד בכל רגע, ולכן היא צריכה בדיוק PTBR אחד.", do=show("k-c1")),
    P("את הכתובות של כל שאר הטבלאות שומרים ב-PCB של כל תהליך, עד שיגיע תורו.", do=show("k-c2"), hold=0.4),
], stage=w.machine("n", cores=2, hidden=True),
   panel=st.card("k-1", "ex", "לכל ליבה: MMU, TLB, PTBR")
         + st.card("k-c1", "rule", "🔑 PTBR <b>אחד</b> לכל ליבה")
         + st.card("k-c2", "rule", "🔑 תהליך שלא רץ: כתובת הטבלה ב-PCB"))

exam = Scene("exam", "שאלה ממבחן", [
    P("ועכשיו שאלה ממבחן: תרגום כתובות נעשה על ידי ה-MMU ולא על ידי מערכת ההפעלה, כי ה-MMU... מה?"),
    P("נחשוב: התרגום קורה בכל גישה לזיכרון. בכל פקודה, לפעמים כמה פעמים.", do=show("x-1")),
    P("אם מערכת ההפעלה הייתה מתרגמת, כל גישה הייתה קוראת לה, עם מעבר לקרנל. זה איטי בהרבה מהגישה עצמה.",
      do=show("x-2")),
    P("ה-MMU הוא חומרה, ועושה את התרגום תוך כדי הגישה, כמעט בלי לעלות זמן.", do=show("x-3")),
    P("התשובה הרשמית: „היא חומרה שלא תלויה במעבד“.", do=show("x-ans")),
    P("שימו לב, הניסוח הרשמי רופף. הסיבה האמיתית היא מהירות: חומרה שרצה בכל גישה, בלי לקרוא למערכת ההפעלה.",
      do=show("x-n")),
    P("ובמבחן כתבו את התשובה הרשמית, והוסיפו את הסיבה: התרגום בחומרה קורה בכל גישה, בלי לקרוא למערכת ההפעלה.", hold=0.5),
], stage=w.stack(w.row("x-1", "תרגום: בכל גישה לזיכרון"),
                 w.row("x-2", "דרך מערכת ההפעלה: קריאה לקרנל בכל גישה ✗"),
                 w.row("x-3", "MMU: חומרה, תוך כדי הגישה ✓"),
                 st.card("x-n", "trap", "⚠️ הניסוח הרשמי רופף: הסיבה האמיתית היא <b>מהירות</b>"), gap=32),
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         + w.qans("x-ans", Q["answer_he"]))

recap = Scene("recap", "סיכום", [
    P("לסיכום: ה-MMU מתרגם בחומרה, בכל גישה.", do=show("r-1")),
    P("ה-TLB שומר תרגומים, ובפגיעה התרגום מגיע ישר מהמטמון.", do=show("r-2")),
    P("ה-PTBR מצביע על הטבלה של התהליך הרץ: אחד לכל ליבה, ומשתנה בהחלפת הקשר.", do=show("r-3")),
    P("ה-PCB שומר את כתובת הטבלה כשהתהליך לא רץ. וביט valid כבוי: page fault. נתראה ברמה הבאה.", do=show("r-4"),
      hold=0.6),
], stage=w.stack(w.machine("z").replace('id="z-a0A" class="pg-ah h"', 'id="z-a0A" class="pg-ah"'), gap=10),
   panel=st.card("r-1", "rule", "🔑 MMU: מתרגם בחומרה")
         + st.card("r-2", "rule", "🔑 TLB: מטמון תרגומים")
         + st.card("r-3", "rule", "🔑 PTBR: אחד לכל ליבה, משתנה בהחלפת הקשר")
         + st.card("r-4", "rule", "🔑 PCB: כתובת הטבלה כשלא רץ"))

# process names A / B are read as letters (a lexicon entry for a lone capital would hit every word)
for _S in (switch, cores):
    for _p in _S.phrases:
        if _p.say_override is None and re.search(r"\b[AB]\b", _p.sub):
            _p.say_override = re.sub(r"\b[AB]\b", lambda m: {"A": "אֵיי", "B": "בִּי"}[m.group(0)], _p.sub)

VIDEO = Video("P06", "paging", "מי עושה מה: MMU, TLB, PTBR, PCB", [title, pieces, access, switch, cores, exam, recap],
              bank={"2017A-7": None})
