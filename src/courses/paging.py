# -*- coding: utf-8 -*-
"""Course 2: paging and address translation."""
from _kit import Q, Lv, Course


def C(expr, fmt="num", want=None):
    d = dict(k="calc", v=expr, fmt=fmt)
    if want is not None:
        d["want"] = want
    return d


def A(ask, vaddr, size, table=None, want=None):
    d = dict(k="addr", ask=ask, vaddr=vaddr, page_size=size, table=table or {})
    if want is not None:
        d["want"] = want
    return d


def ptc(table):
    rows = ["Page  Frame"]
    for p in sorted(table):
        rows.append("%-6d%s" % (p, "-  (invalid)" if table[p] is None else table[p]))
    return "\n".join(rows)


PT = {0: 5, 1: 2, 2: 7, 3: None}

# ------------------------------------------------------------------ level 1
L1 = Lv(
    ("Pages, frames and the address split", "דפים, מסגרות ופיצול הכתובת"),
    ("Cut an address into page number and offset.", "לחתוך כתובת למספר דף והיסט."),
    ("""
<p>Virtual memory is cut into equal blocks called <b>pages</b>; physical memory (RAM) is cut into blocks of the same size called <b>frames</b>. A virtual address has two parts: the <b>page number</b> and the <b>offset</b> inside the page.</p>
<pre>virtual address = [ page number | offset ]
page size = 2^k bytes  ->  offset = k bits
page number bits = address bits - k</pre>
<table>
<tr><th>Page size</th><th>k</th></tr>
<tr><td>1 KB</td><td>10</td></tr>
<tr><td>4 KB</td><td>12</td></tr>
<tr><td>1 MB</td><td>20</td></tr>
</table>
<p>Counting is just powers of two: with <code>v</code> virtual bits there are 2^(v&minus;k) pages, and with <code>p</code> physical bits there are 2^(p&minus;k) frames. A single-level page table has one entry per page.</p>
<p>To split a decimal address: <b>page = address div page size</b>, <b>offset = address mod page size</b>.</p>
""", """
<p>הזיכרון הווירטואלי מחולק לבלוקים שווים שנקראים <b>דפים (pages)</b>; הזיכרון הפיזי (RAM) מחולק לבלוקים באותו גודל שנקראים <b>מסגרות (frames)</b>. לכתובת וירטואלית שני חלקים: <b>מספר הדף</b> וה<b>היסט (offset)</b> בתוך הדף.</p>
<pre>virtual address = [ page number | offset ]
page size = 2^k bytes  ->  offset = k bits
page number bits = address bits - k</pre>
<table>
<tr><th>גודל דף</th><th>k</th></tr>
<tr><td>1 KB</td><td>10</td></tr>
<tr><td>4 KB</td><td>12</td></tr>
<tr><td>1 MB</td><td>20</td></tr>
</table>
<p>הספירה היא רק חזקות של 2: עם <code>v</code> ביטים וירטואליים יש 2^(v&minus;k) דפים, ועם <code>p</code> ביטים פיזיים יש 2^(p&minus;k) מסגרות. בטבלת דפים חד-שלבית יש כניסה אחת לכל דף.</p>
<p>כדי לפצל כתובת עשרונית: <b>דף = כתובת div גודל דף</b>, <b>היסט = כתובת mod גודל דף</b>.</p>
"""),
    [
        Q(("Pages are 4 KB. How many bits does the **offset** use?", "הדפים בגודל 4 KB. כמה ביטים תופס ה**היסט**?"),
          ["12", "20", "4", "10"],
          ("4 KB = 2^12 bytes, so 12 bits address a byte inside a page.", "4 KB = 2^12 בתים, לכן 12 ביטים מכתיבים בית בתוך דף."),
          ("4 KB page = 12 offset bits.", "דף של 4 KB = 12 ביטי היסט."),
          check=C("log2(4096)")),
        Q(("A virtual address has 32 bits and pages are 4 KB. How many bits are the **page number**?",
           "לכתובת וירטואלית 32 ביטים והדפים בגודל 4 KB. כמה ביטים הם **מספר הדף**?"),
          ["20", "12", "32", "10"],
          ("32 − 12 = 20 bits for the page number.", "32 − 12 = 20 ביטים למספר הדף."),
          ("Page bits = address bits − offset bits.", "ביטי דף = ביטי כתובת − ביטי היסט."),
          check=C("32-log2(4096)")),
        Q(("A 36-bit virtual address and 4 KB pages. How many entries does a single-level page table have?",
           "כתובת וירטואלית של 36 ביטים ודפים של 4 KB. כמה כניסות יש בטבלת דפים חד-שלבית?"),
          ["2^24", "2^36", "2^12", "2^48"],
          ("One entry per page: 2^(36−12) = 2^24.", "כניסה אחת לכל דף: 2^(36−12) = 2^24."),
          ("Entries = 2^(virtual bits − offset bits).", "כניסות = 2^(ביטים וירטואליים − ביטי היסט)."),
          check=C("2**(36-log2(4096))", fmt="pow2")),
        Q(("A 42-bit virtual address, page size 1 MB. How many potential frames?",
           "כתובת וירטואלית של 42 ביטים, גודל דף 1 MB. כמה מסגרות פוטנציאליות?"),
          ["2^22", "2^42", "2^20", "2^21"],
          ("1 MB = 2^20, so 42 − 20 = 22 bits: 2^22.", "1 MB = 2^20, לכן 42 − 20 = 22 ביטים: 2^22."),
          ("Count = 2^(address bits − log2 page size).", "מספר = 2^(ביטי כתובת − log2 גודל דף)."),
          check=C("2**(42-log2(2**20))", fmt="pow2"), exam="2024A-7", has="22"),
        Q(("Pages are 4096 bytes. In which page and at which offset is virtual address 13000?",
           "הדפים בגודל 4096 בתים. באיזה דף ובאיזה היסט נמצאת הכתובת הווירטואלית 13000?"),
          ["Page 3, offset 712", "Page 3, offset 4096", "Page 13, offset 0", "Page 4, offset 712"],
          ("13000 div 4096 = 3 and 13000 mod 4096 = 13000 − 12288 = 712.", "13000 div 4096 = 3 ו-13000 mod 4096 = 13000 − 12288 = 712."),
          ("page = div, offset = mod.", "דף = div, היסט = mod."),
          check=[A("page", 13000, 4096, want="3"), A("offset", 13000, 4096, want="712")]),
    ], icon="🧩")

