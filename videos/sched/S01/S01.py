# -*- coding: utf-8 -*-
"""S01 · הגעה, פרץ ושלושת המדדים — video script (build: tools/video/vid.py S01).

Source: src/courses/sched.py level 1 (lesson + goal: turnaround, waiting and response of one process, then the
average of a set). Exam anchor: 2017A-5 (Response time = until the process produces its first output), which no
guided quiz cites.
Avoided on purpose: the level-1 quiz (arrival 2 / burst 3 / completion 8, the FCFS table 4@0 4@1 2@2, 2023A-4
"time in the ready queue", 2026A-4 "waiting + running") and the lesson's own example. 2017B-4 is not used: its stem
("Waiting time is the time from entering the ready queue until ___") is the reverse twin of the quiz item 2023A-4.
Here: a given Gantt chart of three processes 4@0, 7@1, 4@2 (it is Round Robin with quantum 3, not named yet), in which
P2 runs in three pieces, so waiting time is visibly the sum of three gaps. Every number comes from sims.schedule
(w_sched.run) and is asserted below.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_sched as w

# ---------------------------------------------------------------- numbers (verified)
PROCS = [(0, 4), (1, 7), (2, 4)]
R = w.run(PROCS, "RR", 3)
STEPS = w.rr_steps(PROCS, 3)
SL = w.rr_slices(STEPS)
assert SL == [("P1", 0, 3), ("P2", 3, 6), ("P3", 6, 9), ("P1", 9, 10), ("P2", 10, 13), ("P3", 13, 14), ("P2", 14, 15)]
assert R["finish"] == [10, 15, 14] and R["turn"] == [10, 14, 12] and R["wait"] == [6, 7, 8] and R["resp"] == [0, 2, 4]
assert R["avg_wait"] == 7 and R["avg_turn"] == 12
w.assert_fresh(PROCS)
# P2's three gaps in the ready queue: 1-3, 6-10, 13-14
P2 = [(s, e) for n, s, e in SL if n == "P2"]
GAPS = [(1, P2[0][0])] + [(P2[i][1], P2[i + 1][0]) for i in range(len(P2) - 1)]
assert GAPS == [(1, 3), (6, 10), (13, 14)] and sum(e - s for s, e in GAPS) == R["wait"][1] == 14 - 7

GANTT = w.gantt("g", R, slices=SL, width=1000, arrivals=True, finishes=False, hidden=False)
GM = w.gantt("gm", R, slices=SL, width=1000, arrivals=True, finishes=False, hidden=False,
             bands=[("w0", 1, 3), ("w1", 6, 10), ("w2", 13, 14), ("tt", 1, 15)])
GR = w.gantt("gr", R, slices=SL, width=1000, finishes=True, hidden=False)
TAB = w.ptable("t", R, cols=("arr", "burst", "fin", "turn", "wait"), shown=("arr", "burst"), cls="sm",
               avg="ממוצע המתנה: " + w.ltr("(6 + 7 + 8) / 3 = 7"))

Q = BANK["2017A-5"]
assert "פלט הראשון" in Q["answer_he"]

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נלמד את שלושת המספרים של כל תהליך."),
    P("נבנה מהם שלושה מדדים: זמן סבב, זמן המתנה וזמן תגובה, ונראה למה הם לא אותו דבר."),
    P("ובסוף נענה על שאלה ממבחן.", hold=0.4),
], stage='<div class="kicker">S01 · תזמון מעבד: תרשימי גאנט וזמני המתנה</div><h1>הגעה, פרץ ושלושת המדדים</h1>'
         '<p>זמן סבב, זמן המתנה וזמן תגובה של תהליך בודד, וממוצע של קבוצת תהליכים.</p>', layout="title")

idea = Scene("idea", "שלושה מספרים", [
    P("יש מעבד אחד, ויש כמה תהליכים שרוצים אותו. כל תהליך מגיע עם שני מספרים.", do=show("i-tab")),
    P("**הגעה**: הרגע שבו הוא נכנס לתור המוכנים.", do=show("i-c1")),
    P("**פרץ**: כמה זמן מעבד הוא צריך בסך הכול.", do=show("i-c2")),
    P("המתזמן מחליט מי רץ ומתי, והתוצאה היא **תרשים גאנט**: ציר זמן, ועליו מי מחזיק את המעבד.",
      do=show("i-g")),
    P("את התרשים הזה נקבל כנתון. איך בונים אותו נלמד בשלבים הבאים."),
    P("מהתרשים קוראים את המספר השלישי: **סיום**, הרגע שבו התהליך גומר את כל הפרץ שלו.", do=show("i-c3")),
    P("נתמקד ב-P2. הוא מגיע בזמן 1 וצריך 7 יחידות זמן.", do=show("g-a-P2", "g-hl1", "g-hl4", "g-hl6"),
      say="נתמקד בפִּי שתיים. הוא מגיע בזמן אחת, וצריך שבע יחידות זמן."),
    P("הוא רץ בשלוש חתיכות: 3 עד 6, 10 עד 13, ו-14 עד 15. ולכן הוא מסיים בזמן 15.", hold=0.4,
      say="הוא רץ בשלוש חתיכות: משלוש עד שש, מעשר עד שלוש עשרה, ומארבע עשרה עד חמש עשרה. ולכן הוא מסיים בזמן חמש עשרה."),
], stage=w.stack(f'<div id="i-g" class="h">{GANTT}</div>',
                 f'<div id="i-tab" class="h">{w.ptable("ti", R, cols=("arr", "burst"), shown=("arr", "burst"))}</div>',
                 gap=30),
   panel=st.card("i-c1", "ex", "<b>הגעה</b>: נכנס לתור המוכנים")
         + st.card("i-c2", "ex", "<b>פרץ</b>: כמה זמן מעבד הוא צריך")
         + st.card("i-c3", "ex", "<b>סיום</b>: גמר את כל הפרץ. קוראים אותו מהגאנט"))

metrics = Scene("metrics", "שלושת המדדים", [
    P("המדד הראשון: **זמן סבב**. כל הזמן שהתהליך נמצא במערכת, מההגעה ועד הסיום.",
      do=show("m-c1", "gm-a-P2", "gm-hl1", "gm-hl4", "gm-hl6")),
    P("ל-P2: חמש עשרה פחות אחת, כלומר 14.", do=show("gm-b-tt", "m-f1"),
      say="לפִּי שתיים: חמש עשרה פחות אחת, כלומר ארבע עשרה."),
    P("המדד השני: **זמן המתנה**. הזמן שהתהליך עומד בתור המוכנים, ולא רץ.", do=show("m-c2"), hold=0.3),
    P("אפשר לספור אותו בתרשים. מההגעה בזמן 1 ועד הריצה בזמן 3: שתי יחידות.", do=hide("gm-b-tt") + show("gm-b-w0"),
      say="אפשר לספור אותו בתרשים. מההגעה בזמן אחת, ועד הריצה בזמן שלוש: שתי יחידות."),
    P("משש עד עשר הוא שוב מחכה: ארבע יחידות.", do=show("gm-b-w1")),
    P("ומשלוש עשרה עד ארבע עשרה: עוד יחידה אחת. בסך הכול 7.", do=show("gm-b-w2", "m-f2"),
      say="ומשלוש עשרה עד ארבע עשרה: עוד יחידה אחת. בסך הכול שבע."),
    P("אבל לספור חורים זה מסוכן. יש נוסחה שעובדת תמיד: סבב פחות פרץ.", do=show("m-c4")),
    P("ארבע עשרה פחות שבע: שוב 7. כי כל זמן במערכת הוא או ריצה, או המתנה.", do=show("m-f4"),
      say="ארבע עשרה פחות שבע: שוב שבע. כי כל זמן במערכת הוא או ריצה, או המתנה."),
    P("המדד השלישי: **זמן תגובה**. כמה זמן עבר מההגעה ועד הריצה **הראשונה**.", do=show("m-c3"), hold=0.3),
    P("ל-P2: שלוש פחות אחת, כלומר 2. ההמתנות המאוחרות כבר לא נספרות.", do=show("m-f3"),
      say="לפִּי שתיים: שלוש פחות אחת, כלומר שתיים. ההמתנות המאוחרות כבר לא נספרות."),
    P("שימו לב: לאותו תהליך יש סבב 14, המתנה 7 ותגובה 2. שלושה מספרים שונים.", do=show("m-t"), hold=0.5,
      say="שימו לב: לאותו תהליך יש סבב ארבע עשרה, המתנה שבע, ותגובה שתיים. שלושה מספרים שונים."),
], stage=GM,
   panel=st.card("m-c1", "rule", '🔑 סבב = סיום − הגעה <span id="m-f1" class="sc-calc h">15 − 1 = 14</span>')
         + st.card("m-c2", "rule", '🔑 המתנה: זמן בתור <span id="m-f2" class="sc-calc h">2 + 4 + 1 = 7</span>')
         + st.card("m-c4", "rule", '🔑 המתנה = סבב − פרץ <span id="m-f4" class="sc-calc h">14 − 7 = 7</span>')
         + st.card("m-c3", "rule", '🔑 תגובה = ריצה ראשונה − הגעה <span id="m-f3" class="sc-calc h">3 − 1 = 2</span>')
         + st.card("m-t", "trap", "⚠️ 14, 7, 2: שלושה מדדים שונים"))

avg = Scene("avg", "ממוצע של קבוצה", [
    P("במבחן לא שואלים על תהליך אחד, אלא על ממוצע. נמלא את הטבלה לכל השלושה.", do=show("a-tab")),
    P("קוראים מהתרשים את זמני הסיום: P1 בעשר, P2 בחמש עשרה, ו-P3 בארבע עשרה.",
      do=show("t-P1-fin", "t-P2-fin", "t-P3-fin"),
      say="קוראים מהתרשים את זמני הסיום: פִּי אחת בעשר, פִּי שתיים בחמש עשרה, ופִּי שלוש בארבע עשרה."),
    P("סבב הוא סיום פחות הגעה: עשר, ארבע עשרה, ושתים עשרה.", do=show("t-P1-turn", "t-P2-turn", "t-P3-turn")),
    P("המתנה היא סבב פחות פרץ: P1 שש, P2 שבע, ו-P3 שמונה.", do=show("t-P1-wait", "t-P2-wait", "t-P3-wait"),
      say="המתנה היא סבב פחות פרץ: פִּי אחת שש, פִּי שתיים שבע, ופִּי שלוש שמונה."),
    P("זמן ההמתנה הממוצע: הסכום, עשרים ואחת, חלקי שלושה תהליכים. יוצא 7.", do=show("t-avg"),
      say="זמן ההמתנה הממוצע: הסכום, עשרים ואחת, חלקי שלושה תהליכים. יוצא שבע."),
    P("ואם נחשב ממוצע של עמודת הסבב, שלושים ושש חלקי שלוש, נקבל 12. זה מספר אחר לגמרי.", do=show("a-c1"),
      say="ואם נחשב ממוצע של עמודת הסבב, שלושים ושש חלקי שלוש, נקבל שתים עשרה. זה מספר אחר לגמרי."),
    P("המלכודת: שני המספרים נראים סבירים. בדקו איזה מדד ביקשו, ומאיזו עמודה חישבתם את הממוצע.", do=show("a-c2"), hold=0.5),
], stage=f'<div id="a-tab" class="h">{TAB}</div>',
   panel=st.card("a-c1", "ex", "ממוצע סבב: " + w.ltr("36 / 3 = 12"))
         + st.card("a-c2", "trap", "⚠️ ממוצע המתנה ≠ ממוצע סבב. קראו מה נשאל"))

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: Response time הוא הזמן שחולף מאז שהתהליך הורץ, עד ש... מה?"),
    P("זמן תגובה מודד כמה מהר המערכת **מגיבה**: מתי המשתמש רואה ממנה משהו בפעם הראשונה.", do=show("x-1")),
    P("לא מתי התהליך מסיים. הזמן עד הסיום הוא זמן הסבב.", do=show("x-2")),
    P("ולכן התשובה: עד שהתהליך מפיק את **הפלט הראשון** שלו.", do=show("x-ans")),
    P("בתרגילי גאנט המוסכמה בקורס היא למדוד את זמן התגובה עד הריצה הראשונה, כי זה הרגע הראשון שבו התהליך יכול להגיב.",
      do=show("x-3")),
    P("כמו שעשינו עם P2: שלוש פחות אחת, שתיים.", hold=0.5, say="כמו שעשינו עם פִּי שתיים: שלוש פחות אחת, שתיים."),
], stage=w.stack(st.card("x-1", "rule", "🔑 תגובה: מתי רואים <b>תגובה ראשונה</b>"),
                 st.card("x-2", "trap", "⚠️ עד הסיום: זה זמן הסבב, לא התגובה"),
                 st.card("x-3", "ex", "בגאנט: ריצה ראשונה − הגעה. ל-P2: " + w.ltr("3 − 1 = 2")), gap=30),
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         f'<div id="x-ans" class="qans h"><span class="k">תשובה:</span> {Q["answer_he"]}</div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום: לכל תהליך יש הגעה ופרץ, ומהגאנט קוראים את הסיום.", do=show("r-1")),
    P("סבב הוא סיום פחות הגעה.", do=show("r-2")),
    P("המתנה היא סבב פחות פרץ, וזה נכון גם כשתהליך רץ בחתיכות.", do=show("r-3")),
    P("ותגובה נמדדת רק עד הריצה הראשונה. ברמה הבאה נבנה גאנט בעצמנו. נתראה.", do=show("r-4"), hold=0.6),
], stage=GR,
   panel=st.card("r-1", "ex", "הגעה, פרץ, וסיום מהגאנט")
         + st.card("r-2", "rule", "🔑 סבב = סיום − הגעה")
         + st.card("r-3", "rule", "🔑 המתנה = סבב − פרץ")
         + st.card("r-4", "rule", "🔑 תגובה = ריצה ראשונה − הגעה"))

VIDEO = Video("S01", "sched", "הגעה, פרץ ושלושת המדדים", [title, idea, metrics, avg, exam, recap],
              bank={"2017A-5": None})
