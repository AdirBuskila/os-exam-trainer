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
/* localized accessors for the (English-authored) focus/scope metadata */
function isHe(){return I18N.lang==='he';}
function fLabel(){return (isHe()&&FOCUS.label_he)?FOCUS.label_he:FOCUS.label;}
function fNote(){return (isHe()&&FOCUS.note_he)?FOCUS.note_he:FOCUS.note;}
function fExaminer(){return (isHe()&&FOCUS.examiner_he)?FOCUS.examiner_he:FOCUS.examiner;}
function fDropped(){return (isHe()&&FOCUS.dropped_he)?FOCUS.dropped_he:(FOCUS.dropped||[]);}
function qReason(q){return (isHe()&&q.offReason_he)?q.offReason_he:(q.offReason||'');}
function focusBanner(){
  if(!focusOn()) return '';
  const dropped=fDropped();
  return '<div class="banner"><div class="brow"><b>'+t('focus.bannerTitle',{label:esc(fLabel())})+'</b>'+
    '<span class="bx" onclick="toggleFocus()">'+t('focus.showFull')+'</span></div>'+
    '<div class="bnote">'+esc(fNote())+(fExaminer()?' — '+esc(fExaminer()):'')+'</div>'+
    (dropped&&dropped.length?'<div class="bdrop"><b>'+t('focus.hidden')+'</b> '+dropped.map(esc).join(' · ')+'</div>':'')+'</div>';
}

/* ---------------- helpers ---------------- */
function el(h){const d=document.createElement('div');d.innerHTML=h;return d.firstElementChild;}
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
// Hebrew card prose: in HE mode auto-isolate Latin/code/number runs so the bidi
// algorithm can't reorder fork()/PID 4 → 5 → 6/etc. In EN mode keep plain esc()
// so English mode stays byte-for-byte identical to before.
function heContent(s){return isHe()?I18N.autoIsolate(s):esc(s);}
function toast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.remove('hide');clearTimeout(t._t);t._t=setTimeout(()=>t.classList.add('hide'),1400);}
function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function lessonHTML(sid){
  const lo=DATA.lessons[sid]; if(!lo) return '';
  if(typeof lo==='string') return lo;                       // legacy / pre-build shape
  return (isHe()?(lo.he||lo.en):(lo.en||lo.he))||'';        // bilingual {en, he}
}
function qHTML(q){
  let h='';
  if(q.he) h+='<div class="q he" dir="rtl">'+heContent(q.he)+'</div>';
  if(q.code) h+='<pre class="qcode" dir="ltr">'+esc(q.code)+'</pre>';
  if(q.en) h+='<div class="qen" dir="ltr">'+esc(q.en)+'</div>';
  return h;
}
function ansHTML(q){
  let h='<div class="ans">';
  if(q.answer_he) h+='<div class="he" dir="rtl">'+heContent(q.answer_he)+'</div>';
  if(q.answer_en) h+='<div class="en">'+esc(q.answer_en)+'</div>';
  if(q.note) h+='<div class="note">ℹ︎ '+esc(q.note)+'</div>';
  h+='</div>';
  return h;
}
function tagHTML(q){return '<span class="tag '+(q.type||'')+'">'+t('tag.'+(q.type||'concept'))+'</span>';}

/* ---------------- countdown ---------------- */
function updateCount(){
  const exam=new Date(DATA.meta.examDate+'T08:00:00');
  const days=Math.ceil((exam-new Date())/86400000);
  const scoped=scopedQ(); const tot=scoped.length; let strong=0;
  scoped.forEach(q=>{const c=S.cards[q.id]; if(c&&(c.c+c.w)>0&&(c.c/(c.c+c.w))>=0.6)strong++;});
  document.getElementById('count').innerHTML=
    t('count.exam',{date:DATA.meta.examDate,days:(days>=0?days:0)})+'<br>'+
    '<span class="pill">'+t('count.summary',{strong:strong,tot:tot})+' '+t(focusOn()?'count.scopeExam':'count.scopeAll')+'</span>';
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
  if(v==='weak') return renderDeck(scopedQ().filter(q=>isWeak(q.id)),t('weak.title'),t('weak.sub'),view);
  if(v==='years') return renderYears(view);
  if(v==='year') return renderYear(arg,view);
  return renderHome(view);
}
window.addEventListener('hashchange',()=>{});

