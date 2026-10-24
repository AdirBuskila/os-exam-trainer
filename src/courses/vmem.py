# -*- coding: utf-8 -*-
"""Course 3: demand paging and page replacement."""
from _kit import Q, Lv, Course


def R(algo, refs, frames, ask, want=None):
    d = dict(k="repl", algo=algo, refs=refs, frames=frames, ask=ask)
    if want is not None:
        d["want"] = want
    return d


def refs_code(refs, frames):
    return "frames: %d\nreferences: %s" % (frames, " ".join(str(x) for x in refs))


A = [1, 2, 3, 1, 4, 2]
B = [2, 3, 2, 1, 5, 2, 4, 5, 3, 2, 5, 2]
CL = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
D = [3, 2, 1, 3, 4, 1, 2]
E = [1, 2, 3, 4, 1, 2]
BEL = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]

# ------------------------------------------------------------------ level 1
L1 = Lv(
    ("Demand paging and page faults", "דפדוף לפי דרישה ושגיאות דף"),
    ("Pages come into RAM only when they are touched.", "דפים נכנסים ל-RAM רק כשניגשים אליהם."),
    ("""
<p>With <b>demand paging</b> a program is not loaded whole. A page is brought from disk only when it is first <b>needed</b>. A newly scheduled process therefore starts with an <b>empty</b> page table: every entry is invalid.</p>
<ol>
<li>The program touches a page whose valid bit is off; the MMU raises a <b>page fault</b>.</li>
<li>The OS finds a free frame (or evicts a victim, see the next levels) and reads the page from disk into RAM. Pages evicted from RAM live in the <b>swap partition</b> on Linux.</li>
<li>The OS marks the entry valid and the process <b>restarts the instruction that faulted</b>.</li>
</ol>
<p>Each page also has a <b>dirty bit</b>: it says the page was changed since it was loaded from disk (so it must be written back before eviction). <b>Copy-on-Write</b> lets a child share the parent's pages until one of them writes, and only then is the page copied.</p>
""", """
<p>ב<b>דפדוף לפי דרישה (demand paging)</b> התוכנית לא נטענת כולה. דף מובא מהדיסק רק כשהוא <b>נדרש</b> לראשונה. לכן תהליך חדש שמתוזמן מתחיל עם טבלת דפים <b>ריקה</b>: כל הכניסות לא תקפות.</p>
<ol>
<li>התוכנית ניגשת לדף שביט התקף שלו כבוי; ה-MMU מעלה <b>שגיאת דף (page fault)</b>.</li>
<li>מערכת ההפעלה מוצאת מסגרת פנויה (או מפנה קורבן, בשלבים הבאים) וקוראת את הדף מהדיסק ל-RAM. דפים שפונו מה-RAM נשמרים ב-<b>swap partition</b> ב-Linux.</li>
<li>המערכת מסמנת את הכניסה כתקפה והתהליך <b>מריץ מחדש את ההוראה שגרמה לשגיאה</b>.</li>
</ol>
<p>לכל דף יש גם <b>ביט מלוכלך (dirty)</b>: הוא מציין שהדף השתנה מאז שנטען מהדיסק (ולכן צריך לכתוב אותו חזרה לפני פינוי). <b>Copy-on-Write</b> מאפשר לבן לחלוק את דפי האב עד שאחד מהם כותב, ורק אז הדף מועתק.</p>
"""),
    [
        Q(("A part of a program that is never used is not loaded into RAM thanks to which mechanism?", "חלק מתוכנית שלא נעשה בו שימוש לא נטען ל-RAM בזכות איזה מנגנון?"),
          [("Demand paging", "דפדוף לפי דרישה"), "Copy-on-Write", ("Thrashing", "תזזית"), ("Segmentation fault", "שגיאת סגמנטציה")],
          ("Demand paging loads a page only when it is touched.", "דפדוף לפי דרישה טוען דף רק כשניגשים אליו."),
          ("Demand paging = load on first use.", "דפדוף לפי דרישה = טעינה בשימוש ראשון."),
          exam="2016B-7", has="demand"),
        Q(("Under demand paging, what does the page table of a newly scheduled process contain?", "בדפדוף לפי דרישה, מה מכילה טבלת הדפים של תהליך חדש שהתחיל לרוץ?"),
          [("An empty table: no valid pages", "טבלה ריקה: אין דפים תקפים"), ("All pages of the program", "את כל דפי התוכנית"), ("Only the code pages", "רק את דפי הקוד"), ("The pages of its parent", "את דפי האב")],
          ("Nothing is loaded yet, so every entry is invalid and the first accesses fault.", "עוד לא נטען דבר, ולכן כל הכניסות לא תקפות והגישות הראשונות גורמות לשגיאות."),
          ("New process = empty page table.", "תהליך חדש = טבלת דפים ריקה."),
          exam="2019B-7", has="empty"),
        Q(("After a legitimate page fault, to which instruction does the process return?", "אחרי שגיאת דף לגיטימית, לאיזו הוראה התהליך חוזר?"),
          [("The instruction that faulted", "ההוראה שגרמה לשגיאה"), ("The next instruction", "ההוראה הבאה"), ("The first instruction of the program", "ההוראה הראשונה בתוכנית"), ("The previous function call", "הקריאה הקודמת לפונקציה")],
          ("The access did not complete, so the same instruction is executed again, now with the page present.", "הגישה לא הושלמה, ולכן אותה הוראה מורצת שוב, עכשיו כשהדף קיים."),
          ("Page fault = retry the same instruction.", "שגיאת דף = מנסים שוב את אותה הוראה."),
          exam="2019B-6", has="faulted"),
        Q(("Where on disk are pages evicted from RAM stored in Linux?", "היכן בדיסק נשמרים ב-Linux דפים שפונו מה-RAM?"),
          ["swap partition", ("The boot sector", "מגזר האתחול"), ("The PCB", "ה-PCB"), ("The TLB", "ה-TLB")],
          ("Evicted pages go to the swap area.", "דפים שפונו נכתבים לאזור ה-swap."),
          ("Evicted pages live in swap.", "דפים מפונים נמצאים ב-swap."),
          exam="2016A-8", has="swap"),
        Q(("What is the per-page bit that shows the page changed since it was brought in from disk?", "איך נקרא הביט לכל דף שמראה שהדף השתנה מאז שהובא מהדיסק?"),
          [("Dirty bit", "ביט מלוכלך (dirty)"), ("Valid bit", "ביט תקף"), ("Reference bit", "ביט התייחסות"), ("Lock bit", "ביט נעילה")],
          ("The dirty (modify) bit marks a changed page.", "ביט ה-dirty (modify) מסמן דף ששונה."),
          ("Changed since loaded = dirty bit.", "שונה מאז הטעינה = ביט dirty."),
          exam="2015A-7", has="dirty"),
        Q(("Which OS mechanism lets a child share the parent's pages until a write forces a copy?", "איזה מנגנון מאפשר לבן לחלוק את דפי האב עד שכתיבה מחייבת העתקה?"),
          ["Copy-on-Write", "Demand paging", "Swapping", "Clock"],
          ("Copy-on-Write copies a page only at the first write.", "Copy-on-Write מעתיק דף רק בכתיבה הראשונה."),
          ("Share until written = Copy-on-Write.", "שיתוף עד כתיבה = Copy-on-Write."),
          exam="2020A-10", has="copy"),
    ], icon="📥")

