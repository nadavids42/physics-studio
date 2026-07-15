"""Reusable browser-side player for precomputed simulation trajectories.

Each simulation supplies a JSON payload and a small scene adapter. This module
owns playback state, interpolation, controls, events, trails, particles,
responsive/high-DPI canvas setup, accessibility, and deterministic randomness.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

PLAYER_CSS = r"""
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: transparent; color: #263238;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.animation-shell { width: 100%; max-width: 900px; margin: 0 auto; }
.canvas-wrap { position: relative; width: 100%; aspect-ratio: var(--aspect-ratio);
  min-height: 180px; overflow: hidden; border-radius: 18px; }
canvas { display: block; width: 100%; max-width: 100%; height: 100%; }
.hint { position: absolute; left: 50%; top: 12px; transform: translateX(-50%);
  color: #6b7280; font-size: 13px; font-weight: 600; pointer-events: none; }
.message { position: absolute; left: 50%; bottom: 12px; transform: translate(-50%, 6px);
  max-width: 88%; padding: 9px 16px; border-radius: 14px; background: white;
  color: #263238; box-shadow: 0 4px 14px rgba(0,0,0,.18); text-align: center;
  font-size: 14px; font-weight: 650; opacity: 0; transition: .25s ease; pointer-events: none; }
.message.show { opacity: 1; transform: translate(-50%, 0); }
.controls { display: grid; grid-template-columns: auto auto minmax(100px,1fr) auto;
  gap: 8px; align-items: center; padding: 8px 2px 0; }
.controls button, .controls select { min-height: 34px; border: 1px solid #cbd5e1;
  border-radius: 9px; background: white; color: #263238; font-weight: 650; cursor: pointer; }
.controls button { min-width: 42px; padding: 5px 10px; }
.controls button:focus-visible, .controls select:focus-visible, .controls input:focus-visible {
  outline: 3px solid #42A5F5; outline-offset: 2px; }
.controls input[type=range] { width: 100%; accent-color: #1976D2; }
.speed-label { display: flex; align-items: center; gap: 5px; font-size: 12px; white-space: nowrap; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
@media (max-width: 480px) {
  .controls { grid-template-columns: auto auto 1fr; }
  .speed-label { grid-column: 1 / -1; justify-content: flex-end; }
  .controls button { min-width: 38px; padding-inline: 7px; }
}
@media (prefers-reduced-motion: reduce) {
  .message { transition: none; }
}
body.high-contrast .canvas-wrap { outline: 3px solid #fff; background:#000; }
body.high-contrast .controls button, body.high-contrast .controls select { background:#000; color:#fff; border:2px solid #fff; }
body.high-contrast .controls input[type=range] { accent-color:#FFD600; }
"""

PLAYER_JS = r"""
function clamp(value, minimum, maximum) { return Math.min(maximum, Math.max(minimum, value)); }
function lerp(a, b, amount) { return a + (b - a) * amount; }
function sample(values, fraction) {
  if (!values.length) return 0;
  const index = clamp(fraction, 0, 1) * (values.length - 1);
  const lower = Math.floor(index), upper = Math.min(values.length - 1, lower + 1);
  return lerp(values[lower], values[upper], index - lower);
}
function seededRandom(seed) {
  let state = (seed >>> 0) || 1;
  return function() {
    state += 0x6D2B79F5;
    let value = state;
    value = Math.imul(value ^ value >>> 15, value | 1);
    value ^= value + Math.imul(value ^ value >>> 7, value | 61);
    return ((value ^ value >>> 14) >>> 0) / 4294967296;
  };
}
class ParticleSystem {
  constructor(random, reducedMotion) { this.items = []; this.random = random; this.reducedMotion = reducedMotion; }
  burst(x, y, count, colors) {
    if (this.reducedMotion) return;
    for (let index = 0; index < count; index++) {
      const angle = this.random() * Math.PI * 2, speed = 90 + this.random() * 210;
      this.items.push({x, y, vx: Math.cos(angle)*speed, vy: Math.sin(angle)*speed-80,
        life: 1, size: 2+this.random()*3, color: colors[Math.floor(this.random()*colors.length)]});
    }
  }
  reset() { this.items = []; }
  update(seconds) {
    for (const item of this.items) { item.x += item.vx*seconds; item.y += item.vy*seconds;
      item.vy += 320*seconds; item.life -= 1.6*seconds; }
    this.items = this.items.filter(item => item.life > 0);
  }
  draw(ctx) { for (const item of this.items) { ctx.globalAlpha = Math.max(0,item.life);
      ctx.fillStyle=item.color; ctx.beginPath(); ctx.arc(item.x,item.y,item.size,0,Math.PI*2); ctx.fill(); }
    ctx.globalAlpha=1; }
}
class TrailStore {
  constructor(limit=18) { this.limit=limit; this.items=new Map(); }
  reset() { this.items.clear(); }
  push(id, point) { const points=this.items.get(id)||[]; points.push(point);
    while(points.length>this.limit) points.shift(); this.items.set(id,points); }
  get(id) { return this.items.get(id)||[]; }
}
class AnimationPlayer {
  constructor(config, scene) {
    this.config=config; this.scene=scene; this.canvas=document.getElementById('animation-canvas');
    this.ctx=this.canvas.getContext('2d'); this.wrap=document.getElementById('canvas-wrap');
    this.playButton=document.getElementById('play-pause'); this.replayButton=document.getElementById('replay');
    this.scrubber=document.getElementById('scrubber'); this.speed=document.getElementById('speed');
    this.message=document.getElementById('message'); this.hint=document.getElementById('hint');
    this.status=document.getElementById('status'); this.reducedMotion=Boolean(config.reducedMotion)||matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.body.classList.toggle('high-contrast',Boolean(config.highContrast));
    this.random=seededRandom(config.seed); this.particles=new ParticleSystem(this.random,this.reducedMotion);
    this.trails=new TrailStore(config.trailLength||18); this.fraction=0; this.state='idle'; this.playbackRate=1;
    this.lastTimestamp=null; this.fired=new Set(); this.frameRequest=null; this.cssWidth=1; this.cssHeight=1;
    this.bind(); this.resize(); this.render(0);
    if(config.autoplay && !this.reducedMotion) this.play();
    else if(config.autoplay && this.reducedMotion) {
      this.status.textContent='Reduced motion is enabled. Press Play to start the animation.';
    }
  }
  bind() {
    this.playButton.addEventListener('click',()=>this.toggle());
    this.replayButton.addEventListener('click',()=>this.replay());
    this.scrubber.addEventListener('input',event=>this.seek(Number(event.target.value)/1000));
    this.speed.addEventListener('change',event=>{this.playbackRate=Number(event.target.value);});
    new ResizeObserver(()=>this.resize()).observe(this.wrap);
    document.addEventListener('visibilitychange',()=>{if(document.hidden&&this.state==='playing') this.pause();});
    document.addEventListener('keydown',event=>{
      if(['INPUT','SELECT','BUTTON'].includes(document.activeElement.tagName)&&event.key!==' ') return;
      if(event.key===' '){event.preventDefault();this.toggle();}
      else if(event.key==='r'||event.key==='R') this.replay();
      else if(event.key==='ArrowRight') this.seek(this.fraction+.02);
      else if(event.key==='ArrowLeft') this.seek(this.fraction-.02);
    });
  }
  resize() {
    const box=this.wrap.getBoundingClientRect(), dpr=Math.max(1,window.devicePixelRatio||1);
    this.cssWidth=Math.max(1,box.width); this.cssHeight=Math.max(1,box.height);
    this.canvas.width=Math.round(this.cssWidth*dpr); this.canvas.height=Math.round(this.cssHeight*dpr);
    this.ctx.setTransform(dpr,0,0,dpr,0,0); this.render(this.fraction);
  }
  coordinates() { const view=this.config.view||{}; const xmin=view.minimum??0, xmax=view.maximum??1;
    const left=40,right=this.cssWidth-40; return {x:value=>left+(value-xmin)/Math.max(.0001,xmax-xmin)*(right-left),
      y:value=>this.cssHeight-60-value, width:this.cssWidth,height:this.cssHeight}; }
  snapshot(fraction) { const tracks={}; for(const track of this.config.tracks) tracks[track.id]={
      id:track.id,label:track.label,style:track.style||{},x:sample(track.x,fraction),
      y:track.y?sample(track.y,fraction):null,trail:this.trails.get(track.id)}; return tracks; }
  play() { if(this.state==='done') this.replay(); this.state='playing'; this.lastTimestamp=null;
    this.playButton.textContent='⏸'; this.playButton.setAttribute('aria-label','Pause animation');
    this.hint.hidden=true; this.status.textContent='Animation playing'; this.ensureFrame(); }
  pause() { this.state='paused'; this.playButton.textContent='▶'; this.playButton.setAttribute('aria-label','Play animation');
    this.status.textContent='Animation paused'; }
  toggle() { this.state==='playing'?this.pause():this.play(); }
  replay() { this.fraction=0; this.fired.clear(); this.trails.reset(); this.particles.reset();
    this.message.classList.remove('show'); this.scrubber.value='0'; this.state='paused'; this.play(); }
  seek(fraction) { this.fraction=clamp(fraction,0,1); this.scrubber.value=String(Math.round(this.fraction*1000));
    this.fired.clear(); for(const event of this.config.events||[]) if(event.fraction<=this.fraction) this.fired.add(event.id);
    this.trails.reset(); this.particles.reset(); if(this.fraction<1) this.message.classList.remove('show');
    this.render(this.fraction); this.status.textContent=`Animation at ${Math.round(this.fraction*100)} percent`; }
  ensureFrame() { if(this.frameRequest===null) this.frameRequest=requestAnimationFrame(timestamp=>this.tick(timestamp)); }
  tick(timestamp) { this.frameRequest=null; const elapsed=this.lastTimestamp===null?0:(timestamp-this.lastTimestamp)/1000;
    this.lastTimestamp=timestamp; if(this.state==='playing') { const duration=this.config.durationMs/1000;
      this.fraction=clamp(this.fraction+elapsed*this.playbackRate/duration,0,1); this.fireEvents();
      this.scrubber.value=String(Math.round(this.fraction*1000)); if(this.fraction>=1) this.complete(); }
    this.particles.update(Math.min(elapsed,.05)); this.render(this.fraction);
    if(this.state==='playing'||this.particles.items.length) this.ensureFrame(); }
  fireEvents() { for(const event of this.config.events||[]) if(this.fraction>=event.fraction&&!this.fired.has(event.id)) {
      this.fired.add(event.id); if(this.scene.onEvent) this.scene.onEvent(event,this); } }
  complete() { this.state='done'; this.playButton.textContent='▶'; this.playButton.setAttribute('aria-label','Replay animation');
    this.message.textContent=this.config.completionMessage||''; this.message.classList.toggle('show',!!this.config.completionMessage);
    this.status.textContent=this.config.completionMessage||'Animation complete'; }
  render(fraction) { if(!this.scene||!this.ctx) return; const transform=this.coordinates(), tracks=this.snapshot(fraction);
    for(const track of Object.values(tracks)) this.trails.push(track.id,{x:track.x,y:track.y});
    this.scene.draw(this.ctx,{fraction,state:this.state,tracks,transform,particles:this.particles,
      trails:this.trails,reducedMotion:this.reducedMotion,config:this.config}); this.particles.draw(this.ctx); }
}
"""


def build_player_document(
    *,
    config: dict[str, Any],
    scene_javascript: str,
    logical_width: int,
    logical_height: int,
    accessible_label: str,
    idle_hint: str,
    extra_css: str = "",
) -> str:
    """Build a standalone responsive player document for Streamlit embedding."""

    try:
        from physics_playground.presentation.accessibility import get_accessibility_settings
        settings=get_accessibility_settings()
        config={**config,"reducedMotion":settings.reduced_motion,"highContrast":settings.high_contrast}
    except Exception:
        config={**config,"reducedMotion":False,"highContrast":False}
    payload = json.dumps(config, allow_nan=False, separators=(",", ":"))
    aspect_ratio = logical_width / logical_height
    return _cached_player_document(payload,scene_javascript,aspect_ratio,accessible_label,idle_hint,extra_css)


@lru_cache(maxsize=128)
def _cached_player_document(payload:str,scene_javascript:str,aspect_ratio:float,accessible_label:str,idle_hint:str,extra_css:str)->str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>:root{{--aspect-ratio:{aspect_ratio};}}{PLAYER_CSS}{extra_css}</style></head>
<body><div class="animation-shell" role="group" aria-label={json.dumps(accessible_label)}>
  <div class="canvas-wrap" id="canvas-wrap"><canvas id="animation-canvas" role="img" aria-label={json.dumps(accessible_label)}></canvas>
    <div class="hint" id="hint">{idle_hint}</div><div class="message" id="message" aria-live="polite"></div></div>
  <div class="controls" aria-label="Animation controls">
    <button id="play-pause" type="button" aria-label="Play animation" title="Play or pause (Space)">▶</button>
    <button id="replay" type="button" aria-label="Replay animation" title="Replay (R)">↺</button>
    <label class="sr-only" for="scrubber">Animation position</label><input id="scrubber" type="range" min="0" max="1000" value="0">
    <label class="speed-label" for="speed">Speed <select id="speed"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="1.5">1.5×</option><option value="2">2×</option></select></label>
  </div><div id="status" class="sr-only" aria-live="polite">Animation ready</div></div>
<script>{PLAYER_JS}\nconst playerConfig={payload};\n{scene_javascript}\nwindow.animationPlayer=new AnimationPlayer(playerConfig,scene);</script>
</body></html>"""


def player_document_cache_info():
    return _cached_player_document.cache_info()
