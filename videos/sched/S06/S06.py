# -*- coding: utf-8 -*-
"""S06 · מילות התאוריה — video script (build: tools/video/vid.py S06).

Source: src/courses/sched.py level 6 (lesson + goal: preemptive, CPU burst, starvation and aging, the Windows focus
window, the Linux epoch and Multilevel Queue). Exam anchor: 2014B-4 (which kind of CPU scheduler is missing on desktop
computers but often present on supercomputers: the long-term scheduler), which no guided quiz cites.
Not used on purpose: 2016A-5 (Linux epoch) and 2017B-5 (Windows focus window) are free bank ids but content twins of
the quiz items 2020A-7 and 2023A-5; 2017A-4 (CPU burst) is a near twin of the quiz item 2020B-4.
Content note: the level's terms ARE its quiz answers (2020A-4, 2021A-4, 2023A-5, 2020A-7, 2024A-5, 2020B-4). The
video teaches each term as the lesson does, through a mechanism (the state diagram, a burst strip, an SJF run in which
a long job is postponed), never phrases a definition as the quiz stem (preemption is named as the running->ready
move; focus window, epoch and Multilevel Queue get one short phrase each), and skips the register-adding example of 2020B-4.
The starvation run 2@0 9@1 2@2 2@4 2@6 2@8 comes from sims.schedule (SJF, strict) and is asserted below.
"""
from vid import P, Scene, Video, show, hide, BANK
import stage as st
import w_sched as w

# ---------------------------------------------------------------- numbers (verified)
S = [(0, 2), (1, 9), (2, 2), (4, 2), (6, 2), (8, 2)]
RS = w.run(S, "SJF")
assert RS["gantt"] == [("P1", 0, 2), ("P3", 2, 4), ("P4", 4, 6), ("P5", 6, 8), ("P6", 8, 10), ("P2", 10, 19)]
assert RS["wait"][1] == 9 and all(x == 0 for i, x in enumerate(RS["wait"]) if i != 1)
w.assert_fresh(S)

Q = BANK["2014B-4"]
assert Q["answer_he"] == "Long term scheduler"

ST = w.states_svg("sd")
BS = w.burst_strip("bs", [("cpu", 3), ("io", 2), ("cpu", 4), ("io", 3), ("cpu", 2)])
GS = w.gantt("gs", RS, width=1000, arrivals=False, finishes=False)

# ---------------------------------------------------------------- scenes
title = Scene("title", "", [
    P("בסרטון הזה נעבור על מילות התאוריה של התזמון. במבחן הן שאלות קצרות, וכל אחת שווה נקודות."),
    P("נשלף, פרץ חישוב, הרעבה ו-aging, ושתי מוזרויות של Windows ושל Linux."),
    P("ובסוף שאלה ממבחן על סוג מתזמן שלא דיברנו עליו עד עכשיו.", hold=0.4),
], stage='<div class="kicker">S06 · תזמון מעבד: תרשימי גאנט וזמני המתנה</div><h1>מילות התאוריה</h1>'
         '<p>נשלף, הרעבה, aging, epoch והמוזרויות של מערכות ההפעלה.</p>', layout="title")

