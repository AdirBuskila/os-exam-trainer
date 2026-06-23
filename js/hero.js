/* =======================================================================
   hero.js — "forking process tree" canvas animation for the home view.

   A root PID spawns children generation-by-generation (fork waves). Each
   node pops in, flashes green, then settles to the accent ring; a pulse
   ripples down the tree while it holds, then leaves are reaped first and a
   fresh tree grows. Pure canvas, no deps. Reads theme colors from CSS vars
   so it tracks light/dark + the accent palette, mirrors for RTL, pauses
   off-screen / when the tab is hidden, and self-destructs once its canvas
   leaves the DOM (i.e. when you navigate away from home).

   Public API:  HERO.mount(container)   — (re)start inside an element
                HERO.destroy()          — stop + remove the current run
   ======================================================================= */
(function(){
  'use strict';

  var GEN_MS   = 520;   // delay between fork generations
  var APPEAR   = 380;   // node pop-in duration
  var FLASH    = 720;   // green spawn-flash decay
  var HOLD     = 1600;  // pause once the tree is fully grown
  var REAP_STG = 180;   // per-depth stagger when reaping (leaves first)
  var REAP_DUR = 360;   // fade-out duration per node
  var NODE_CAP = 13;    // max processes per tree
  var MAX_DEPTH= 4;     // max fork depth

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
      line: v('--line','#313a57'),
      card: v('--card','#1d2438'),
      mut : v('--mut' ,'#9aa6c4')
    };
  }

  // Build a random fork tree: array of {depth, parent} with root at index 0.
  function buildTree(){
    var nodes = [{ depth:0, parent:-1, pid:1000 + Math.floor(Math.random()*9000) }];
    var frontier = [0];
    var nextPid = nodes[0].pid + 1 + Math.floor(Math.random()*40);
    var depth = 1;
    while (depth <= MAX_DEPTH && frontier.length && nodes.length < NODE_CAP){
      var next = [];
      for (var f=0; f<frontier.length && nodes.length < NODE_CAP; f++){
        // each live process forks 1–2 children (sometimes 0 so shape varies)
        var kids = Math.random() < 0.78 ? (Math.random() < 0.5 ? 2 : 1) : 0;
        for (var k=0; k<kids && nodes.length < NODE_CAP; k++){
          nodes.push({ depth:depth, parent:frontier[f], pid:nextPid++ });
          next.push(nodes.length-1);
        }
      }
      if (!next.length) break;
      frontier = next;
      depth++;
    }
    // ensure the root has at least one child so it never looks dead
    if (nodes.length === 1) nodes.push({ depth:1, parent:0, pid:nodes[0].pid+1 });
    return nodes;
  }

  // Tidy layout: x by depth, y by leaf ordering (parent = mean of children).
  function layout(nodes, w, h, rtl){
    var kids = nodes.map(function(){ return []; });
    var maxDepth = 0;
    nodes.forEach(function(n,i){
      if (n.parent >= 0) kids[n.parent].push(i);
      if (n.depth > maxDepth) maxDepth = n.depth;
    });
    var leaves = 0;
    nodes.forEach(function(n,i){ if (!kids[i].length) n._leaf = true; });
    nodes.forEach(function(n,i){ if (n._leaf) leaves++; });

    var xm = Math.max(26, w*0.07), ym = Math.max(18, h*0.16);
    var levelGap = (w - 2*xm) / Math.max(1, maxDepth);
    var rowGap   = leaves > 1 ? (h - 2*ym) / (leaves - 1) : 0;
    var cursor = 0;

    function assign(i){
      var n = nodes[i];
      if (kids[i].length){
        var sum = 0;
        kids[i].forEach(function(c){ sum += assign(c); });
        n._row = sum / kids[i].length;
      } else {
        n._row = cursor++;
      }
      var x = xm + n.depth * levelGap;
      n.tx = rtl ? (w - x) : x;
      n.ty = (leaves > 1) ? (ym + n._row * rowGap) : (h/2);
      return n._row;
    }
    assign(0);
    nodes.forEach(function(n,i){ n._kids = kids[i]; n._maxDepth = maxDepth; });
  }

  function ease(t){ return t<0?0 : t>1?1 : 1-Math.pow(1-t,3); }     // easeOutCubic
  function pop(t){ // slight overshoot for the pop-in
    if (t<=0) return 0; if (t>=1) return 1;
    return 1 + 2.2*Math.pow(t-1,3) + 1.2*Math.pow(t-1,2);
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
    this.w = 0; this.h = 0;
    this.colors = readColors();
    this.visible = true;
    this.raf = 0;
    this.cycleStart = 0;
    this.nodes = [];
    this.colorTick = 0;

    var self = this;
    this.ro = (window.ResizeObserver) ? new ResizeObserver(function(){ self.resize(); }) : null;
    if (this.ro) this.ro.observe(container);
    this.io = (window.IntersectionObserver) ? new IntersectionObserver(function(e){
      self.visible = e[0].isIntersecting;
      if (self.visible && !self.raf && !reduce) self.loop(0);
    }, { threshold: 0.01 }) : null;
    if (this.io) this.io.observe(container);

    this._onVis = function(){
      if (document.hidden){ if (self.raf){ cancelAnimationFrame(self.raf); self.raf=0; } }
      else if (self.visible && !reduce){ if (!self.raf) self.loop(0); }
    };
    document.addEventListener('visibilitychange', this._onVis);

    this.resize();
    this.regen(0);
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
    if (this.nodes.length) layout(this.nodes, w, h, this.rtl());
    if (reduce) this.drawStatic();
  };

  Instance.prototype.regen = function(now){
    var nodes = buildTree();
    layout(nodes, this.w, this.h, this.rtl());
    var maxDepth = nodes[0]._maxDepth || 1;
    nodes.forEach(function(n){
      n.revealAt = n.depth * GEN_MS + Math.random()*120;
      n.cx = null; n.cy = null;                 // set on first reveal (emerge from parent)
      n.wp = Math.random()*Math.PI*2;           // idle-wander phase
    });
    this.nodes = nodes;
    this.maxDepth = maxDepth;
    this.growEnd = maxDepth*GEN_MS + APPEAR;
    this.holdEnd = this.growEnd + HOLD;
    this.reapEnd = this.holdEnd + (maxDepth+1)*REAP_STG + REAP_DUR;
    this.cycleLen= this.reapEnd + 300;
    this.cycleStart = now;
  };

  Instance.prototype.loop = function(now){
    var self = this;
    this.draw(now);
    this.raf = requestAnimationFrame(function(t){ self.loop(t); });
  };

  Instance.prototype.draw = function(now){
    // self-destruct once we've been detached from the DOM (navigated away)
    if (!this.canvas.isConnected){ this.destroy(); return; }
    if (!this.visible) return;

    if ((this.colorTick++ % 30) === 0) this.colors = readColors(); // pick up theme flips

    var ctx = this.ctx, w = this.w, h = this.h, C = this.colors;
    var elapsed = now - this.cycleStart;
    if (elapsed > this.cycleLen) { this.regen(now); elapsed = 0; }

    ctx.setTransform(this.dpr,0,0,this.dpr,0,0);
    ctx.clearRect(0,0,w,h);

    var r = Math.max(5, Math.min(9, h/20));
    var nodes = this.nodes, maxDepth = this.maxDepth;

    // advance springs + compute per-node visibility/glow
    for (var i=0;i<nodes.length;i++){
      var n = nodes[i];
      var appearIn = ease((elapsed - n.revealAt)/APPEAR);
      var dieStart = this.holdEnd + (maxDepth - n.depth)*REAP_STG;
      var dieOut   = ease((elapsed - dieStart)/REAP_DUR);
      n.vis = appearIn * (1 - dieOut);
      n.scale = pop((elapsed - n.revealAt)/APPEAR) * (1 - dieOut);

      // emerge from parent the first frame it appears
      if (n.cx === null){
        if (elapsed >= n.revealAt){
          var p = n.parent>=0 ? nodes[n.parent] : null;
          n.cx = p && p.cx!==null ? p.cx : n.tx;
          n.cy = p && p.cy!==null ? p.cy : n.ty;
        } else { n.cx = n.tx; n.cy = n.ty; }
      }
      n.cx += (n.tx - n.cx) * 0.16;
      n.cy += (n.ty - n.cy) * 0.16;

      // green spawn flash + a pulse that ripples down the tree during HOLD
      var flash = Math.max(0, 1 - (elapsed - n.revealAt)/FLASH);
      var pulse = 0;
      if (elapsed > this.growEnd && elapsed < this.holdEnd){
        var localT = (elapsed - this.growEnd) % 900;
        var front  = localT / 150;                 // travels ~depth/150ms
        pulse = Math.max(0, 1 - Math.abs(front - n.depth)) * 0.85;
      }
      n.glow = Math.max(flash, pulse) * (n.vis>0?1:0);
    }

    // edges (under nodes)
    ctx.lineWidth = 1.4;
    for (var e=0;e<nodes.length;e++){
      var c = nodes[e]; if (c.parent < 0 || c.vis <= 0.02) continue;
      var par = nodes[c.parent];
      var wob = Math.sin(now*0.0012 + c.wp);
      var x1 = par.cx, y1 = par.cy + wob*1.2;
      var x2 = c.cx,   y2 = c.cy   + wob*1.2;
      ctx.globalAlpha = c.vis * 0.9;
      ctx.strokeStyle = C.line;
      ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
      if (c.glow > 0.04){                          // accent overlay as the pulse passes
        ctx.globalAlpha = c.vis * c.glow;
        ctx.strokeStyle = C.acc;
        ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
      }
    }

    // nodes
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = '10px ui-monospace, "SF Mono", Menlo, Consolas, monospace';
    for (var j=0;j<nodes.length;j++){
      var nd = nodes[j]; if (nd.vis <= 0.02) continue;
      var wy = Math.sin(now*0.0012 + nd.wp) * 1.2;
      var x = nd.cx, y = nd.cy + wy;
      var rad = r * Math.max(0, nd.scale);
      var isRoot = nd.parent < 0;
      var ring = isRoot ? C.acc2 : C.acc;

      ctx.globalAlpha = nd.vis;
      ctx.shadowBlur = 6 + nd.glow*16;
      ctx.shadowColor = nd.glow>0.04 ? C.good : ring;

      ctx.beginPath(); ctx.arc(x, y, rad, 0, Math.PI*2);
      ctx.fillStyle = C.card; ctx.fill();
      ctx.lineWidth = isRoot ? 2.4 : 2;
      ctx.strokeStyle = ring; ctx.stroke();

      if (nd.glow > 0.04){                          // green flash ring over the accent
        ctx.globalAlpha = nd.vis * nd.glow;
        ctx.strokeStyle = C.good; ctx.stroke();
      }
      ctx.shadowBlur = 0;

      // pid label (skip on cramped layouts)
      if (rad >= 5 && h >= 90){
        ctx.globalAlpha = nd.vis * 0.7;
        ctx.fillStyle = C.mut;
        ctx.fillText(String(nd.pid), x, y + rad + 8);
      }
    }
    ctx.globalAlpha = 1;
  };

  // One fully-grown static tree for prefers-reduced-motion.
  Instance.prototype.drawStatic = function(){
    if (!this.w) return;
    var ctx=this.ctx, C=this.colors, nodes=this.nodes, r=Math.max(5,Math.min(9,this.h/20));
    ctx.setTransform(this.dpr,0,0,this.dpr,0,0);
    ctx.clearRect(0,0,this.w,this.h);
    nodes.forEach(function(n){ n.cx=n.tx; n.cy=n.ty; });
    ctx.lineWidth=1.4; ctx.strokeStyle=C.line;
    nodes.forEach(function(c){ if(c.parent<0)return; var p=nodes[c.parent];
      ctx.beginPath(); ctx.moveTo(p.cx,p.cy); ctx.lineTo(c.cx,c.cy); ctx.stroke(); });
    ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.font='10px ui-monospace,"SF Mono",Menlo,Consolas,monospace';
    nodes.forEach(function(n){
      var isRoot=n.parent<0;
      ctx.beginPath(); ctx.arc(n.cx,n.cy,r,0,Math.PI*2);
      ctx.fillStyle=C.card; ctx.fill();
      ctx.lineWidth=isRoot?2.4:2; ctx.strokeStyle=isRoot?C.acc2:C.acc; ctx.stroke();
      if(r>=5&&this.h>=90){ ctx.fillStyle=C.mut; ctx.fillText(String(n.pid),n.cx,n.cy+r+8); }
    }, this);
  };

  Instance.prototype.destroy = function(){
    if (this.raf){ cancelAnimationFrame(this.raf); this.raf=0; }
    if (this.ro){ try{ this.ro.disconnect(); }catch(e){} }
    if (this.io){ try{ this.io.disconnect(); }catch(e){} }
    document.removeEventListener('visibilitychange', this._onVis);
    if (inst === this) inst = null;
  };

  window.HERO = {
    mount: function(container){
      if (!container) return;
      if (inst) inst.destroy();
      inst = new Instance(container);
    },
    destroy: function(){ if (inst) inst.destroy(); }
  };
})();
