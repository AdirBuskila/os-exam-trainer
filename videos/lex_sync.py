# -*- coding: utf-8 -*-
"""Pronunciation additions for the sync course videos (Y01-Y07). Merged by videos/lexicon.py into every video of the
app; replacement is substring-based and longest first, so compounds that contain a shorter key ("busy waiting" holds
"wait", "readcount" holds "count", "deadlock" holds no key) are listed whole. The class says these terms in English:
the subtitles keep them in Latin letters, the voice gets the Hebrew transliteration."""

WORDS = {
    # the semaphore and its operations
    "semaphores": "סֶמָפוֹרִים",
    "Semaphores": "סֶמָפוֹרִים",
    "semaphore": "סֶמָפוֹר",
    "Semaphore": "סֶמָפוֹר",
    "wait": "ווֵייט",
    "signal": "סִיגְנָל",
    "mutex": "מְיוּטֶקְס",
    # Linux system V calls and fields
    "semget": "סֶם גֶט",
    "semop": "סֶם אוֹפּ",
    "semctl": "סֶם קוֹנְטְרוֹל",
    "sembuf": "סֶם בָּאף",
    "sem_op": "סֶם אוֹפּ",
    "sem_num": "סֶם נָאם",
    "sem_flg": "סֶם פְלַאג",
    "semid": "סֶם אַיי דִי",
    "nsops": "אֶן סֶם אוֹפְּס",
    "SETVAL": "סֶט וַואל",
    "SETALL": "סֶט אוֹל",
    "IPC_PRIVATE": "אַיי פִּי סִי פְּרַייבֶט",
    # the critical-section vocabulary
    "race condition": "רֵייס קוֹנְדִישֶׁן",
    "critical section": "קְרִיטִיקָל סֶקְשֶׁן",
    "Mutual exclusion": "מְיוּצ'וּאַל אֶקְסְקְלוּזְ'ן",
    "mutual exclusion": "מְיוּצ'וּאַל אֶקְסְקְלוּזְ'ן",
    "Progress": "פְּרוֹגְרֶס",
    "progress": "פְּרוֹגְרֶס",
    "Bounded waiting": "בָּאוּנְדֶד ווֵייטִינְג",
    "bounded waiting": "בָּאוּנְדֶד ווֵייטִינְג",
    "busy waiting": "בִּיזִי ווֵייטִינְג",
    "Deadlock": "דֶד לוֹק",
    "deadlock": "דֶד לוֹק",
    "TestAndSet": "טֶסְט אֶנְד סֶט",
    "Bakery": "בֵּייקֶרִי",
    "spin-lock": "סְפִּין לוֹק",
    "Spin-lock": "סְפִּין לוֹק",
    "producer-consumer": "פְּרוֹדְיוּסֶר קוֹנְסְיוּמֶר",
    "readers-writers": "רִידֶרְס רַייטֶרְס",
    "Coffman": "קוֹפְמַן",
    # variables the videos name aloud
    "readcount": "רִיד קָאוּנְט",
    "count": "קָאוּנְט",
    "empty": "אֶמְפְּטִי",
    "full": "פוּל",
    "PID": "פִּי אַיי דִי",
    "Ready": "רֶדִי",
}

HOMOPHONES = {}

TEX_TOKENS = {}
