/* =============================================================================
   courses.js — "🧭 צריך עזרה?" guided courses.
   A course is a ladder of levels: a short lesson, then 4-6 multiple-choice questions, then a
   summary. The last level of every course is a 🏆 boss built from real exam items. All levels
   are open; a level is passed at >= 80%. Progress lives in the app state (S.courses) so it is
   saved with the flashcard progress, per course and per level.

   Content comes from DATA.courses (built by build.py from src/courses/*.py). Every text field is
   {en, he}; the language follows the app (I18N.lang), so a language switch redraws in place.

   Public API (window.COURSE_UI): route(view), openMap(cid), openLesson(level), startLevel(level),
   hubHTML(), homeCard(). window.COURSES is {id: course} (used by the render audit).
   ============================================================================= */
(function (root, doc) {
'use strict';

var PASS = 80;
var C = (root.DATA && root.DATA.courses) || {};
root.COURSES = C;
var ORDER = ['sched', 'paging', 'vmem', 'sync'].filter(function (id) { return C[id]; });

var st = { cid: null, L: null, view: 'map', qi: 0, picked: [] };

function T(k, p) { return root.I18N.t(k, p); }
function lang() { return root.I18N ? root.I18N.lang : 'en'; }
function he() { return lang() === 'he'; }
function loc(x) { if (x == null) return ''; if (typeof x === 'string') return x; return x[lang()] || x.en || ''; }
function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
/* 2^24, 2^(v−k), 128^4 -> real superscripts (a literal caret reads as a typo on a phone) */
function sup(h) { return h.replace(/([A-Za-z0-9)])\^(\([^()]*\)|[0-9A-Za-z]+)/g, '$1<sup>$2</sup>'); }
/* Hebrew: isolate each Latin/number run as ONE left-to-right unit, lists included ("P1, P2, P3" must not
   be split per item, or the RTL line order reverses it). Trailing punctuation stays outside the unit. */
var RUN = /[(\[]?[A-Za-z0-9][A-Za-z0-9 	,.:;()\[\]<>*+\-−×=\/^&|%#_'→←·]*/g;
var TRAILN = /[ 	.,:;!?'"([<]+$/;
function isoHe(str) {
  var out = '', last = 0, m;
  RUN.lastIndex = 0;
  while ((m = RUN.exec(str))) {
    var full = m[0], tm = TRAILN.exec(full);
    if (tm) full = full.slice(0, full.length - tm[0].length);
    if (!full) { RUN.lastIndex = m.index + 1; continue; }
    out += esc(str.slice(last, m.index)) + '<bdi dir="ltr">' + esc(full) + '</bdi>';
    last = m.index + full.length; RUN.lastIndex = last;
  }
  return out + esc(str.slice(last));
}
function iso(s) { return sup(he() ? isoHe(s) : esc(s)); }

/* question / explanation text: **bold**, `code`, newlines; Latin runs are isolated in Hebrew */
function rich(s) {
  s = String(s == null ? '' : s);
  var out = '', parts = s.split(/(\*\*[^*]+\*\*|`[^`]+`)/);
  for (var i = 0; i < parts.length; i++) {
    var p = parts[i];
    if (!p) continue;
    if (p.slice(0, 2) === '**') out += '<b>' + iso(p.slice(2, -2)) + '</b>';
    else if (p.charAt(0) === '`') out += '<code dir="ltr">' + esc(p.slice(1, -1)) + '</code>';
    else out += iso(p);
  }
  return out.replace(/\n/g, '<br>');
}
/* lesson html is authored markup: isolate Latin/number runs in its text nodes (Hebrew only) */
function lessonHtml(h) {
  h = String(h || '');
  var skip = 0, out = '', toks = h.match(/<[^>]+>|[^<]+/g) || [];
  toks.forEach(function (tk) {
    if (tk.charAt(0) === '<') {
      if (/^<(pre|code)/i.test(tk)) skip++;
      else if (/^<\/(pre|code)>/i.test(tk)) skip = Math.max(0, skip - 1);
      out += tk;
    } else if (skip) out += tk;
    else out += iso(tk.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&'));
  });
  return out.replace(/<table>/g, '<div class="tscroll"><table>').replace(/<\/table>/g, '</table></div>');
}

/* ---------------- progress ---------------- */
function prog(cid) { S.courses = S.courses || {}; return (S.courses[cid] = S.courses[cid] || {}); }
function best(cid, L) { return (prog(cid)[L.id] || {}).best || 0; }
function passed(cid, L) { return best(cid, L) >= PASS; }
function nextLevel(c) { for (var i = 0; i < c.levels.length; i++) if (!passed(c.id, c.levels[i])) return c.levels[i]; return null; }
function nPassed(c) { return c.levels.filter(function (L) { return passed(c.id, L); }).length; }

/* ---------------- routing ---------------- */
function setHash(h) { try { history.replaceState(null, '', '#' + h); } catch (e) { root.location.hash = h; } }
function ensure(view) {
  view = view || doc.getElementById('view');
  var s = doc.getElementById('screen-course');
  if (!s || !view.contains(s)) {
    view.innerHTML = '<div id="screen-course"><div id="crsMapView" class="hidden"></div><div id="crsLessonView" class="hidden"></div>' +
      '<div id="crsQuizView" class="hidden"></div><div id="crsSumView" class="hidden"></div></div>';
  }
}
function show(id) {
  ['crsMapView', 'crsLessonView', 'crsQuizView', 'crsSumView'].forEach(function (v) {
    var e = doc.getElementById(v); if (e) e.classList.toggle('hidden', v !== id);
  });
}
function levelOf(cid, n) { var c = C[cid]; return c && c.levels[n - 1]; }

/* called by app.js render() for #help[/cid[/n]] */
function route(view) {
  var seg = root.location.hash.replace(/^#/, '').split('/');
  var cid = seg[1], n = parseInt(seg[2], 10);
  if (!cid || !C[cid]) return hub(view);
  var L = levelOf(cid, n);
  if (L && st.cid === cid && st.L === L && st.view === 'quiz') { ensure(view); return drawQuiz(); }
  if (L && st.cid === cid && st.L === L && st.view === 'sum') { ensure(view); return drawSum(); }
  ensure(view);
  if (L) return openLesson(L, true);
  return openMap(cid, true);
}

/* ---------------- hub (the "צריך עזרה?" page) ---------------- */
function courseCard(c) {
  var n = nPassed(c), m = c.levels.length, nx = nextLevel(c);
  var sub = n ? (nx ? T('crs.progressNext', { n: n, m: m, title: esc(loc(nx.title)) }) : T('crs.finished')) : T('crs.notStarted', { m: m });
  return '<button type="button" class="crs-card" data-course="' + c.id + '" onclick="COURSE_UI.openMap(\'' + c.id + '\')">' +
    '<span class="crs-ic">' + c.icon + '</span><span class="crs-ct">' +
    '<b' + (he() ? ' dir="rtl"' : '') + '>' + iso(loc(c.title)) + '</b>' +
    '<span class="crs-cs">' + sub + '</span>' +
    '<span class="bar"><i style="width:' + Math.round(100 * n / m) + '%"></i></span></span></button>';
}
function hub(view) {
  var h = '<h2 class="sec">' + T('help.title') + '</h2><p class="progresshint">' + T('help.sub') + '</p><div class="crs-list">' +
    ORDER.map(function (id) { return courseCard(C[id]); }).join('') + '</div>' +
    '<div class="row" style="margin-top:12px"><button class="btn ghost" onclick="go(\'home\')">' + T('crs.toHome') + '</button></div>';
  view.innerHTML = h;
}
function homeCard() {
  if (!ORDER.length) return '';
  return '<div class="card crs-home"><div class="row"><b style="font-size:17px">' + T('help.title') + '</b></div>' +
    '<p class="progresshint" style="margin:6px 0 10px">' + T('help.homeHint') + '</p><div class="crs-list">' +
    ORDER.map(function (id) { return courseCard(C[id]); }).join('') + '</div></div>';
}

/* ---------------- map ---------------- */
function openMap(cid, quiet) {
  var c = C[cid]; if (!c) return;
  st.cid = cid; st.L = null; st.view = 'map';
  ensure();
  var nx = nextLevel(c), n = nPassed(c), m = c.levels.length;
  var h = '<div class="row"><button class="btn ghost" onclick="go(\'help\')">' + T('crs.toHub') + '</button></div>' +
    '<h2 class="sec" style="margin-top:12px">' + c.icon + ' <span' + (he() ? ' dir="rtl"' : '') + '>' + iso(loc(c.title)) + '</span></h2>' +
    '<p class="crs-intro">' + iso(loc(c.intro)) + '</p>' +
    '<div class="card crs-overall">' + T('crs.levelsPassed', { n: '<b>' + n + '</b>', m: '<b>' + m + '</b>' }) +
    '<div class="bar"><i style="width:' + Math.round(100 * n / m) + '%"></i></div>' +
    (n === m ? '<p style="margin:10px 0 0">' + T('crs.allDone') + '</p>' : '') + '</div>' +
    '<div class="crs-map">' + c.levels.map(function (L) {
      var p = prog(cid)[L.id], status = !p ? T('crs.status.new', { n: L.questions.length })
        : passed(cid, L) ? T('crs.status.passed', { best: p.best }) : T('crs.status.try', { last: p.last, best: p.best });
      return '<button type="button" class="crs-lvl' + (passed(cid, L) ? ' passed' : '') + (L === nx ? ' next' : '') + (L.boss ? ' boss' : '') + '" data-id="' + L.id + '" onclick="COURSE_UI.openLevelById(\'' + L.id + '\')">' +
        '<span class="num">' + T('crs.level', { n: L.order }) + (L.boss ? ' · ' + T('crs.boss') : '') + '</span>' +
        '<span class="ttl">' + L.icon + ' ' + iso(loc(L.title)) + '</span>' +
        '<span class="gl">' + iso(loc(L.goal)) + '</span><span class="st">' + status + '</span></button>';
    }).join('') + '</div>' +
    '<div class="row" style="margin-top:14px"><button class="btn ghost" onclick="COURSE_UI.reset()">' + T('crs.reset') + '</button></div>' +
    '<p class="progresshint">' + T('crs.rule') + '</p>';
  doc.getElementById('crsMapView').innerHTML = h;
  show('crsMapView');
  if (!quiet) { setHash('help/' + cid); root.scrollTo(0, 0); }
}
function openLevelById(id) {
  var c = C[st.cid]; var L = c && c.levels.filter(function (x) { return x.id === id; })[0];
  if (L) openLesson(L);
}
function reset() {
  if (!st.cid) return;
  if (root.confirm(T('crs.resetConfirm'))) { S.courses[st.cid] = {}; save(); openMap(st.cid, true); }
}

/* ---------------- lesson ---------------- */
function openLesson(L, quiet) {
  var cid = L.id.split('-')[0], c = C[cid];
  st.cid = cid; st.L = L; st.view = 'lesson';
  ensure();
  var nReal = L.questions.filter(function (q) { return q.exam; }).length;
  var h = '<div class="row crs-head"><span class="chip">' + T('crs.levelOf', { n: L.order, m: c.levels.length }) + '</span>' +
    '<span class="chip soft">' + T('crs.qCount', { n: L.questions.length }) + (nReal ? ' · ' + T('crs.fromExams', { n: nReal }) : '') + '</span></div>' +
    '<h2 class="sec" style="margin-top:12px">' + L.icon + ' <span' + (he() ? ' dir="rtl"' : '') + '>' + iso(loc(L.title)) + '</span></h2>' +
    '<p class="crs-goal">' + iso(loc(L.goal)) + '</p>' +
    '<div class="lesson lessonbody crs-lesson">' + lessonHtml(loc(L.lesson)) + '</div>' +
    '<div class="row crs-actions"><button class="btn" id="crsLessonGo" onclick="COURSE_UI.startCurrent()">' + T('crs.start') + '</button>' +
    '<button class="btn ghost" id="crsLessonBack" onclick="COURSE_UI.openMap(\'' + cid + '\')">' + T('crs.toMap') + '</button></div>';
  doc.getElementById('crsLessonView').innerHTML = h;
  show('crsLessonView');
  if (!quiet) { setHash('help/' + cid + '/' + L.order); root.scrollTo(0, 0); }
}

/* ---------------- level quiz ---------------- */
function startLevel(L) {
  st.cid = L.id.split('-')[0]; st.L = L; st.view = 'quiz'; st.qi = 0; st.picked = [];
  ensure();
  setHash('help/' + st.cid + '/' + L.order);
  drawQuiz();
  root.scrollTo(0, 0);
}
function drawQuiz() {
  var L = st.L, q = L.questions[st.qi], picked = st.picked[st.qi], answered = picked !== undefined;
  var h = '<div class="row crs-head"><span class="chip">' + iso(loc(L.title)) + '</span>' +
    '<span class="pill" style="margin-inline-start:auto">' + T('crs.question', { i: st.qi + 1, n: L.questions.length }) + '</span></div>' +
    '<div class="bar"><i style="width:' + Math.round(100 * st.qi / L.questions.length) + '%"></i></div>' +
    '<div class="card crs-qcard">' +
    (q.exam ? '<div class="crs-exam">' + T('crs.exam', { exam: '<bdi dir="ltr">' + esc(examLabel(q.exam)) + '</bdi>' }) + '</div>' : '') +
    '<div id="crsQText" class="crs-q" data-key="' + q.id + '"' + (he() ? ' dir="rtl"' : '') + '>' + rich(loc(q.q)) + '</div>' +
    (q.code ? '<pre class="qcode" dir="ltr">' + esc(q.code) + '</pre>' : '') +
    '<div class="crs-opts">' + q.opts.map(function (o, i) {
      var cls = 'opt';
      if (answered) cls += (i === q.ans ? ' right' : (i === picked ? ' wrong' : ''));
      return '<button type="button" class="' + cls + '" data-i="' + i + '"' + (answered ? ' disabled' : '') + '><span class="txt">' + rich(loc(o)) + '</span></button>';
    }).join('') + '</div>' +
    '<div id="crsFeedback" class="crs-fb' + (answered ? (picked === q.ans ? ' ok' : ' no') : ' hidden') + '">' +
    (answered ? '<b>' + T(picked === q.ans ? 'crs.correct' : 'crs.wrong') + '</b> ' + rich(loc(q.why)) : '') + '</div>' +
    (root.Feedback ? root.Feedback.reportRow({ id: q.id, exam: 'Course ' + st.cid + ' L' + L.order, text: loc(q.q) }) : '') +
    '</div><div class="row"><button class="btn ghost" id="crsQuitBtn" onclick="COURSE_UI.leave()">' + T('crs.quit') + '</button>' +
    '<button class="btn' + (answered ? '' : ' hidden') + '" id="crsNextBtn" style="margin-inline-start:auto" onclick="COURSE_UI.next()">' +
    T(st.qi + 1 < L.questions.length ? 'crs.nextQ' : 'crs.finish') + '</button></div>';
  var v = doc.getElementById('crsQuizView');
  v.innerHTML = h;
  v.querySelectorAll('.opt').forEach(function (b) { b.onclick = function () { pick(parseInt(b.getAttribute('data-i'), 10)); }; });
  show('crsQuizView');
}
function examLabel(id) { var m = /^(\w+)-(\d+)$/.exec(id); return m ? m[1] + ' Q' + m[2] : id; }
function pick(i) {
  if (st.picked[st.qi] !== undefined) return;
  st.picked[st.qi] = i;
  drawQuiz();
  var nb = doc.getElementById('crsNextBtn'); if (nb && nb.scrollIntoView) { try { nb.scrollIntoView({ block: 'nearest' }); } catch (e) {} }
}
function next() {
  if (st.qi + 1 < st.L.questions.length) { st.qi++; drawQuiz(); root.scrollTo(0, 0); }
  else finish();
}
function leave() { st.view = 'lesson'; openLesson(st.L); }

/* ---------------- summary ---------------- */
function finish() {
  var L = st.L, cid = st.cid, qs = L.questions, ok = 0;
  qs.forEach(function (q, i) { if (st.picked[i] === q.ans) ok++; });
  var pct = Math.round(100 * ok / qs.length), p = prog(cid)[L.id] || {};
  prog(cid)[L.id] = { best: Math.max(p.best || 0, pct), last: pct };
  save();
  st.view = 'sum';
  drawSum();
  root.scrollTo(0, 0);
}
function drawSum() {
  var L = st.L, cid = st.cid, c = C[cid], qs = L.questions, ok = 0, wrong = [];
  qs.forEach(function (q, i) { if (st.picked[i] === q.ans) ok++; else wrong.push(q); });
  var pct = Math.round(100 * ok / qs.length), pass = pct >= PASS, nx = c.levels[c.levels.indexOf(L) + 1];
  var msg = pass ? (L.boss ? T('crs.bossMsg', { name: iso(loc(c.title)) }) : T('crs.passMsg')) : T('crs.failMsg');
  var h = '<div class="card center crs-sum"><div class="row" style="justify-content:center"><span class="chip">' + T('crs.level', { n: L.order }) + ' · ' + iso(loc(L.title)) + '</span></div>' +
    '<div class="crs-big">' + pct + '%</div><div><b><bdi dir="ltr">' + ok + ' / ' + qs.length + '</bdi></b> ' + T('crs.correctWord') + '</div>' +
    '<p class="crs-msg">' + msg + '</p>' +
    (wrong.length ? '<div class="crs-review"><div class="crs-review-t">' + T('crs.review') + '</div>' +
      wrong.map(function (q) { return '<div>• ' + rich(loc(q.recap)) + '</div>'; }).join('') + '</div>' : '') +
    '<div class="crs-btns">' +
    (nx ? '<button class="btn' + (pass ? '' : ' ghost') + '" onclick="COURSE_UI.openNext()">' + T('crs.nextLevel', { title: iso(loc(nx.title)) }) + '</button>' : '') +
    (!nx ? '<button class="btn" onclick="COURSE_UI.toReal()">' + T('crs.real') + '</button>' : '') +
    '<button class="btn' + (pass ? ' ghost' : '') + '" onclick="COURSE_UI.startCurrent()">' + T('crs.retry') + '</button>' +
    '<button class="btn ghost" onclick="COURSE_UI.openLessonCurrent()">' + T('crs.lessonBtn') + '</button>' +
    '<button class="btn ghost" onclick="COURSE_UI.openMap(\'' + cid + '\')">' + T('crs.mapBtn') + '</button></div></div>';
  doc.getElementById('crsSumView').innerHTML = h;
  show('crsSumView');
}
function openNext() { var c = C[st.cid], nx = c.levels[c.levels.indexOf(st.L) + 1]; if (nx) openLesson(nx); }
function toReal() { var c = C[st.cid]; root.go('sec', c.section); }

root.COURSE_UI = {
  PASS: PASS, route: route, hub: hub, homeCard: homeCard, openMap: openMap, openLesson: openLesson, startLevel: startLevel,
  openLevelById: openLevelById, startCurrent: function () { startLevel(st.L); }, openLessonCurrent: function () { openLesson(st.L); },
  next: next, leave: leave, openNext: openNext, toReal: toReal, reset: reset, rich: rich, state: st, available: ORDER.length > 0
};

})(typeof window !== 'undefined' ? window : globalThis, typeof document !== 'undefined' ? document : null);
