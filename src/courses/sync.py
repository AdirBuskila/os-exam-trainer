# -*- coding: utf-8 -*-
"""Course 4: synchronization, semaphores and deadlock."""
from _kit import Q, Lv, Course


def M(init, ops, ask, want=None):
    d = dict(k="sem", init=init, ops=ops, ask=ask)
    if want is not None:
        d["want"] = want
    return d


def DL(procs=None, n=None, ordered=False, want="deadlock"):
    d = dict(k="dead", want=want)
    if n is not None:
        d["n"] = n
        d["ordered"] = ordered
    else:
        d["procs"] = procs
    return d


# ------------------------------------------------------------------ level 1
L1 = Lv(
    ("Race conditions and the critical section", "מצבי תחרות וקטע קריטי"),
    ("The three conditions every solution must meet.", "שלושת התנאים שכל פתרון חייב לעמוד בהם."),
    ("""
<p>When several processes read and write shared data and the result depends on who runs first, that is a <b>race condition</b>. The code that touches the shared data is the <b>critical section</b>. A correct solution must give three things:</p>
<table>
<tr><th>Condition</th><th>Meaning</th></tr>
<tr><td>Mutual exclusion</td><td>only one process is inside at a time</td></tr>
<tr><td>Progress</td><td>if nobody is inside, someone who wants to enter gets in: no deadlock</td></tr>
<tr><td>Bounded waiting</td><td>a limit on how many others enter before a waiting process does; without it, <b>starvation</b> is possible</td></tr>
</table>
<p>Related words: <b>busy waiting</b> is when a process burns CPU time repeatedly checking whether it may enter; <b>starvation</b> is when a process is passed over again and again and never enters (the consequence of missing bounded waiting); <b>deadlock</b> is when no process manages to enter at all.</p>
""", """
<p>כשכמה תהליכים קוראים וכותבים נתונים משותפים והתוצאה תלויה במי רץ ראשון, זה <b>מצב תחרות (race condition)</b>. הקוד שנוגע בנתונים המשותפים הוא ה<b>קטע הקריטי</b>. פתרון נכון חייב לספק שלושה דברים:</p>
<table>
<tr><th>תנאי</th><th>משמעות</th></tr>
<tr><td>הדדיות (Mutual exclusion)</td><td>רק תהליך אחד בפנים בכל רגע</td></tr>
<tr><td>התקדמות (Progress)</td><td>אם אף אחד לא בפנים, מי שרוצה להיכנס נכנס: אין קיפאון</td></tr>
<tr><td>המתנה חסומה (Bounded waiting)</td><td>חסם על כמה אחרים נכנסים לפני תהליך ממתין; בלעדיו אפשרית <b>הרעבה</b></td></tr>
</table>
<p>מושגים קשורים: <b>המתנה פעילה (busy waiting)</b> היא כשתהליך שורף זמן מעבד ובודק שוב ושוב אם מותר לו להיכנס; <b>הרעבה (starvation)</b> היא כשתהליך נדחה שוב ושוב ולעולם לא נכנס (תוצאה של היעדר המתנה חסומה); <b>קיפאון (deadlock)</b> הוא כשאף תהליך לא מצליח להיכנס בכלל.</p>
"""),
    [
        Q(("Concurrent access to a shared resource gives results that depend on the order of execution. What is this state called?", "גישה במקביל למשאב משותף נותנת תוצאות שתלויות בסדר הריצה. איך נקרא המצב?"),
          [("Race condition", "מצב תחרות (race condition)"), ("Deadlock", "קיפאון"), ("Thrashing", "תזזית"), ("Aging", "הזדקנות")],
          ("An order-dependent result is a race condition.", "תוצאה שתלויה בסדר היא מצב תחרות."),
          ("Order-dependent result = race condition.", "תוצאה תלוית סדר = מצב תחרות."),
          exam="2024B-5", has="race"),
        Q(("Which critical-section condition requires exclusive access while one process writes shared memory?", "איזה תנאי של הקטע הקריטי דורש גישה בלעדית בזמן שתהליך אחד כותב לזיכרון משותף?"),
          [("Mutual exclusion", "הדדיות"), ("Progress", "התקדמות"), ("Bounded waiting", "המתנה חסומה"), ("Fairness", "הוגנות")],
          ("Exclusive access is exactly mutual exclusion.", "גישה בלעדית היא בדיוק הדדיות."),
          ("Only one inside = mutual exclusion.", "רק אחד בפנים = הדדיות."),
          exam="2021A-6", has="mutual"),
        Q(("Which condition bounds how many processes may enter before a given waiting process?", "איזה תנאי חוסם כמה תהליכים נכנסים לפני תהליך ממתין מסוים?"),
          [("Bounded waiting", "המתנה חסומה"), ("Mutual exclusion", "הדדיות"), ("Progress", "התקדמות"), ("Atomicity", "אטומיות")],
          ("Bounded waiting limits the overtaking.", "המתנה חסומה מגבילה את העקיפות."),
          ("Limit on overtaking = bounded waiting.", "הגבלת עקיפות = המתנה חסומה."),
          exam="2020A-8", has="bounded"),
        Q(("Which critical-section condition guarantees that no deadlock occurs?", "איזה תנאי של הקטע הקריטי מבטיח שלא יתרחש קיפאון?"),
          [("Progress", "התקדמות"), ("Mutual exclusion", "הדדיות"), ("Bounded waiting", "המתנה חסומה"), ("Busy waiting", "המתנה פעילה")],
          ("Progress: if the section is free, someone who wants in gets in.", "התקדמות: אם הקטע פנוי, מי שרוצה להיכנס נכנס."),
          ("No deadlock = progress.", "אין קיפאון = התקדמות."),
          exam="2021B-6", has="progress"),
        Q(("Process A cannot progress because B is in the critical section, so A wastes CPU time repeatedly checking whether it may enter. What is this called?", "תהליך A לא יכול להתקדם כי B בקטע הקריטי, ולכן A מבזבז זמן מעבד בבדיקות חוזרות אם מותר לו להיכנס. איך זה נקרא?"),
          [("Busy waiting", "המתנה פעילה"), ("Starvation", "הרעבה"), ("Deadlock", "קיפאון"), ("Context switching", "החלפת הקשר")],
          ("Spinning on a check burns CPU: busy waiting.", "ספינינג על בדיקה שורף מעבד: המתנה פעילה."),
          ("Checking in a loop = busy waiting.", "בדיקה בלולאה = המתנה פעילה."),
          exam="2015A-3", has="busy"),
        Q(("One process, or a group, is continually passed over by others entering the critical section and never enters. What is this called?", "תהליך אחד, או קבוצה, נדחה שוב ושוב על ידי אחרים שנכנסים לקטע הקריטי ולעולם לא נכנס. איך זה נקרא?"),
          [("Starvation", "הרעבה"), ("Busy waiting", "המתנה פעילה"), ("Race condition", "מצב תחרות"), ("Deadlock", "קיפאון")],
          ("Being passed over forever is starvation; a deadlock would block everyone.", "דחייה לנצח היא הרעבה; קיפאון היה חוסם את כולם."),
          ("Passed over forever = starvation.", "נדחה לנצח = הרעבה."),
          exam="2015A-4", has="starvation"),
    ], icon="🚧")

