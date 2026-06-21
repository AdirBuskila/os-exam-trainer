/* ---------------- state ---------------- */
const LS='os_trainer_v1';
let S=JSON.parse(localStorage.getItem(LS)||'{}');
S.cards=S.cards||{}; S.prefs=S.prefs||{theme:'dark'};
function save(){localStorage.setItem(LS,JSON.stringify(S));}
function rec(id,ok){const c=S.cards[id]||{c:0,w:0};if(ok)c.c++;else c.w++;c.last=ok?1:0;S.cards[id]=c;save();}
function mastery(id){const c=S.cards[id];if(!c||(c.c+c.w)===0)return 0;return c.c/(c.c+c.w);}
function isWeak(id){const c=S.cards[id];return !c||c.last===0||mastery(id)<0.6;}

const Q=DATA.questions, SEC=DATA.meta.sections;
const byId={}; Q.forEach(q=>byId[q.id]=q);
const bySec={}; SEC.forEach(s=>bySec[s.id]=[]); Q.forEach(q=>{(bySec[q.section]||(bySec[q.section]=[])).push(q);});

/* ---------------- focus mode (current-semester exam scope) ---------------- */
const FOCUS=DATA.meta.focus||{label:'Exam',dropped:[],note:''};
(function(){const p=new URLSearchParams(location.search);
  if(p.has('focus')) S.prefs.focus=(p.get('focus')!=='0');
  S.prefs.focus=!!S.prefs.focus; save();})();
const GEN_OFF_FOCUS={disk:1};                 // the disk generator is geometry — off in focus
function focusOn(){return !!S.prefs.focus;}
function inScope(q){return !focusOn() || !q.offExam;}
function secList(sid){return (bySec[sid]||[]).filter(inScope);}
function scopedQ(){return Q.filter(inScope);}
function toggleFocus(){
  S.prefs.focus=!S.prefs.focus; save();
  const u=new URL(location.href);
  if(S.prefs.focus) u.searchParams.set('focus','1'); else u.searchParams.delete('focus');
  history.replaceState(null,'',u.toString());
  render();
}
function focusBanner(){
  if(!focusOn()) return '';
  return '<div class="banner"><div class="brow"><b>🎯 Focused on the '+esc(FOCUS.label)+'</b>'+
    '<span class="bx" onclick="toggleFocus()">show full course ✕</span></div>'+
    '<div class="bnote">'+esc(FOCUS.note)+(FOCUS.examiner?' — '+esc(FOCUS.examiner):'')+'</div>'+
    (FOCUS.dropped&&FOCUS.dropped.length?'<div class="bdrop"><b>Hidden:</b> '+FOCUS.dropped.map(esc).join(' · ')+'</div>':'')+'</div>';
}

/* ---------------- helpers ---------------- */
function el(h){const d=document.createElement('div');d.innerHTML=h;return d.firstElementChild;}
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function toast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.remove('hide');clearTimeout(t._t);t._t=setTimeout(()=>t.classList.add('hide'),1400);}
function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function qHTML(q){
  let h='';
  if(q.he) h+='<div class="q he" dir="rtl">'+esc(q.he)+'</div>';
  if(q.code) h+='<pre class="qcode" dir="ltr">'+esc(q.code)+'</pre>';
  if(q.en) h+='<div class="qen" dir="ltr">'+esc(q.en)+'</div>';
  return h;
}
function ansHTML(q){
  let h='<div class="ans">';
  if(q.answer_he) h+='<div class="he" dir="rtl">'+esc(q.answer_he)+'</div>';
  if(q.answer_en) h+='<div class="en">'+esc(q.answer_en)+'</div>';
  if(q.note) h+='<div class="note">ℹ︎ '+esc(q.note)+'</div>';
  h+='</div>';
  return h;
}
function tagHTML(q){return '<span class="tag '+(q.type||'')+'">'+(q.type||'concept')+'</span>';}

/* ---------------- countdown ---------------- */
function updateCount(){
  const exam=new Date(DATA.meta.examDate+'T08:00:00');
  const days=Math.ceil((exam-new Date())/86400000);
  const scoped=scopedQ(); const tot=scoped.length; let strong=0;
  scoped.forEach(q=>{const c=S.cards[q.id]; if(c&&(c.c+c.w)>0&&(c.c/(c.c+c.w))>=0.6)strong++;});
  document.getElementById('count').innerHTML=
    'Exam '+DATA.meta.examDate+' · <b>'+(days>=0?days:0)+' days</b><br>'+
    '<span class="pill">'+strong+'/'+tot+' strong · '+tot+(focusOn()?' on your exam':' questions')+'</span>';
}

