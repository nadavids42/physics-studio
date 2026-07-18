"""Boing Machine adapters for the shared animation player."""

from __future__ import annotations

from physics_playground.canvas.player import build_player_document
from physics_playground.serialization import to_jsonable
from physics_playground.subjects.waves_and_oscillations.boing.physics import SpringResult

CANVAS_W, CANVAS_H, PLAYER_HEIGHT = 680, 300, 360

SCENE = r"""
const scene={draw(ctx,s){
  const t=s.transform,c=s.config.boing||{},tracks=Object.values(s.tracks),count=tracks.length;
  PhysicsExperience.context(ctx,s,'laboratory');
  const wall=48,span=Math.max(1,t.x(1)-t.x(0));
  tracks.forEach((track,index)=>{
    const meta=c.oscillators[index]||{},cy=(index+1)*t.height/(count+1),equilibrium=t.x(0),x=t.x(track.x),velocity=track.y||0,displacement=track.x||0;
    ctx.save();ctx.strokeStyle=PhysicsVisuals.token(s,'colors','text_muted','#526577');ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(wall,cy-54);ctx.lineTo(wall,cy+54);ctx.stroke();ctx.restore();
    PhysicsAnnotations.pathGuide(ctx,s,{points:[{x:equilibrium,y:cy-54},{x:equilibrium,y:cy+54}],dashes:[5,5],opacity:.7});
    const amplitude=Math.abs(meta.initialDisplacementM||0),left=t.x(-amplitude),right=t.x(amplitude);PhysicsAnnotations.pathGuide(ctx,s,{points:[{x:left,y:cy-38},{x:left,y:cy+38}],opacity:.3});PhysicsAnnotations.pathGuide(ctx,s,{points:[{x:right,y:cy-38},{x:right,y:cy+38}],opacity:.3});
    if((meta.dampingNsM||0)>0&&!meta.driven){const envelope=amplitude*Math.exp(-(meta.dampingNsM||0)*(meta.durationS||0)*s.fraction/(2*(meta.massKg||1))),elo=t.x(-envelope),ehi=t.x(envelope);PhysicsAnnotations.dimensionLine(ctx,s,{x:elo,y:cy-46,end:{x:ehi,y:cy-46},label:`damping envelope ±${envelope.toFixed(2)} m`});}
    PhysicsAssets.spring(ctx,s,{x:wall,y:cy,end:{x:x-wall-23,y:0},turns:14,amplitude:10,label:''});
    const trail=track.trail||[];PhysicsAnnotations.velocityTrail(ctx,s,{points:trail.map(q=>({x:t.x(q.x),y:cy})),direction:false,opacity:.16,line_width:5});
    PhysicsAssets.mass(ctx,s,{x,y:cy,radius:22,label:track.label,fill:PhysicsVisuals.token(s,'colors',meta.role||'displacement','#1769AA'),selected:count>1});
    const vectors=[];if(Math.abs(displacement)>1e-8)vectors.push({x:equilibrium,y:cy,dx:displacement,dy:0,role:'displacement',label:`x ${displacement.toFixed(2)} m`,scale_mode:'physical',pixels_per_unit:Math.abs(span),units:'m'});
    if(Math.abs(velocity)>1e-8)vectors.push({x,y:cy-8,dx:velocity,dy:0,role:'velocity',label:`v ${velocity.toFixed(2)} m/s`,scale_mode:'normalized',fixed_length_px:38});
    const restoring=-(meta.stiffnessNm||0)*displacement;if(Math.abs(restoring)>1e-8)vectors.push({x,y:cy+8,dx:restoring,dy:0,role:'net_force',label:`spring force ${restoring.toFixed(1)} N`,scale_mode:'normalized',fixed_length_px:46});PhysicsAnnotations.vectorSet(ctx,s,vectors,s.progress,{x:12,y:12+index*28});
    ctx.save();PhysicsVisuals.applyText(ctx,s,'annotation');ctx.fillStyle=PhysicsVisuals.token(s,'colors','text_muted','#526577');ctx.fillText('−A',left-9,cy+58);ctx.fillText('equilibrium',equilibrium-34,cy+58);ctx.fillText('+A',right-7,cy+58);ctx.restore();
  });
}};
"""


def _velocity_samples(result: SpringResult) -> list[float]:
    velocity_plot = next(plot for plot in result.plots if plot.id == "velocity_time")
    return list(velocity_plot.series[0].y)


def _document(
    results: list[tuple[str, SpringResult, str]], *, seed: int, autoplay: bool, message: str
) -> str:
    minimum = min(r.animation.view["minimum"] for _, r, _ in results)
    maximum = max(r.animation.view["maximum"] for _, r, _ in results)
    tracks = []
    oscillators = []
    roles = ("accent", "energy", "displacement")
    for i, (label, result, _color) in enumerate(results):
        track = to_jsonable(result.animation.tracks[0])
        track["id"] = f"mass_{i}"
        track["label"] = label
        track["y"] = _velocity_samples(result)
        track["style"] = {"role": roles[i % len(roles)]}
        tracks.append(track)
        p = result.parameters
        oscillators.append(
            {
                "initialDisplacementM": p.initial_displacement_m,
                "stiffnessNm": p.stiffness_n_m,
                "dampingNsM": p.damping_n_s_m,
                "massKg": p.mass_kg,
                "durationS": p.duration_s,
                "driven": p.drive_force_n > 0,
                "role": roles[i % len(roles)],
            }
        )
    config = {
        "durationMs": 4200,
        "autoplay": autoplay,
        "seed": seed,
        "trailLength": 12,
        "view": {"minimum": minimum, "maximum": maximum},
        "tracks": tracks,
        "boing": {"oscillators": oscillators},
        "events": [],
        "completionMessage": message,
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Masses oscillating horizontally on springs with equilibrium, amplitude, and vector annotations.",
        idle_hint="Use Play or press BOING!",
    )


def build_boing_canvas(result: SpringResult, *, seed: int, autoplay: bool) -> str:
    return _document(
        [("Spring mass", result, "")], seed=seed, autoplay=autoplay, message="Oscillation complete!"
    )


def build_boing_comparison_canvas(
    a: SpringResult, b: SpringResult, *, labels: tuple[str, str], seed: int, autoplay: bool
) -> str:
    return _document(
        [(labels[0], a, ""), (labels[1], b, "")],
        seed=seed,
        autoplay=autoplay,
        message="Comparison complete",
    )
