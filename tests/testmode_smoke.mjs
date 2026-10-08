// Smoke test for Test Mode (the former "By Year" view): loads the whole app in
// jsdom and drives the question-by-question flow — list of exams -> pick one ->
// reveal answer -> Got it -> advance. Catches runtime throws and verifies the
// flashcard-style flow is wired up and ordered (q1 first, not shuffled).
import { JSDOM } from 'jsdom';
import { readFileSync } from 'node:fs';

const F = (p) => readFileSync(new URL('../' + p, import.meta.url), 'utf8');
const fail = (m) => { console.error('FAIL:', m); process.exit(1); };

const dom = new JSDOM(F('index.html'), {
  url: 'http://localhost/',
  pretendToBeVisual: true,
  runScripts: 'outside-only',
});
const { window } = dom;
const doc = window.document;

// --- stubs jsdom lacks (canvas + animation, used by the home hero) ---
window.HTMLCanvasElement.prototype.getContext = () => new Proxy({}, { get: () => () => {}, set: () => true });
window.requestAnimationFrame = () => 1;
window.cancelAnimationFrame = () => {};
window.matchMedia = () => ({ matches: false, addEventListener(){}, removeEventListener(){} });
window.scrollTo = () => {};
window.ResizeObserver = class { observe(){} disconnect(){} };
window.IntersectionObserver = class { constructor(cb){ this.cb = cb; } observe(){ this.cb([{ isIntersecting: true }]); } disconnect(){} };

// load the app scripts in the same order index.html does, then export the
// router fns (classic-script top-level fns are global in a browser; mirror that).
for (const f of ['js/engines.js', 'js/data.js', 'js/i18n.js', 'js/hero.js']) window.eval(F(f));
window.eval(F('js/app.js') + '\n;window.__go=go;window.__render=render;');

const view = () => doc.getElementById('view');
const text = () => view().textContent;

// 1) Test Mode list shows every exam, including the newly added ones
window.__go('years');
if (!/Test Mode/i.test(text())) fail('years view missing "Test Mode" title');
for (const code of ['2014A', '2016B', '2017SA', '2017SB', '2024B']) {
  if (!text().includes(code)) fail('Test Mode list missing exam tile ' + code);
}

// 2) Pick an exam -> question-by-question deck, in order, with "Show answer"
window.__go('year', '2017SB');
const v = view();
if (!/Show answer/i.test(v.textContent)) fail('exam view has no "Show answer" control');
if (!/1\s*\/\s*10/.test(v.textContent)) fail('exam view did not start at card 1 / 10');
const q1he = window.DATA.questions.find(q => q.exam === '2017SB' && q.q === 1).he.slice(0, 18);
if (!v.textContent.includes(q1he)) fail('first card is not Q1 (ordered flow broken). Expected: ' + q1he);

// 3) Reveal the answer -> Got it / Missed buttons appear with the answer text
const flip = v.querySelector('#flip');
if (!flip) fail('no #flip button'); flip.onclick();
if (!v.querySelector('#got') || !v.querySelector('#miss')) fail('Got it / Missed buttons not shown after reveal');
const a1 = window.DATA.questions.find(q => q.exam === '2017SB' && q.q === 1).answer_he.slice(0, 6);
if (!v.querySelector('#rev').textContent.includes(a1)) fail('revealed answer missing expected text');

// 4) Got it -> advances to card 2 / 10 and records progress
v.querySelector('#got').onclick();
if (!/2\s*\/\s*10/.test(view().textContent)) fail('Got it did not advance to card 2 / 10');
const saved = JSON.parse(window.localStorage.getItem('os_trainer_v1') || '{}');
if (!saved.cards || !saved.cards['2017SB-1'] || saved.cards['2017SB-1'].last !== 1)
  fail('Got it was not recorded to localStorage for 2017SB-1');

// 5) Previous -> back to card 1, shown as already graded (answer revealed, no re-grade); Next -> card 2 again
const prev = view().querySelector('#prev');
if (!prev || prev.disabled) fail('card 2 has no enabled #prev button');
prev.onclick();
if (!/1\s*\/\s*10/.test(view().textContent)) fail('Previous did not go back to card 1 / 10');
if (!view().querySelector('#rev').textContent.includes(a1)) fail('previous card did not show its revealed answer');
if (view().querySelector('#got') || view().querySelector('#miss')) fail('previous card offers re-grading');
if (!/Got it/i.test(view().querySelector('#ctrl').textContent)) fail('previous card does not show how it was graded');
if (!view().querySelector('#prev').disabled) fail('#prev is not disabled on the first card');
const before = JSON.stringify(JSON.parse(window.localStorage.getItem('os_trainer_v1')).cards['2017SB-1']);
view().querySelector('#next').onclick();
if (!/2\s*\/\s*10/.test(view().textContent)) fail('Next did not return to card 2 / 10');
if (!view().querySelector('#flip')) fail('card 2 lost its Show answer control after back/next');
if (JSON.stringify(JSON.parse(window.localStorage.getItem('os_trainer_v1')).cards['2017SB-1']) !== before) fail('back/next changed recorded progress');

// 6) Deck complete -> Previous returns to the last card, shown as graded
for (let k = 2; k <= 10; k++) { view().querySelector('#flip').onclick(); view().querySelector('#got').onclick(); }
if (!/Deck complete/i.test(view().textContent)) fail('deck did not complete after grading all 10 cards');
view().querySelector('#prev').onclick();
if (!/10\s*\/\s*10/.test(view().textContent) || !view().querySelector('#next')) fail('Previous from the complete screen did not show card 10 as graded');

console.log('test-mode smoke OK — list shows all exams; ordered Q-by-Q; reveal + Got it/Missed + progress; previous/next through graded cards.');