# ------------------------------------------------------------------ level 2
L2 = Lv(
    ("FIFO replacement", "החלפת דפים FIFO"),
    ("Evict the page that has been in RAM the longest.", "מפנים את הדף שנמצא ב-RAM הכי הרבה זמן."),
    ("""
<p>When RAM has no free frame, the OS must pick a <b>victim</b>. A <b>reference string</b> is the sequence of pages the program touches; a reference to a page already in a frame is a <b>hit</b>, otherwise it is a <b>fault</b> (and, if the frames are full, one page is evicted).</p>
<p><b>FIFO</b> evicts the page that was <b>loaded</b> the longest ago, even if it was just used. A hit changes nothing in the order.</p>
<pre>3 frames, references 1 2 3 1 4 2
1 fault [1]
2 fault [1 2]
3 fault [1 2 3]
1 hit   [1 2 3]
4 fault [2 3 4]   evict 1 (oldest)
2 hit   [2 3 4]
-> 4 faults, 2 hits</pre>
<p>Method: keep the frames as a queue, oldest on the left. Count faults; hits + faults = number of references.</p>
""", """
<p>כשב-RAM אין מסגרת פנויה, המערכת צריכה לבחור <b>קורבן</b>. <b>מחרוזת הפניות (reference string)</b> היא רצף הדפים שהתוכנית ניגשת אליהם; הפניה לדף שכבר נמצא במסגרת היא <b>פגיעה (hit)</b>, אחרת היא <b>שגיאה (fault)</b> (ואם המסגרות מלאות, מפנים דף אחד).</p>
<p><b>FIFO</b> מפנה את הדף ש<b>נטען</b> לפני הכי הרבה זמן, גם אם השתמשו בו הרגע. פגיעה לא משנה את הסדר.</p>
<pre>3 frames, references 1 2 3 1 4 2
1 fault [1]
2 fault [1 2]
3 fault [1 2 3]
1 hit   [1 2 3]
4 fault [2 3 4]   evict 1 (oldest)
2 hit   [2 3 4]
-> 4 faults, 2 hits</pre>
<p>שיטה: שומרים את המסגרות כתור, הוותיק משמאל. סופרים שגיאות; פגיעות + שגיאות = מספר ההפניות.</p>
"""),
    [
        Q(("Count the page faults under FIFO.", "ספרו את שגיאות הדף ב-FIFO."),
          ["4", "5", "6", "3"],
          ("Faults on 1, 2, 3, 4; the references 1 and 2 hit. Total 4.", "שגיאות על 1, 2, 3, 4; ההפניות 1 ו-2 פוגעות. סך הכול 4."),
          ("Count the faults one reference at a time.", "סופרים שגיאות הפניה אחר הפניה."),
          code=refs_code(A, 3), check=R("FIFO", A, 3, "faults")),
        Q(("Same string under FIFO. Which page is evicted when page 4 is referenced?", "אותה מחרוזת ב-FIFO. איזה דף מפונה כשפונים להפניה 4?"),
          ["1", "2", "3", "No page: there is a free frame"],
          ("Page 1 was loaded first. Using it again at the fourth reference did not move it.", "דף 1 נטען ראשון. השימוש החוזר בו בהפניה הרביעית לא הזיז אותו."),
          ("FIFO ignores recent use.", "FIFO מתעלם משימוש אחרון."),
          code=refs_code(A, 3), check=R("FIFO", A, 3, "victim:4")),
        Q(("Count the page faults under FIFO with 3 frames.", "ספרו את שגיאות הדף ב-FIFO עם 3 מסגרות."),
          ["15", "12", "9", "14"],
          ("Working through all 20 references gives 15 faults (LRU would give 12, the optimal 9).", "מעבר על כל 20 ההפניות נותן 15 שגיאות (LRU היה נותן 12, האופטימלי 9)."),
          ("FIFO on the classic string: 15 faults.", "FIFO על המחרוזת הקלאסית: 15 שגיאות."),
          code=refs_code(CL, 3), check=R("FIFO", CL, 3, "faults")),
        Q(("Which page does FIFO choose as the victim?", "איזה דף FIFO בוחר כקורבן?"),
          [("The page that has been in memory the longest", "הדף שנמצא בזיכרון הכי הרבה זמן"), ("The page unused for the longest time", "הדף שלא נעשה בו שימוש הכי הרבה זמן"),
           ("The page used farthest in the future", "הדף שישמש הכי מאוחר בעתיד"), ("The largest page", "הדף הגדול ביותר")],
          ("FIFO looks at load time only.", "FIFO מסתכל רק על זמן הטעינה."),
          ("FIFO = oldest loaded.", "FIFO = הכי ותיק בזיכרון.")),
        Q(("How many references are hits under FIFO?", "כמה מההפניות הן פגיעות ב-FIFO?"),
          ["3", "9", "4", "7"],
          ("There are 12 references and 9 faults under FIFO, so 3 hits.", "יש 12 הפניות ו-9 שגיאות ב-FIFO, ולכן 3 פגיעות."),
          ("Hits = references − faults.", "פגיעות = הפניות − שגיאות."),
          code=refs_code(B, 3), check=R("FIFO", B, 3, "hits")),
    ], icon="📬")

