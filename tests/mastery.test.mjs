/* Tests for card mastery / progress logic (mirrors js/app.js rec/known/isWeak).
   Run: node tests/mastery.test.mjs */

// --- replicate the state model from js/app.js ---
let S = { cards: {} };
function rec(id, ok){ const c=S.cards[id]||{c:0,w:0}; if(ok)c.c++; else c.w++; c.last=ok?1:0; S.cards[id]=c; }

// OLD definition (buggy): cumulative ratio, ignores most recent answer.
function masteryRatio(id){ const c=S.cards[id]; if(!c||(c.c+c.w)===0)return 0; return c.c/(c.c+c.w); }
function knownOld(id){ return masteryRatio(id) >= 0.6; }

// NEW definition (fix): a card is "known" when the most recent answer was correct.
function known(id){ const c=S.cards[id]; return !!c && c.last===1; }
function isWeak(id){ return !known(id); }

let fails=0;
function eq(actual, expected, msg){
  if(actual!==expected){ console.error(`FAIL: ${msg} — got ${actual}, expected ${expected}`); fails++; }
  else console.log(`ok: ${msg}`);
}

// Scenario reproducing the reported bug: a 15-card deck where 3 cards were
// missed in earlier sessions, then the user presses "Got It" on every card.
function buildDeck(){
  S = { cards: {} };
  const deck = Array.from({length:15}, (_,i)=>'c'+i);
  rec('c0', false);                 // missed once earlier
  rec('c1', false); rec('c1', false); // missed twice earlier
  rec('c2', false);                 // missed once earlier
  for(let i=3;i<15;i++) rec('c'+i, true);
  deck.forEach(id => rec(id, true)); // user now presses "Got It" on every card
  return deck;
}

// Demonstrate the bug: old logic gets stuck below 100%.
let deck = buildDeck();
const oldPct = Math.round(100 * deck.filter(id=>knownOld(id)).length / deck.length);
eq(oldPct, 80, 'BUG REPRODUCED: old ratio logic shows 80% after Got-It on every card');

// The fix: latest-answer logic reaches 100%.
deck = buildDeck();
const pct = Math.round(100 * deck.filter(id=>known(id)).length / deck.length);
eq(pct, 100, 'FIX: pressing Got It on every card yields 100%');

// a card whose latest answer was a miss is weak / not known
S = { cards: {} };
rec('x', true); rec('x', false);
eq(known('x'), false, 'a card missed most recently is not known');
eq(isWeak('x'), true, 'a card missed most recently is weak');

// a never-seen card is weak and not known
S = { cards: {} };
eq(known('new'), false, 'unseen card is not known');
eq(isWeak('new'), true, 'unseen card is weak');

if(fails){ console.error(`\n${fails} test(s) failed`); process.exit(1); }
console.log('\nall mastery tests passed');
