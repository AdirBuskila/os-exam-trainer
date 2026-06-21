// Fuzz-tests the in-app problem GENERATORS (mirrors js/app.js logic)
// against independent recomputation, using the verified engine.
//   node tests/gentest.js
const OSE = require("../js/engines.js");
function rint(a, b) { return a + Math.floor(Math.random() * (b - a + 1)); }

function genDisk() {
  const platters = rint(1, 4), surfaces = platters * 2;
  const cyl = Math.pow(2, rint(10, 14)), spt = Math.pow(2, rint(9, 12)), sec = Math.pow(2, rint(10, 13));
  const total = cyl * surfaces * spt, cap = total * sec;
  const unknown = ["cyl", "surf", "spt"][rint(0, 2)];
  let answer = unknown === "cyl" ? cyl : unknown === "surf" ? surfaces : spt;
  return { answer, ok: cap / sec === cyl * surfaces * spt && total === cyl * surfaces * spt };
}
function genSched() {
  const algo = ["FCFS", "SJF", "SRTF", "RR"][rint(0, 3)];
  const n = rint(3, 4), ps = [];
  for (let i = 0; i < n; i++) ps.push({ name: "P" + (i + 1), arrival: i === 0 ? 0 : rint(0, 4), burst: rint(2, 9) });
  const q = algo === "RR" ? rint(2, 4) : null;
  const r = OSE.schedule(ps, algo, q);
  const answer = +r.avg.toFixed(2);
  const fin = {}, arr = {}, bur = {};
  ps.forEach(p => { arr[p.name] = p.arrival; bur[p.name] = p.burst; });
  r.gantt.forEach(g => fin[g[0]] = g[2]);
  let sum = 0; ps.forEach(p => sum += fin[p.name] - arr[p.name] - bur[p.name]);
  return { answer, ok: answer === +(sum / n).toFixed(2) && answer >= 0 && isFinite(answer) };
}
function genPaging() {
  const kind = rint(0, 2);
  if (kind === 0) { const lv = rint(2, 4); return { answer: lv + 1, ok: true }; }
  const vb = rint(28, 44), pexp = rint(10, 22), bits = vb - pexp;
  return { answer: "2^" + bits, ok: bits > 0 };
}

let fail = 0;
for (let i = 0; i < 2000; i++) {
  if (!genDisk().ok) { fail++; console.log("DISK FAIL"); }
  if (!genSched().ok) { fail++; console.log("SCHED FAIL"); }
  if (!genPaging().ok) { fail++; console.log("PAGE FAIL"); }
}
console.log(fail ? fail + " FAILURES" : "Generators: 6000 random problems verified, 0 failures.");
process.exit(fail ? 1 : 0);