# ------------------------------------------------------------------ level 3
L3 = Lv(
    ("LRU replacement", "החלפת דפים LRU"),
    ("Evict the page not used for the longest time.", "מפנים את הדף שלא השתמשו בו הכי הרבה זמן."),
    ("""
<p><b>LRU</b> (Least Recently Used) looks at the <b>past</b>: it evicts the page whose last use is the oldest. Unlike FIFO, <b>a hit refreshes the page</b>, moving it to the "most recent" end.</p>
<pre>3 frames, references 1 2 3 1 4 2   (oldest use on the left)
1 fault [1]      2 fault [1 2]     3 fault [1 2 3]
1 hit   [2 3 1]  (1 is now the most recent)
4 fault [3 1 4]  evict 2
2 fault [1 4 2]  evict 3
-> 5 faults</pre>
<p>LRU usually beats FIFO because pages used recently tend to be used again. Exact LRU needs an update on <b>every</b> memory reference, which is too expensive in practice, so real systems approximate it with a reference bit (the Clock algorithm, level 6).</p>
""", """
<p><b>LRU</b> (Least Recently Used) מסתכל על ה<b>עבר</b>: הוא מפנה את הדף שהשימוש האחרון בו הוא הוותיק ביותר. בניגוד ל-FIFO, <b>פגיעה מרעננת את הדף</b> ומעבירה אותו לצד ה"אחרון בשימוש".</p>
<pre>3 frames, references 1 2 3 1 4 2   (oldest use on the left)
1 fault [1]      2 fault [1 2]     3 fault [1 2 3]
1 hit   [2 3 1]  (1 is now the most recent)
4 fault [3 1 4]  evict 2
2 fault [1 4 2]  evict 3
-> 5 faults</pre>
<p>LRU בדרך כלל טוב מ-FIFO כי דפים ששימשו לאחרונה נוטים לשמש שוב. LRU מדויק דורש עדכון ב<b>כל</b> הפניה לזיכרון, וזה יקר מדי בפועל, ולכן מערכות אמיתיות מקרבות אותו בעזרת ביט התייחסות (אלגוריתם Clock, שלב 6).</p>
"""),
    [
        Q(("Count the page faults under LRU.", "ספרו את שגיאות הדף ב-LRU."),
          ["5", "4", "6", "3"],
          ("A hit on 1 protects it, so 2 is evicted for page 4 and then page 2 faults again: 5 faults.", "פגיעה ב-1 מגנה עליו, ולכן 2 מפונה בשביל 4 ואז 2 גורם שוב לשגיאה: 5 שגיאות."),
          ("A hit refreshes recency under LRU.", "ב-LRU פגיעה מרעננת את הדף."),
          code=refs_code(A, 3), check=R("LRU", A, 3, "faults")),
        Q(("Same string under LRU. Which page is evicted when page 4 is referenced?", "אותה מחרוזת ב-LRU. איזה דף מפונה כשפונים להפניה 4?"),
          ["2", "1", "3", "4"],
          ("The recency order is 2, 3, 1 (oldest first); page 2 was used least recently.", "סדר השימוש הוא 2, 3, 1 (הוותיק ראשון); דף 2 שימש הכי מזמן."),
          ("Evict the oldest last use.", "מפנים את השימוש האחרון הוותיק ביותר."),
          code=refs_code(A, 3), check=R("LRU", A, 3, "victim:4")),
        Q(("Count the page faults under LRU with 3 frames.", "ספרו את שגיאות הדף ב-LRU עם 3 מסגרות."),
          ["12", "15", "9", "10"],
          ("LRU gives 12 faults here: FIFO needs 15 and the optimal algorithm 9.", "LRU נותן כאן 12 שגיאות: FIFO צריך 15 והאלגוריתם האופטימלי 9."),
          ("LRU on the classic string: 12.", "LRU על המחרוזת הקלאסית: 12."),
          code=refs_code(CL, 3), check=R("LRU", CL, 3, "faults")),
        Q(("Count the page faults under LRU.", "ספרו את שגיאות הדף ב-LRU."),
          ["7", "9", "6", "8"],
          ("Repeated use of page 2 keeps it in memory, giving 7 faults (FIFO gives 9).", "שימוש חוזר בדף 2 שומר אותו בזיכרון, ונותן 7 שגיאות (FIFO נותן 9)."),
          ("Refresh the page on every hit.", "מרעננים את הדף בכל פגיעה."),
          code=refs_code(B, 3), check=R("LRU", B, 3, "faults")),
        Q(("Why is exact LRU rarely implemented in hardware?", "מדוע LRU מדויק כמעט לא ממומש בחומרה?"),
          [("It must be updated on every memory reference", "צריך לעדכן אותו בכל הפניה לזיכרון"), ("It needs to know the future", "הוא צריך לדעת את העתיד"),
           ("It suffers from Belady's anomaly", "הוא סובל מאנומליית Belady"), ("It cannot evict dirty pages", "הוא לא יכול לפנות דפים מלוכלכים")],
          ("Tracking the exact order costs work on every access; knowing the future is what OPT needs, and LRU is immune to Belady.", "מעקב אחר הסדר המדויק עולה עבודה בכל גישה; ידיעת העתיד היא מה ש-OPT צריך, ו-LRU חסין ל-Belady."),
          ("Exact LRU is updated on every reference.", "LRU מדויק מתעדכן בכל הפניה.")),
    ], icon="🕰️")

