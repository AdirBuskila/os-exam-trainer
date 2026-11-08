// Smoke test for the video course (js/video-ui.js + videos.js): loads the app in jsdom and drives
// list -> player -> practice-this-level, the guided lesson's "watch the video" button, the ?video= deep link,
// both languages, and checks that every video in the manifest belongs to a real guided level.
import { JSDOM } from 'jsdom';
import { readFileSync } from 'node:fs';

const F = (p) => readFileSync(new URL('../' + p, import.meta.url), 'utf8');
const fail = (m) => { console.error('FAIL:', m); process.exit(1); };

function boot(search, lang) {
  const dom = new JSDOM(F('index.html'), { url: 'http://localhost/' + (search || ''), pretendToBeVisual: true, runScripts: 'outside-only' });
  const { window } = dom;
  window.HTMLCanvasElement.prototype.getContext = () => new Proxy({}, { get: () => () => {}, set: () => true });
  window.requestAnimationFrame = () => 1;
  window.cancelAnimationFrame = () => {};
  window.matchMedia = () => ({ matches: false, addEventListener(){}, removeEventListener(){} });
  window.scrollTo = () => {};
  window.ResizeObserver = class { observe(){} disconnect(){} };
  window.IntersectionObserver = class { constructor(cb){ this.cb = cb; } observe(){ this.cb([{ isIntersecting: true }]); } disconnect(){} };
  if (lang) window.localStorage.setItem('os_trainer_lang', lang);
  for (const f of ['js/engines.js', 'js/data.js', 'js/i18n.js', 'js/feedback.js', 'js/hero.js', 'videos.js']) window.eval(F(f));
  window.eval(F('js/video-ui.js'));
  window.eval(F('js/courses.js') + '\n' + F('js/app.js') + '\n;window.__go=go;window.__render=render;');
  return window;
}

let w = boot('', 'en');
const doc = () => w.document;
const view = () => doc().getElementById('view');
const VC = w.VIDEO_COURSE;
const ALL = VC.courses.flatMap(c => c.videos.map(v => ({ ...v, course: c.id })));
if (!ALL.length) { console.log('video_smoke: no videos in videos.js yet — skipped'); process.exit(0); }

// every video belongs to an existing guided level of its course
for (const v of ALL) {
  const C = w.COURSES[v.course];
  if (!C) fail(`${v.id}: unknown course ${v.course}`);
  if (!C.levels.some(L => L.id === v.level)) fail(`${v.id}: level ${v.level} not in course ${v.course}`);
}

// list (English): every video row, Hebrew titles tagged, the Hebrew-narration note
w.__go('videos');
const rows = view().querySelectorAll('.vid-row');
if (rows.length !== ALL.length) fail(`list shows ${rows.length} rows, manifest has ${ALL.length}`);
if (!view().querySelector('.vid-henote')) fail('English list lacks the Hebrew-narration note');
if (!view().querySelector('.vid-tag.he')) fail('English list lacks the Hebrew tag on titles');

// player: open the first video, then next, then practice -> guided lesson of that level
rows[0].click();
w.__render();
const v0 = ALL[0];
if (w.location.hash !== '#video/' + v0.id) fail('row click did not route to the player: ' + w.location.hash);
if (!doc().getElementById('vidFrame')) fail('player has no frame');
if (!view().textContent.includes(v0.id)) fail('player does not show the video id');
const nb = doc().getElementById('vidNext');
if (ALL.length > 1) {
  nb.click(); w.__render();
  if (w.location.hash !== '#video/' + ALL[1].id) fail('next did not move to the second video');
}
w.__go('video', v0.id);
const wb = doc().getElementById('vidWatchBtn');
wb.click();
if (!JSON.parse(w.localStorage.getItem('os_trainer_video_v1')).watched[v0.id]) fail('mark as watched not saved');
doc().getElementById('vidLevel').click();
if (!doc().getElementById('crsLessonView') || doc().getElementById('crsLessonView').classList.contains('hidden')) fail('practice did not open the guided lesson');

// lesson screen: the "watch this level's video" button opens the player, back returns to the lesson
const btn = view().querySelector('.vid-open');
if (!btn) fail('guided lesson has no video button');
btn.click(); w.__render();
if (w.location.hash !== '#video/' + v0.id) fail('lesson video button did not open the video');
doc().getElementById('vidBack').click();
if (!doc().getElementById('crsLessonView') || doc().getElementById('crsLessonView').classList.contains('hidden')) fail('back did not return to the lesson');

// home card
w.__go('home');
if (!view().querySelector('.vid-home')) fail('home has no video card');

// Hebrew + deep link ?video=<ID>
const last = ALL[ALL.length - 1];
w = boot('?video=' + last.id, 'he');
if (w.location.hash !== '#video/' + last.id) fail('?video deep link did not open the player');
if (!view().textContent.includes(last.title.slice(0, 10))) fail('Hebrew player does not show the title');
if (view().querySelector('.vid-tag.he')) fail('Hebrew mode should not tag titles as Hebrew');

console.log(`video_smoke: OK (${ALL.length} videos)`);