/* ---------------- home ---------------- */
function renderHome(view){
  let h='<div class="hero-tree" id="heroTree"><div class="hero-cap">fork()</div></div>';
  h+=focusBanner();
  h+='<div class="card"><h2 class="sec">'+t('home.planTitle')+'</h2>'+
    '<p class="progresshint">'+t('home.planHint')+'</p>'+
    '<div class="row" style="margin-top:8px">'+
    '<button class="btn" onclick="go(\'mock\')">'+t('home.takeMock')+'</button>'+
    '<button class="btn ghost" onclick="go(\'weak\')">'+t('home.reviewWeak')+'</button></div></div>';
  h+='<details class="lesson" open><summary>'+t('home.howToTitle')+'</summary><div class="lessonbody">'+t('home.howToBody')+'</div></details>';
  h+='<div class="grid">';
  SEC.forEach(s=>{
    const list=secList(s.id); const hidden=(bySec[s.id]||[]).length-list.length;
    const m=list.length?Math.round(100*list.filter(q=>mastery(q.id)>=0.6).length/list.length):0;
    const he=isHe();
    const t1=he?s.he:s.title, t2=he?s.title:s.he, t2dir=he?'ltr':'rtl';
    h+='<div class="tile'+(list.length?'':' off')+'" onclick="go(\'sec\',\''+s.id+'\')">'+
       '<h3'+(he?' dir="rtl"':'')+'>'+esc(t1)+'</h3><div class="he" dir="'+t2dir+'">'+esc(t2)+'</div>'+
       '<div class="bar"><i style="width:'+m+'%"></i></div>'+
       '<div class="meta"><span>'+t('home.cards',{n:list.length})+(hidden?' <span class="offtag">'+t('home.offCount',{n:hidden})+'</span>':'')+'</span><span>'+m+'%</span></div></div>';
  });
  h+='</div>';
  h+='<div class="card" style="margin-top:14px"><b>'+t('home.trapsTitle')+'</b>'+t('home.trapsBody')+'</div>';
  view.innerHTML=h;
  if(window.HERO)HERO.mount(document.getElementById('heroTree'));
  updateCount();
}

/* ---------------- section ---------------- */
function renderSection(sid,view){
  const sec=SEC.find(s=>s.id===sid); if(!sec)return go('home');
  const list=secList(sid); const hidden=(bySec[sid]||[]).length-list.length;
  const genOff=focusOn()&&GEN_OFF_FOCUS[sid];
  const he=isHe();
  const secName=he?sec.he:sec.title, secAlt=he?sec.title:sec.he, altDir=he?'ltr':'rtl';
  let h=focusBanner();
  h+='<h2 class="sec"'+(he?' dir="rtl"':'')+'>'+esc(secName)+' <span class="he" dir="'+altDir+'" style="color:var(--mut);font-size:15px">'+esc(secAlt)+'</span></h2>';
  h+='<details class="lesson"><summary>'+t('section.lessonLabel',{name:esc(secName)})+'</summary><div class="lessonbody">'+lessonHTML(sid)+'</div></details>';
  const gen=['fork','scheduling','disk','memory'].includes(sid) && !genOff;
  if(gen) h+='<div class="row" style="margin-bottom:12px"><button class="btn" onclick="go(\'sec\',\''+sid+'\');startGen(\''+sid+'\')">'+t('gen.practiceBtn')+'</button> <span class="pill">'+t('gen.practiceTag')+'</span></div>';
  if(hidden) h+='<div class="offnote">'+t('section.offNote',{n:hidden,qword:t(hidden>1?'section.questionMany':'section.questionOne'),label:esc(fLabel()),extra:(genOff?t('section.offNoteGen'):'')})+'<a onclick="toggleFocus()">'+t('focus.showFullLink')+'</a></div>';
  h+='<div id="gen"></div>';
  view.innerHTML=h;
  if(!list.length){ view.appendChild(el('<div class="card center"><p>'+t('section.nothingScope',{label:esc(fLabel())})+'</p></div>')); return; }
  deckInto(view.appendChild(el('<div class="card"></div>')), list, secName);
}

