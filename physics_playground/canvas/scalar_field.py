"""Reusable scientific graph-plane adapter for precomputed scalar fields."""

from __future__ import annotations

from physics_playground.canvas.player import build_player_document

SCENE = r"""
const scene={draw(ctx,s){
  const w=s.transform.width,h=s.transform.height,c=s.config,frames=c.fieldFrames||[],xs=c.fieldX||[],pad={l:58,r:28,t:46,b:52},left=pad.l,right=w-pad.r,top=pad.t,bottom=h-pad.b,mid=(top+bottom)/2,limit=Math.max(.001,c.fieldLimit||1),X=x=>left+(x-(xs[0]||0))/Math.max(.001,(xs.at(-1)||1)-(xs[0]||0))*(right-left),Y=y=>mid-y/limit*(bottom-top)/2;
  PhysicsExperience.context(ctx,s,'laboratory');PhysicsAssets.grid(ctx,s,{x:left,y:top,width:right-left,height:bottom-top,step:Math.max(28,(right-left)/10),opacity:.22});
  ctx.save();ctx.strokeStyle=PhysicsVisuals.token(s,'colors','text','#152536');ctx.fillStyle=PhysicsVisuals.token(s,'colors','text_muted','#526577');ctx.lineWidth=1.5;PhysicsVisuals.applyText(ctx,s,'axis');ctx.beginPath();ctx.moveTo(left,mid);ctx.lineTo(right,mid);ctx.moveTo(left,top);ctx.lineTo(left,bottom);ctx.stroke();
  const xMax=xs.at(-1)||1;for(let i=0;i<=5;i++){const x=left+i/5*(right-left),value=i/5*xMax;ctx.beginPath();ctx.moveTo(x,mid-4);ctx.lineTo(x,mid+4);ctx.stroke();ctx.fillText(`${value.toFixed(1)} m`,x-14,bottom+24)}for(const sign of [-1,0,1]){const y=Y(sign*limit);ctx.beginPath();ctx.moveTo(left-4,y);ctx.lineTo(left+4,y);ctx.stroke();ctx.fillText((sign*limit).toFixed(1),8,y+4)}ctx.fillText('displacement',8,top-12);ctx.fillText('equilibrium',right-76,mid-7);ctx.restore();
  if(!frames.length)return;const fi=Math.min(frames.length-1,Math.round(s.fraction*(frames.length-1))),roles=['accent','energy','displacement','electric_field'],styles=[[],[8,5],[2,4],[11,4,2,4]];
  for(let source=0;source<(c.sourceFrames||[]).length;source++){const ys=c.sourceFrames[source][fi],color=PhysicsVisuals.token(s,'colors',roles[source%roles.length],'#1769AA');ctx.save();ctx.strokeStyle=color;ctx.lineWidth=1.8;ctx.globalAlpha=.72;ctx.setLineDash(styles[source%styles.length]);ctx.beginPath();ys.forEach((y,i)=>i?ctx.lineTo(X(xs[i]),Y(y)):ctx.moveTo(X(xs[i]),Y(y)));ctx.stroke();ctx.restore();}
  const ys=frames[fi];ctx.save();ctx.strokeStyle=PhysicsVisuals.token(s,'colors','text','#152536');ctx.lineWidth=4;ctx.beginPath();ys.forEach((y,i)=>i?ctx.lineTo(X(xs[i]),Y(y)):ctx.moveTo(X(xs[i]),Y(y)));ctx.stroke();ctx.restore();
  for(const marker of c.measurements||[]){const i=Math.max(0,Math.min(xs.length-1,marker.index));ctx.save();ctx.strokeStyle=PhysicsVisuals.token(s,'colors','selected','#7C3AED');ctx.setLineDash([4,4]);ctx.beginPath();ctx.moveTo(X(xs[i]),top);ctx.lineTo(X(xs[i]),bottom);ctx.stroke();ctx.restore();}
  const sources=c.sources||[];sources.forEach((source,i)=>{ctx.save();PhysicsVisuals.applyText(ctx,s,'annotation');ctx.fillStyle=PhysicsVisuals.token(s,'colors',roles[i%roles.length],'#1769AA');ctx.fillText(`Source ${i+1} (${styles[i%styles.length].length?'dashed':'solid'}): φ=${source.phaseDeg.toFixed(0)}°`,left+i%2*210,20+Math.floor(i/2)*18);ctx.restore()});
  PhysicsAssets.callout(ctx,s,{x:right-226,y:top+10,width:210,height:55,text:c.interferenceLabel||'Interference\nvaries across the field'});ctx.save();PhysicsVisuals.applyText(ctx,s,'annotation');ctx.fillStyle=PhysicsVisuals.token(s,'colors','text','#152536');ctx.fillText(`Resultant (heavy) · t=${c.fieldTimes[fi].toFixed(2)} s`,right-230,bottom+42);ctx.restore();
}};
"""


def build_scalar_field_document(
    *,
    x: tuple[float, ...],
    frames: tuple[tuple[float, ...], ...],
    duration_s: float,
    accessible_label: str,
    completion_message: str,
    seed: int,
    autoplay: bool = False,
    source_frames: tuple[tuple[tuple[float, ...], ...], ...] = (),
    sources: tuple[dict, ...] = (),
    measurements: tuple[dict, ...] = (),
    time_s: tuple[float, ...] = (),
    interference_label: str = "",
) -> str:
    """Build a fixed-scale graph whose curves are the supplied recorded samples."""
    theoretical_limit = sum(abs(float(source.get("amplitude", 0))) for source in sources)
    recorded_limit = max((abs(value) for frame in frames for value in frame), default=1.0)
    limit = max(1e-6, theoretical_limit, recorded_limit)
    times = time_s or tuple(duration_s * i / max(1, len(frames) - 1) for i in range(len(frames)))
    config = {
        "durationMs": max(1000, int(duration_s * 2500)),
        "fieldDurationS": duration_s,
        "autoplay": autoplay,
        "seed": seed,
        "frameCount": len(frames),
        "tracks": [{"id": "field-clock", "label": "Wave field", "x": [0, 1]}],
        "events": [],
        "completionMessage": completion_message,
        "fieldX": x,
        "fieldFrames": frames,
        "sourceFrames": source_frames,
        "sources": sources,
        "measurements": measurements,
        "fieldTimes": times,
        "interferenceLabel": interference_label,
        "fieldLimit": limit,
        "view": {"minimum": 0, "maximum": 1},
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=820,
        logical_height=390,
        accessible_label=accessible_label,
        idle_hint="Press Play or use frame-step controls to inspect the field",
    )