# ------------------------------------------------------------------ level 2
L2 = Lv(
    ("Semaphores: wait, signal and the value", "סמפורים: wait, signal והערך"),
    ("What the number inside a semaphore means.", "מה המספר בתוך סמפור אומר."),
    ("""
<p>A <b>semaphore</b> in kernel memory holds an <b>integer</b> and a <b>queue</b> of waiting processes. Two atomic operations:</p>
<ul>
<li><b>wait</b> (P): subtract 1. If the value became <b>negative</b>, the process is added to the queue and sleeps.</li>
<li><b>signal</b> (V): add 1. If the value is still <b>not positive</b>, one process is removed from the queue and made ready.</li>
</ul>
<p>So a negative value means "|value| processes are waiting". Starting values that matter:</p>
<ul>
<li><b>1</b> for mutual exclusion (one process allowed in; ten processes sharing a variable also use 1);</li>
<li><b>0</b> for ordering: to make F of process A run before G of process B, B does wait before G, A does signal after F, and the semaphore starts at 0;</li>
<li><b>N</b> for N identical resources (counting semaphore).</li>
</ul>
<pre>init 1:  P:A  -> 0 (A in)    P:B -> -1 (B waits)    P:C -> -2 (C waits)
         V:D  -> -1 (one waiter wakes)</pre>
""", """
<p><b>סמפור (semaphore)</b> בזיכרון הליבה מחזיק <b>מספר שלם</b> ו<b>תור</b> של תהליכים ממתינים. שתי פעולות אטומיות:</p>
<ul>
<li><b>wait</b> (P): מחסירים 1. אם הערך נעשה <b>שלילי</b>, התהליך נכנס לתור והולך לישון.</li>
<li><b>signal</b> (V): מוסיפים 1. אם הערך עדיין <b>לא חיובי</b>, תהליך אחד יוצא מהתור והופך למוכן.</li>
</ul>
<p>לכן ערך שלילי אומר "|ערך| תהליכים ממתינים". ערכי התחלה שחשובים:</p>
<ul>
<li><b>1</b> להדדיות (תהליך אחד נכנס; גם עשרה תהליכים שחולקים משתנה משתמשים ב-1);</li>
<li><b>0</b> לסדר: כדי ש-F של תהליך A ירוץ לפני G של תהליך B, ‏B עושה wait לפני G, ‏A עושה signal אחרי F, והסמפור מתחיל ב-0;</li>
<li><b>N</b> ל-N משאבים זהים (סמפור סופר).</li>
</ul>
<pre>init 1:  P:A  -> 0 (A in)    P:B -> -1 (B waits)    P:C -> -2 (C waits)
         V:D  -> -1 (one waiter wakes)</pre>
"""),
    [
        Q(("To what value is a semaphore initialised when it solves the critical-section problem (ten processes must not modify shared memory together)?", "לאיזה ערך מאתחלים סמפור שפותר את בעיית הקטע הקריטי (עשרה תהליכים לא צריכים לשנות זיכרון משותף יחד)?"),
          ["1", "0", "10", "-1"],
          ("1 lets exactly one process in.", "הערך 1 מכניס בדיוק תהליך אחד."),
          ("Mutual exclusion semaphore starts at 1.", "סמפור להדדיות מתחיל ב-1."),
          exam="2017SB-9", has="1"),
        Q(("To make function F of process A run before function G of process B, you use a semaphore initialised to ____.", "כדי לגרום לפונקציה F של תהליך A לרוץ לפני פונקציה G של תהליך B משתמשים בסמפור שמאותחל ל-____."),
          ["0", "1", "2", "-1"],
          ("B's wait blocks until A signals after F, so it must start at 0.", "ה-wait של B חוסם עד ש-A עושה signal אחרי F, ולכן הוא חייב להתחיל ב-0."),
          ("Ordering semaphore starts at 0.", "סמפור לסדר מתחיל ב-0."),
          exam="2017SA-10", has="0"),
        Q(("A semaphore starts at 1 and three processes A, B, C each do wait. What are the value and the number of sleeping processes?", "סמפור מתחיל ב-1 ושלושה תהליכים A, B, C עושים כל אחד wait. מהם הערך ומספר התהליכים הישנים?"),
          [("Value -2, two sleeping", "ערך -2, שני תהליכים ישנים"), ("Value -3, three sleeping", "ערך -3, שלושה ישנים"), ("Value 2, none sleeping", "ערך 2, אף אחד לא ישן"), ("Value -1, one sleeping", "ערך -1, אחד ישן")],
          ("1 → 0 (A enters) → −1 (B sleeps) → −2 (C sleeps).", "1 ← 0 (A נכנס) ← ‎-1 (B ישן) ← ‎-2 (C ישן)."),
          ("Negative value = number of sleepers.", "ערך שלילי = מספר הישנים."),
          check=[M(1, "P:A P:B P:C", "value", want="-2"), M(1, "P:A P:B P:C", "waiting", want="2")]),
        Q(("A semaphore starts at 1. Three processes do wait and then a fourth does signal. What is the value?", "סמפור מתחיל ב-1. שלושה תהליכים עושים wait ואז רביעי עושה signal. מהו הערך?"),
          ["-1", "-2", "0", "1"],
          ("After three waits the value is −2; the signal adds 1 and wakes one sleeper: −1.", "אחרי שלושה wait הערך ‎-2; ה-signal מוסיף 1 ומעיר ישן אחד: ‎-1."),
          ("signal adds 1.", "signal מוסיף 1."),
          check=M(1, "P:A P:B P:C V:D", "value")),
        Q(("A semaphore's kernel allocation holds an integer and, in addition, what?", "ההקצאה של סמפור בליבה מחזיקה מספר שלם ובנוסף מה?"),
          [("A queue of waiting processes", "תור של תהליכים ממתינים"), ("A copy of the shared data", "עותק של הנתונים המשותפים"), ("The owner's PID only", "רק את ה-PID של הבעלים"), ("A timer", "טיימר")],
          ("The queue is how a sleeping process is found and woken, which also prevents starvation.", "התור הוא הדרך למצוא ולהעיר תהליך ישן, והוא גם מונע הרעבה."),
          ("Semaphore = integer + queue.", "סמפור = מספר שלם + תור."),
          exam="2015A-5", has="queue"),
        Q(("A wait makes the semaphore value negative. What does the kernel additionally do?", "פעולת wait הופכת את ערך הסמפור לשלילי. מה הליבה עושה בנוסף?"),
          [("Adds the process to the semaphore's wait queue", "מוסיפה את התהליך לתור ההמתנה של הסמפור"), ("Terminates the process", "מסיימת את התהליך"), ("Resets the value to 0", "מאפסת את הערך ל-0"), ("Busy-waits for it", "ממתינה בהמתנה פעילה")],
          ("The process sleeps in the queue until a signal.", "התהליך ישן בתור עד signal."),
          ("Negative: enqueue and sleep.", "שלילי: להיכנס לתור ולישון."),
          exam="2017A-6", has="queue"),
    ], icon="🚦")