pre = Scene("pre", "נשלף או לא", [
    P("בתזמון מעניינים אותנו שלושה מצבים: מוכן, רץ, וממתין לקלט פלט."),
    P("המתזמן בוחר תהליך מוכן, והוא עובר למצב רץ.", do=show("sd-e-disp")),
    P("ממצב ריצה אפשר לצאת בדרכים שונות. אם הוא סיים, הוא יוצא מהמערכת.", do=show("sd-e-exit")),
    P("אם הוא ביקש קלט פלט, הוא עובר להמתין. וכשהקלט פלט מסתיים, הוא חוזר למוכן.",
      do=show("sd-e-io", "sd-e-back")),
    P("והמעבר החשוב: מרץ חזרה למוכן, בלי שהתהליך ביקש משהו. המתזמן לקח ממנו את המעבד.",
      do=show("sd-e-pre", "p-c1")),
    P("זו **שליפה**. אלגוריתם שמשתמש בה הוא אלגוריתם נשלף, ובאנגלית preemptive.", do=show("p-c2"),
      say="זו שליפה. אלגוריתם שמשתמש בה הוא אלגוריתם נשלף, ובאנגלית פְּרִי אֶמְפְּטִיב."),
    P("בשלבים הקודמים ראינו שני אלגוריתמים כאלה: SRTF ו-Round Robin.", do=show("p-c3"),
      say="בשלבים הקודמים ראינו שני אלגוריתמים כאלה: אֶס אַר טִי אֶף ורָאוּנְד רוֹבִּין."),
    P("ו-FCFS ו-SJF לא נשלפים: אצלם תהליך עוזב את המעבד רק כשסיים, או כשביקש קלט פלט.", do=show("p-c4"),
      hold=0.4, say="ואֶף סִי אֶף אֶס ואֶס גֵ'יי אֶף לא נשלפים: אצלם תהליך עוזב את המעבד רק כשסיים, או כשביקש קלט פלט."),
], stage=ST,
   panel=st.card("p-c1", "trap", "⚠️ רץ ← מוכן: המתזמן לקח את המעבד")
         + st.card("p-c2", "rule", "🔑 שליפה: רץ ← מוכן ביוזמת המתזמן")
         + st.card("p-c3", "ex", "נשלפים: SRTF, Round Robin")
         + st.card("p-c4", "ex", "לא נשלפים: FCFS, SJF"))

burst = Scene("burst", "פרץ חישוב", [
    P("עכשיו המילה פרץ. תהליך אמיתי לא רק מחשב: הוא מחשב, מבקש קלט פלט, מחכה, וחוזר לחשב.",
      do=show("bs-p0", "bs-p1", "bs-p2", "bs-p3", "bs-p4")),
    P("כל קטע של חישוב טהור, בין שתי בקשות קלט פלט, נקרא **פרץ חישוב**, CPU burst.", do=show("b-c1"),
      say="כל קטע של חישוב טהור, בין שתי בקשות קלט פלט, נקרא פרץ חישוב, סִי פִּי יוּ בֶּרְסְט."),
    P("והקטעים שבהם הוא מחכה לדיסק או למקלדת הם פרצי קלט פלט.", do=show("b-c2")),
    P("המספר בעמודת הפרץ בכל הטבלאות שלנו הוא בדיוק זה: אורך פרץ החישוב הבא.", do=show("b-c3"), hold=0.4),
], stage=w.stack(BS, '<div class="sc-line">חיים של תהליך: חישוב, קלט/פלט, חישוב…</div>', gap=30),
   panel=st.card("b-c1", "rule", "🔑 פרץ חישוב: חישוב בין שתי בקשות קלט/פלט")
         + st.card("b-c2", "ex", "פרץ קלט/פלט: ממתין להתקן")
         + st.card("b-c3", "ex", "עמודת הפרץ בטבלה = פרץ החישוב הבא"))

