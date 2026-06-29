/* =============================================================================
   OS Exam Trainer — verified practice engines (browser + node)
   Ported from coach/verify.py (which was validated against official exam keys).
   Run `node engines.js` to re-validate against known answers.
   ============================================================================= */
(function (root) {
'use strict';

/* ---------- FORK process-tree simulator ----------------------------------- */
// prog(fork, printf): straight-line code. Returns {procs, prints}.
function forkSim(prog) {
  const queue = [[]];
  let procs = 0, prints = 0;
  while (queue.length) {
    const decisions = queue.shift();
    const st = { i: 0, pos: 0, prints: 0, branch: null };
    const BRANCH = {};
    const fork = () => {
      const j = st.i++;
      if (j < decisions.length) return decisions[j] ? (++st.pos) : 0;
      st.branch = [decisions.concat([true]), decisions.concat([false])];
      throw BRANCH;
    };
    const printf = () => { st.prints++; };
    try { prog(fork, printf); }
    catch (e) {
      if (e === BRANCH) { queue.push(st.branch[0]); queue.push(st.branch[1]); continue; }
      throw e;
    }
    procs++; prints += st.prints;
  }
  return { procs, prints };
}

// Library of fork programs (src shown to student, prog drives the simulator).
// `count` = what the question asks for: 'prints' or 'procs'.
const FORK_BANK = [
  { src: 'fork();\nfork();\nprintf("x\\n");', prog:(f,p)=>{f();f();p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'fork();\nfork();\nfork();\nprintf("x\\n");', prog:(f,p)=>{f();f();f();p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'for(i=0;i<3;i++)\n    fork();\nprintf("x\\n");', prog:(f,p)=>{for(let i=0;i<3;i++)f();p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'a=b=c=fork();\nprintf("HIT\\n");', prog:(f,p)=>{const v=f();p();}, count:'prints', ask:'How many times is "HIT" printed?' },
  { src: 'if(fork()==0)\n    printf("x\\n");', prog:(f,p)=>{if(f()===0)p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'if(fork())\n    printf("x\\n");', prog:(f,p)=>{if(f())p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'if(fork()+fork()==0)\n    printf("x\\n");', prog:(f,p)=>{if(f()+f()===0)p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'if(fork()-fork()==0)\n    printf("x\\n");', prog:(f,p)=>{if(f()-f()===0)p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'if(fork()*fork()*fork()==0)\n    printf("x\\n");', prog:(f,p)=>{if(f()*f()*f()===0)p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'if(fork()==fork())\n    printf("x\\n");', prog:(f,p)=>{if(f()===f())p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'if(fork()!=fork())\n    printf("x\\n");', prog:(f,p)=>{if(f()!==f())p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'fork()?fork():fork();\nprintf("x\\n");', prog:(f,p)=>{(f()?f():f());p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'fork() && fork() && fork();\nprintf("x\\n");', prog:(f,p)=>{(f()&&f()&&f());p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'fork() || fork();\nprintf("x\\n");', prog:(f,p)=>{(f()||f());p();}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'if(fork()+fork()==0){\n    fork();\n    printf("x\\n");\n}', prog:(f,p)=>{if(f()+f()===0){f();p();}}, count:'prints', ask:'How many times is "x" printed?' },
  { src: 'fork();\nfork();\nfork();\nprintf("x\\n");', prog:(f,p)=>{f();f();f();p();}, count:'procs', ask:'How many processes exist in total?' },
];

function forkProblem(idx) {
  const item = FORK_BANK[idx % FORK_BANK.length];
  const r = forkSim(item.prog);
  const answer = item.count === 'procs' ? r.procs : r.prints;
  return {
    src: 'main() {\n    ' + item.src.replace(/\n/g, '\n    ') + '\n}',
    ask: item.ask,
    answer,
    explain: `Total processes spawned: ${r.procs}. ${item.count==='procs' ? 'Count = all processes.' : 'Of those, ' + r.prints + ' reach the printf.'}`
  };
}

/* ---------- SCHEDULING (FCFS / SJF / SRTF / RR) ---------------------------- */
// procs: [{name, arrival, burst}]. Returns {avg, gantt:[[name,s,e]], per:{name:[turn,wait]}}.
function schedule(procs, algo, quantum) {
  const n = procs.length;
  const idxOf = {}; procs.forEach((p,i)=>idxOf[p.name]=i);
  const rem = {}, arr = {}, burst = {}, finish = {};
  procs.forEach(p => { rem[p.name]=p.burst; arr[p.name]=p.arrival; burst[p.name]=p.burst; });
  let t = 0, done = 0; const gantt = [];
  const push = (name, s, e) => {
    if (gantt.length && gantt[gantt.length-1][0]===name) gantt[gantt.length-1][2]=e;
    else gantt.push([name,s,e]);
  };

  if (algo==='FCFS' || algo==='SJF' || algo==='SRTF') {
    while (done < n) {
      const avail = procs.filter(p => arr[p.name]<=t && rem[p.name]>0);
      if (!avail.length) { t = Math.min(...procs.filter(p=>rem[p.name]>0).map(p=>arr[p.name])); continue; }
      let cur, run;
      if (algo==='FCFS') {
        cur = avail.reduce((a,b)=> (arr[a.name]<arr[b.name]||(arr[a.name]===arr[b.name]&&idxOf[a.name]<idxOf[b.name]))?a:b);
        run = rem[cur.name];
      } else if (algo==='SJF') {
        cur = avail.reduce((a,b)=> (burst[a.name]<burst[b.name]||(burst[a.name]===burst[b.name]&&idxOf[a.name]<idxOf[b.name]))?a:b);
        run = rem[cur.name];
      } else { // SRTF
        cur = avail.reduce((a,b)=> (rem[a.name]<rem[b.name]||(rem[a.name]===rem[b.name]&&idxOf[a.name]<idxOf[b.name]))?a:b);
        const fut = procs.filter(p=>arr[p.name]>t && rem[p.name]>0).map(p=>arr[p.name]);
        run = fut.length ? Math.min(Math.min(...fut)-t, rem[cur.name]) : rem[cur.name];
      }
      push(cur.name, t, t+run); rem[cur.name]-=run; t+=run;
      if (rem[cur.name]===0) { finish[cur.name]=t; done++; }
    }
  } else if (algo==='RR') {
    const pending = procs.slice().sort((a,b)=> arr[a.name]-arr[b.name] || idxOf[a.name]-idxOf[b.name]);
    const rq = []; let idx = 0; t = pending[0].arrival;
    while (idx<n && arr[pending[idx].name]<=t) rq.push(pending[idx++].name);
    while (rq.length) {
      const name = rq.shift();
      const run = Math.min(quantum, rem[name]);
      push(name, t, t+run); t+=run; rem[name]-=run;
      while (idx<n && arr[pending[idx].name]<=t) rq.push(pending[idx++].name);
      if (rem[name]>0) rq.push(name); else finish[name]=t;
      if (!rq.length && idx<n) { t = arr[pending[idx].name]; while (idx<n && arr[pending[idx].name]<=t) rq.push(pending[idx++].name); }
    }
  }
  const per = {}; let sumW = 0;
  procs.forEach(p => { const ta=finish[p.name]-arr[p.name], w=ta-burst[p.name]; per[p.name]=[ta,w]; sumW+=w; });
  return { avg: sumW/n, gantt, per };
}

/* ---------- DISK GEOMETRY -------------------------------------------------- */
// total_sectors = cylinders * surfaces * sectorsPerTrack ; capacity = total_sectors * sectorSize
function diskSolve(o) {
  const total = o.capacity / o.sectorSize;
  if (o.cylinders==null) return total / (o.surfaces*o.spt);
  if (o.surfaces==null)  return total / (o.cylinders*o.spt);
  if (o.spt==null)       return total / (o.cylinders*o.surfaces);
  if (o.sectorSize==null) return total; // not used
  return total;
}

/* ---------- PAGING --------------------------------------------------------- */
const log2 = x => Math.round(Math.log2(x));
function pagingFrames(physBits, pageBytes) { return Math.pow(2, physBits - log2(pageBytes)); }
function pagingEntries(virtBits, pageBytes) { return Math.pow(2, virtBits - log2(pageBytes)); }
function tlbMissAccesses(levels) { return levels + 1; }

/* ---------- exports -------------------------------------------------------- */
const API = { forkSim, FORK_BANK, forkProblem, schedule, diskSolve, pagingFrames, pagingEntries, tlbMissAccesses };
if (typeof module !== 'undefined' && module.exports) module.exports = API;
root.OSE = API;

/* ---------- self-test (node) ---------------------------------------------- */
if (typeof require !== 'undefined' && require.main === module) {
  let pass=0, fail=0;
  const check=(label,got,exp)=>{ const ok=String(got)===String(exp); console.log(`${ok?'OK ':'XX '} ${label}: got=${got} exp=${exp}`); ok?pass++:fail++; };

  console.log('--- FORK (vs official keys) ---');
  const F=(src,fn,c)=>{const r=forkSim(fn);return c==='procs'?r.procs:r.prints;};
  check('for 3x fork (2017B)        =8', F(0,(f,p)=>{for(let i=0;i<3;i++)f();p();},'prints'),8);
  check('a=b=c=fork (2022A)         =2', F(0,(f,p)=>{f();p();},'prints'),2);
  check('fork()!=fork() (2022B)     =3', F(0,(f,p)=>{if(f()!==f())p();},'prints'),3);
  check('fork()==fork() (2019B)     =1', F(0,(f,p)=>{if(f()===f())p();},'prints'),1);
  check('fork()+fork()==0{fork} 23A =2', F(0,(f,p)=>{if(f()+f()===0){f();p();}},'prints'),2);
  check('fork()?fork():fork() 23B   =4', F(0,(f,p)=>{(f()?f():f());p();},'prints'),4);
  check('fork()-fork()==0 (2024B)   =1', F(0,(f,p)=>{if(f()-f()===0)p();},'prints'),1);
  check('fork()*fork()*fork()==0 24A=7', F(0,(f,p)=>{if(f()*f()*f()===0)p();},'prints'),7);
  check('fork()&&fork()&&fork() DIAG=4', F(0,(f,p)=>{(f()&&f()&&f());p();},'prints'),4);

  console.log('--- SCHEDULING (vs official keys) ---');
  const avg=(ps,a,q)=>+schedule(ps,a,q).avg.toFixed(2);
  check('FCFS 7@0,3@1,22@4 (2020A)  =4',  avg([{name:'P1',arrival:0,burst:7},{name:'P2',arrival:1,burst:3},{name:'P3',arrival:4,burst:22}],'FCFS'),4);
  check('SRTF 7@0,3@1,22@4 (2020B)  =3',  avg([{name:'P1',arrival:0,burst:7},{name:'P2',arrival:1,burst:3},{name:'P3',arrival:4,burst:22}],'SRTF'),3);
  check('SRTF 9@0,7@1,4@2 (2022A)   =5',  avg([{name:'P1',arrival:0,burst:9},{name:'P2',arrival:1,burst:7},{name:'P3',arrival:2,burst:4}],'SRTF'),5);
  check('RR4 9,3,7,1@0 (2019A)      =9.5',avg([{name:'P1',arrival:0,burst:9},{name:'P2',arrival:0,burst:3},{name:'P3',arrival:0,burst:7},{name:'P4',arrival:0,burst:1}],'RR',4),9.5);
  check('RR4 7,7,7@0 (2021A)        =11', avg([{name:'P1',arrival:0,burst:7},{name:'P2',arrival:0,burst:7},{name:'P3',arrival:0,burst:7}],'RR',4),11);
  check('FCFS 7@0,7@1,7@2 (2021B)   =6',  avg([{name:'P1',arrival:0,burst:7},{name:'P2',arrival:1,burst:7},{name:'P3',arrival:2,burst:7}],'FCFS'),6);
  check('RR4 9@0,7@1,4@3 (2022B)    =9',  avg([{name:'P1',arrival:0,burst:9},{name:'P2',arrival:1,burst:7},{name:'P3',arrival:3,burst:4}],'RR',4),9);
  check('SRTF 7@0,2@2,4@4 (DIAG)    =2',  avg([{name:'P1',arrival:0,burst:7},{name:'P2',arrival:2,burst:2},{name:'P3',arrival:4,burst:4}],'SRTF'),2);
  check('FCFS 7@0,4@2,1@4,4@5 (2017SB)=4.75', avg([{name:'P1',arrival:0,burst:7},{name:'P2',arrival:2,burst:4},{name:'P3',arrival:4,burst:1},{name:'P4',arrival:5,burst:4}],'FCFS'),4.75);

  console.log('--- DISK / PAGING ---');
  check('disk sectors 1000*8*50      =400000', diskSolve({capacity:1000*8*50*512, sectorSize:512, cylinders:1000, surfaces:8, spt:50}),400000);
  check('disk cyl 1TB,4surf,2K,4KB   =32768',  diskSolve({capacity:Math.pow(2,40), sectorSize:4096, surfaces:4, spt:2048, cylinders:null}),32768);
  check('disk surf 0.5TB,8Kcyl,2K,4K =8',       diskSolve({capacity:Math.pow(2,39), sectorSize:4096, cylinders:8192, spt:2048, surfaces:null}),8);
  check('disk cyl DIAG 2TB,8s,16K,8K =2048',    diskSolve({capacity:Math.pow(2,41), sectorSize:8192, surfaces:8, spt:16384, cylinders:null}),2048);
  check('paging frames 42b,1MB       =4194304', pagingFrames(42,Math.pow(2,20)),4194304);
  check('paging entries 36b,4KB      =16777216',pagingEntries(36,4096),16777216);
  check('paging frames 32b,4KB (2015B) =1048576',pagingEntries(32,4096),1048576);
  check('tlb miss 3 levels           =4',       tlbMissAccesses(3),4);

  console.log(`\n${pass} passed, ${fail} failed.`);
  if (fail) process.exit(1);
}

})(typeof window !== 'undefined' ? window : globalThis);