# ------------------------------------------------------------------ level 2
L2 = Lv(
    ("Translating an address with a page table", "תרגום כתובת בעזרת טבלת דפים"),
    ("Page number to frame number, offset unchanged.", "ממספר דף למספר מסגרת, וההיסט נשאר."),
    ("""
<p>The page table maps each page number to a frame number. Translation changes only the page part; the <b>offset never changes</b>.</p>
<pre>physical address = frame * page size + offset

page size 1024, page 2 -> frame 7, virtual address 2100
page   = 2100 div 1024 = 2
offset = 2100 mod 1024 = 52
physical = 7 * 1024 + 52 = 7220</pre>
<p>Every page-table entry has a <b>valid-invalid bit</b>. If it says invalid (the page is not in RAM), the MMU raises a <b>page fault</b> instead of producing an address, and the OS must bring the page in.</p>
""", """
<p>טבלת הדפים ממפה כל מספר דף למספר מסגרת. התרגום משנה רק את חלק הדף; ה<b>היסט אף פעם לא משתנה</b>.</p>
<pre>physical address = frame * page size + offset

page size 1024, page 2 -> frame 7, virtual address 2100
page   = 2100 div 1024 = 2
offset = 2100 mod 1024 = 52
physical = 7 * 1024 + 52 = 7220</pre>
<p>בכל כניסה בטבלת הדפים יש <b>ביט תקף-לא תקף (valid-invalid)</b>. אם הוא מציין לא תקף (הדף לא נמצא ב-RAM), ה-MMU מעלה <b>שגיאת דף (page fault)</b> במקום להפיק כתובת, והמערכת צריכה להביא את הדף.</p>
"""),
    [
        Q(("Page size 1024. What physical address does virtual address 2100 map to?", "גודל דף 1024. לאיזו כתובת פיזית ממופה הכתובת הווירטואלית 2100?"),
          ["7220", "2100", "5172", "7168"],
          ("Page 2, offset 52. Page 2 sits in frame 7: 7 × 1024 + 52 = 7220.", "דף 2, היסט 52. דף 2 נמצא במסגרת 7: 7 × 1024 + 52 = 7220."),
          ("physical = frame × size + offset.", "פיזית = מסגרת × גודל + היסט."),
          code=ptc(PT), check=A("paddr", 2100, 1024, PT)),
        Q(("Same table, page size 1024. What physical address does virtual address 1030 map to?", "אותה טבלה, גודל דף 1024. לאיזו כתובת פיזית ממופה 1030?"),
          ["2054", "5126", "1030", "2048"],
          ("Page 1, offset 6, frame 2: 2 × 1024 + 6 = 2054.", "דף 1, היסט 6, מסגרת 2: 2 × 1024 + 6 = 2054."),
          ("Look up the frame of the page, keep the offset.", "מחפשים את המסגרת של הדף ושומרים את ההיסט."),
          code=ptc(PT), check=A("paddr", 1030, 1024, PT)),
        Q(("Same table, page size 1024. The CPU accesses virtual address 3500. What happens?", "אותה טבלה, גודל דף 1024. המעבד ניגש לכתובת 3500. מה קורה?"),
          [("A page fault: page 3 is invalid", "שגיאת דף: דף 3 לא תקף"), ("The address 3500 is used directly", "הכתובת 3500 משמשת ישירות"),
           ("Frame 3 is used", "משתמשים במסגרת 3"), ("The process is terminated at once", "התהליך מסתיים מיד")],
          ("3500 div 1024 = 3, and page 3 is marked invalid, so the MMU traps to the OS with a page fault.", "3500 div 1024 = 3, ודף 3 מסומן לא תקף, ולכן ה-MMU קורא למערכת ההפעלה עם שגיאת דף."),
          ("Invalid page = page fault.", "דף לא תקף = שגיאת דף."),
          code=ptc(PT), check=A("paddr", 3500, 1024, PT, want="fault")),
        Q(("Virtual address 2100 is translated to frame 7. What is the offset inside the physical frame?", "הכתובת הווירטואלית 2100 מתורגמת למסגרת 7. מהו ההיסט בתוך המסגרת הפיזית?"),
          ["52", "7", "2100", "0"],
          ("The offset is copied unchanged: 2100 mod 1024 = 52.", "ההיסט מועתק ללא שינוי: 2100 mod 1024 = 52."),
          ("The offset never changes.", "ההיסט אף פעם לא משתנה."),
          check=A("offset", 2100, 1024, want="52")),
        Q(("What is the page-table-entry bit that tells whether an access causes a page fault called?", "איך נקרא הביט בכניסה לטבלת הדפים שקובע אם גישה תגרום לשגיאת דף?"),
          [("Valid-invalid bit", "ביט תקף-לא תקף"), ("Dirty bit", "ביט מלוכלך (dirty)"), ("Reference bit", "ביט התייחסות"), ("Present-in-TLB bit", "ביט נמצא-ב-TLB")],
          ("The valid-invalid bit marks whether the page is in RAM.", "ביט תקף-לא תקף מציין אם הדף נמצא ב-RAM."),
          ("Valid-invalid bit decides page faults.", "ביט תקף-לא תקף מכריע על שגיאות דף."),
          exam="2017B-8", has="valid"),
    ], icon="🔀")

