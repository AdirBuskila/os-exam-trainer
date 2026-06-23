/* =============================================================================
   i18n.js — lightweight bilingual layer (English default, Hebrew additive).
   No external dependencies. Dictionaries are inlined into window.DATA.i18n by
   build.py (same "everything is generated into data.js" pattern as the rest of
   the app, so it works from file:// with no fetch).

   Public API (window.I18N):
     lang            current language ('en' | 'he')
     t(key, params)  translate with {var} interpolation + English fallback
     wrapLtr(token)  isolate one Latin/code token: <bdi dir="ltr">…</bdi>
     autoIsolate(s)  HTML-safe string with Latin/code/number runs auto-isolated
     setLanguage(l)  set lang+dir, persist, re-scan static markup, fire event
     toggleLang()    flip en<->he
     applyLang()     (re)apply lang/dir to <html> and fill [data-i18n] nodes
   Also exposes window.t as a convenience alias.
   ============================================================================= */
(function (root, doc) {
'use strict';

var LS_KEY = 'os_trainer_lang';
var DICT = (root.DATA && root.DATA.i18n) || { en: {}, he: {} };
if (!DICT.en) DICT.en = {};
if (!DICT.he) DICT.he = {};

function readLang() {
  var l;
  try { l = localStorage.getItem(LS_KEY); } catch (e) { l = null; }
  return l === 'he' ? 'he' : 'en';
}
var lang = readLang();

/* ---- html escaping (self-contained; app.js's esc() may not be loaded yet) -- */
var ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' };
function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return ESC[c]; }); }

/* ---- translation --------------------------------------------------------- */
function has(d, k) { return d && Object.prototype.hasOwnProperty.call(d, k); }
function t(key, params) {
  var v = has(DICT[lang], key) ? DICT[lang][key]
        : has(DICT.en, key)    ? DICT.en[key]
        : null;
  if (v == null) return key;                       // last-resort: surface the key
  if (params) v = v.replace(/\{(\w+)\}/g, function (m, p) {
    return params[p] != null ? params[p] : m;
  });
  return v;
}

/* ---- bidi isolation ------------------------------------------------------ */
// Wrap a single token (e.g. "fork()", "PID 4 → 5 → 6") so the Unicode Bidi
// Algorithm cannot reorder it inside RTL prose. <bdi> is the semantic choice.
function wrapLtr(token) { return '<bdi dir="ltr">' + esc(token) + '</bdi>'; }

// Auto-isolate maximal Latin/code/number runs embedded in (possibly Hebrew)
// text, returning an HTML-SAFE string. Hebrew letters break a run, so runs stay
// short and local. Trailing sentence punctuation/spaces are left outside the
// isolate so Hebrew punctuation still flows naturally. In LTR text this is a
// harmless no-op wrap.
var LTR_RUN = /[(\[{<]?[A-Za-z0-9][A-Za-z0-9 \t()\[\]{}<>.,:;!?*+\-=\/\\^&|%#_'"→←↔]*/g;
// Trailing neutrals (incl. an opening bracket/comma that really belongs to the
// following Hebrew clause) are left OUTSIDE the isolate so Hebrew flows normally.
var TRAIL  = /[ \t.,:;!?'"([{<]+$/;
function autoIsolate(str) {
  str = String(str == null ? '' : str);
  var out = '', last = 0, m;
  LTR_RUN.lastIndex = 0;
  while ((m = LTR_RUN.exec(str))) {
    var start = m.index, full = m[0];
    var tm = TRAIL.exec(full);
    if (tm) full = full.slice(0, full.length - tm[0].length); // strip trailing neutral
    if (!full) { LTR_RUN.lastIndex = start + 1; continue; }
    out += esc(str.slice(last, start));                       // Hebrew/neutral before
    out += '<bdi dir="ltr">' + esc(full) + '</bdi>';          // isolated LTR run
    last = start + full.length;                               // trail re-scanned as plain
    LTR_RUN.lastIndex = last;
  }
  out += esc(str.slice(last));
  return out;
}

/* ---- apply to the DOM ---------------------------------------------------- */
function applyLang() {
  var html = doc.documentElement;
  html.lang = lang;
  html.setAttribute('dir', lang === 'he' ? 'rtl' : 'ltr');
  try { doc.title = t('app.title'); } catch (e) {}
  // Static markup: any element with data-i18n gets its inner HTML replaced.
  var nodes = doc.querySelectorAll('[data-i18n]');
  for (var i = 0; i < nodes.length; i++) {
    nodes[i].innerHTML = t(nodes[i].getAttribute('data-i18n'));
  }
  // Language toggle button shows the OTHER language as the call-to-action.
  var btn = doc.getElementById('langBtn');
  if (btn) btn.innerHTML = lang === 'he' ? '🌐 EN' : '🌐 עברית';
}

function setLanguage(l) {
  l = (l === 'he') ? 'he' : 'en';
  if (l === lang) return;
  lang = l;
  try { localStorage.setItem(LS_KEY, lang); } catch (e) {}
  applyLang();
  root.dispatchEvent(new Event('languagechange'));
}
function toggleLang() { setLanguage(lang === 'he' ? 'en' : 'he'); }

var API = {
  get lang() { return lang; },
  t: t, wrapLtr: wrapLtr, autoIsolate: autoIsolate,
  applyLang: applyLang, setLanguage: setLanguage, toggleLang: toggleLang
};
root.I18N = API;
root.t = t; // convenience alias used throughout app.js

})(typeof window !== 'undefined' ? window : globalThis,
   typeof document !== 'undefined' ? document : { documentElement: {}, querySelectorAll: function () { return []; }, getElementById: function () { return null; } });