# ------------------------------------------------------------------ level 4
L4 = Lv(
    ("The optimal algorithm", "האלגוריתם האופטימלי"),
    ("Evict the page needed farthest in the future.", "מפנים את הדף שיידרש הכי מאוחר בעתיד."),
    ("""
<p>The <b>optimal</b> algorithm (OPT) evicts the page that will be used <b>farthest in the future</b> (or never again). It gives the fewest faults possible, but it needs the future, so it cannot be built. It is the yardstick the others are measured against.</p>
<pre>3 frames, references 3 2 1 3 4 1 2
3 f  2 f  1 f  [3 2 1]
3 hit
4 fault: the rest is "1 2". Page 3 is never used again -> evict 3   [2 1 4]
1 hit
2 hit
-> 4 faults</pre>
<p>Method: at each fault, look <b>right</b> along the reference string; the victim is the resident page whose next use is the latest, or that never appears again.</p>
""", """
<p>האלגוריתם ה<b>אופטימלי</b> (OPT) מפנה את הדף שישמש <b>הכי מאוחר בעתיד</b> (או אף פעם). הוא נותן את מספר השגיאות הקטן ביותר האפשרי, אבל הוא צריך את העתיד ולכן אי אפשר לבנות אותו. הוא קנה המידה שמודדים אליו את האחרים.</p>
<pre>3 frames, references 3 2 1 3 4 1 2
3 f  2 f  1 f  [3 2 1]
3 hit
4 fault: the rest is "1 2". Page 3 is never used again -> evict 3   [2 1 4]
1 hit
2 hit
-> 4 faults</pre>
<p>שיטה: בכל שגיאה מסתכלים <b>ימינה</b> במחרוזת ההפניות; הקורבן הוא הדף שנמצא בזיכרון והשימוש הבא בו מאוחר ביותר, או שלא מופיע יותר.</p>
"""),
    [
        Q(("Count the page faults under the optimal algorithm.", "ספרו את שגיאות הדף באלגוריתם האופטימלי."),
          ["9", "12", "15", "8"],
          ("Always evicting the page needed farthest ahead gives 9 faults.", "פינוי תמידי של הדף שנדרש הכי רחוק קדימה נותן 9 שגיאות."),
          ("OPT on the classic string: 9.", "OPT על המחרוזת הקלאסית: 9."),
          code=refs_code(CL, 3), check=R("OPT", CL, 3, "faults")),
        Q(("Under OPT, which page is evicted when page 4 is referenced?", "ב-OPT, איזה דף מפונה כשפונים להפניה 4?"),
          ["3", "1", "2", "4"],
          ("The remaining references are 1, 2; page 3 is never used again.", "ההפניות שנותרו הן 1, 2; דף 3 לא ישמש עוד."),
          ("Look to the right for the latest next use.", "מסתכלים ימינה על השימוש הבא המאוחר ביותר."),
          code=refs_code(D, 3), check=R("OPT", D, 3, "victim:4")),
        Q(("Which page does the optimal page-replacement algorithm choose as victim?", "איזה דף בוחר אלגוריתם ההחלפה האופטימלי כקורבן?"),
          [("The page used farthest in the future", "הדף שישמש הכי מאוחר בעתיד"), ("The page used least recently", "הדף ששימש הכי מזמן"),
           ("The oldest loaded page", "הדף הוותיק ביותר בזיכרון"), ("A random page", "דף אקראי")],
          ("OPT looks forward, not backward.", "OPT מסתכל קדימה, לא אחורה."),
          ("OPT = farthest in the future.", "OPT = הכי רחוק בעתיד."),
          exam="2019B-8", has="farthest"),
        Q(("Why can the optimal algorithm not be implemented in a real OS?", "מדוע אי אפשר לממש את האלגוריתם האופטימלי במערכת הפעלה אמיתית?"),
          [("It needs to know future references", "הוא צריך לדעת הפניות עתידיות"), ("It needs a special disk", "הוא צריך דיסק מיוחד"),
           ("It always thrashes", "הוא תמיד גורם לתזזית"), ("It only works with one frame", "הוא עובד רק עם מסגרת אחת")],
          ("The OS cannot know which pages the program will touch next.", "המערכת לא יודעת לאילו דפים התוכנית תיגש בהמשך."),
          ("OPT needs the future, so it is only a benchmark.", "OPT צריך את העתיד, ולכן הוא רק קנה מידה.")),
        Q(("Count the page faults under the optimal algorithm.", "ספרו את שגיאות הדף באלגוריתם האופטימלי."),
          ["4", "6", "5", "3"],
          ("1, 2, 3 and 4 fault; evicting 3 (never used again) lets the later 1 and 2 hit. FIFO needs 6 here.", "1, 2, 3 ו-4 גורמים לשגיאה; פינוי 3 (שלא ישמש עוד) גורם לכך ש-1 ו-2 המאוחרים פוגעים. FIFO צריך כאן 6."),
          ("OPT can never be worse than FIFO or LRU.", "OPT לעולם לא גרוע מ-FIFO או LRU."),
          code=refs_code(E, 3), check=R("OPT", E, 3, "faults")),
    ], icon="🔮")