# ------------------------------------------------------------------ level 3
L3 = Lv(
    ("Whole pages and internal fragmentation", "דפים שלמים ופיצול פנימי"),
    ("Memory comes in whole pages, so the last page is partly wasted.", "הזיכרון ניתן בדפים שלמים, לכן הדף האחרון מבוזבז חלקית."),
    ("""
<p>The OS gives memory only in whole pages. If a process needs 10,000 bytes and pages are 4096 bytes, it gets 3 pages (12,288 bytes) and 2,288 bytes of the last page are unused. This waste <b>inside an allocated block</b> is <b>internal fragmentation</b>.</p>
<pre>pages = ceil(size / page size)
waste = pages * page size - size
maximum waste = page size - 1   (4095 for 4 KB pages)</pre>
<p>Three facts that come up in the exam. A shared memory region is always a <b>multiple of the page size</b>; <code>shmget</code> of a single <code>int</code> still takes <b>4096 bytes</b> (one page). And the unused part of a page still belongs to the process, so writing there causes <b>no fault</b>.</p>
""", """
<p>מערכת ההפעלה נותנת זיכרון רק בדפים שלמים. אם תהליך צריך 10,000 בתים והדפים הם 4096 בתים, הוא מקבל 3 דפים (12,288 בתים) ו-2,288 בתים בדף האחרון לא בשימוש. הבזבוז הזה <b>בתוך בלוק שהוקצה</b> נקרא <b>פיצול פנימי (internal fragmentation)</b>.</p>
<pre>pages = ceil(size / page size)
waste = pages * page size - size
maximum waste = page size - 1   (4095 for 4 KB pages)</pre>
<p>שלוש עובדות שחוזרות במבחן. אזור זיכרון משותף הוא תמיד <b>כפולה של גודל הדף</b>; <code>shmget</code> של <code>int</code> בודד עדיין תופס <b>4096 בתים</b> (דף אחד). והחלק הלא מנוצל של הדף עדיין שייך לתהליך, ולכן כתיבה אליו <b>לא גורמת לשגיאה</b>.</p>
"""),
    [
        Q(("A process needs 10,000 bytes and pages are 4096 bytes. How many bytes of internal fragmentation?", "תהליך צריך 10,000 בתים והדפים הם 4096 בתים. כמה בתים של פיצול פנימי?"),
          ["2288", "4095", "1808", "3"],
          ("It needs 3 pages = 12,288 bytes; 12,288 − 10,000 = 2288.", "הוא צריך 3 דפים = 12,288 בתים; 12,288 − 10,000 = 2288."),
          ("waste = pages × size − requested.", "בזבוז = דפים × גודל − מבוקש."),
          check=C("(-(-10000//4096))*4096-10000")),
        Q(("What is the maximum internal fragmentation in one page when the page size is 4096 bytes?", "מהו הפיצול הפנימי המרבי בדף אחד כשגודל הדף 4096 בתים?"),
          ["4095", "4096", "2048", "0"],
          ("At worst a single byte of the last page is used: 4096 − 1 = 4095.", "במקרה הגרוע משתמשים בבית אחד של הדף האחרון: 4096 − 1 = 4095."),
          ("Max waste = page size − 1.", "בזבוז מרבי = גודל דף − 1."),
          check=C("4096-1"), exam="2021A-8", has="4095"),
        Q(("A 6K request is given an 8K allocation. What is the wasted space called?", "בקשה של 6K קיבלה הקצאה של 8K. איך נקרא המקום המבוזבז?"),
          [("Internal fragmentation", "פיצול פנימי"), ("External fragmentation", "פיצול חיצוני"), ("Thrashing", "תזזית (thrashing)"), ("Swapping", "החלפה (swapping)")],
          ("The waste is inside the allocated block: internal fragmentation.", "הבזבוז נמצא בתוך הבלוק שהוקצה: פיצול פנימי."),
          ("Waste inside an allocation = internal.", "בזבוז בתוך הקצאה = פנימי."),
          exam="2014B-6", has="internal"),
        Q(("How many bytes does Linux/Pentium allocate for `shmget(IPC_PRIVATE, sizeof(int), 0600)`?", "כמה בתים מקצה Linux/Pentium עבור `shmget(IPC_PRIVATE, sizeof(int), 0600)`?"),
          ["4096", "4", "8", "1024"],
          ("Shared memory comes in whole pages: one 4096-byte page.", "זיכרון משותף ניתן בדפים שלמים: דף אחד של 4096 בתים."),
          ("Shared memory = whole pages.", "זיכרון משותף = דפים שלמים."),
          exam="2015A-10", has="4096"),
        Q(("A process writes into the unused part of its last page (internal fragmentation). What happens?", "תהליך כותב לחלק הלא מנוצל של הדף האחרון שלו (פיצול פנימי). מה קורה?"),
          [("The value is written, no fault", "הערך נכתב, בלי שגיאה"), ("Segmentation fault", "שגיאת סגמנטציה"), ("A page fault brings a new page", "שגיאת דף מביאה דף חדש"), ("The OS kills the process", "המערכת הורגת את התהליך")],
          ("The whole page belongs to the process, so the write succeeds silently.", "כל הדף שייך לתהליך, ולכן הכתיבה מצליחה בשקט."),
          ("Inside its own page = no fault.", "בתוך הדף שלו = בלי שגיאה."),
          exam="2022B-7", has="without"),
        Q(("The size of a shared-memory region must be a multiple of what?", "גודל אזור זיכרון משותף חייב להיות כפולה של מה?"),
          [("The page size", "גודל הדף"), ("The word size", "גודל המילה"), ("The sector size", "גודל הסקטור"), ("The cache line", "שורת המטמון")],
          ("Memory is shared by mapping pages, so the size is a multiple of the page size.", "הזיכרון משותף על ידי מיפוי דפים, ולכן הגודל כפולה של גודל הדף."),
          ("Shared region = multiple of page size.", "אזור משותף = כפולה של גודל הדף."),
          exam="2020B-9", has="page"),
    ], icon="🧱")