/* ---------------- router ---------------- */
function go(v,arg){location.hash=v+(arg?'/'+arg:'');render();window.scrollTo(0,0);}
function render(){
  applyPrefs();
  document.onkeydown=null;
  const [v,arg]=location.hash.replace(/^#/,'').split('/');
  const view=document.getElementById('view');
  if(v==='sec') return renderSection(arg,view);
  if(v==='mock') return renderMock(view);
  if(v==='weak') return renderDeck(scopedQ().filter(q=>isWeak(q.id)),'🔁 Review Weak','Cards you have missed or not seen.',view);
  if(v==='years') return renderYears(view);
  if(v==='year') return renderYear(arg,view);
  return renderHome(view);
}
window.addEventListener('hashchange',()=>{});

/* ---------------- home ---------------- */
function renderHome(view){
  let h=focusBanner();
  h+='<div class="card"><h2 class="sec">🎯 10-day plan · aim: 100%</h2>'+
    '<p class="progresshint">7/10 questions are exact-term recall from a recurring bank; 3/10 are mechanical (fork / scheduling / disk) and worth guaranteed points. Drill the free points to reflex, memorize the bank, over-learn the traps.</p>'+
    '<div class="row" style="margin-top:8px">'+
    '<button class="btn" onclick="go(\'mock\')">📝 Take a Mock Exam</button>'+
    '<button class="btn ghost" onclick="go(\'weak\')">🔁 Review Weak Cards</button></div></div>';
  h+='<details class="lesson" open><summary>ℹ️ How to use this app</summary><div class="lessonbody"><ul style="line-height:1.75;font-size:13.5px">'+
    '<li><b>Sections</b> (below): open one → read the short lesson, then flip flashcards. Tap <b>✓ Got it</b> / <b>✗ Missed</b> — missed cards come back automatically (spaced repetition). Press <span class="kbd">space</span> to flip.</li>'+
    '<li><b>⚡ Practice Generator</b> (fork · scheduling · memory): infinite fresh problems with instantly-checked, verified answers.</li>'+
    '<li><b>📝 Mock Exam</b>: 10 random questions scored like the real exam · <b>🔁 Review Weak</b>: only what you missed · <b>📅 By Year</b>: every real past exam.</li>'+
    '<li><b>🎯 Focus</b>: shows only what is on your current-semester exam. Every card shows the <b>Hebrew question + the code + an English hint</b>.</li>'+
    '<li>Progress is saved on your device.</li>'+
    '</ul></div></details>';
  h+='<div class="grid">';
  SEC.forEach(s=>{
    const list=secList(s.id); const hidden=(bySec[s.id]||[]).length-list.length;
    const m=list.length?Math.round(100*list.filter(q=>mastery(q.id)>=0.6).length/list.length):0;
    h+='<div class="tile'+(list.length?'':' off')+'" onclick="go(\'sec\',\''+s.id+'\')">'+
       '<h3>'+esc(s.title)+'</h3><div class="he" dir="rtl">'+esc(s.he)+'</div>'+
       '<div class="bar"><i style="width:'+m+'%"></i></div>'+
       '<div class="meta"><span>'+list.length+' cards'+(hidden?' <span class="offtag">+'+hidden+' off</span>':'')+'</span><span>'+m+'%</span></div></div>';
  });
  h+='</div>';
  h+='<div class="card" style="margin-top:14px"><b>⚠️ The 3 traps that cost aces their last points</b>'+
     '<ul class="progresshint" style="line-height:1.7">'+
     '<li><b>Who sets which bit:</b> CPU/MMU <i>sets</i> reference &amp; dirty bits; the <b>OS</b> clears the reference bit (Clock) &amp; sets present/valid.</li>'+
     '<li><b>Critical-section conditions:</b> Mutual Exclusion / Progress / Bounded Waiting. "Starvation" is a <i>consequence</i>, not a condition.</li>'+
     '<li><b>Scheduling identity:</b> RR(quantum=∞)=FCFS; SJF=non-preemptive, SRTF=preemptive.</li></ul></div>';
  view.innerHTML=h;
  updateCount();
}

/* ---------------- section ---------------- */
function renderSection(sid,view){
  const sec=SEC.find(s=>s.id===sid); if(!sec)return go('home');
  const list=secList(sid); const hidden=(bySec[sid]||[]).length-list.length;
  const genOff=focusOn()&&GEN_OFF_FOCUS[sid];
  let h=focusBanner();
  h+='<h2 class="sec">'+esc(sec.title)+' <span class="he" dir="rtl" style="color:var(--mut);font-size:15px">'+esc(sec.he)+'</span></h2>';
  h+='<details class="lesson"><summary>Lesson — '+esc(sec.title)+'</summary><div class="lessonbody">'+(DATA.lessons[sid]||'')+'</div></details>';
  const gen=['fork','scheduling','disk','memory'].includes(sid) && !genOff;
  if(gen) h+='<div class="row" style="margin-bottom:12px"><button class="btn" onclick="go(\'sec\',\''+sid+'\');startGen(\''+sid+'\')">⚡ Practice Generator (infinite)</button> <span class="pill">fresh problems, verified answers</span></div>';
  if(hidden) h+='<div class="offnote">🎯 '+hidden+' question'+(hidden>1?'s':'')+' hidden — off your '+esc(FOCUS.label)+(genOff?' (incl. the disk-geometry generator)':'')+'. <a onclick="toggleFocus()">show full course</a></div>';
  h+='<div id="gen"></div>';
  view.innerHTML=h;
  if(!list.length){ view.appendChild(el('<div class="card center"><p>🎉 Nothing here is on your '+esc(FOCUS.label)+'.</p></div>')); return; }
  deckInto(view.appendChild(el('<div class="card"></div>')), list, sec.title);
}

/* ---------------- generic flashcard deck ---------------- */
function renderDeck(list,title,sub,view){
  if(!list.length){view.innerHTML='<div class="card"><h2 class="sec">'+title+'</h2><p>🎉 Nothing here — all strong!</p></div>';return;}
  let h='<h2 class="sec">'+title+'</h2><p class="progresshint">'+(sub||'')+'</p>';
  view.innerHTML=h; deckInto(view.appendChild(el('<div class="card"></div>')),list,title);
}
function deckInto(box,list,title){
  list=shuffle(list); let i=0,shown=false;
  function draw(){
    const q=list[i]; shown=false;
    box.innerHTML='<div class="row"><span class="pill">'+(i+1)+' / '+list.length+'</span> '+tagHTML(q)+
      '<span class="pill" style="margin-inline-start:auto">'+esc(q.exam)+' · Q'+q.q+'</span></div>'+
      '<div class="fc"><div id="qa">'+qHTML(q)+'</div>'+
      '<div id="rev"></div>'+
      '<div class="row" id="ctrl"><button class="btn" id="flip">Show answer <span class="kbd">space</span></button></div></div>';
    box.querySelector('#flip').onclick=flip;
    function flip(){
      if(shown)return; shown=true;
      box.querySelector('#rev').innerHTML=ansHTML(q);
      box.querySelector('#ctrl').innerHTML=
        '<button class="btn good" id="got">✓ Got it</button>'+
        '<button class="btn bad" id="miss">✗ Missed</button>';
      box.querySelector('#got').onclick=()=>{rec(q.id,true);next();};
      box.querySelector('#miss').onclick=()=>{rec(q.id,false);toast('Will resurface');next();};
    }
    box._flip=flip;
  }
  function next(){i++;if(i>=list.length){box.innerHTML='<div class="center"><h3>Deck complete ✓</h3><button class="btn" onclick="render()">Back</button></div>';document.onkeydown=null;updateCount();return;}draw();}
  box._key=(e)=>{if(e.code==='Space'){e.preventDefault();if(!shown)box._flip();}};
  draw();
  document.onkeydown=(e)=>{if(box._key)box._key(e);};
}

/* ---------------- computational generators ---------------- */
function startGen(sid){
  const g=document.getElementById('gen'); if(!g)return;
  let prob;
  if(sid==='fork'){
    const idx=Math.floor(Math.random()*OSE.FORK_BANK.length);
    prob=OSE.forkProblem(idx);
    show('<pre>'+esc(prob.src)+'</pre><p>'+esc(prob.ask)+'</p>',prob.answer,prob.explain);
  } else if(sid==='disk'){
    prob=genDisk(); show(prob.q,prob.answer,prob.explain);
  } else if(sid==='scheduling'){
    prob=genSched(); show(prob.q,prob.answer,prob.explain);
  } else if(sid==='memory'){
    prob=genPaging(); show(prob.q,prob.answer,prob.explain);
  }
  function show(qhtml,answer,explain){
    g.innerHTML='<div class="card"><div class="row"><b>⚡ Generated problem</b> <span class="pill" style="margin-inline-start:auto">verified</span></div>'+
      '<div style="margin:10px 0">'+qhtml+'</div>'+
      '<div class="row"><input class="input" id="guess" placeholder="your answer" autocomplete="off"> '+
      '<button class="btn" id="chk">Check</button> <button class="btn ghost" id="again">New ↻</button></div>'+
      '<div id="res" style="margin-top:10px"></div></div>';
    g.querySelector('#again').onclick=()=>startGen(sid);
    g.querySelector('#chk').onclick=()=>{
      const raw=g.querySelector('#guess').value.trim(); const a=String(answer);
      let ok=false;
      if(raw!==''){
        const vn=parseFloat(raw.replace(/[\s,]/g,'')), an=parseFloat(a);
        if(a.indexOf('^')<0 && !isNaN(vn) && !isNaN(an)) ok=Math.abs(vn-an)<0.011;
        else ok=raw.replace(/\s/g,'').toLowerCase()===a.replace(/\s/g,'').toLowerCase();
      }
      g.querySelector('#res').innerHTML='<div class="ans"><div class="en">'+(ok?'✓ Correct!':'✗ Answer: <b>'+esc(a)+'</b>')+'</div><div class="note" style="color:var(--mut)">'+explain+'</div></div>';
    };
    g.querySelector('#guess').addEventListener('keydown',e=>{if(e.key==='Enter')g.querySelector('#chk').click();});
  }
}
function rint(a,b){return a+Math.floor(Math.random()*(b-a+1));}
function genDisk(){
  const platters=rint(1,4), surfaces=platters*2;
  const cyl=Math.pow(2,rint(10,14)), spt=Math.pow(2,rint(9,12)), sec=Math.pow(2,rint(10,13));
  const total=cyl*surfaces*spt, cap=total*sec;
  const unknown=['cyl','surf','spt'][rint(0,2)];
  const human=b=>b>=Math.pow(2,40)?(b/Math.pow(2,40))+'TB':b>=Math.pow(2,30)?(b/Math.pow(2,30))+'GB':(b/Math.pow(2,20))+'MB';
  let ask,answer;
  let q='A hard disk: capacity <b>'+human(cap)+'</b>, '+platters+' platters ('+surfaces+' surfaces), '+
        'sector size <b>'+human(sec)+'</b>'+(unknown!=='spt'?', <b>'+spt+'</b> sectors/track':'')+
        (unknown!=='cyl'?', <b>'+cyl+'</b> cylinders':'')+'. ';
  if(unknown==='cyl'){answer=cyl;ask='How many cylinders?';}
  else if(unknown==='surf'){answer=surfaces;ask='How many surfaces?';}
  else{answer=spt;ask='How many sectors per track?';}
  return {q:q+ask,answer,explain:'total sectors = capacity/sector = '+total+'; = cylinders×surfaces×sectors-per-track. Solve for the unknown.'};
}
function genSched(){
  const algos=['FCFS','SJF','SRTF','RR'], algo=algos[rint(0,3)];
  const n=rint(3,4); const ps=[];
  for(let i=0;i<n;i++)ps.push({name:'P'+(i+1),arrival:i===0?0:rint(0,4),burst:rint(2,9)});
  const q=algo==='RR'?rint(2,4):null;
  const r=OSE.schedule(ps,algo,q);
  const tbl=ps.map(p=>'P'+p.name.slice(1)+': burst '+p.burst+' @ '+p.arrival).join(' · ');
  const g=r.gantt.map(x=>x[0]+'['+x[1]+'-'+x[2]+']').join(' ');
  return {q:'Algorithm <b>'+algo+(q?' (q='+q+')':'')+'</b>. Processes: '+tbl+'. <br>Average waiting time?',
    answer:+r.avg.toFixed(2),
    explain:'Gantt: '+g+'. Avg waiting = '+(+r.avg.toFixed(2))+' (turnaround−burst, averaged).'};
}
function genPaging(){
  const kind=rint(0,2);
  if(kind===0){const lv=rint(2,4);return {q:'Multilevel paging with <b>'+lv+'</b> levels. On a TLB miss, how many memory accesses?',answer:lv+1,explain:lv+' page-table levels + 1 access to the page = '+(lv+1)+'.'};}
  const vb=rint(28,44), pexp=rint(10,22), pb=Math.pow(2,pexp), bits=vb-pexp;
  const human=b=>b>=Math.pow(2,20)?(b/Math.pow(2,20))+'MB':(b/Math.pow(2,10))+'KB';
  if(kind===1){return {q:'Virtual address <b>'+vb+' bits</b>, page size <b>'+human(pb)+'</b>. Entries in a single-level page table?',answer:'2^'+bits,explain:'page-number bits = '+vb+' − '+pexp+' = '+bits+' → 2^'+bits+' entries.'};}
  return {q:'Physical address <b>'+vb+' bits</b>, page size <b>'+human(pb)+'</b>. How many frames?',answer:'2^'+bits,explain:'frame bits = '+vb+' − '+pexp+' = '+bits+' → 2^'+bits+' frames.'};
}

/* ---------------- mock exam ---------------- */
function renderMock(view){
  // 1 fork + 1 disk/sched compute + 8 others, mirror the real spread
  const pool=scopedQ();
  const fork=shuffle(pool.filter(q=>q.section==='fork'))[0];
  const comp=shuffle(pool.filter(q=>q.type==='compute'&&q.section!=='fork'))[0];
  const rest=shuffle(pool.filter(q=>q!==fork&&q!==comp)).slice(0,8);
  const ex=shuffle([fork,comp].filter(Boolean).concat(rest)).slice(0,10);
  let i=0,score=0,answered=0;
  let h='<h2 class="sec">📝 Mock Exam <span class="tag">10 × 10 pts · ≤5 words</span></h2>'+
        '<div class="card" id="mx"></div>';
  view.innerHTML=h;
  const mx=document.getElementById('mx');
  const t0=Date.now();
  function draw(){
    const q=ex[i];
    mx.innerHTML='<div class="row"><span class="pill">Q'+(i+1)+' / 10</span> '+tagHTML(q)+
      '<span class="pill" style="margin-inline-start:auto">score '+score+'/'+answered*10+'</span></div>'+
      '<div class="fc"><div>'+qHTML(q)+'</div><div id="rev"></div>'+
      '<div class="row" id="ctrl"><button class="btn" id="flip">Reveal answer</button></div></div>';
    mx.querySelector('#flip').onclick=()=>{
      mx.querySelector('#rev').innerHTML=ansHTML(q);
      mx.querySelector('#ctrl').innerHTML='<button class="btn good" id="r">✓ I got it</button><button class="btn bad" id="w">✗ Missed</button>';
      mx.querySelector('#r').onclick=()=>{score+=10;answered++;rec(q.id,true);adv();};
      mx.querySelector('#w').onclick=()=>{answered++;rec(q.id,false);adv();};
    };
  }
  function adv(){i++;if(i>=10){const sec=Math.round((Date.now()-t0)/1000);
    mx.innerHTML='<div class="center"><div class="bigtimer">'+score+'/100</div>'+
      '<p class="progresshint">'+(score>=90?'Ace range. 🔥':score>=70?'Solid — close the gaps.':'Early days — keep drilling.')+' · '+Math.floor(sec/60)+'m '+(sec%60)+'s</p>'+
      '<button class="btn" onclick="go(\'mock\')">Another</button> <button class="btn ghost" onclick="go(\'weak\')">Review weak</button></div>';
    updateCount();return;}draw();}
  draw();
}

/* ---------------- browse by year ---------------- */
function renderYears(view){
  const exams=[...new Set(Q.map(q=>q.exam))].sort();
  let h='<h2 class="sec">📅 Browse by Exam</h2><div class="grid">';
  exams.forEach(e=>{h+='<div class="tile" onclick="go(\'year\',\''+e+'\')"><h3>'+e+'</h3><div class="meta"><span>'+Q.filter(q=>q.exam===e).length+' questions</span><span>→</span></div></div>';});
  view.innerHTML=h+'</div>';
}
function renderYear(e,view){
  const list=Q.filter(q=>q.exam===e).sort((a,b)=>a.q-b.q);
  let h='<h2 class="sec">'+e+' <span class="tag">'+list.length+' Q</span></h2><div class="card examlist">';
  list.forEach(q=>{h+='<div class="examq'+(q.offExam?' offexam':'')+'">'+
    (q.offExam?'<div class="offbadge">⛔ off the '+esc(FOCUS.label)+' — '+esc(q.offReason||'')+'</div>':'')+
    qHTML(q)+ansHTML(q)+'</div>';});
  view.innerHTML=h+'</div><button class="btn ghost" onclick="go(\'years\')">← All exams</button>';
}

/* ---------------- prefs ---------------- */
function applyPrefs(){document.body.classList.toggle('light',S.prefs.theme==='light');
  document.body.classList.toggle('focusmode',focusOn());
  const fb=document.getElementById('focusBtn'); if(fb){fb.classList.toggle('on',focusOn()); fb.textContent=focusOn()?'🎯 '+FOCUS.label:'🎯 Focus';}}
function toggleTheme(){S.prefs.theme=S.prefs.theme==='light'?'dark':'light';save();applyPrefs();}

applyPrefs(); if(!location.hash)location.hash='home'; render(); updateCount();
window.onhashchange=render;