# ------------------------------------------------------------------ level 3
L3 = Lv(
    ("Linux semaphores: semget, semop, semctl", "סמפורים ב-Linux: semget, semop, semctl"),
    ("The three system calls and what they really do.", "שלוש קריאות המערכת ומה הן באמת עושות."),
    ("""
<table>
<tr><th>Call</th><th>What it does</th></tr>
<tr><td><code>semget(key, n, flags)</code></td><td>creates an <b>array of n semaphores</b>; <code>semget(IPC_PRIVATE, 123, 0600)</code> gives 123 semaphores. The call decides the size of the array.</td></tr>
<tr><td><code>semop(sops, nsops)</code></td><td>does the wait and signal operations. One call can carry <b>many operations</b>, and they are done <b>atomically</b>.</td></tr>
<tr><td><code>semctl</code></td><td>initialises the values and also removes the semaphores (depending on its parameters).</td></tr>
</table>
<p>In <code>struct sembuf</code>, <code>sem_op = -1</code> is one wait, <code>sem_op = -10</code> is ten waits, <code>sem_op = +1</code> is a signal. Filling in <code>sem_op</code> does nothing until <code>semop()</code> is called. A wait on a semaphore whose value is 0 makes the process <b>sleep</b>. After the semaphores were removed with <code>semctl</code>, <code>semop</code> returns <b>-1</b>. A semaphore not removed explicitly stays until the computer reboots or crashes; the shell command <code>ipcrm -s 666</code> removes the set with id 666.</p>
<pre>wait on 5 semaphores and signal on 5 others, atomically:
one semop call with nsops = 10</pre>
""", """
<table>
<tr><th>קריאה</th><th>מה היא עושה</th></tr>
<tr><td><code>semget(key, n, flags)</code></td><td>יוצרת <b>מערך של n סמפורים</b>; ‏<code>semget(IPC_PRIVATE, 123, 0600)</code> נותנת 123 סמפורים. הקריאה קובעת את גודל המערך.</td></tr>
<tr><td><code>semop(sops, nsops)</code></td><td>מבצעת את פעולות ה-wait וה-signal. קריאה אחת יכולה לשאת <b>הרבה פעולות</b>, והן מתבצעות <b>אטומית</b>.</td></tr>
<tr><td><code>semctl</code></td><td>מאתחלת את הערכים וגם מוחקת את הסמפורים (לפי הפרמטרים).</td></tr>
</table>
<p>ב-<code>struct sembuf</code>, הערך <code>sem_op = -1</code> הוא wait אחד, ‏<code>sem_op = -10</code> הם עשרה wait, ו-<code>sem_op = +1</code> הוא signal. מילוי <code>sem_op</code> לא עושה דבר עד שקוראים ל-<code>semop()</code>. wait על סמפור שערכו 0 גורם לתהליך <b>לישון</b>. אחרי שהסמפורים נמחקו ב-<code>semctl</code>, הקריאה <code>semop</code> מחזירה <b>-1</b>. סמפור שלא נמחק במפורש נשאר עד שהמחשב עושה אתחול או קורס; פקודת הקונסולה <code>ipcrm -s 666</code> מוחקת את הקבוצה שמספרה 666.</p>
<pre>wait on 5 semaphores and signal on 5 others, atomically:
one semop call with nsops = 10</pre>
"""),
    [
        Q(("In Linux, which system call performs both the semaphore wait and the signal, depending on the values passed?", "ב-Linux, איזו קריאת מערכת מבצעת גם wait וגם signal על סמפור, לפי הערכים שמועברים?"),
          ["semop()", "semget()", "semctl()", "shmat()"],
          ("semop carries the operations; the sign of sem_op chooses wait or signal.", "semop נושאת את הפעולות; סימן sem_op בוחר בין wait ל-signal."),
          ("semop = wait and signal.", "semop = wait ו-signal."),
          exam="2026A-10", has="semop"),
        Q(("In struct sembuf, what value should sem_op have to perform 10 wait operations on a semaphore?", "ב-struct sembuf, איזה ערך צריך להיות ל-sem_op כדי לבצע 10 פעולות wait על סמפור?"),
          ["-10", "10", "-1 (ten times)", "0"],
          ("A negative sem_op subtracts: −10 is ten waits.", "sem_op שלילי מחסיר: ‎-10 הם עשרה wait."),
          ("Wait = negative sem_op.", "wait = sem_op שלילי."),
          exam="2015A-9", has="10"),
        Q(("What is allocated in the Linux kernel after `semget(IPC_PRIVATE, 123, 0600)`?", "מה מוקצה בליבה של Linux אחרי `semget(IPC_PRIVATE, 123, 0600)`?"),
          [("An array of 123 semaphores", "מערך של 123 סמפורים"), ("One semaphore with value 123", "סמפור אחד עם ערך 123"), ("123 bytes of shared memory", "123 בתים של זיכרון משותף"), ("A semaphore for process 123", "סמפור לתהליך 123")],
          ("The second argument is the number of semaphores in the array.", "הארגומנט השני הוא מספר הסמפורים במערך."),
          ("semget n = array size.", "n ב-semget = גודל המערך."),
          exam="2022A-10", has="123"),
        Q(("`sem_op = -1` is performed on a semaphore whose value is 0. What happens to the process?", "מבוצע `sem_op = -1` על סמפור שערכו 0. מה קורה לתהליך?"),
          [("It sleeps (blocks)", "הוא ישן (נחסם)"), ("semop returns an error at once", "semop מחזירה שגיאה מיד"), ("The value becomes 1", "הערך נעשה 1"), ("The process is killed", "התהליך נהרג")],
          ("A wait on 0 cannot proceed, so the process sleeps in the queue.", "wait על 0 לא יכול להמשיך, ולכן התהליך ישן בתור."),
          ("Wait on 0 = sleep.", "wait על 0 = שינה."),
          exam="2024B-10", has="sleep"),
        Q(("What happens in Linux if semop is called on a semaphore after it was deleted with semctl?", "מה קורה ב-Linux אם קוראים ל-semop על סמפור אחרי שנמחק ב-semctl?"),
          [("semop returns -1", "semop מחזירה ‎-1"), ("It recreates the semaphore", "היא יוצרת מחדש את הסמפור"), ("It blocks forever", "היא נחסמת לנצח"), ("It succeeds as usual", "היא מצליחה כרגיל")],
          ("The semaphore no longer exists, so the call fails with −1.", "הסמפור כבר לא קיים, ולכן הקריאה נכשלת עם ‎-1."),
          ("Deleted semaphore: semop = −1.", "סמפור שנמחק: semop = ‎-1."),
          exam="2022B-10", has="-1"),
        Q(("Besides deleting semaphores, what other operation does the semctl system call perform?", "מלבד מחיקת סמפורים, איזו פעולה נוספת מבצעת קריאת המערכת semctl?"),
          [("Initialising the semaphore values", "אתחול ערכי הסמפורים"), ("Waiting on a semaphore", "ביצוע wait על סמפור"), ("Creating the semaphore array", "יצירת מערך הסמפורים"), ("Attaching shared memory", "חיבור זיכרון משותף")],
          ("semctl sets the initial values; semget creates and semop waits/signals.", "semctl קובעת ערכי התחלה; semget יוצרת ו-semop עושה wait/signal."),
          ("semctl = initialise + remove.", "semctl = אתחול + מחיקה."),
          exam="2023B-10", has="initializ"),
    ], icon="🐧")