# ------------------------------------------------------------------ level 4
L4 = Lv(
    ("Multilevel page tables", "טבלאות דפים רב-שלביות"),
    ("Several lookups, several levels, a huge address space.", "כמה חיפושים, כמה שלבים, מרחב כתובות עצום."),
    ("""
<p>A single-level table for a 32-bit space with 4 KB pages needs 2^20 entries, almost all unused. A <b>multilevel</b> table splits the page number into several indexes; only the parts of the tree that are in use are kept in memory.</p>
<pre>32 bits, 4 KB pages, two levels:
[ 10 bits | 10 bits | 12 bits offset ]
 outer      inner</pre>
<p>The price: each level is one more memory access. On a <b>TLB miss</b> a translation costs <b>levels + 1</b> memory accesses (one per level, then the data itself).</p>
<p>The reachable address space is (entries per table)^levels &times; frame size. Example: frame 1024 bytes, 4 levels, 128 entries per table: 1024 &times; 128^4 = 2^10 &times; 2^28 = 2^38 bytes.</p>
""", """
<p>טבלה חד-שלבית למרחב של 32 ביטים עם דפים של 4 KB צריכה 2^20 כניסות, כמעט כולן לא בשימוש. טבלה <b>רב-שלבית</b> מפצלת את מספר הדף לכמה אינדקסים; רק החלקים בעץ שבשימוש נשמרים בזיכרון.</p>
<pre>32 bits, 4 KB pages, two levels:
[ 10 bits | 10 bits | 12 bits offset ]
 outer      inner</pre>
<p>המחיר: כל שלב הוא גישה נוספת לזיכרון. ב<b>החטאת TLB</b> תרגום עולה <b>שלבים + 1</b> גישות לזיכרון (אחת לכל שלב, ואז הנתון עצמו).</p>
<p>מרחב הכתובות שאפשר להגיע אליו הוא (כניסות בטבלה)^שלבים &times; גודל מסגרת. דוגמה: מסגרת 1024 בתים, 4 שלבים, 128 כניסות בטבלה: 1024 &times; 128^4 = 2^10 &times; 2^28 = 2^38 בתים.</p>
"""),
    [
        Q(("3-level paging, TLB miss. How many memory accesses to read one value?", "דפדוף ב-3 שלבים, החטאת TLB. כמה גישות לזיכרון לקריאת ערך אחד?"),
          ["4", "3", "1", "6"],
          ("3 page-table levels + 1 access to the data = 4.", "3 שלבי טבלה + גישה אחת לנתון = 4."),
          ("TLB miss = levels + 1.", "החטאת TLB = שלבים + 1."),
          check=C("3+1"), exam="2024B-7", has="4"),
        Q(("4-level paging, TLB miss. How many memory accesses to read one value?", "דפדוף ב-4 שלבים, החטאת TLB. כמה גישות לזיכרון לקריאת ערך אחד?"),
          ["5", "4", "8", "1"],
          ("4 levels + 1 = 5.", "4 שלבים + 1 = 5."),
          ("TLB miss = levels + 1.", "החטאת TLB = שלבים + 1."),
          check=C("4+1")),
        Q(("Frame size 1024 bytes, a 4-level page table, 128 entries per table at every level. What is the virtual address space?", "גודל מסגרת 1024 בתים, טבלת דפים בת 4 שלבים, 128 כניסות בכל טבלה בכל שלב. מהו מרחב הכתובות הווירטואלי?"),
          ["2^38 bytes", "2^28 bytes", "2^45 bytes", "2^17 bytes"],
          ("128^4 = 2^28 pages, each 2^10 bytes: 2^38 bytes.", "128^4 = 2^28 דפים, כל אחד 2^10 בתים: 2^38 בתים."),
          ("Space = entries^levels × page size.", "מרחב = כניסות^שלבים × גודל דף."),
          check=C("1024*128**4", fmt="pow2", want="2^38"),
          exam="2017SA-8", has="128"),
        Q(("Pages are 4 KB and a page-table entry is 4 bytes. How many entries fit in one page-table page?", "הדפים בגודל 4 KB וכניסה בטבלה היא 4 בתים. כמה כניסות נכנסות בדף טבלה אחד?"),
          ["1024", "4096", "512", "16"],
          ("4096 / 4 = 1024 entries, which is why each level uses 10 bits.", "4096 / 4 = 1024 כניסות, ולכן כל שלב משתמש ב-10 ביטים."),
          ("Entries per table = page size / entry size.", "כניסות בטבלה = גודל דף / גודל כניסה."),
          check=C("4096//4")),
        Q(("Two-level paging, 1024 entries per table, 4 KB pages. How big is the virtual address space?", "דפדוף דו-שלבי, 1024 כניסות בטבלה, דפים של 4 KB. מה גודל מרחב הכתובות הווירטואלי?"),
          ["2^32 bytes", "2^22 bytes", "2^42 bytes", "2^20 bytes"],
          ("2^10 × 2^10 pages × 2^12 bytes = 2^32.", "2^10 × 2^10 דפים × 2^12 בתים = 2^32."),
          ("Multiply the index ranges and the page size.", "מכפילים את טווחי האינדקסים ואת גודל הדף."),
          check=dict(k="calc", v="1024*1024*4096", fmt="pow2", want="2^32")),
        Q(("What is the main benefit of a multilevel page table over a single-level one?", "מהו היתרון העיקרי של טבלת דפים רב-שלבית על פני חד-שלבית?"),
          [("It keeps memory for page tables only where the address space is used", "היא שומרת זיכרון לטבלאות רק היכן שמרחב הכתובות בשימוש"),
           ("It makes translation need fewer memory accesses", "היא גורמת לתרגום להזדקק לפחות גישות לזיכרון"),
           ("It removes the need for a TLB", "היא מבטלת את הצורך ב-TLB"), ("It removes internal fragmentation", "היא מבטלת פיצול פנימי")],
          ("It saves table memory; it actually costs extra accesses on a TLB miss.", "היא חוסכת זיכרון לטבלאות; בפועל היא מוסיפה גישות בהחטאת TLB."),
          ("Multilevel saves table memory, not time.", "רב-שלבית חוסכת זיכרון, לא זמן."))
    ], icon="🪜")