/* ---------------- generic flashcard deck ---------------- */
function renderDeck(list,title,sub,view){
  if(!list.length){view.innerHTML='<div class="card"><h2 class="sec">'+title+'</h2><p>'+t('deck.allStrong')+'</p></div>';return;}
  let h='<h2 class="sec">'+title+'</h2><p class="progresshint">'+(sub||'')+'</p>';
  view.innerHTML=h; deckInto(view.appendChild(el('<div class="card"></div>')),list,title);
}
function deckInto(box,list,title){
  list=shuffle(list); let i=0,shown=false;
  function draw(){
    const q=list[i]; shown=false;
    box.innerHTML='<div class="row"><span class="pill">'+t('deck.progress',{i:(i+1),n:list.length})+'</span> '+tagHTML(q)+
      '<span class="pill" style="margin-inline-start:auto">'+t('deck.examq',{exam:esc(q.exam),q:q.q})+'</span></div>'+
      '<div class="fc"><div id="qa">'+qHTML(q)+'</div>'+
      '<div id="rev"></div>'+
      '<div class="row" id="ctrl"><button class="btn" id="flip">'+t('deck.showAnswer')+' <span class="kbd">'+t('common.space')+'</span></button></div></div>';
    box.querySelector('#flip').onclick=flip;
    function flip(){
      if(shown)return; shown=true;
      box.querySelector('#rev').innerHTML=ansHTML(q);
      box.querySelector('#ctrl').innerHTML=
        '<button class="btn good" id="got">'+t('deck.gotIt')+'</button>'+
        '<button class="btn bad" id="miss">'+t('deck.missed')+'</button>';
      box.querySelector('#got').onclick=()=>{rec(q.id,true);next();};
      box.querySelector('#miss').onclick=()=>{rec(q.id,false);toast(t('deck.willResurface'));next();};
    }
    box._flip=flip;
  }
  function next(){i++;if(i>=list.length){box.innerHTML='<div class="center"><h3>'+t('deck.complete')+'</h3><button class="btn" onclick="render()">'+t('common.back')+'</button></div>';document.onkeydown=null;updateCount();return;}draw();}
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
    const item=OSE.FORK_BANK[idx];
    const base=OSE.forkProblem(idx);                 // {src, ask, answer, explain} (English)
    const r=OSE.forkSim(item.prog);                  // {procs, prints} for localized prose
    const ask=isHe()?t(item.count==='procs'?'gen.fork.askProcs':'gen.fork.askPrints'):base.ask;
    const explain=isHe()
      ?(item.count==='procs'?t('gen.fork.explainProcs',{procs:r.procs}):t('gen.fork.explainPrints',{procs:r.procs,prints:r.prints}))
      :base.explain;
    show('<pre>'+esc(base.src)+'</pre><p>'+esc(ask)+'</p>',base.answer,explain);
  } else if(sid==='disk'){
    prob=genDisk(); show(prob.q,prob.answer,prob.explain);
  } else if(sid==='scheduling'){
    prob=genSched(); show(prob.q,prob.answer,prob.explain);
  } else if(sid==='memory'){
    prob=genPaging(); show(prob.q,prob.answer,prob.explain);
  }
  function show(qhtml,answer,explain){
    g.innerHTML='<div class="card"><div class="row"><b>'+t('gen.generated')+'</b> <span class="pill" style="margin-inline-start:auto">'+t('common.verified')+'</span></div>'+
      '<div style="margin:10px 0">'+qhtml+'</div>'+
      '<div class="row"><input class="input" id="guess" placeholder="'+esc(t('gen.placeholder'))+'" autocomplete="off"> '+
      '<button class="btn" id="chk">'+t('gen.check')+'</button> <button class="btn ghost" id="again">'+t('gen.newProblem')+'</button></div>'+
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
      g.querySelector('#res').innerHTML='<div class="ans"><div class="en">'+(ok?t('gen.correct'):t('gen.answerIs',{a:esc(a)}))+'</div><div class="note" style="color:var(--mut)">'+explain+'</div></div>';
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
  let q=t('gen.disk.intro',{cap:human(cap),platters:platters,surfaces:surfaces,sec:human(sec)})+
        (unknown!=='spt'?t('gen.disk.spt',{spt:spt}):'')+
        (unknown!=='cyl'?t('gen.disk.cyl',{cyl:cyl}):'')+'. ';
  if(unknown==='cyl'){answer=cyl;ask=t('gen.disk.askCyl');}
  else if(unknown==='surf'){answer=surfaces;ask=t('gen.disk.askSurf');}
  else{answer=spt;ask=t('gen.disk.askSpt');}
  return {q:q+ask,answer,explain:t('gen.disk.explain',{total:total})};
}
function genSched(){
  const algos=['FCFS','SJF','SRTF','RR'], algo=algos[rint(0,3)];
  const n=rint(3,4); const ps=[];
  for(let i=0;i<n;i++)ps.push({name:'P'+(i+1),arrival:i===0?0:rint(0,4),burst:rint(2,9)});
  const q=algo==='RR'?rint(2,4):null;
  const r=OSE.schedule(ps,algo,q);
  const tbl=ps.map(p=>t('gen.sched.proc',{n:p.name.slice(1),burst:p.burst,arrival:p.arrival})).join(' · ');
  const g=r.gantt.map(x=>x[0]+'['+x[1]+'-'+x[2]+']').join(' ');
  const algoLabel=algo+(q?' (q='+q+')':'');
  return {q:t('gen.sched.q',{algo:algoLabel,tbl:tbl}),
    answer:+r.avg.toFixed(2),
    explain:t('gen.sched.explain',{gantt:g,avg:(+r.avg.toFixed(2))})};
}
function genPaging(){
  const kind=rint(0,2);
  if(kind===0){const lv=rint(2,4);return {q:t('gen.paging.levelsQ',{lv:lv}),answer:lv+1,explain:t('gen.paging.levelsExplain',{lv:lv,ans:(lv+1)})};}
  const vb=rint(28,44), pexp=rint(10,22), pb=Math.pow(2,pexp), bits=vb-pexp;
  const human=b=>b>=Math.pow(2,20)?(b/Math.pow(2,20))+'MB':(b/Math.pow(2,10))+'KB';
  if(kind===1){return {q:t('gen.paging.entriesQ',{vb:vb,pb:human(pb)}),answer:'2^'+bits,explain:t('gen.paging.entriesExplain',{vb:vb,pexp:pexp,bits:bits})};}
  return {q:t('gen.paging.framesQ',{vb:vb,pb:human(pb)}),answer:'2^'+bits,explain:t('gen.paging.framesExplain',{vb:vb,pexp:pexp,bits:bits})};
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
  let h='<h2 class="sec">'+t('mock.title')+' <span class="tag">'+t('mock.tag')+'</span></h2>'+
        '<div class="card" id="mx"></div>';
  view.innerHTML=h;
  const mx=document.getElementById('mx');
  const t0=Date.now();
  function draw(){
    const q=ex[i];
    mx.innerHTML='<div class="row"><span class="pill">'+t('mock.qcount',{n:(i+1)})+'</span> '+tagHTML(q)+
      '<span class="pill" style="margin-inline-start:auto">'+t('mock.score',{score:score,outof:answered*10})+'</span></div>'+
      '<div class="fc"><div>'+qHTML(q)+'</div><div id="rev"></div>'+
      '<div class="row" id="ctrl"><button class="btn" id="flip">'+t('mock.reveal')+'</button></div></div>';
    mx.querySelector('#flip').onclick=()=>{
      mx.querySelector('#rev').innerHTML=ansHTML(q);
      mx.querySelector('#ctrl').innerHTML='<button class="btn good" id="r">'+t('mock.gotIt')+'</button><button class="btn bad" id="w">'+t('deck.missed')+'</button>';
      mx.querySelector('#r').onclick=()=>{score+=10;answered++;rec(q.id,true);adv();};
      mx.querySelector('#w').onclick=()=>{answered++;rec(q.id,false);adv();};
    };
  }
  function adv(){i++;if(i>=10){const sec=Math.round((Date.now()-t0)/1000);
    mx.innerHTML='<div class="center"><div class="bigtimer">'+score+'/100</div>'+
      '<p class="progresshint">'+(score>=90?t('mock.verdictAce'):score>=70?t('mock.verdictSolid'):t('mock.verdictEarly'))+' · '+t('mock.time',{m:Math.floor(sec/60),s:(sec%60)})+'</p>'+
      '<button class="btn" onclick="go(\'mock\')">'+t('mock.another')+'</button> <button class="btn ghost" onclick="go(\'weak\')">'+t('mock.reviewWeak')+'</button></div>';
    updateCount();return;}draw();}
  draw();
}