# ------------------------------------------------------------------ level 4
L4 = Lv(
    ("Producer-consumer and readers-writers", "יצרן-צרכן וקוראים-כותבים"),
    ("Reading the value of a semaphore as a story.", "קריאת ערך הסמפור כסיפור."),
    ("""
<p><b>Bounded buffer</b> (producer-consumer) uses three semaphores: <code>mutex = 1</code>, <code>empty = N</code> (free slots), <code>full = 0</code> (filled slots). The producer waits on <code>empty</code>, the consumer waits on <code>full</code>.</p>
<ul>
<li>A positive <code>empty</code> is the <b>number of empty slots</b>.</li>
<li>A negative <code>full</code> is the <b>number of consumers waiting</b> (the buffer is empty and they sleep).</li>
<li>A consumer starting on an empty buffer blocks, because <code>full</code> starts at 0.</li>
</ul>
<p><b>Readers-writers</b>: many readers may share the data, a writer needs it alone. While a writer is inside, <b>0 readers</b> may be inside. A reader leaving signals the writer only when <b>no readers remain</b>. The simple classroom solution can <b>starve</b> writers, so it violates bounded waiting.</p>
""", """
<p><b>חוצץ חסום (bounded buffer)</b> (יצרן-צרכן) משתמש בשלושה סמפורים: ‏<code>mutex = 1</code>, ‏<code>empty = N</code> (מקומות פנויים), ‏<code>full = 0</code> (מקומות מלאים). היצרן עושה wait על <code>empty</code>, הצרכן עושה wait על <code>full</code>.</p>
<ul>
<li>ערך חיובי של <code>empty</code> הוא <b>מספר המקומות הפנויים</b>.</li>
<li>ערך שלילי של <code>full</code> הוא <b>מספר הצרכנים הממתינים</b> (החוצץ ריק והם ישנים).</li>
<li>צרכן שמתחיל על חוצץ ריק נחסם, כי <code>full</code> מתחיל ב-0.</li>
</ul>
<p><b>קוראים-כותבים</b>: קוראים רבים יכולים לחלוק את הנתונים, וכותב צריך אותם לבד. כשכותב בפנים, <b>0 קוראים</b> יכולים להיות בפנים. קורא שיוצא מעיר כותב רק כש<b>לא נשארו קוראים</b>. הפתרון הפשוט מהכיתה יכול <b>להרעיב</b> כותבים, ולכן הוא מפר המתנה חסומה.</p>
"""),
    [
        Q(("In the bounded-buffer solution, a consumer starts on an empty buffer with `full = 0`. What happens when it does wait(full)?", "בפתרון החוצץ החסום, צרכן מתחיל על חוצץ ריק עם `full = 0`. מה קורה כשהוא עושה wait(full)?"),
          [("It blocks", "הוא נחסם"), ("It takes an item", "הוא לוקח פריט"), ("full becomes 1", "full הופך ל-1"), ("It deadlocks the producer", "הוא גורם לקיפאון ליצרן")],
          ("full is 0, so the wait makes it −1 and the consumer sleeps.", "full הוא 0, ולכן ה-wait מביא אותו ל-‎-1 והצרכן ישן."),
          ("Empty buffer: the consumer sleeps.", "חוצץ ריק: הצרכן ישן."),
          check=M(0, "P:C", "blocks:C", want="yes")),
        Q(("In the bounded-buffer solution, what does a positive value of the `empty` semaphore represent?", "בפתרון החוצץ החסום, מה מייצג ערך חיובי של הסמפור `empty`?"),
          [("The number of empty buffer slots", "מספר המקומות הפנויים בחוצץ"), ("The number of consumers waiting", "מספר הצרכנים הממתינים"), ("The number of filled slots", "מספר המקומות המלאים"), ("The number of producers", "מספר היצרנים")],
          ("empty counts free slots.", "empty סופר מקומות פנויים."),
          ("empty = free slots.", "empty = מקומות פנויים."),
          exam="2019A-5", has="empty"),
        Q(("Three consumers wait on `full` while the buffer is empty (`full` started at 0). What is its value, and what does the negative number mean?", "שלושה צרכנים עושים wait על `full` כשהחוצץ ריק (`full` התחיל ב-0). מהו הערך ומה משמעות המספר השלילי?"),
          [("-3: three consumers are waiting", "‎-3: שלושה צרכנים ממתינים"), ("-3: three items are missing in the producer", "‎-3: חסרים שלושה פריטים ביצרן"), ("3: three full slots", "3: שלושה מקומות מלאים"), ("0: nobody waits", "0: אף אחד לא ממתין")],
          ("0 − 3 = −3, and |−3| is the number of sleeping consumers.", "0 − 3 = ‎-3, ו-|‎-3| הוא מספר הצרכנים הישנים."),
          ("Negative full = waiting consumers.", "full שלילי = צרכנים ממתינים."),
          check=[M(0, "P:C1 P:C2 P:C3", "value", want="-3"), M(0, "P:C1 P:C2 P:C3", "waiting", want="3")], exam="2019B-4", has="consumers"),
        Q(("In readers-writers, what is the maximum number of readers allowed in the critical section while a writer is inside?", "בקוראים-כותבים, מהו המספר המרבי של קוראים המותרים בקטע הקריטי בזמן שכותב בפנים?"),
          ["0", "1", "As many as want", "Exactly one reader"],
          ("A writer needs exclusive access, so zero readers.", "כותב צריך גישה בלעדית, ולכן אפס קוראים."),
          ("Writer inside = no readers.", "כותב בפנים = אין קוראים."),
          exam="2021B-7", has="0"),
        Q(("The classroom readers-writers semaphore solution suffers from which problem?", "פתרון הסמפורים לקוראים-כותבים מהכיתה סובל מאיזו בעיה?"),
          [("Starvation", "הרעבה"), ("Race conditions", "מצבי תחרות"), ("Busy waiting", "המתנה פעילה"), ("Lost mutual exclusion", "אובדן הדדיות")],
          ("Steady readers can keep a writer out forever.", "קוראים רצופים יכולים להשאיר כותב בחוץ לנצח."),
          ("Readers-writers starves writers.", "קוראים-כותבים מרעיב כותבים."),
          exam="2015B-5", has="starvation"),
        Q(("In readers-writers, when does an exiting reader signal a writer to enter?", "בקוראים-כותבים, מתי קורא שיוצא מאותת לכותב להיכנס?"),
          [("When no readers remain inside", "כשלא נשארו קוראים בפנים"), ("Always on exit", "תמיד ביציאה"), ("When the buffer is full", "כשהחוצץ מלא"), ("When it is the first reader", "כשהוא הקורא הראשון")],
          ("Only the last reader out lets the writer in.", "רק הקורא האחרון שיוצא מכניס את הכותב."),
          ("Last reader out signals the writer.", "הקורא האחרון שיוצא מאותת לכותב."),
          exam="2022B-6", has="no readers"),
    ], icon="🏭")

