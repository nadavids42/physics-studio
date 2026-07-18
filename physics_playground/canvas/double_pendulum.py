"""Shared-asset Double Pendulum animation adapter."""
from __future__ import annotations

from physics_playground.canvas.player import build_player_document
from physics_playground.serialization import to_jsonable

CANVAS_W, CANVAS_H, PLAYER_HEIGHT = 560, 500, 590

SCENE = r"""
const scene={draw(ctx,f){
  const t=f.transform,W=t.width,H=t.height,c=f.config.doublePendulum||{},pivot={x:W/2,y:54},scale=Math.min(W,H)*.38/f.config.limit;
  PhysicsExperience.context(ctx,f,'laboratory');
  PhysicsAssets.pivot(ctx,f,{x:pivot.x,y:pivot.y-4,width:34,height:26,label:'fixed pivot'});
  for(const [index,prefix] of f.config.systems.entries()){
    const joint=f.tracks[prefix+'_joint'],bob=f.tracks[prefix+'_bob'],meta=c.systems[index],jx=pivot.x+joint.x*scale,jy=pivot.y-joint.y*scale,bx=pivot.x+bob.x*scale,by=pivot.y-bob.y*scale,dashed=meta.lineStyle==='dashed';
    PhysicsAssets.rod(ctx,f,{x:pivot.x,y:pivot.y,end:{x:jx-pivot.x,y:jy-pivot.y},lineWidth:index?4:6,dashed,opacity:index?.82:1,fill:PhysicsVisuals.token(f,'colors',meta.role,'#1769AA')});
    PhysicsAssets.pivot(ctx,f,{x:jx,y:jy,width:22,height:18,label:'',fill:PhysicsVisuals.token(f,'colors',meta.role,'#1769AA')});
    PhysicsAssets.rod(ctx,f,{x:jx,y:jy,end:{x:bx-jx,y:by-jy},lineWidth:index?4:6,dashed,opacity:index?.82:1,fill:PhysicsVisuals.token(f,'colors',meta.role,'#1769AA')});
    const trail=f.trails.get(prefix+'_bob')||[];PhysicsAnnotations.velocityTrail(ctx,f,{points:trail.map(q=>({x:pivot.x+q.x*scale,y:pivot.y-(q.y||0)*scale})),direction:false,opacity:index?.2:.3,line_width:index?2:3,dashed});
    PhysicsAssets.pendulumBob(ctx,f,{x:jx,y:jy,radius:9,label:'',fill:PhysicsVisuals.token(f,'colors',meta.role,'#1769AA'),outline:PhysicsVisuals.token(f,'colors','text','#152536')});
    PhysicsAssets.pendulumBob(ctx,f,{x:bx,y:by,radius:14,label:meta.label,fill:PhysicsVisuals.token(f,'colors',meta.role,'#1769AA'),outline:PhysicsVisuals.token(f,'colors','text','#152536'),selected:index===1});
  }
  const a=f.tracks.a_bob,b=f.tracks.b_bob,separation=Math.hypot(a.x-b.x,(a.y||0)-(b.y||0)),mx=pivot.x+(a.x+b.x)*scale/2,my=pivot.y-(a.y+b.y)*scale/2;
  if(c.showSeparation)PhysicsAssets.callout(ctx,f,{x:Math.min(W-210,Math.max(16,mx+16)),y:Math.min(H-76,Math.max(18,my-70)),width:192,height:54,text:`Recorded separation\n${separation.toFixed(3)} m`,target:{x:mx,y:my}});
  if(c.inspectSystem){const chosen=f.tracks[c.inspectSystem+'_bob'],focusOpacity=f.reducedMotion?1:Math.min(1,.35+f.fraction*2);ctx.save();ctx.globalAlpha=focusOpacity;PhysicsAssets.callout(ctx,f,{x:16,y:H-76,width:185,height:50,text:`Inspecting ${c.inspectSystem==='a'?'baseline':'perturbed'}\nFixed camera`,target:{x:pivot.x+chosen.x*scale,y:pivot.y-(chosen.y||0)*scale}});ctx.restore();}
}};
"""


def build_double_canvas(r, *, seed, autoplay, show_separation: bool = True,
                        inspect_system: str | None = None):
    """Render synchronized recorded tracks with a fixed camera by default."""
    if inspect_system not in (None, "a", "b"):
        raise ValueError("inspect_system must be 'a', 'b', or None")
    tracks = [to_jsonable(track) for track in r.animation.tracks]
    limit = r.parameters.length_1_m + r.parameters.length_2_m
    config = {"durationMs": 6000, "autoplay": autoplay, "seed": seed, "trailLength": 72,
              "view": {"minimum": -limit, "maximum": limit}, "limit": limit,
              "systems": ["a", "b"], "tracks": tracks, "events": [],
              "camera": {"x": 0, "y": 0, "zoom": 1},
              "doublePendulum": {"showSeparation": show_separation,
                  "inspectSystem": inspect_system,
                  "systems": [{"label": "Baseline A (solid)", "role": "accent", "lineStyle": "solid"},
                              {"label": "Perturbed B (dashed)", "role": "energy", "lineStyle": "dashed"}]},
              "completionMessage": "Chaos comparison complete"}
    return build_player_document(config=config, scene_javascript=SCENE, logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Baseline A with solid rods and perturbed B with dashed rods, evolving on one synchronized fixed-camera timeline.",
        idle_hint="Use Play or press RELEASE!")