# ------------------------------------------------------------------ level 5
L5 = Lv(
    ("The TLB and effective access time", "ה-TLB וזמן הגישה האפקטיבי"),
    ("Average cost of a memory access with a TLB.", "העלות הממוצעת של גישה לזיכרון עם TLB."),
    ("""
<p>The <b>TLB</b> (Translation Lookaside Buffer) is a small cache of the page table inside the CPU. On a <b>hit</b> the translation is free and only the data access remains; on a <b>miss</b> the page-table levels must be read from RAM first. The TLB saves the page-table accesses in RAM.</p>
<pre>hit  = 1 memory access
miss = levels + 1 memory accesses
EAT  = h * hit + (1 - h) * miss      (add the TLB lookup time to both if it is not negligible)

h = 80%, two levels, memory 10 ns:
EAT = 0.8 * 10 + 0.2 * (3 * 10) = 8 + 6 = 14 ns</pre>
""", """
<p>ה-<b>TLB</b> (Translation Lookaside Buffer) הוא מטמון קטן של טבלת הדפים בתוך המעבד. ב<b>פגיעה</b> התרגום חינמי ונשארת רק גישת הנתון; ב<b>החטאה</b> צריך קודם לקרוא את שלבי הטבלה מה-RAM. ה-TLB חוסך את הגישות לטבלת הדפים ב-RAM.</p>
<pre>hit  = 1 memory access
miss = levels + 1 memory accesses
EAT  = h * hit + (1 - h) * miss      (add the TLB lookup time to both if it is not negligible)

h = 80%, two levels, memory 10 ns:
EAT = 0.8 * 10 + 0.2 * (3 * 10) = 8 + 6 = 14 ns</pre>
"""),
    [
        Q(("TLB hit rate 80%, two-level page table, negligible TLB time, memory access 10 ns. What is the average memory access time?", "שיעור פגיעות TLB 80%, טבלת דפים דו-שלבית, זמן TLB זניח, גישה לזיכרון 10 ננו-שניות. מהו זמן הגישה הממוצע?"),
          ["14 ns", "10 ns", "16 ns", "30 ns"],
          ("0.8 × 10 + 0.2 × 30 = 14 ns.", "0.8 × 10 + 0.2 × 30 = 14 ננו-שניות."),
          ("EAT = h·hit + (1−h)·miss.", "EAT = h·פגיעה + (1−h)·החטאה."),
          check=dict(k="eat", hit=0.8, mem=10, levels=2, want="14"), exam="2026A-8", has="14"),
        Q(("Single-level page table, hit rate 90%, memory 100 ns, negligible TLB time. Average access time?", "טבלת דפים חד-שלבית, שיעור פגיעות 90%, זיכרון 100 ננו-שניות, זמן TLB זניח. מהו זמן הגישה הממוצע?"),
          ["110 ns", "100 ns", "190 ns", "120 ns"],
          ("Hit 100, miss 2 × 100 = 200: 0.9 × 100 + 0.1 × 200 = 110 ns.", "פגיעה 100, החטאה 2 × 100 = 200: 0.9 × 100 + 0.1 × 200 = 110 ננו-שניות."),
          ("Miss costs levels + 1 accesses.", "החטאה עולה שלבים + 1 גישות."),
          check=dict(k="eat", hit=0.9, mem=100, levels=1, want="110")),
        Q(("Three-level page table, hit rate 50%, memory 20 ns, negligible TLB time. Average access time?", "טבלת דפים תלת-שלבית, שיעור פגיעות 50%, זיכרון 20 ננו-שניות, זמן TLB זניח. מהו זמן הגישה הממוצע?"),
          ["50 ns", "80 ns", "20 ns", "40 ns"],
          ("Hit 20, miss 4 × 20 = 80: 0.5 × 20 + 0.5 × 80 = 50 ns.", "פגיעה 20, החטאה 4 × 20 = 80: 0.5 × 20 + 0.5 × 80 = 50 ננו-שניות."),
          ("Weight hit and miss by their probabilities.", "שוקלים פגיעה והחטאה לפי ההסתברויות."),
          check=dict(k="eat", hit=0.5, mem=20, levels=3, want="50")),
        Q(("Two-level table, hit rate 80%, memory 100 ns, and every access also pays a 5 ns TLB lookup. Average access time?", "טבלה דו-שלבית, שיעור פגיעות 80%, זיכרון 100 ננו-שניות, וכל גישה משלמת גם 5 ננו-שניות חיפוש ב-TLB. מהו זמן הגישה הממוצע?"),
          ["145 ns", "140 ns", "125 ns", "305 ns"],
          ("Hit 5 + 100 = 105; miss 5 + 300 = 305; 0.8 × 105 + 0.2 × 305 = 145 ns.", "פגיעה 5 + 100 = 105; החטאה 5 + 300 = 305; 0.8 × 105 + 0.2 × 305 = 145 ננו-שניות."),
          ("Add the TLB time to both cases.", "מוסיפים את זמן ה-TLB לשני המקרים."),
          check=dict(k="eat", hit=0.8, mem=100, levels=2, tlb=5, want="145")),
        Q(("What access time does the TLB save?", "איזה זמן גישה חוסך ה-TLB?"),
          [("Accessing the page table in RAM", "הגישה לטבלת הדפים ב-RAM"), ("Accessing the disk", "הגישה לדיסק"), ("The context switch", "החלפת ההקשר"), ("The page-fault handler", "טיפול בשגיאת דף")],
          ("On a hit the page-table reads in RAM are skipped.", "בפגיעה מדלגים על קריאות טבלת הדפים ב-RAM."),
          ("TLB saves page-table accesses in RAM.", "ה-TLB חוסך גישות לטבלת הדפים ב-RAM."),
          exam="2021B-8", has="page table"),
    ], icon="⚡")

