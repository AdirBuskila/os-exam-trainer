# -*- coding: utf-8 -*-
"""Pronunciation additions for the vmem videos (V01-V07): demand paging and page replacement.
Merged by videos/lexicon.py into every video of the app, so the keys are specific multi-letter terms.
Shared terms that lex_paging.py already has (page fault(s), valid, MMU, frame) are not repeated here.
Replacement is substring based, longest key first: plural / longer forms have their own keys."""

WORDS = {
    "Page fault": "פֵּייג' פוֹלְט",
    "demand paging": "דִּימַאנְד פֵּייגִ'ינְג",
    "Demand paging": "דִּימַאנְד פֵּייגִ'ינְג",
    "swap partition": "סְווֹפּ פַּרְטִישְׁן",
    "swap": "סְווֹפּ",
    "Copy-on-Write": "קוֹפִּי אוֹן רַייט",
    "reference bit": "רֶפֶרֶנְס בִּיט",
    "dirty bit": "דֶּרְטִי בִּיט",
    "dirty": "דֶּרְטִי",
    "thrashing": "תְרָשִׁינְג",
    "Thrashing": "תְרָשִׁינְג",
    "working set": "ווֹרְקִינְג סֶט",
    "Belady": "בֵּלָדִי",
    "Clock": "קְלוֹק",
    "FIFO": "פִיפוֹ",
    "LRU": "אֶל אַר יוּ",
    "LFU": "אֶל אֶף יוּ",
    "OPT": "אוֹפְּט",
    "O(N)": "סדר גודל של אֶן",
    "O(n)": "סדר גודל של אֶן",
}

HOMOPHONES = {}

TEX_TOKENS = {}