starve = Scene("starve", "הרעבה ו-aging", [
    P("ראינו ש-SJF מעדיף קצרים. מה קורה כשכל הזמן מגיעים קצרים?", do=show("gs-s0"),
      say="ראינו שאֶס גֵ'יי אֶף מעדיף קצרים. מה קורה כשכל הזמן מגיעים קצרים?"),
    P("P2 צריך תשע יחידות, ומגיע בזמן 1. אבל כל שתי יחידות מגיע תהליך חדש של שתיים.", do=show("gs-s1", "gs-s2"),
      say="פִּי שתיים צריך תשע יחידות, ומגיע בזמן אחת. אבל כל שתי יחידות מגיע תהליך חדש של שתיים."),
    P("ובכל פעם שהמעבד מתפנה, יש מישהו קצר ממנו. הוא נדחה, ונדחה שוב.", do=show("gs-s3", "gs-s4")),
    P("כאן הזרם נעצר, ו-P2 רץ רק בזמן 10. אבל אם הקצרים לא היו נגמרים, הוא לא היה רץ לעולם.",
      do=show("gs-s5", "s-c1"),
      say="כאן הזרם נעצר, ופִּי שתיים רץ רק בזמן עשר. אבל אם הקצרים לא היו נגמרים, הוא לא היה רץ לעולם."),
    P("לזה קוראים **הרעבה**, starvation. זה קורה ב-SJF, ב-SRTF, ובתזמון לפי עדיפויות.", do=show("s-c2"),
      say="לזה קוראים הרעבה, סְטַארְוֵויישֶׁן. זה קורה באֶס גֵ'יי אֶף, באֶס אַר טִי אֶף, ובתזמון לפי עדיפויות."),
    P("בתזמון לפי עדיפויות התרופה נקראת **aging**, הזדקנות: ככל שתהליך מחכה יותר, מעלים לו את העדיפות.",
      do=show("s-c3"),
      say="בתזמון לפי עדיפויות התרופה נקראת אֵייגִ'ינְג, הזדקנות: ככל שתהליך מחכה יותר, מעלים לו את העדיפות."),
    P("בסוף הוא עוקף את החדשים, ומקבל את המעבד. ו-Round Robin? אצלו אין הרעבה בכלל, כי כולם מסתובבים בתור.",
      do=show("s-c4"), hold=0.4,
      say="בסוף הוא עוקף את החדשים, ומקבל את המעבד. ורָאוּנְד רוֹבִּין? אצלו אין הרעבה בכלל, כי כולם מסתובבים בתור."),
], stage=w.stack(GS, '<div class="sc-line">ב-SJF, התהליך <span class="sc-ltr">P2</span> (פרץ 9) מגיע בזמן 1, ונדחה שוב ושוב</div>', gap=24),
   panel=st.card("s-c1", "trap", "⚠️ P2 הגיע בזמן 1 ורץ רק בזמן 10")
         + st.card("s-c2", "rule", "🔑 הרעבה: תהליך שלא מקבל מעבד לעולם")
         + st.card("s-c3", "rule", "🔑 aging: העדיפות עולה עם ההמתנה")
         + st.card("s-c4", "ex", "Round Robin: אין הרעבה"))

os_ = Scene("os", "Windows ו-Linux", [
    P("ועוד כמה מונחים קצרים ממערכות הפעלה אמיתיות. ב-Windows, החלון שהמשתמש עובד בו מקבל עדיפות.",
      do=show("o-w", "o-w1"),
      say="ועוד כמה מונחים קצרים ממערכות הפעלה אמיתיות. בווינְדוֹאוּז, החלון שהמשתמש עובד בו מקבל עדיפות."),
    P("הפרוסות שלו ארוכות יותר, פי שלושה.", do=show("o-w2")),
    P("וב-Linux, הקורס מתאר כמה תורים לפי סוגי תהליכים, שעוברים עליהם בסבבים. לסבב כזה קוראים epoch.",
      do=show("o-l", "o-l1", "o-l2"),
      say="ובלִינוּקְס, הקורס מתאר כמה תורים לפי סוגי תהליכים, שעוברים עליהם בסבבים. לסבב כזה קוראים אֶפּוֹק."),
    P("כדאי לזכור את השמות האלה בדיוק כמו שהם כתובים כאן.", hold=0.4),
], stage=w.stack(w.line("o-w", "🖥️ <b>Windows</b>"), w.line("o-w1", "חלון הפוקוס, " + w.ltr("focus window")),
                 w.line("o-w2", "קוונטום ארוך <b>פי 3</b>"),
                 w.line("o-l", "🐧 <b>Linux</b>", cls="sc-gapt"), w.line("o-l1", "סבב מלא = " + w.ltr("<b>epoch</b>")),
                 w.line("o-l2", "הגישה: " + w.ltr("<b>Multilevel Queue</b>")), gap=14),
   layout="full")