# ------------------------------------------------------------------ level 6
L6 = Lv(
    ("Who does what: MMU, TLB, PTBR, PCB", "מי עושה מה: MMU, TLB, PTBR, PCB"),
    ("The hardware and kernel pieces of address translation.", "רכיבי החומרה והליבה בתרגום כתובות."),
    ("""
<table>
<tr><th>Piece</th><th>Job</th></tr>
<tr><td>MMU</td><td>hardware that translates virtual to physical on <b>every</b> access. It is done in hardware because trapping to the OS each time would be far slower.</td></tr>
<tr><td>TLB</td><td>cache of the page table; it can translate without accessing memory.</td></tr>
<tr><td>PTBR</td><td>register that points to the running process's page table. <b>One per CPU core</b>; it changes on a <b>context switch</b>.</td></tr>
<tr><td>PCB</td><td>kernel structure that keeps a process's page-table address while it is not running.</td></tr>
<tr><td>Valid bit off</td><td>the MMU traps to the OS: a page fault.</td></tr>
</table>
""", """
<table>
<tr><th>רכיב</th><th>תפקיד</th></tr>
<tr><td>MMU</td><td>חומרה שמתרגמת וירטואלי לפיזי ב<b>כל</b> גישה. זה נעשה בחומרה כי קריאה למערכת ההפעלה בכל פעם הייתה איטית בהרבה.</td></tr>
<tr><td>TLB</td><td>מטמון של טבלת הדפים; הוא יכול לתרגם בלי לגשת לזיכרון.</td></tr>
<tr><td>PTBR</td><td>אוגר שמצביע על טבלת הדפים של התהליך הרץ. <b>אחד לכל ליבת מעבד</b>; הוא משתנה ב<b>החלפת הקשר</b>.</td></tr>
<tr><td>PCB</td><td>מבנה בליבה ששומר את כתובת טבלת הדפים של תהליך כשהוא לא רץ.</td></tr>
<tr><td>ביט תקף כבוי</td><td>ה-MMU קורא למערכת ההפעלה: שגיאת דף.</td></tr>
</table>
"""),
    [
        Q(("What is the role of the MMU?", "מהו תפקידו של ה-MMU?"),
          [("Translate virtual addresses to physical addresses", "לתרגם כתובות וירטואליות לפיזיות"), ("Schedule processes", "לתזמן תהליכים"), ("Cache disk blocks", "לשמור בלוקי דיסק במטמון"), ("Allocate frames to processes", "להקצות מסגרות לתהליכים")],
          ("The MMU is the translation hardware.", "ה-MMU הוא חומרת התרגום."),
          ("MMU = translation hardware.", "MMU = חומרת התרגום."),
          exam="2019A-6", has="translate"),
        Q(("When does the value of the page-table base register (PTBR) change?", "מתי ערך אוגר בסיס טבלת הדפים (PTBR) משתנה?"),
          [("On a context switch", "בהחלפת הקשר"), ("On every memory access", "בכל גישה לזיכרון"), ("On every page fault", "בכל שגיאת דף"), ("Never", "אף פעם")],
          ("Each process has its own page table, so a context switch loads the new one.", "לכל תהליך טבלת דפים משלו, ולכן החלפת הקשר טוענת את החדשה."),
          ("PTBR changes on a context switch.", "PTBR משתנה בהחלפת הקשר."),
          exam="2017SB-1", has="context"),
        Q(("What is the maximum number of PTBR registers per CPU core?", "מהו המספר המרבי של אוגרי PTBR בכל ליבת מעבד?"),
          ["1", "2", "One per process", "One per page"],
          ("A core runs one process at a time, so it needs exactly one PTBR.", "ליבה מריצה תהליך אחד בכל רגע, ולכן היא צריכה PTBR אחד."),
          ("One PTBR per core.", "PTBR אחד לכל ליבה."),
          exam="2021A-9", has="1"),
        Q(("In which kernel structure is a process's page-table address stored while it is not running?", "באיזה מבנה בליבה נשמרת כתובת טבלת הדפים של תהליך כשהוא לא רץ?"),
          ["PCB", "TLB", "MMU", "The swap partition"],
          ("The PCB keeps everything needed to resume the process, including its page-table address.", "ה-PCB שומר כל מה שנדרש לחידוש התהליך, כולל כתובת טבלת הדפים."),
          ("Not running: page-table address in the PCB.", "לא רץ: כתובת הטבלה ב-PCB."),
          exam="2019B-2", has="pcb"),
        Q(("The MMU translates an address and the valid/invalid bit is off. What does it do?", "ה-MMU מתרגם כתובת וביט תקף/לא תקף כבוי. מה הוא עושה?"),
          [("Traps to the OS: a page fault", "קורא למערכת ההפעלה: שגיאת דף"), ("Uses frame 0", "משתמש במסגרת 0"), ("Reads the disk itself", "קורא את הדיסק בעצמו"), ("Ignores the access", "מתעלם מהגישה")],
          ("The MMU cannot fetch the page itself; it raises a page-fault trap.", "ה-MMU לא יכול להביא את הדף בעצמו; הוא מעלה פסיקת שגיאת דף."),
          ("Valid bit off = page fault trap.", "ביט תקף כבוי = פסיקת שגיאת דף."),
          exam="2023A-7", has="page fault"),
        Q(("Which CPU component sometimes translates a virtual address to a physical one without accessing memory?", "איזה רכיב במעבד מתרגם לפעמים כתובת וירטואלית לפיזית בלי לגשת לזיכרון?"),
          ["The TLB", "The PTBR", "The PCB", "The swap area"],
          ("On a TLB hit the translation comes from the cache, with no memory access.", "בפגיעת TLB התרגום מגיע מהמטמון, בלי גישה לזיכרון."),
          ("TLB hit = translation without memory.", "פגיעת TLB = תרגום בלי זיכרון."),
          exam="2017SB-7", has="tlb"),
    ], icon="🧠")

