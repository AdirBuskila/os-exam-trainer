# -*- coding: utf-8 -*-
"""App configuration for the video engine (tools/video/vid.py and friends).

The guided courses live in src/courses/{sched,paging,vmem,sync}.py (loaded through src/courses/loader.py); their
levels have no ids of their own in the sources, the app numbers them "<course>-<n>". A video id is a course letter
+ the level number: S03 = sched level 3, P05 = paging level 5, V02 = vmem level 2, Y06 = sync level 6.

The question bank is short-answer (src/data/q_<EXAM>.json, ids "<EXAM>-<q>" as build.py makes them). The engine
wants one JSON file keyed by id: videos/make_bank.py writes videos/bank.json, refreshed here on import, so the gate
never reads a stale bank. Open questions are referenced in a script with bank={"2022B-4": None}.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

APP_NAME = "מערכות הפעלה"
COURSE_CODE = "61206"
SITE = "https://adirbuskila.github.io/os-exam-trainer/"
BANK = "videos/bank.json"
SIM_PATHS = ["src/courses"]          # sims.py: schedule, replace, split_address, translate, eat, semaphore, …

# (course id, Hebrew title, icon) in the order of src/courses/loader.ORDER (the app's course list)
COURSES = [
    ("sched", "תזמון מעבד: תרשימי גאנט וזמני המתנה", "🕒"),
    ("paging", "דפדוף ותרגום כתובות", "🧮"),
    ("vmem", "דפדוף לפי דרישה והחלפת דפים", "💾"),
    ("sync", "סנכרון: סמפורים וקיפאון", "🔒"),
]
LETTER = {"S": "sched", "P": "paging", "V": "vmem", "Y": "sync"}
COURSE_LETTER = {v: k for k, v in LETTER.items()}

BONUS_GOAL = {}

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import make_bank  # noqa: E402
make_bank.write()

_SOURCES = None


def _sources():
    """{course id: course dict as authored} (src/courses/<id>.py through loader.load_sources)"""
    global _SOURCES
    if _SOURCES is None:
        p = str(ROOT / "src" / "courses")
        if p not in sys.path:
            sys.path.insert(0, p)
        import loader
        _SOURCES = {c["id"]: c for c in loader.load_sources()}
    return _SOURCES


def _level(video_or_level_id):
    """S03 / 'sched-3' -> (course id, level dict, 1-based number)"""
    m = re.fullmatch(r"([A-Z])(\d+)[a-z]?", video_or_level_id)
    if m:
        cid, n = LETTER[m.group(1)], int(m.group(2))
    else:
        cid, n = video_or_level_id.rsplit("-", 1)
        n = int(n)
    return cid, _sources()[cid]["levels"][n - 1], n


def level_id(video_id):
    """the app's id of the guided level a video belongs to: S03 -> 'sched-3' (js/courses.js level ids)"""
    cid, _, n = _level(video_id)
    return f"{cid}-{n}"


def quiz_ids():
    """bank ids cited by any guided-course question (level quizzes and the boss levels): never solved in a video"""
    return {q["exam"] for c in _sources().values() for L in c["levels"] for q in L["qs"] if q.get("exam")}


def boss_ids():
    return quiz_ids()


def is_boss(video_id):
    return bool(_level(video_id)[1]["boss"])


def level_goal(course, level_id):
    """level_id is the video id (P03) or the app's level id ('paging-3'); the Hebrew goal sentence"""
    return _level(level_id)[1]["goal"][1]

_sources()      # load now: src/courses/sched.py shares its name with the stdlib module `sched`
