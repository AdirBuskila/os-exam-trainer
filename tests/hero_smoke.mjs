// Smoke test for js/hero.js: drives the animation through a stubbed canvas
// (jsdom can't rasterize) to catch runtime throws and NaN geometry.
import { JSDOM } from 'jsdom';
import { readFileSync } from 'node:fs';

const bad = [];
function check(name, args){ for(const a of args) if(typeof a==='number' && !Number.isFinite(a)) bad.push(name+'('+args.join(',')+')'); }

const ctxStub = new Proxy({}, { get(_,p){
  if(p==='canvas') return undefined;
  if(p==='setTransform'||p==='clearRect'||p==='beginPath'||p==='moveTo'||p==='lineTo'||
     p==='arc'||p==='fill'||p==='stroke'||p==='fillText'||p==='save'||p==='restore')
    return (...args)=>check(p,args);
  // string/number props (fillStyle, font, globalAlpha, shadowBlur, ...) are settable no-ops
  return undefined;
}, set(){ return true; }});

const dom = new JSDOM('<!doctype html><body><div id="host" style="width:600px;height:160px"></div></body>',
  { pretendToBeVisual:true, runScripts:'outside-only' });
const { window } = dom;

// --- stubs jsdom lacks ---
window.HTMLCanvasElement.prototype.getContext = () => ctxStub;
let rafQ = [];
window.requestAnimationFrame = (cb)=>{ rafQ.push(cb); return rafQ.length; };
window.cancelAnimationFrame = ()=>{};
window.matchMedia = ()=>({ matches:false });
window.ResizeObserver = class { observe(){} disconnect(){} };
window.IntersectionObserver = class { constructor(cb){ cb([{isIntersecting:true}]); } observe(){} disconnect(){} };
// give the host a real size (jsdom returns 0 by default)
const host = window.document.getElementById('host');
host.getBoundingClientRect = ()=>({ width:600, height:160, top:0, left:0, right:600, bottom:160 });

// load hero.js into the window
window.eval(readFileSync(new URL('../js/hero.js', import.meta.url),'utf8'));
if(!window.HERO) throw new Error('HERO not defined');

// run ~200 frames across several tree cycles
let t = 0;
window.HERO.mount(host);
for(let frame=0; frame<200; frame++){
  t += 33;
  const q = rafQ; rafQ = [];
  for(const cb of q) cb(t);
}
window.HERO.destroy();

if(bad.length){ console.error('NON-FINITE GEOMETRY:', bad.slice(0,8)); process.exit(1); }
console.log('hero smoke OK — '+200+' frames, no throws, no NaN geometry');