# ------------------------------------------------------------------ level 5
L5 = Lv(
    ("More frames, more faults? Belady's anomaly", "יותר מסגרות, יותר שגיאות? האנומליה של Belady"),
    ("Why only FIFO can get worse with more memory.", "מדוע רק FIFO יכול להחמיר עם יותר זיכרון."),
    ("""
<p>Intuition says more frames means fewer or equal faults. <b>FIFO</b> can break this: on the string below, 3 frames give 9 faults but 4 frames give <b>10</b>. This is <b>Belady's anomaly</b>.</p>
<pre>references 1 2 3 4 1 2 5 1 2 3 4 5
FIFO  3 frames: 9 faults     4 frames: 10 faults   (anomaly)
LRU   3 frames: 10 faults    4 frames: 8 faults
</pre>
<p>LRU and OPT are <b>stack algorithms</b>: the pages held with n frames are always a subset of those held with n+1 frames, so they are immune. The anomaly is a FIFO-only trap.</p>
""", """
<p>האינטואיציה אומרת שיותר מסגרות פירושו פחות שגיאות או שווה. <b>FIFO</b> יכול לשבור את זה: במחרוזת שלמטה 3 מסגרות נותנות 9 שגיאות אבל 4 מסגרות נותנות <b>10</b>. זו <b>האנומליה של Belady</b>.</p>
<pre>references 1 2 3 4 1 2 5 1 2 3 4 5
FIFO  3 frames: 9 faults     4 frames: 10 faults   (anomaly)
LRU   3 frames: 10 faults    4 frames: 8 faults
</pre>
<p>LRU ו-OPT הם <b>אלגוריתמי מחסנית (stack algorithms)</b>: הדפים שמוחזקים עם n מסגרות הם תמיד תת-קבוצה של אלה שמוחזקים עם n+1 מסגרות, ולכן הם חסינים. האנומליה היא מלכודת של FIFO בלבד.</p>
"""),
    [
        Q(("Count the page faults under FIFO with 3 frames.", "ספרו את שגיאות הדף ב-FIFO עם 3 מסגרות."),
          ["9", "10", "12", "7"],
          ("Faults on 1 2 3 4 1 2 5 3 4: nine.", "שגיאות על 1 2 3 4 1 2 5 3 4: תשע."),
          ("Count carefully, the oldest page leaves first.", "סופרים בזהירות, הוותיק יוצא ראשון."),
          code=refs_code(BEL, 3), check=R("FIFO", BEL, 3, "faults")),
        Q(("Same string, FIFO with **4** frames. How many page faults?", "אותה מחרוזת, FIFO עם **4** מסגרות. כמה שגיאות דף?"),
          ["10", "9", "8", "6"],
          ("With 4 frames FIFO faults 10 times, more than with 3.", "עם 4 מסגרות FIFO גורם ל-10 שגיאות, יותר מאשר עם 3."),
          ("More frames can mean more FIFO faults.", "יותר מסגרות יכולות להביא יותר שגיאות ב-FIFO."),
          code=refs_code(BEL, 4), check=R("FIFO", BEL, 4, "faults")),
        Q(("FIFO gives 9 faults with 3 frames and 10 faults with 4 frames on the same string. What is this called?", "FIFO נותן 9 שגיאות עם 3 מסגרות ו-10 שגיאות עם 4 מסגרות על אותה מחרוזת. איך קוראים לזה?"),
          [("Belady's anomaly", "האנומליה של Belady"), ("Thrashing", "תזזית"), ("The convoy effect", "אפקט השיירה"), ("Internal fragmentation", "פיצול פנימי")],
          ("More memory causing more faults is Belady's anomaly.", "יותר זיכרון שגורם ליותר שגיאות הוא האנומליה של Belady."),
          ("More frames, more faults = Belady.", "יותר מסגרות, יותר שגיאות = Belady."),
          check=[R("FIFO", BEL, 3, "faults", want="9"), R("FIFO", BEL, 4, "faults", want="10")]),
        Q(("Same string, LRU with 4 frames. How many page faults?", "אותה מחרוזת, LRU עם 4 מסגרות. כמה שגיאות דף?"),
          ["8", "10", "9", "12"],
          ("LRU improves from 10 faults (3 frames) to 8 (4 frames): it has no anomaly.", "LRU משתפר מ-10 שגיאות (3 מסגרות) ל-8 (4 מסגרות): אין לו אנומליה."),
          ("Stack algorithms never get worse with more frames.", "אלגוריתמי מחסנית לא מחמירים עם יותר מסגרות."),
          code=refs_code(BEL, 4), check=R("LRU", BEL, 4, "faults")),
        Q(("Which page-replacement algorithm can suffer Belady's anomaly, where more frames cause more page faults?", "איזה אלגוריתם החלפת דפים עלול לסבול מהאנומליה של Belady, שבה יותר מסגרות גורמות ליותר שגיאות?"),
          ["FIFO", "LRU", "Optimal", "None of them"],
          ("Only FIFO; LRU and OPT are stack algorithms.", "רק FIFO; LRU ו-OPT הם אלגוריתמי מחסנית."),
          ("Belady = FIFO only.", "Belady = רק FIFO."),
          exam="2023A-8", has="fifo"),
    ], icon="📉")

