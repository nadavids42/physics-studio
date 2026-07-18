"""Bounded shared-player renderer for seeded diffusion trajectories."""

from __future__ import annotations

from physics_playground.canvas.player import build_player_document

VISIBLE_WINDOW_SEGMENTS = 48

SCENE = r"""
const scene={draw(ctx,s){
  const w=s.transform.width,h=s.transform.height,c=s.config.diffusion||{},paths=c.paths||[],pad=54,scale=Math.min((w-2*pad)/(2*c.extent),(h-2*pad)/(2*c.extent)),cx=w/2,cy=h/2,roles=['accent','energy','displacement','electric_field','selected'],dashes=[[],[7,4],[2,4],[10,4,2,4],[1,3]];
  PhysicsExperience.context(ctx,s,'laboratory');
  if(c.dimensions===2)PhysicsAssets.grid(ctx,s,{x:pad,y:pad,width:w-2*pad,height:h-2*pad,step:Math.max(30,scale*c.gridStepM),opacity:.25});
  ctx.save();ctx.strokeStyle=PhysicsVisuals.token(s,'colors','text','#152536');ctx.fillStyle=PhysicsVisuals.token(s,'colors','text_muted','#526577');ctx.lineWidth=1.5;PhysicsVisuals.applyText(ctx,s,'axis');ctx.beginPath();ctx.moveTo(pad,cy);ctx.lineTo(w-pad,cy);if(c.dimensions===2){ctx.moveTo(cx,pad);ctx.lineTo(cx,h-pad)}ctx.stroke();ctx.fillText('x position (m)',w-pad-76,cy+22);if(c.dimensions===2)ctx.fillText('y position (m)',cx+8,pad+14);ctx.restore();
  const rms=Math.max(0,c.rmsDistanceM||0);ctx.save();ctx.strokeStyle=PhysicsVisuals.token(s,'colors','uncertainty','#6B7280');ctx.setLineDash([7,6]);ctx.lineWidth=2;if(c.dimensions===2){ctx.beginPath();ctx.arc(cx,cy,rms*scale,0,Math.PI*2);ctx.stroke()}else{for(const sign of [-1,1]){ctx.beginPath();ctx.moveTo(cx+sign*rms*scale,cy-42);ctx.lineTo(cx+sign*rms*scale,cy+42);ctx.stroke()}}PhysicsVisuals.applyText(ctx,s,'annotation');ctx.fillStyle=PhysicsVisuals.token(s,'colors','text_muted','#526577');ctx.fillText(`statistical RMS distance ${rms.toFixed(2)} m`,pad,30);ctx.restore();
  for(let j=0;j<paths.length;j++){const path=paths[j],last=Math.max(0,Math.min(path.length-1,Math.floor((path.length-1)*s.fraction))),start=Math.max(0,last-c.visibleWindowSegments),role=roles[j%roles.length],color=PhysicsVisuals.token(s,'colors',role,'#1769AA');ctx.save();ctx.strokeStyle=color;ctx.lineWidth=j%2?1.8:2.6;ctx.setLineDash(dashes[j%dashes.length]);for(let i=start+1;i<=last;i++){const a=path[i-1],b=path[i],progress=(i-start)/Math.max(1,last-start);ctx.globalAlpha=.12+.68*progress;ctx.beginPath();ctx.moveTo(cx+a[0]*scale,cy-(c.dimensions===2?a[1]:0)*scale);ctx.lineTo(cx+b[0]*scale,cy-(c.dimensions===2?b[1]:0)*scale);ctx.stroke()}ctx.restore();
    const origin=path[0],current=path[last],ox=cx+origin[0]*scale,oy=cy-(c.dimensions===2?origin[1]:0)*scale,x=cx+current[0]*scale,y=cy-(c.dimensions===2?current[1]:0)*scale;ctx.save();ctx.strokeStyle=color;ctx.fillStyle=PhysicsVisuals.token(s,'colors','surface','#FFF');ctx.lineWidth=2;ctx.beginPath();ctx.rect(ox-3,oy-3,6,6);ctx.fill();ctx.stroke();ctx.restore();PhysicsAssets.mass(ctx,s,{x,y,radius:j%2?5:7,label:`T${j+1} ${dashes[j%dashes.length].length?'dashed':'solid'}`,fill:color,outline:PhysicsVisuals.token(s,'colors','text','#152536'),shadow:false});}
  PhysicsAssets.callout(ctx,s,{x:w-230,y:18,width:210,height:54,text:`${c.dimensions}D sample trajectories\nDistribution uses ${c.sampledParticleCount} particles`});
}};
"""


def build_diffusion_document(
    *,
    paths,
    dimensions: int,
    extent: float,
    message: str,
    seed: int,
    rms_distance_m: float = 0,
    sampled_particle_count: int | None = None,
) -> str:
    if dimensions not in (1, 2):
        raise ValueError("dimensions must be 1 or 2")
    immutable_paths = tuple(tuple(tuple(point) for point in path) for path in paths)
    extent = max(float(extent), 1e-9)
    config = {
        "durationMs": 2400,
        "autoplay": False,
        "seed": seed,
        "frameCount": max((len(path) for path in immutable_paths), default=2),
        "tracks": [{"id": "walks", "label": "Particle trajectories", "x": [0, 1]}],
        "events": [],
        "completionMessage": message,
        "diffusion": {
            "paths": immutable_paths,
            "dimensions": dimensions,
            "extent": extent,
            "rmsDistanceM": max(0, float(rms_distance_m)),
            "sampledParticleCount": sampled_particle_count or len(immutable_paths),
            "visibleWindowSegments": VISIBLE_WINDOW_SEGMENTS,
            "gridStepM": max(extent / 5, 1e-9),
        },
        "view": {"minimum": -extent, "maximum": extent},
    }
    label = (
        "1-dimensional random-walk trajectories constrained to the labeled horizontal axis. "
        if dimensions == 1
        else "2-dimensional random-walk trajectories on a labeled coordinate grid. "
    )
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=760,
        logical_height=500,
        accessible_label=label
        + "Trajectories use numbered solid and dashed identities; the RMS guide describes the statistical distribution. "
        + message,
        idle_hint="Press Play or use frame-step controls to inspect the seeded walks",
    )