exam = Scene("exam", "שאלה ממבחן", [
    P("שאלה ממבחן: איזה סוג מתזמן מעבד לא קיים במחשבים שולחניים, אבל קיים פעמים רבות במחשבי על?"),
    P("כל מה שלמדנו עד עכשיו הוא **המתזמן לטווח קצר**: הוא בוחר מתור המוכנים, כל כמה מילישניות.",
      do=show("x-1")),
    P("אבל יש החלטה מוקדמת יותר: איזה מהעבודות שהוגשו בכלל ייכנסו למערכת, לזיכרון ולתור המוכנים.",
      do=show("x-2")),
    P("את זה מחליט **המתזמן לטווח ארוך**. הוא שולט בכמה תהליכים רצים יחד.", do=show("x-3")),
    P("במחשב על, משתמשים מגישים עבודות ענק, והן מחכות במאגר עד שהמתזמן הזה מכניס אותן.", do=show("x-4")),
    P("ובמחשב שולחני? כל תוכנה שפותחים נכנסת מיד לתור המוכנים. אין מי שיחזיק אותה בחוץ.", do=show("x-5")),
    P("ולכן התשובה: Long term scheduler, המתזמן לטווח ארוך.", do=show("x-ans"), hold=0.5,
      say="ולכן התשובה: לוֹנְג טֶרְם סְקֶדְיוּלֶר, המתזמן לטווח ארוך."),
], stage=w.stack(st.card("x-1", "ex", "⏱️ <b>טווח קצר</b>: מי רץ עכשיו, מתוך תור המוכנים"),
                 st.card("x-2", "ex", "📥 קודם לכן: אילו עבודות בכלל נכנסות למערכת?"),
                 st.card("x-3", "rule", "🔑 <b>טווח ארוך</b>: מכניס עבודות, וקובע כמה רצות יחד"),
                 st.card("x-4", "ex", "מחשב על: עבודות ממתינות במאגר"),
                 st.card("x-5", "trap", "⚠️ מחשב שולחני: כל תוכנה נכנסת מיד, אין טווח ארוך"), gap=16),
   panel=f'<div class="qstem"><span class="qid">{Q["id"]}</span>{Q["he"]}</div>'
         f'<div id="x-ans" class="qans h"><span class="k">תשובה:</span> <span class="sc-ltr">{Q["answer_he"]}</span></div>')

recap = Scene("recap", "סיכום", [
    P("לסיכום: שליפה היא מעבר מרץ למוכן ביוזמת המתזמן. SRTF ו-Round Robin שולפים, FCFS ו-SJF לא.", do=show("r-1"),
      say="לסיכום: שליפה היא מעבר מרץ למוכן ביוזמת המתזמן. אֶס אַר טִי אֶף ורָאוּנְד רוֹבִּין שולפים, אֶף סִי אֶף אֶס ואֶס גֵ'יי אֶף לא."),
    P("פרץ חישוב הוא חישוב טהור בין שתי בקשות קלט פלט.", do=show("r-2")),
    P("הרעבה נפתרת ב-aging. ו-Windows נותנת לחלון הפוקוס קוונטום פי שלושה.", do=show("r-3"),
      say="הרעבה נפתרת באֵייגִ'ינְג. ווינְדוֹאוּז נותנת לחלון הפוקוס קְוַונְטוּם פי שלושה."),
    P("ב-Linux סבב הוא epoch, והגישה Multilevel Queue. ברמה הבאה: מבחן הבוס. בהצלחה.", do=show("r-4"), hold=0.6,
      say="בלִינוּקְס סבב הוא אֶפּוֹק, והגישה מוּלְטִי לֶבֶל קְיוּ. ברמה הבאה: מבחן הבוס. בהצלחה."),
], stage=w.states_svg("sr").replace('class="h"', 'class=""'),
   panel=st.card("r-1", "rule", "🔑 שליפה: רץ ← מוכן")
         + st.card("r-2", "rule", "🔑 פרץ חישוב: בין שתי בקשות קלט/פלט")
         + st.card("r-3", "rule", "🔑 הרעבה ← aging · פוקוס ← קוונטום ×3")
         + st.card("r-4", "rule", "🔑 Linux: epoch, Multilevel Queue"))

VIDEO = Video("S06", "sched", "מילות התאוריה", [title, pre, burst, starve, os_, exam, recap], bank={"2014B-4": None})