# ------------------------------------------------------------------ level 6
L6 = Lv(
    ("Clock, reference bits, local allocation, thrashing", "Clock, ביטי התייחסות, הקצאה מקומית ותזזית"),
    ("The practical algorithm and what goes wrong.", "האלגוריתם המעשי ומה משתבש."),
    ("""
<p><b>Clock</b> (second chance) approximates LRU with a <b>reference bit</b> per frame. Frames form a circle with a hand:</p>
<pre>hand at A: R=1 -> second chance: clear R to 0, move on
hand at B: R=1 -> clear R to 0, move on
hand at C: R=0 -> VICTIM
worst case the hand passes all N frames: O(N)</pre>
<p>Who touches the bit: the <b>MMU (hardware) sets</b> the reference bit (and the dirty bit) on an access; the <b>OS clears</b> the reference bit while sweeping.</p>
<p><b>Local allocation</b>: a process may evict only its own pages, so a fault of process X evicts a page of X. Global allocation may evict anyone's page.</p>
<p><b>Thrashing</b>: processes need more frames than exist, so the system spends most of its time swapping pages instead of running. At process exit, its frames are simply freed (even dirty pages are not written back).</p>
""", """
<p><b>Clock</b> (הזדמנות שנייה) מקרב את LRU בעזרת <b>ביט התייחסות</b> לכל מסגרת. המסגרות מסודרות במעגל עם מחוג:</p>
<pre>hand at A: R=1 -> second chance: clear R to 0, move on
hand at B: R=1 -> clear R to 0, move on
hand at C: R=0 -> VICTIM
worst case the hand passes all N frames: O(N)</pre>
<p>מי נוגע בביט: ה-<b>MMU (חומרה) קובע</b> את ביט ההתייחסות (ואת ביט ה-dirty) בגישה; ה-<b>OS מאפס</b> את ביט ההתייחסות בזמן הסריקה.</p>
<p><b>הקצאה מקומית (local)</b>: תהליך יכול לפנות רק דפים משלו, ולכן שגיאה של תהליך X מפנה דף של X. הקצאה גלובלית יכולה לפנות דף של כל אחד.</p>
<p><b>תזזית (thrashing)</b>: התהליכים צריכים יותר מסגרות ממה שקיים, ולכן המערכת מבלה את רוב הזמן בהחלפת דפים במקום בריצה. כשתהליך מסתיים, המסגרות שלו פשוט משוחררות (גם דפים מלוכלכים לא נכתבים חזרה).</p>
"""),
    [
        Q(("What is the worst-case time complexity of finding a victim in Clock with N frames?", "מהי סיבוכיות הזמן במקרה הגרוע למציאת קורבן ב-Clock עם N מסגרות?"),
          ["O(N)", "O(1)", "O(log N)", "O(N²)"],
          ("The hand may have to pass every frame once.", "ייתכן שהמחוג יצטרך לעבור על כל מסגרת פעם אחת."),
          ("Clock victim search = O(N).", "חיפוש קורבן ב-Clock = O(N)."),
          exam="2019A-8", has="o("),
        Q(("In the Clock algorithm, who writes 0 to the reference bit?", "באלגוריתם Clock, מי כותב 0 לביט ההתייחסות?"),
          [("The operating system", "מערכת ההפעלה"), ("The MMU hardware", "חומרת ה-MMU"), ("The user program", "תוכנית המשתמש"), ("The disk controller", "בקר הדיסק")],
          ("The OS clears it while sweeping; the hardware only sets it.", "ה-OS מאפס אותו בסריקה; החומרה רק קובעת אותו."),
          ("OS clears, hardware sets.", "ה-OS מאפס, החומרה קובעת."),
          exam="2019B-5", has="operating"),
        Q(("When the accessed (reference) bit needs to be set, who sets it?", "כשצריך לקבוע את ביט הגישה (ההתייחסות), מי קובע אותו?"),
          [("The MMU (hardware)", "ה-MMU (חומרה)"), ("The operating system", "מערכת ההפעלה"), ("The user process", "תהליך המשתמש"), ("The swap daemon", "תהליך ה-swap")],
          ("Setting it on each access must be automatic, so the MMU does it.", "קביעה בכל גישה חייבת להיות אוטומטית, ולכן ה-MMU עושה זאת."),
          ("MMU sets the reference and dirty bits.", "ה-MMU קובע את ביטי ההתייחסות וה-dirty."),
          exam="2017SB-6", has="mmu"),
        Q(("What does Clock do to a frame whose reference bit is set?", "מה Clock עושה למסגרת שביט ההתייחסות שלה דלוק?"),
          [("Clears the bit and moves on (second chance)", "מאפס את הביט וממשיך (הזדמנות שנייה)"), ("Evicts it immediately", "מפנה אותה מיד"),
           ("Writes it to disk", "כותב אותה לדיסק"), ("Sets the dirty bit", "קובע את ביט ה-dirty")],
          ("A referenced page gets a second chance.", "דף שהתייחסו אליו מקבל הזדמנות שנייה."),
          ("Bit set: clear it and skip.", "ביט דלוק: מאפסים ומדלגים."),
          exam="2021B-10", has="clear"),
        Q(("Each process must evict others' pages to reload its own, so the system spends most of its time swapping. What is this state?", "כל תהליך צריך לפנות דפים של אחרים כדי לטעון את שלו, והמערכת מבלה את רוב הזמן בהחלפות. איזה מצב זה?"),
          [("Thrashing", "תזזית (thrashing)"), ("Starvation", "הרעבה"), ("Deadlock", "קיפאון"), ("Convoy effect", "אפקט השיירה")],
          ("Too little memory for the demand: thrashing.", "מעט מדי זיכרון ביחס לביקוש: תזזית."),
          ("Constant swapping = thrashing.", "החלפות בלתי פוסקות = תזזית."),
          exam="2017A-8", has="thrashing"),
        Q(("Under local allocation, whose page is evicted when a page must be brought in for process X?", "בהקצאה מקומית, דף של מי מפונה כשצריך להביא דף עבור תהליך X?"),
          [("A page of process X", "דף של תהליך X"), ("A page of any process", "דף של כל תהליך"), ("The oldest process's page", "דף של התהליך הוותיק"), ("A kernel page", "דף של הליבה")],
          ("Local allocation confines eviction to the faulting process.", "הקצאה מקומית מגבילה את הפינוי לתהליך שגרם לשגיאה."),
          ("Local = evict own page.", "מקומי = מפנים דף משלו."),
          exam="2021A-10", has="x"),
    ], icon="🕐")

