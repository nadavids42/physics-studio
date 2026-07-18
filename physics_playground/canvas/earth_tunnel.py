"""Shared-asset Earth Tunnel animation adapters."""

from __future__ import annotations

from physics_playground.canvas.player import build_player_document
from physics_playground.serialization import to_jsonable

CANVAS_W, CANVAS_H, PLAYER_HEIGHT = 640, 390, 470

SCENE = r"""
const scene={draw(ctx,f){
  const t=f.transform,W=t.width,H=t.height,c=f.config.earthTunnel||{},cx=W/2,cy=H/2,R=Math.min(W,H)*.34,X=km=>cx+(km/f.config.radiusKm)*R;
  PhysicsExperience.context(ctx,f,'space');PhysicsAssets.planet(ctx,f,{x:cx,y:cy,radius:R,label:'idealized spherical planet',shadow:false});
  PhysicsAnnotations.pathGuide(ctx,f,{points:[{x:cx-R,y:cy},{x:cx+R,y:cy}],dashes:[8,7],opacity:.75});
  PhysicsAnnotations.centerOfMass(ctx,f,{x:cx,y:cy,label:'center',radius:9});
  PhysicsAnnotations.dimensionLine(ctx,f,{x:cx,y:cy-R-18,end:{x:cx+R,y:cy-R-18},label:`planet radius ${f.config.radiusKm.toFixed(0)} km`});
  for(const [index,track] of Object.values(f.tracks).entries()){
    const meta=c.travelers[index]||{},x=X(track.x),acceleration=track.y||0,turn=X(meta.turningPointKm||0),trail=f.trails.get(track.id)||[],dashed=index%2===1;
    PhysicsAnnotations.pathGuide(ctx,f,{points:[{x:turn,y:cy-23},{x:turn,y:cy+23},{x:X(-(meta.turningPointKm||0)),y:cy+23},{x:X(-(meta.turningPointKm||0)),y:cy-23}],dashes:dashed?[4,4]:[1,0],opacity:.55});
    PhysicsAnnotations.velocityTrail(ctx,f,{points:trail.map(q=>({x:X(q.x),y:cy})),direction:false,opacity:index?.18:.28,line_width:index?3:5,dashed});
    PhysicsAssets.mass(ctx,f,{x,y:cy,radius:index?11:14,label:`${meta.label} — ${dashed?'dashed':'solid'}`,fill:PhysicsVisuals.token(f,'colors',meta.role,'#1769AA'),outline:PhysicsVisuals.token(f,'colors','text','#152536'),selected:index>0});
    PhysicsAnnotations.dimensionLine(ctx,f,{x:cx,y:cy+36+index*18,end:{x,y:cy+36+index*18},label:`r = ${track.x.toFixed(0)} km`});
    if(Math.abs(acceleration)>1e-8)PhysicsAnnotations.vector(ctx,f,{x,y:cy-8,dx:acceleration,dy:0,role:'acceleration',label:`a ${acceleration.toFixed(2)} m/s²`,scale_mode:'normalized',fixed_length_px:46,scale_disclosure:'Acceleration direction is physical; length is normalized'},f.progress,index===0);
  }
  ctx.save();PhysicsVisuals.applyText(ctx,f,'annotation');ctx.fillStyle=PhysicsVisuals.token(f,'colors','text','#152536');ctx.fillText(c.modelSummary||'',18,28);ctx.restore();
}};
"""


def _acceleration_samples(result) -> list[float]:
    plot = next(item for item in result.plots if item.id == "acceleration_position")
    return list(plot.series[0].y)


def _doc(items, seed, autoplay, message):
    tracks = []
    travelers = []
    roles = ("trajectory", "energy", "selected")
    for i, (label, result, _color) in enumerate(items):
        track = to_jsonable(result.animation.tracks[0])
        track["id"] = f"traveler_{i}"
        track["label"] = label
        track["y"] = _acceleration_samples(result)
        track["style"] = {"role": roles[i % len(roles)]}
        tracks.append(track)
        travelers.append(
            {
                "label": f"{label}: {result.parameters.model.value}",
                "model": result.parameters.model.value,
                "turningPointKm": result.parameters.radius_m
                * result.parameters.start_fraction
                / 1000,
                "role": roles[i % len(roles)],
            }
        )
    radius = max(result.parameters.radius_m / 1000 for _, result, _ in items)
    models = list(dict.fromkeys(result.parameters.model.value for _, result, _ in items))
    config = {
        "durationMs": 4500,
        "autoplay": autoplay,
        "seed": seed,
        "trailLength": 36,
        "frameCount": max(len(track["x"]) for track in tracks),
        "view": {"minimum": -radius, "maximum": radius},
        "radiusKm": radius,
        "earthTunnel": {"travelers": travelers, "modelSummary": " vs. ".join(models)},
        "tracks": tracks,
        "events": [],
        "completionMessage": message,
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Travelers on synchronized recorded timelines inside a labeled tunnel, distinguished by labels, solid or dashed trails, and outlines.",
        idle_hint="Use Play or press JUMP IN!",
    )


def build_tunnel_canvas(r, *, seed, autoplay):
    return _doc([("Traveler", r, "")], seed, autoplay, "Reached the opposite turning point")


def build_tunnel_comparison_canvas(items, *, seed, autoplay):
    return _doc(
        [(label, result, color) for label, result, color in items],
        seed,
        autoplay,
        "Comparison complete",
    )