# ------------------------------------------------------------------ level 5
L5 = Lv(
    ("Deadlock and the dining philosophers", "קיפאון והפילוסופים הסועדים"),
    ("When everybody waits for somebody else.", "כשכולם מחכים למישהו אחר."),
    ("""
<p>A <b>deadlock</b> is a state where no process manages to make progress, each one waiting for something another holds. The classic recipe: two binary semaphores taken in <b>opposite order</b>.</p>
<pre>P1: wait(A); wait(B)        P2: wait(B); wait(A)
P1 takes A, P2 takes B, then each waits for the other forever.
Same order in both (A then B)  ->  no deadlock.</pre>
<p>So the smallest number of binary semaphores that can cause a deadlock is <b>2</b>; one semaphore alone cannot.</p>
<p><b>Dining philosophers</b>: each philosopher takes the left chopstick, then the right. If all take the left one and wait for the right, that is a deadlock. The smallest number of philosophers for a possible deadlock is <b>2</b>. Fixes: take both chopsticks <b>atomically</b> (Linux semop can wait on two semaphores in one all-or-nothing call), or number the chopsticks and always take the lower number first.</p>
""", """
<p><b>קיפאון (deadlock)</b> הוא מצב שבו אף תהליך לא מצליח להתקדם, וכל אחד מחכה למשהו שאחר מחזיק. המתכון הקלאסי: שני סמפורים בינאריים שנלקחים ב<b>סדר הפוך</b>.</p>
<pre>P1: wait(A); wait(B)        P2: wait(B); wait(A)
P1 takes A, P2 takes B, then each waits for the other forever.
Same order in both (A then B)  ->  no deadlock.</pre>
<p>לכן המספר הקטן ביותר של סמפורים בינאריים שיכול לגרום לקיפאון הוא <b>2</b>; סמפור אחד לבדו לא יכול.</p>
<p><b>הפילוסופים הסועדים</b>: כל פילוסוף לוקח את המקל השמאלי ואחר כך את הימני. אם כולם לקחו שמאלי וממתינים לימני, זה קיפאון. המספר הקטן ביותר של פילוסופים לקיפאון אפשרי הוא <b>2</b>. פתרונות: לקחת את שני המקלות <b>אטומית</b> (‏semop ב-Linux יכולה לחכות על שני סמפורים בקריאה אחת של הכול-או-כלום), או למספר את המקלות ולקחת תמיד קודם את המספר הנמוך.</p>
"""),
    [
        Q(("In the dining-philosophers problem each philosopher holds the left chopstick and waits for the right one. What is this situation called?", "בבעיית הפילוסופים הסועדים כל פילוסוף מחזיק את המקל השמאלי וממתין לימני. איך נקרא המצב?"),
          [("Deadlock", "קיפאון"), ("Starvation", "הרעבה"), ("Busy waiting", "המתנה פעילה"), ("Thrashing", "תזזית")],
          ("Everybody waits for a resource another holds: deadlock.", "כולם מחכים למשאב שאחר מחזיק: קיפאון."),
          ("Circular wait = deadlock.", "המתנה מעגלית = קיפאון."),
          exam="2022A-6", has="deadlock"),
        Q(("What is the minimum number of binary semaphores that can cause a deadlock?", "מהו המספר המינימלי של סמפורים בינאריים שיכול לגרום לקיפאון?"),
          ["2", "1", "3", "4"],
          ("Two processes taking A and B in opposite order deadlock; with one semaphore a process always eventually releases it.", "שני תהליכים שלוקחים A ו-B בסדר הפוך נכנסים לקיפאון; עם סמפור אחד תהליך תמיד משחרר אותו בסוף."),
          ("Deadlock needs at least two semaphores.", "קיפאון דורש לפחות שני סמפורים."),
          check=[DL(procs=[["A", "B"], ["B", "A"]], want="deadlock"), DL(procs=[["A"], ["A"]], want="safe")], exam="2023A-6", has="2"),
        Q(("In the dining-philosophers model, what is the smallest number of philosophers that can cause a possible deadlock?", "במודל הפילוסופים הסועדים, מהו המספר הקטן ביותר של פילוסופים שיכול לגרום לקיפאון אפשרי?"),
          ["2", "1", "3", "5"],
          ("With 2 philosophers and 2 chopsticks each can grab one and wait for the other.", "עם 2 פילוסופים ו-2 מקלות כל אחד יכול לתפוס מקל אחד ולחכות לשני."),
          ("Smallest deadlock: 2 philosophers.", "הקיפאון הקטן ביותר: 2 פילוסופים."),
          check=DL(n=2, want="deadlock"), exam="2017SB-8", has="2"),
        Q(("P1 does wait(A) then wait(B). P2 does wait(A) then wait(B) too. Can these two processes deadlock?", "P1 עושה wait(A) ואז wait(B). גם P2 עושה wait(A) ואז wait(B). האם שני התהליכים יכולים להיכנס לקיפאון?"),
          [("No: both take the semaphores in the same order", "לא: שניהם לוקחים את הסמפורים באותו סדר"), ("Yes: always", "כן: תמיד"), ("Yes: if P2 starts first", "כן: אם P2 מתחיל ראשון"), ("Only with three processes", "רק עם שלושה תהליכים")],
          ("Whoever gets A first also gets B; the other one waits at A. No circular wait.", "מי שמקבל את A ראשון מקבל גם את B; השני ממתין ב-A. אין המתנה מעגלית."),
          ("Same order = no deadlock.", "אותו סדר = אין קיפאון."),
          check=DL(procs=[["A", "B"], ["A", "B"]], want="safe")),
        Q(("How can Linux's semop solve the dining-philosophers deadlock when a philosopher needs two semaphores?", "איך semop של Linux יכולה לפתור את הקיפאון של הפילוסופים הסועדים כשפילוסוף צריך שני סמפורים?"),
          [("It performs the wait on both atomically (all or nothing)", "היא מבצעת wait על שניהם אטומית (הכול או כלום)"), ("It makes the second wait faster", "היא מזרזת את ה-wait השני"), ("It removes one chopstick", "היא מסירה מקל אחד"), ("It cannot help", "היא לא יכולה לעזור")],
          ("One semop call can carry both waits; either both are granted or the process sleeps holding neither.", "קריאת semop אחת יכולה לשאת את שני ה-wait; או ששניהם ניתנים או שהתהליך ישן בלי להחזיק אף אחד."),
          ("Atomic double wait removes hold-and-wait.", "wait כפול אטומי מבטל החזקה-והמתנה."),
          exam="2017SA-9", has="atomically"),
        Q(("Three philosophers number their chopsticks 0, 1, 2. Which rule removes the deadlock?", "שלושה פילוסופים ממספרים את המקלות שלהם 0, 1, 2. איזה כלל מבטל את הקיפאון?"),
          [("Always take the lower-numbered chopstick first", "תמיד לוקחים קודם את המקל עם המספר הנמוך"), ("Always take the left chopstick first", "תמיד לוקחים קודם את המקל השמאלי"), ("Take the right chopstick first, but only if it is free", "לוקחים קודם את הימני, אבל רק אם הוא פנוי"), ("Add a fourth philosopher", "מוסיפים פילוסוף רביעי")],
          ("A fixed global order breaks the circular wait. Left-first for everyone still deadlocks.", "סדר גלובלי קבוע שובר את ההמתנה המעגלית. שמאלי-קודם לכולם עדיין מתקע."),
          ("Ordered resources = no circular wait.", "משאבים ממוספרים = אין המתנה מעגלית."),
          check=[DL(n=3, ordered=True, want="safe"), DL(n=3, ordered=False, want="deadlock")]),
    ], icon="🍝")

