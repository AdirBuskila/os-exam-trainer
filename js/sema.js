/* =======================================================================
   sema.js — "producer / consumer bounded buffer" canvas animation.

   A producer and a consumer share a bounded ring buffer guarded by three
   semaphores exactly as the course teaches them:  mutex=1, empty=N, full=0.
     Producer:  wait(empty) → wait(mutex) → [deposit] → signal(mutex) → signal(full)
     Consumer:  wait(full)  → wait(mutex) → [remove]  → signal(mutex) → signal(empty)
   Each wait()/signal() ticks the matching semaphore chip; when a wait()
   finds its semaphore at 0 the actor BLOCKS (amber, "WAITING") until the
   other side signals it awake — the canonical full/empty-buffer stall. The
   mutex serialises the critical section (a small lock closes while an actor
   is inside). Pure canvas, no deps. Reads theme colors from CSS vars so it
   tracks light/dark + the accent palette, mirrors for RTL, pauses off-screen
   / when the tab is hidden, honors prefers-reduced-motion, and self-destructs
   once its canvas leaves the DOM (i.e. when you navigate away from home).

   Public API:  SEMA.mount(container)   — (re)start inside an element
                SEMA.destroy()          — stop + remove the current run
   ======================================================================= */
(function(){
  'use strict';

  var OP_MS   = 460;   // how long a wait()/signal() label lingers
  var CS_MS   = 900;   // critical-section token transfer duration (the slow glide)
  var APPEAR  = 380;   // deposited-token pop-in duration

  // Slow "tempo" oscillator: every PHASE_MS we swap which actor is fast, so the
  // buffer swings fully full↔empty and BOTH blocking cases get shown — producer
  // stalled on a full buffer (empty=0), consumer stalled on an empty one (full=0).
  var PHASE_MS  = 13000;
  var T_FAST_MIN= 420, T_FAST_MAX = 820;    // think time for the fast actor
  var T_SLOW_MIN= 4200, T_SLOW_MAX = 6400;  // think time for the slow (near-idle) actor

  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch(e){}

  var inst = null; // the live instance, if any

  function readColors(){
    var cs = getComputedStyle(document.body);
    function v(n,f){ var x=cs.getPropertyValue(n); return (x&&x.trim())||f; }
    return {
      acc : v('--acc' ,'#5b8cff'),
      acc2: v('--acc2','#7c5bff'),
      good: v('--good','#3ecf8e'),
      warn: v('--warn','#ffcf5b'),
      bad : v('--bad' ,'#ff6b6b'),
      line: v('--line','#313a57'),
      card: v('--card','#1d2438'),
      card2:v('--card2','#232c45'),
      mut : v('--mut' ,'#9aa6c4'),
      txt : v('--txt' ,'#e8ecf6')
    };
  }

  function ease(t){ return t<0?0 : t>1?1 : 1-Math.pow(1-t,3); }      // easeOutCubic
  function pop(t){ if (t<=0) return 0; if (t>=1) return 1;           // slight overshoot
    return 1 + 2.2*Math.pow(t-1,3) + 1.2*Math.pow(t-1,2); }
  function clamp(x,a,b){ return x<a?a : x>b?b : x; }
  function rand(a,b){ return a + Math.random()*(b-a); }
  function rr(ctx,x,y,w,h,r){                                        // rounded-rect path
    r = Math.min(r, w/2, h/2);
    ctx.beginPath();
    ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r);
    ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r); ctx.closePath();
  }

  function Instance(container){
    this.container = container;
    this.canvas = container.querySelector('canvas.hero-canvas');
    if (!this.canvas){
      this.canvas = document.createElement('canvas');
      this.canvas.className = 'hero-canvas';
      container.insertBefore(this.canvas, container.firstChild);
    }
    this.ctx = this.canvas.getContext('2d');
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.w = 0; this.h = 0; this.N = 0;
    this.colors = readColors();
    this.visible = true;
    this.raf = 0;
    this.last = null;
    this.colorTick = 0;
    this._needInit = false;
    this.geo = null;

    var self = this;
    this.ro = (window.ResizeObserver) ? new ResizeObserver(function(){ self.resize(); }) : null;
    if (this.ro) this.ro.observe(container);
    this.io = (window.IntersectionObserver) ? new IntersectionObserver(function(e){
      self.visible = e[0].isIntersecting;
      if (self.visible && !self.raf && !reduce){ self.last = null; self.loop(0); }
    }, { threshold: 0.01 }) : null;
    if (this.io) this.io.observe(container);

    this._onVis = function(){
      if (document.hidden){ if (self.raf){ cancelAnimationFrame(self.raf); self.raf=0; } }
      else if (self.visible && !reduce){ if (!self.raf){ self.last = null; self.loop(0); } }
    };
    document.addEventListener('visibilitychange', this._onVis);

    this.resize();
    if (reduce) this.drawStatic();
    else this.loop(0);
  }

  Instance.prototype.rtl = function(){
    return document.documentElement.getAttribute('dir') === 'rtl';
  };

  Instance.prototype.resize = function(){
    var r = this.container.getBoundingClientRect();
    var w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
    if (w === this.w && h === this.h) return;
    this.w = w; this.h = h;
    this.canvas.width  = Math.round(w * this.dpr);
    this.canvas.height = Math.round(h * this.dpr);
    this.canvas.style.width  = w + 'px';
    this.canvas.style.height = h + 'px';
    this.layout();
    if (this._needInit){ this._needInit = false; this.initSim(); }
    if (reduce) this.drawStatic();
  };

  // Geometry only (positions). Sim state is kept across resizes unless N changes.
  Instance.prototype.layout = function(){
    var w = this.w, h = this.h; if (!w) return;
    var rtl = this.rtl();
    var newN = w < 300 ? 2 : 3;
    if (newN !== this.N){ this.N = newN; this._needInit = true; }
    var N = this.N;

    var aw  = clamp(w*0.10, 34, 52);
    var ah  = clamp(h*0.32, 30, 46);
    var midY = h*0.42;
    var padX = Math.max(10, w*0.035);
    var prodX0 = padX + aw/2;          // LTR: producer at the left
    var consX0 = w - padX - aw/2;      // LTR: consumer at the right
    var gap = Math.max(14, w*0.04);
    var bufL = prodX0 + aw/2 + gap;
    var bufR = consX0 - aw/2 - gap;
    var bufW = Math.max(40, bufR - bufL);
    var slotGap  = Math.max(6, bufW*0.04);
    var slotSize = clamp((bufW - (N-1)*slotGap)/N, 12, Math.min(h*0.20, 34));
    var total = N*slotSize + (N-1)*slotGap;
    var x0 = bufL + (bufW - total)/2 + slotSize/2;

    var mx = function(x){ return rtl ? (w - x) : x; };
    var slots = [];
    for (var i=0;i<N;i++){ slots.push({ x: mx(x0 + i*(slotSize+slotGap)), y: midY }); }

    var prodX = mx(prodX0), consX = mx(consX0);
    var centerX = mx((bufL+bufR)/2);
    var pdir = centerX >= prodX ? 1 : -1;     // direction from producer toward buffer
    var cdir = centerX >= consX ? 1 : -1;

    this.geo = {
      aw: aw, ah: ah, midY: midY, slotSize: slotSize,
      prod: { x: prodX, y: midY },
      cons: { x: consX, y: midY },
      prodEdge: { x: prodX + pdir*aw/2, y: midY },
      consEdge: { x: consX + cdir*aw/2, y: midY },
      slots: slots,
      labelY: midY - ah/2 - 9,
      badgeY: midY + ah/2 + 11,
      chipsY: h - 13,
      rtl: rtl
    };
  };

  Instance.prototype.initSim = function(){
    var N = this.N;
    this.sem = { empty: N, full: 0, mutex: 1 };
    this.inPtr = 0; this.outPtr = 0;
    this.buf = [];
    for (var i=0;i<N;i++) this.buf.push({ filled:false, born:0 });
    this.chipFlash = { empty:0, full:0, mutex:0 };
    this.prodFast = true;   // producer fills first → buffer reaches full → producer blocks
    this.phaseT = 0;
    var prodOps = [ {k:'think'}, {k:'acq',s:'empty'}, {k:'acq',s:'mutex'}, {k:'xfer'}, {k:'rel',s:'mutex'}, {k:'rel',s:'full'}  ];
    var consOps = [ {k:'think'}, {k:'acq',s:'full'},  {k:'acq',s:'mutex'}, {k:'xfer'}, {k:'rel',s:'mutex'}, {k:'rel',s:'empty'} ];
    this.prod = this.mkActor('prod', 'producer', prodOps);
    this.cons = this.mkActor('cons', 'consumer', consOps);
  };

  Instance.prototype.mkActor = function(role, name, ops){
    return { role:role, roleName:name, ops:ops, i:0, t:0, dur:0,
             entered:false, acquired:false, blocked:false, blockedOn:null,
             label:name, labelKind:'idle', token:null, xp:0, slot:0 };
  };

  Instance.prototype.nextOp = function(a){
    a.i = (a.i + 1) % a.ops.length; a.entered = false; a.acquired = false; a.t = 0;
  };

  Instance.prototype.startTransfer = function(a, now){
    var g = this.geo;
    if (a.role === 'prod'){
      a.slot = this.inPtr; var s = g.slots[a.slot];
      a.token = { fx:g.prodEdge.x, fy:g.prodEdge.y, tx:s.x, ty:s.y };
    } else {
      a.slot = this.outPtr; var s2 = g.slots[a.slot];
      this.buf[a.slot].filled = false;                 // pulled out of the slot
      a.token = { fx:s2.x, fy:s2.y, tx:g.consEdge.x, ty:g.consEdge.y };
    }
  };

  Instance.prototype.endTransfer = function(a, now){
    if (a.role === 'prod'){
      this.buf[a.slot].filled = true; this.buf[a.slot].born = now;
      this.inPtr = (this.inPtr + 1) % this.N;
    } else {
      this.outPtr = (this.outPtr + 1) % this.N;
    }
    a.token = null;
  };

  // Advance one actor's little state machine by dt ms.
  Instance.prototype.stepActor = function(a, dt, now){
    var op = a.ops[a.i];
    a.t += dt;
    if (op.k === 'think'){
      if (!a.entered){ a.entered=true; a.t=0;
                       var fast = ((a.role==='prod') === this.prodFast);
                       a.dur = fast ? rand(T_FAST_MIN,T_FAST_MAX) : rand(T_SLOW_MIN,T_SLOW_MAX);
                       a.label=a.roleName; a.labelKind='idle'; a.blocked=false; }
      if (a.t >= a.dur) this.nextOp(a);

    } else if (op.k === 'acq'){
      a.label = 'wait(' + op.s + ')';
      if (!a.acquired){
        if (this.sem[op.s] > 0){
          this.sem[op.s]--; this.chipFlash[op.s]=1;
          a.acquired=true; a.t=0; a.blocked=false; a.labelKind='ok';
        } else {
          a.blocked=true; a.blockedOn=op.s; a.labelKind='block';   // BLOCKED until signalled
        }
      } else if (a.t >= OP_MS){
        this.nextOp(a);
      }

    } else if (op.k === 'rel'){
      if (!a.entered){ a.entered=true; a.t=0; this.sem[op.s]++; this.chipFlash[op.s]=1;
                       a.label='signal(' + op.s + ')'; a.labelKind='ok'; a.blocked=false; }
      if (a.t >= OP_MS) this.nextOp(a);

    } else if (op.k === 'xfer'){
      if (!a.entered){ a.entered=true; a.t=0; this.startTransfer(a, now);
                       a.label='in CS'; a.labelKind='ok'; }
      a.xp = ease(a.t / CS_MS);
      if (a.t >= CS_MS){ this.endTransfer(a, now); this.nextOp(a); }
    }
  };

  Instance.prototype.loop = function(now){
    var self = this;
    this.draw(now);
    this.raf = requestAnimationFrame(function(t){ self.loop(t); });
  };

  Instance.prototype.draw = function(now){
    if (!this.canvas.isConnected){ this.destroy(); return; }   // navigated away → self-destruct
    if (!this.visible) return;
    if (!this.geo) return;
    if ((this.colorTick++ % 30) === 0) this.colors = readColors();

    if (this.last == null) this.last = now;
    var dt = Math.min(Math.max(now - this.last, 0), 50);       // clamp (resume/hidden safe)
    this.last = now;

    this.phaseT += dt;
    if (this.phaseT >= PHASE_MS){ this.phaseT = 0; this.prodFast = !this.prodFast; }

    this.stepActor(this.prod, dt, now);
    this.stepActor(this.cons, dt, now);
    var cf = this.chipFlash;
    cf.empty = Math.max(0, cf.empty - dt/320);
    cf.full  = Math.max(0, cf.full  - dt/320);
    cf.mutex = Math.max(0, cf.mutex - dt/320);

    this.render(now);
  };

  Instance.prototype.render = function(now){
    var ctx=this.ctx, w=this.w, h=this.h, C=this.colors, g=this.geo;
    ctx.setTransform(this.dpr,0,0,this.dpr,0,0);
    ctx.clearRect(0,0,w,h);

    // faint conveyor line grounding producer → buffer → consumer
    ctx.globalAlpha = 0.5; ctx.strokeStyle = C.line; ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.moveTo(g.prodEdge.x, g.midY); ctx.lineTo(g.consEdge.x, g.midY); ctx.stroke();
    ctx.globalAlpha = 1;

    this.drawBuffer(now);
    this.drawActor(this.prod, C.acc);
    this.drawActor(this.cons, C.acc2);
    this.drawToken(this.prod, C.acc);
    this.drawToken(this.cons, C.acc2);
    this.drawChips(now);
  };

  Instance.prototype.drawBuffer = function(now){
    var ctx=this.ctx, C=this.colors, g=this.geo, sz=g.slotSize, h=this.h;
    for (var i=0;i<this.N;i++){
      var s = g.slots[i], x = s.x - sz/2, y = s.y - sz/2;
      // slot frame
      ctx.globalAlpha = 0.9; ctx.lineWidth = 1.4; ctx.strokeStyle = C.line;
      rr(ctx, x, y, sz, sz, 5); ctx.stroke();
      // filled token
      if (this.buf[i].filled){
        var sc = pop((now - this.buf[i].born)/APPEAR);
        var tsz = sz*0.62*Math.max(0, sc), tx = s.x - tsz/2, ty = s.y - tsz/2;
        ctx.globalAlpha = 1; ctx.shadowBlur = 6; ctx.shadowColor = C.acc;
        ctx.fillStyle = C.acc; rr(ctx, tx, ty, tsz, tsz, 4); ctx.fill();
        ctx.shadowBlur = 0;
      }
      // in / out pointer ticks (color-coded), only when there's vertical room
      if (h >= 115){
        var below = s.y + sz/2 + 5;
        if (i === this.inPtr){ this.drawTick(s.x + (this.inPtr===this.outPtr? -4:0), below, C.acc); }
        if (i === this.outPtr){ this.drawTick(s.x + (this.inPtr===this.outPtr? 4:0), below, C.acc2); }
      }
    }
    ctx.globalAlpha = 1;
  };

  Instance.prototype.drawTick = function(x, y, color){
    var ctx = this.ctx;
    ctx.globalAlpha = 0.9; ctx.fillStyle = color;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x-3.5, y+5); ctx.lineTo(x+3.5, y+5); ctx.closePath(); ctx.fill();
    ctx.globalAlpha = 1;
  };

  Instance.prototype.drawActor = function(a, color, now){
    var ctx=this.ctx, C=this.colors, g=this.geo, aw=g.aw, ah=g.ah;
    var cx=g[a.role==='prod'?'prod':'cons'].x, cy=g[a.role==='prod'?'prod':'cons'].y;
    var inCS = a.ops[a.i].k === 'xfer';
    var ring = a.blocked ? C.warn : (inCS ? C.good : color);

    ctx.globalAlpha = 1;
    ctx.shadowBlur = a.blocked ? 10 : (inCS ? 12 : 4);
    ctx.shadowColor = ring;
    rr(ctx, cx-aw/2, cy-ah/2, aw, ah, 8);
    ctx.fillStyle = C.card; ctx.fill();
    ctx.lineWidth = 2.2; ctx.strokeStyle = ring; ctx.stroke();
    ctx.shadowBlur = 0;

    // big P / C letter
    ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.font='700 15px ui-monospace,"SF Mono",Menlo,Consolas,monospace';
    ctx.fillStyle = ring;
    ctx.fillText(a.role==='prod'?'P':'C', cx, cy+0.5);

    // operation label above the actor
    if (a.label){
      ctx.font='11px ui-monospace,"SF Mono",Menlo,Consolas,monospace';
      ctx.fillStyle = a.labelKind==='block' ? C.warn : a.labelKind==='ok' ? C.good : C.mut;
      ctx.globalAlpha = a.labelKind==='idle' ? 0.85 : 1;
      ctx.fillText(a.label, cx, g.labelY);
      ctx.globalAlpha = 1;
    }
    // WAITING badge below a blocked actor (pulsing)
    if (a.blocked){
      var puls = 0.55 + 0.45*Math.abs(Math.sin((this.colorTick)*0.12));
      ctx.font='700 9px ui-monospace,"SF Mono",Menlo,Consolas,monospace';
      ctx.fillStyle = C.warn; ctx.globalAlpha = puls;
      ctx.fillText('WAITING', cx, g.badgeY);
      ctx.globalAlpha = 1;
    }
  };

  Instance.prototype.drawToken = function(a, color){
    if (!a.token || a.ops[a.i].k !== 'xfer') return;
    var ctx=this.ctx, C=this.colors, t=a.token, p=a.xp;
    var x = t.fx + (t.tx-t.fx)*p, y = t.fy + (t.ty-t.fy)*p;
    var sz = this.geo.slotSize*0.5;
    ctx.globalAlpha = 1; ctx.shadowBlur = 10; ctx.shadowColor = color;
    ctx.fillStyle = color; rr(ctx, x-sz/2, y-sz/2, sz, sz, 4); ctx.fill();
    ctx.shadowBlur = 0;
  };

  Instance.prototype.drawChips = function(now){
    var ctx=this.ctx, C=this.colors, g=this.geo, w=this.w;
    var data = [ ['empty', this.sem.empty], ['full', this.sem.full], ['mutex', this.sem.mutex] ];
    if (g.rtl) data.reverse();

    ctx.font='600 11px ui-monospace,"SF Mono",Menlo,Consolas,monospace';
    var padIn=7, lockW=14, gap=10, y=g.chipsY, chipH=17;
    var sizes = data.map(function(d){
      var nameW = ctx.measureText(d[0]+' ').width;
      var valW  = ctx.measureText(String(d[1])).width;
      var lock  = d[0]==='mutex' ? lockW : 0;
      return { w: padIn*2 + lock + nameW + valW, nameW:nameW, valW:valW, lock:lock };
    });
    var total = sizes.reduce(function(s,z){ return s+z.w; },0) + gap*(data.length-1);
    var x = (w - total)/2;

    for (var i=0;i<data.length;i++){
      var d=data[i], z=sizes[i], name=d[0], val=String(d[1]);
      var flash = this.chipFlash[name] || 0;
      var held  = name==='mutex' && this.sem.mutex===0;
      // pill
      ctx.globalAlpha = 1; rr(ctx, x, y-chipH/2, z.w, chipH, chipH/2);
      ctx.fillStyle = C.card2; ctx.fill();
      ctx.lineWidth = 1; ctx.strokeStyle = flash>0.02 ? C.good : (held ? C.warn : C.line); ctx.stroke();
      if (flash>0.02){ ctx.globalAlpha = flash*0.30; ctx.fillStyle = C.good; ctx.fill(); ctx.globalAlpha = 1; }

      var cx = x + padIn;
      if (z.lock){ this.drawLock(cx + lockW/2 - 2, y, held, held ? C.warn : C.mut); cx += lockW; }
      ctx.textAlign='left'; ctx.textBaseline='middle';
      ctx.fillStyle = C.mut; ctx.fillText(name+' ', cx, y+0.5);
      ctx.fillStyle = name==='mutex' ? (held ? C.warn : C.good) : C.txt;
      ctx.font='700 11px ui-monospace,"SF Mono",Menlo,Consolas,monospace';
      ctx.fillText(val, cx + z.nameW, y+0.5);
      ctx.font='600 11px ui-monospace,"SF Mono",Menlo,Consolas,monospace';

      x += z.w + gap;
    }
    ctx.textAlign='center';
  };

  Instance.prototype.drawLock = function(cx, cy, locked, color){
    var ctx=this.ctx, bw=8, bh=6, by=cy-1;
    ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = 1.4;
    // shackle
    ctx.beginPath();
    ctx.arc(cx, by-bh/2, 2.6, Math.PI, locked ? 2*Math.PI : Math.PI*1.55, false);
    ctx.stroke();
    // body
    ctx.globalAlpha = 1; rr(ctx, cx-bw/2, by-bh/2+1, bw, bh, 1.5); ctx.fill();
  };

  // Static frame for prefers-reduced-motion: a half-full buffer, sems consistent.
  Instance.prototype.drawStatic = function(){
    if (!this.geo) return;
    var filled = Math.ceil(this.N/2);
    for (var i=0;i<this.N;i++){ this.buf[i].filled = i < filled; this.buf[i].born = -99999; }
    this.sem = { empty: this.N - filled, full: filled, mutex: 1 };
    this.inPtr = filled % this.N; this.outPtr = 0;
    this.prod.label='producer'; this.prod.labelKind='idle'; this.prod.blocked=false;
    this.cons.label='consumer'; this.cons.labelKind='idle'; this.cons.blocked=false;
    this.prod.token=null; this.cons.token=null;
    this.render(0);
  };

  Instance.prototype.destroy = function(){
    if (this.raf){ cancelAnimationFrame(this.raf); this.raf=0; }
    if (this.ro){ try{ this.ro.disconnect(); }catch(e){} }
    if (this.io){ try{ this.io.disconnect(); }catch(e){} }
    document.removeEventListener('visibilitychange', this._onVis);
    if (inst === this) inst = null;
  };

  window.SEMA = {
    mount: function(container){
      if (!container) return;
      if (inst) inst.destroy();
      inst = new Instance(container);
    },
    destroy: function(){ if (inst) inst.destroy(); }
  };
})();
