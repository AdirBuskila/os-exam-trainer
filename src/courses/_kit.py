# -*- coding: utf-8 -*-
"""Authoring helpers for the guided courses ("צריך עזרה?").

A text is either a plain str (same in both languages: numbers, terms, code) or an (en, he) tuple.
Q(...) lists the CORRECT option first; build.py moves it to a deterministic position per question
so the answers are spread out, and tests/courses_check.py asserts that option 0 is what the
simulator computes (`check=`) and/or what the deck says (`exam=` + `has=`).
"""


def Q(q, opts, why, recap, code=None, check=None, exam=None, has=None):
    """q: text. opts: [correct, wrong, wrong, wrong]. why/recap: text.
    check: dict or list of dicts (see tests/courses_check.py). exam: deck id like '2022B-4'
    (shown as a real exam question). has: substring the deck answer must contain."""
    assert 2 <= len(opts) <= 5
    return dict(q=q, opts=list(opts), why=why, recap=recap, code=code, check=check, exam=exam, has=has)


def Lv(title, goal, lesson, qs, icon="📘", boss=False):
    return dict(title=title, goal=goal, lesson=lesson, qs=qs, icon=icon, boss=boss)


def Course(id, icon, title, intro, section, levels):
    return dict(id=id, icon=icon, title=title, intro=intro, section=section, levels=levels)