# ------------------------------------------------------------------ level 6
L6 = Lv(
    ("Bakery, TestAndSet and the kernel", "מאפייה, TestAndSet והליבה"),
    ("Critical sections without the OS, and why the kernel is special.", "קטעים קריטיים בלי מערכת ההפעלה, ולמה הליבה מיוחדת."),
    ("""
<p>The <b>Bakery algorithm</b> solves the critical section for any number of processes with <b>no OS calls</b>. Each process takes a number (like a bakery ticket) and the smallest number enters first. If two numbers are <b>equal</b>, the process with the <b>smaller PID</b> goes first. The <code>choosing</code> array protects the moment a process picks its number; without it <b>mutual exclusion</b> breaks.</p>
<pre>tickets: PID 4 -> 2, PID 2 -> 2, PID 7 -> 1
order: PID 7 (ticket 1), PID 2 (tie, smaller PID), PID 4</pre>
<p>Any solution that does not call the OS cannot put a process to sleep, so it inevitably uses <b>busy waiting</b>. The entry code has two jobs: announce the intent to enter, then check that nobody else is inside.</p>
<p>Inside the kernel Linux uses a <b>TestAndSet</b> style lock (spin-lock). The kernel cannot use semaphores to coordinate cores, because kernel code <b>cannot go to sleep</b>. Binary and counting semaphores can each be built from the other.</p>
""", """
<p>אלגוריתם ה<b>מאפייה (Bakery)</b> פותר את הקטע הקריטי לכל מספר תהליכים <b>בלי קריאות למערכת ההפעלה</b>. כל תהליך לוקח מספר (כמו מספר בתור במאפייה) והמספר הקטן ביותר נכנס ראשון. אם שני מספרים <b>שווים</b>, נכנס התהליך עם ה-<b>PID הקטן יותר</b>. מערך ה-<code>choosing</code> מגן על הרגע שבו תהליך בוחר את המספר שלו; בלעדיו <b>ההדדיות</b> נשברת.</p>
<pre>tickets: PID 4 -> 2, PID 2 -> 2, PID 7 -> 1
order: PID 7 (ticket 1), PID 2 (tie, smaller PID), PID 4</pre>
<p>כל פתרון שלא קורא למערכת ההפעלה לא יכול להרדים תהליך, ולכן הוא בהכרח משתמש ב<b>המתנה פעילה</b>. לקוד הכניסה שני תפקידים: להכריז על כוונה להיכנס, ואז לבדוק שאף אחד אחר לא בפנים.</p>
<p>בתוך הליבה Linux משתמשת בנעילה מסוג <b>TestAndSet</b> (‏spin-lock). הליבה לא יכולה להשתמש בסמפורים כדי לתאם בין ליבות מעבד, כי קוד ליבה <b>לא יכול ללכת לישון</b>. סמפור בינארי וסמפור סופר אפשר לבנות זה מזה.</p>
"""),
    [
        Q(("Bakery algorithm: PID 4 holds ticket 2, PID 2 holds ticket 2, PID 7 holds ticket 1. In what order do they enter?", "אלגוריתם המאפייה: ל-PID 4 כרטיס 2, ל-PID 2 כרטיס 2, ל-PID 7 כרטיס 1. באיזה סדר הם נכנסים?"),
          ["PID 7, PID 2, PID 4", "PID 7, PID 4, PID 2", "PID 2, PID 4, PID 7", "PID 4, PID 2, PID 7"],
          ("The smallest ticket first, and on equal tickets the smaller PID: 7, then 2, then 4.", "הכרטיס הקטן קודם, ובשוויון ה-PID הקטן: 7, אחר כך 2, אחר כך 4."),
          ("Order by (ticket, PID).", "סדר לפי (כרטיס, PID)."),
          check=dict(k="calc", v='", ".join("PID %d" % p for t, p in sorted([(2, 4), (2, 2), (1, 7)]))'),
          exam="2016B-6", has="pid"),
        Q(("Which critical-section solution needs no OS calls and works for any number of processes?", "איזה פתרון לקטע הקריטי לא צריך קריאות מערכת הפעלה ועובד לכל מספר תהליכים?"),
          [("The Bakery algorithm", "אלגוריתם המאפייה"), ("A semaphore", "סמפור"), ("The semop call", "קריאת semop"), ("A monitor in the kernel", "מוניטור בליבה")],
          ("The Bakery algorithm is pure software.", "אלגוריתם המאפייה הוא תוכנה בלבד."),
          ("Software solution for n processes = Bakery.", "פתרון תוכנה ל-n תהליכים = מאפייה."),
          exam="2021A-7", has="bakery"),
        Q(("A critical-section solution that does not call the OS cannot remove a process from running. What problem does that inevitably cause?", "פתרון לקטע קריטי שלא קורא למערכת ההפעלה לא יכול להוריד תהליך מריצה. איזו בעיה זה גורם בהכרח?"),
          [("Busy waiting", "המתנה פעילה"), ("Deadlock", "קיפאון"), ("Thrashing", "תזזית"), ("Priority inversion only", "היפוך עדיפויות בלבד")],
          ("Without sleeping, a waiting process can only spin.", "בלי שינה, תהליך ממתין יכול רק לעשות ספינינג."),
          ("No OS = spinning.", "בלי OS = ספינינג."),
          exam="2020B-7", has="busy"),
        Q(("Why can the OS not use semaphores to schedule between kernels running on multiple cores?", "מדוע מערכת ההפעלה לא יכולה להשתמש בסמפורים כדי לתזמן בין ליבות שרצות על כמה ליבות מעבד?"),
          [("Kernel code cannot go to sleep", "קוד הליבה לא יכול ללכת לישון"), ("Semaphores are too slow to initialise", "סמפורים איטיים מדי לאתחול"), ("Semaphores only work for user threads", "סמפורים עובדים רק עם תהליכונים של משתמש"), ("There is no hardware for them", "אין להם חומרה")],
          ("A semaphore wait puts the caller to sleep, which the kernel itself cannot do.", "wait על סמפור מרדים את הקורא, וזה משהו שהליבה עצמה לא יכולה לעשות."),
          ("Kernel cannot sleep, so it spins.", "הליבה לא יכולה לישון, ולכן היא עושה ספינינג."),
          exam="2023B-5", has="sleep"),
        Q(("When does Linux use the shared-boolean + TestAndSet mechanism for a critical section?", "מתי Linux משתמשת במנגנון של משתנה בוליאני משותף ו-TestAndSet לקטע קריטי?"),
          [("To implement critical sections inside the kernel", "כדי לממש קטעים קריטיים בתוך הליבה"), ("For user-program mutexes only", "רק למנעולים של תוכניות משתמש"), ("Never", "אף פעם"), ("Only on single-core machines", "רק במחשבים עם ליבה אחת")],
          ("Kernel code cannot sleep, so it uses spinning locks.", "קוד ליבה לא יכול לישון, ולכן הוא משתמש בנעילות ספינינג."),
          ("TestAndSet is for kernel critical sections.", "TestAndSet מיועד לקטעים קריטיים בליבה."),
          exam="2017SB-4", has="kernel"),
        Q(("In the Bakery algorithm with the `choosing` array removed, which critical-section condition no longer holds?", "באלגוריתם המאפייה כשמסירים את מערך ה-`choosing`, איזה תנאי של הקטע הקריטי כבר לא מתקיים?"),
          [("Mutual exclusion", "הדדיות"), ("Progress", "התקדמות"), ("Bounded waiting", "המתנה חסומה"), ("None of them", "אף אחד מהם")],
          ("Two processes can pick numbers at once and both think they are first, so both enter.", "שני תהליכים יכולים לבחור מספרים בו-זמנית וכל אחד חושב שהוא ראשון, ושניהם נכנסים."),
          ("No choosing array = mutual exclusion broken.", "בלי choosing = הדדיות נשברת."),
          exam="2017SA-7", has="mutual"),
    ], icon="🥖")