/* ---------------- browse by year ---------------- */
function renderYears(view){
  const exams=[...new Set(Q.map(q=>q.exam))].sort();
  let h='<h2 class="sec">'+t('years.title')+'</h2><div class="grid">';
  exams.forEach(e=>{h+='<div class="tile" onclick="go(\'year\',\''+e+'\')"><h3>'+e+'</h3><div class="meta"><span>'+t('years.count',{n:Q.filter(q=>q.exam===e).length})+'</span><span>'+t('common.arrowNext')+'</span></div></div>';});
  view.innerHTML=h+'</div>';
}
function renderYear(e,view){
  const list=Q.filter(q=>q.exam===e).sort((a,b)=>a.q-b.q);
  let h='<h2 class="sec">'+e+' <span class="tag">'+t('year.qTag',{n:list.length})+'</span></h2><div class="card examlist">';
  list.forEach(q=>{h+='<div class="examq'+(q.offExam?' offexam':'')+'">'+
    (q.offExam?'<div class="offbadge">'+t('year.offBadge',{label:esc(fLabel()),reason:esc(qReason(q))})+'</div>':'')+
    qHTML(q)+ansHTML(q)+'</div>';});
  view.innerHTML=h+'</div><button class="btn ghost" onclick="go(\'years\')">'+t('year.allExams')+'</button>';
}

/* ---------------- prefs ---------------- */
function applyPrefs(){document.body.classList.toggle('light',S.prefs.theme==='light');
  document.body.classList.toggle('focusmode',focusOn());
  const fb=document.getElementById('focusBtn'); if(fb){fb.classList.toggle('on',focusOn()); fb.textContent=focusOn()?'🎯 '+fLabel():t('nav.focus');}}
function toggleTheme(){S.prefs.theme=S.prefs.theme==='light'?'dark':'light';save();applyPrefs();}

/* ---------------- boot ---------------- */
I18N.applyLang();
applyPrefs(); if(!location.hash)location.hash='home'; render(); updateCount();
window.onhashchange=render;
// Re-render the whole UI when the language toggle fires.
window.addEventListener('languagechange',function(){I18N.applyLang();render();updateCount();});