# ------------------------------------------------------------------ level 7
L7 = Lv(
    ("Boss: page replacement exam", "בוס: מבחן החלפת דפים"),
    ("Past-exam items and a full simulation.", "שאלות ממבחנים קודמים וסימולציה מלאה."),
    ("""
<p>Exam level. Keep three images in mind: OPT looks right (future), LRU looks left (past), FIFO looks at load time. Only FIFO has Belady's anomaly. Clock: hardware sets, OS clears, O(N). 80% passes.</p>
""", """
<p>שלב המבחן. שלוש תמונות לזכור: OPT מסתכל ימינה (עתיד), LRU מסתכל שמאלה (עבר), FIFO מסתכל על זמן הטעינה. רק ל-FIFO יש את האנומליה של Belady. Clock: חומרה קובעת, OS מאפס, O(N). 80% עובר.</p>
"""),
    [
        Q(("Which algorithm can have **more** page faults when given **more** frames?", "איזה אלגוריתם יכול לגרום ל**יותר** שגיאות כשנותנים לו **יותר** מסגרות?"),
          ["FIFO", "LRU", "Optimal", "Clock with a reference bit only"],
          ("FIFO suffers Belady's anomaly.", "FIFO סובל מהאנומליה של Belady."), ("Belady = FIFO.", "Belady = רק FIFO."),
          exam="2023A-8", has="fifo"),
        Q(("Which page does the optimal algorithm evict?", "איזה דף האלגוריתם האופטימלי מפנה?"),
          [("The one used farthest in the future", "זה שישמש הכי רחוק בעתיד"), ("The one used longest ago", "זה ששימש הכי מזמן"), ("The one loaded first", "זה שנטען ראשון"), ("The one with the dirty bit set", "זה שביט ה-dirty שלו דלוק")],
          ("OPT is defined by the future.", "OPT מוגדר לפי העתיד."), ("OPT = farthest next use.", "OPT = השימוש הבא הרחוק ביותר."),
          exam="2019B-8", has="farthest"),
        Q(("The OS spends most of its time swapping pages instead of running processes. What is this state called?", "מערכת ההפעלה מבלה את רוב זמנה בהחלפת דפים במקום בהרצת תהליכים. איך נקרא המצב?"),
          ["Thrashing", "Starvation", "Aging", "Convoy"],
          ("Thrashing.", "תזזית (thrashing)."), ("Swapping all the time = thrashing.", "החלפות כל הזמן = תזזית."),
          exam="2024A-8", has="thrashing"),
        Q(("What is the worst-case complexity of finding a victim in Clock with n frames?", "מהי הסיבוכיות במקרה הגרוע של מציאת קורבן ב-Clock עם n מסגרות?"),
          ["O(n)", "O(1)", "O(n log n)", "O(2^n)"],
          ("One full sweep of the hand.", "סריקה מלאה אחת של המחוג."), ("Clock = O(n).", "Clock = סריקה אחת, O(n)."),
          exam="2024B-8", has="o("),
        Q(("Count the page faults under LRU.", "ספרו את שגיאות הדף ב-LRU."),
          ["8", "10", "9", "7"],
          ("Simulating LRU with 4 frames gives 8 faults.", "סימולציית LRU עם 4 מסגרות נותנת 8 שגיאות."), ("Refresh on a hit, evict the oldest use.", "מרעננים בפגיעה, מפנים את השימוש הוותיק."),
          code="frames: 4\nreferences: 1 2 3 4 1 2 5 1 2 3 4 5", check=R("LRU", BEL, 4, "faults")),
        Q(("Count the page faults under FIFO.", "ספרו את שגיאות הדף ב-FIFO."),
          ["14", "10", "8", "12"],
          ("FIFO makes 14 faults here; LRU 10 and OPT 8.", "FIFO עושה כאן 14 שגיאות; LRU 10 ו-OPT 8."), ("Queue order never changes on a hit.", "סדר התור לא משתנה בפגיעה."),
          code="frames: 4\nreferences: 1 2 3 4 2 1 5 6 2 1 2 3 7 6 3 2 1 2 3 6",
          check=R("FIFO", [1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3, 2, 1, 2, 3, 6], 4, "faults")),
    ], icon="🏆", boss=True)

COURSE = Course(
    "vmem", "💾",
    ("Demand paging and page replacement", "דפדוף לפי דרישה והחלפת דפים"),
    ("When RAM is full the OS must pick a victim. This course starts from what a page fault is, then simulates FIFO, LRU and the optimal algorithm on reference strings, explains Belady's anomaly, and ends with Clock, local allocation and thrashing. Every level is open; 80% passes.",
     "כשה-RAM מלא מערכת ההפעלה חייבת לבחור קורבן. הקורס מתחיל ממה זו שגיאת דף, ממשיך לסימולציות של FIFO, LRU והאלגוריתם האופטימלי על מחרוזות הפניות, מסביר את האנומליה של Belady ומסיים ב-Clock, הקצאה מקומית ותזזית. כל השלבים פתוחים; 80% עובר."),
    "replacement", [L1, L2, L3, L4, L5, L6, L7])