# ------------------------------------------------------------------ level 7
L7 = Lv(
    ("Boss: synchronization exam", "בוס: מבחן סנכרון"),
    ("Real exam items across the whole topic.", "שאלות מהמבחנים מכל הנושא."),
    ("""
<p>Exam level. Quick reminders: semaphore for mutual exclusion starts at 1, for ordering at 0; negative value = sleepers; <code>semop</code> bundles operations atomically; bakery ties go to the smaller PID; the minimum deadlock needs 2 semaphores or 2 philosophers. 80% passes.</p>
""", """
<p>שלב המבחן. תזכורות מהירות: סמפור להדדיות מתחיל ב-1, לסדר ב-0; ערך שלילי = ישנים; ‏<code>semop</code> אוגדת פעולות אטומית; בשוויון במאפייה נכנס ה-PID הקטן; קיפאון מינימלי דורש 2 סמפורים או 2 פילוסופים. 80% עובר.</p>
"""),
    [
        Q(("What is the minimum number of semop calls needed to atomically wait on 5 semaphores and signal on 5 others?", "מהו המספר המינימלי של קריאות semop שדרושות כדי לבצע אטומית wait על 5 סמפורים ו-signal על 5 אחרים?"),
          ["1", "2", "5", "10"],
          ("One call with nsops = 10 carries all ten operations atomically.", "קריאה אחת עם nsops = 10 נושאת את כל עשר הפעולות אטומית."),
          ("One semop call can hold many operations.", "קריאת semop אחת יכולה להכיל הרבה פעולות."),
          exam="2024A-10", has="1"),
        Q(("You set `sops->sem_op = -1` but never call semop(). What happens to the semaphore?", "קבעת `sops->sem_op = -1` אך לא קראת ל-semop(). מה קורה לסמפור?"),
          [("No operation occurs", "לא מתבצעת שום פעולה"), ("A wait is performed", "מתבצע wait"), ("The process sleeps", "התהליך ישן"), ("The semaphore is deleted", "הסמפור נמחק")],
          ("Filling the structure does nothing until semop is called.", "מילוי המבנה לא עושה דבר עד שקוראים ל-semop."),
          ("The operation happens only inside semop.", "הפעולה מתרחשת רק בתוך semop."),
          exam="2023A-10", has="no operation"),
        Q(("In Linux, when are semaphores that were not explicitly removed with semctl finally deleted?", "ב-Linux, מתי סמפורים שלא נמחקו במפורש ב-semctl נמחקים סופית?"),
          [("When the computer crashes or reboots", "כשהמחשב קורס או עושה אתחול"), ("When the creating process exits", "כשהתהליך שיצר אותם מסתיים"), ("After one hour", "אחרי שעה"), ("When the last waiter wakes", "כשהממתין האחרון מתעורר")],
          ("They belong to the kernel, not to the process, so they outlive it until reboot.", "הם שייכים לליבה ולא לתהליך, ולכן הם שורדים אותו עד אתחול."),
          ("Leaked semaphores live until reboot.", "סמפורים שדלפו חיים עד אתחול."),
          exam="2014B-9", has="reboot"),
        Q(("What does the shell command `ipcrm -s 666` do?", "מה עושה פקודת הקונסולה `ipcrm -s 666`?"),
          [("Deletes semaphore set 666", "מוחקת את קבוצת הסמפורים 666"), ("Creates semaphore 666", "יוצרת סמפור 666"), ("Sets a semaphore to 666", "קובעת סמפור ל-666"), ("Kills process 666", "הורגת את תהליך 666")],
          ("ipcrm removes an IPC object; -s selects semaphores.", "ipcrm מסירה אובייקט IPC; ‏-s בוחר סמפורים."),
          ("ipcrm -s = remove a semaphore set.", "ipcrm -s = מחיקת קבוצת סמפורים."),
          exam="2017A-10", has="666"),
        Q(("Consumers wait on `full` (started at 0) and its value is −3. What does that mean?", "צרכנים ממתינים על `full` (שהתחיל ב-0) וערכו ‎-3. מה זה אומר?"),
          [("Three consumers are waiting", "שלושה צרכנים ממתינים"), ("Three slots are full", "שלושה מקומות מלאים"), ("An error", "שגיאה"), ("Three producers are waiting", "שלושה יצרנים ממתינים")],
          ("A negative value counts the sleepers.", "ערך שלילי סופר את הישנים."),
          ("Negative full = waiting consumers.", "full שלילי = צרכנים ממתינים."),
          exam="2019B-4", has="consumers"),
        Q(("What is the fewest binary semaphores with which two processes can still deadlock?", "מהו המספר הקטן ביותר של סמפורים בינאריים שבהם שני תהליכים עדיין יכולים להיכנס לקיפאון?"),
          ["2", "1", "3", "It cannot happen"],
          ("Two processes, two semaphores, opposite order.", "שני תהליכים, שני סמפורים, סדר הפוך."),
          ("Minimum: 2.", "מינימום: 2."),
          check=DL(procs=[["A", "B"], ["B", "A"]], want="deadlock"), exam="2023A-6", has="2"),
    ], icon="🏆", boss=True)

COURSE = Course(
    "sync", "🔒",
    ("Synchronization: semaphores and deadlock", "סנכרון: סמפורים וקיפאון"),
    ("Synchronization is the biggest topic in the question bank, and most of its questions are exact one-line answers. This course builds them up: race conditions and the three conditions, what a semaphore value means, the Linux system calls, producer-consumer and readers-writers, deadlock and the philosophers, and the software solutions. Every level is open; 80% passes.",
     "סנכרון הוא הנושא הגדול ביותר בבנק השאלות, ורוב שאלותיו הן תשובות מדויקות של שורה אחת. הקורס בונה אותן שלב אחר שלב: מצבי תחרות ושלושת התנאים, מה אומר ערך של סמפור, קריאות המערכת של Linux, יצרן-צרכן וקוראים-כותבים, קיפאון והפילוסופים, והפתרונות בתוכנה. כל השלבים פתוחים; 80% עובר."),
    "sync", [L1, L2, L3, L4, L5, L6, L7])