# ------------------------------------------------------------------ level 7
L7 = Lv(
    ("Boss: memory exam", "בוס: מבחן זיכרון"),
    ("Real exam items on paging and translation.", "שאלות מהמבחנים על דפדוף ותרגום."),
    ("""
<p>Exam level: every question is a past-exam item. Reminders: powers of two for counting, <code>physical = frame * size + offset</code>, a TLB miss costs <b>levels + 1</b> accesses, EAT is a weighted average. 80% passes.</p>
""", """
<p>שלב המבחן: כל שאלה היא פריט ממבחן קודם. תזכורות: חזקות של 2 לספירה, <code>physical = frame * size + offset</code>, החטאת TLB עולה <b>שלבים + 1</b> גישות, ו-EAT הוא ממוצע משוקלל. 80% עובר.</p>
"""),
    [
        Q(("How many potential frames does a 42-bit virtual address give with 1 MB pages?", "כמה מסגרות פוטנציאליות נותנת כתובת וירטואלית של 42 ביטים עם דפים של 1 MB?"),
          ["2^22", "2^42", "2^20", "2^32"],
          ("1 MB = 2^20, so 42 − 20 = 22 bits.", "1 MB = 2^20, לכן 42 − 20 = 22 ביטים."), ("Frames = 2^(42−20).", "מסגרות = 2^(42−20)."),
          check=C("2**(42-20)", fmt="pow2"), exam="2024A-7", has="22"),
        Q(("A process uses 3-level multilevel paging. After a TLB miss, how many memory accesses does one load take?", "תהליך משתמש בדפדוף רב-שלבי עם 3 שלבים. אחרי החטאת TLB, כמה גישות לזיכרון דורשת טעינה אחת?"),
          ["4", "3", "2", "1"],
          ("3 levels + the page itself = 4.", "3 שלבים + הדף עצמו = 4."), ("Levels + 1.", "שלבים + 1."),
          check=C("3+1"), exam="2024B-7", has="4"),
        Q(("The TLB hits 80% of the time, the page table has two levels, a memory access takes 10 ns and the TLB itself is free. Average access time?", "ה-TLB פוגע ב-80% מהמקרים, לטבלה שני שלבים, גישה לזיכרון לוקחת 10 ננו-שניות וה-TLB עצמו חינמי. זמן גישה ממוצע?"),
          ["14 ns", "12 ns", "18 ns", "10 ns"],
          ("0.8 × 10 + 0.2 × 30 = 14 ns.", "0.8 × 10 + 0.2 × 30 = 14 ננו-שניות."), ("Weighted average of hit and miss.", "ממוצע משוקלל של פגיעה והחטאה."),
          check=dict(k="eat", hit=0.8, mem=10, levels=2, want="14"), exam="2026A-8", has="14"),
        Q(("Frame size 1024 bytes, a 4-level page table, 128 entries per table. Size of the virtual address space?", "גודל מסגרת 1024 בתים, טבלה בת 4 שלבים, 128 כניסות בטבלה. גודל מרחב הכתובות הווירטואלי?"),
          ["2^38 bytes", "2^32 bytes", "2^28 bytes", "2^40 bytes"],
          ("1024 × 128^4 = 2^10 × 2^28 = 2^38 bytes.", "1024 × 128^4 = 2^10 × 2^28 = 2^38 בתים."), ("entries^levels × frame size.", "כניסות^שלבים × גודל מסגרת."),
          check=dict(k="calc", v="1024*128**4", fmt="pow2", want="2^38"), exam="2017SA-8", has="128"),
        Q(("Pages are 4096 bytes. At most how many bytes of one page can internal fragmentation waste?", "הדפים בגודל 4096 בתים. לכל היותר כמה בתים של דף אחד יכול פיצול פנימי לבזבז?"),
          ["4095 bytes", "4096 bytes", "2047 bytes", "1 byte"],
          ("Page size minus one byte.", "גודל דף פחות בית אחד."), ("Max waste = page size − 1.", "בזבוז מרבי = גודל דף − 1."),
          check=C("4096-1", want="4095"), exam="2021A-8", has="4095"),
        Q(("What does the MMU do when translating a virtual address whose valid/invalid bit is off?", "מה עושה ה-MMU בתרגום כתובת וירטואלית שביט תקף/לא תקף שלה כבוי?"),
          [("Traps to the OS with a page fault", "קורא למערכת ההפעלה עם שגיאת דף"), ("Loads the page from disk by itself", "טוען את הדף מהדיסק בעצמו"), ("Flushes the TLB", "מרוקן את ה-TLB"), ("Changes the PTBR", "משנה את ה-PTBR")],
          ("The OS, not the hardware, brings the page in.", "מערכת ההפעלה, לא החומרה, מביאה את הדף."), ("Invalid = trap to OS.", "לא תקף = קריאה למערכת ההפעלה."),
          exam="2023A-7", has="page fault"),
    ], icon="🏆", boss=True)

COURSE = Course(
    "paging", "🧮",
    ("Paging and address translation", "דפדוף ותרגום כתובות"),
    ("Memory is the topic with the most computation after scheduling: splitting addresses, counting pages and frames, translating through a page table, multilevel tables and the TLB. The course starts from one address and ends at the exam's table and timing questions. Every level is open; 80% passes.",
     "זיכרון הוא הנושא עם הכי הרבה חישובים אחרי תזמון: פיצול כתובות, ספירת דפים ומסגרות, תרגום דרך טבלת דפים, טבלאות רב-שלביות ו-TLB. הקורס מתחיל מכתובת אחת ומסתיים בשאלות הטבלאות והתזמון של המבחן. כל השלבים פתוחים; 80% עובר."),
    "memory", [L1, L2, L3, L4, L5, L6, L7])
