"""Bumper Cars scene adapter for the shared browser-side animation player."""

from physics_playground.canvas.player import build_player_document
from physics_playground.models.collision import CollisionResult
from physics_playground.serialization import to_jsonable

CANVAS_W, CANVAS_H = 680, 260
PLAYER_HEIGHT = 350

SCENE_JAVASCRIPT = r"""
function drawFace(ctx,cx,cy,r){const ex=r*.32,ey=-r*.05,er=r*.11;ctx.fillStyle='white';
  ctx.beginPath();ctx.arc(cx-ex,cy+ey,er,0,Math.PI*2);ctx.arc(cx+ex,cy+ey,er,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#1a1a1a';ctx.beginPath();ctx.arc(cx-ex,cy+ey,er*.55,0,Math.PI*2);
  ctx.arc(cx+ex,cy+ey,er*.55,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#1a1a1a';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.arc(cx,cy+r*.28,r*.28,.15*Math.PI,.85*Math.PI);ctx.stroke();}
function drawBackground(ctx,t){const W=t.width,H=t.height,ground=H-60;ctx.clearRect(0,0,W,H);
  const gradient=ctx.createLinearGradient(0,0,0,ground);gradient.addColorStop(0,'#FFF3E0');
  gradient.addColorStop(1,'#FFE0B2');ctx.fillStyle=gradient;ctx.fillRect(0,0,W,ground);
  ctx.fillStyle='#8D6E63';ctx.fillRect(0,ground,W,H-ground);ctx.strokeStyle='rgba(255,255,255,.6)';
  ctx.lineWidth=3;ctx.setLineDash([14,10]);ctx.beginPath();ctx.moveTo(0,ground+30);ctx.lineTo(W,ground+30);ctx.stroke();ctx.setLineDash([]);}
function drawCar(ctx,x,color,label,squash,ground,trail){const w=46*(1-.3*squash),h=30*(1+.2*squash),y=ground-h/2-4;
  for(let i=0;i<trail.length;i++){ctx.globalAlpha=(i/trail.length)*.18;ctx.fillStyle=color;
    ctx.fillRect(trail[i].px-7,ground-20,14,5);}ctx.globalAlpha=1;ctx.fillStyle='rgba(0,0,0,.15)';
  ctx.beginPath();ctx.ellipse(x,ground+2,w*.55,6,0,0,Math.PI*2);ctx.fill();ctx.fillStyle='#333';
  ctx.beginPath();ctx.arc(x-w*.3,ground+2,7,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(x+w*.3,ground+2,7,0,Math.PI*2);ctx.fill();
  ctx.fillStyle=color;ctx.beginPath();ctx.roundRect(x-w/2,y-h/2,w,h,8);ctx.fill();ctx.strokeStyle='rgba(0,0,0,.25)';ctx.stroke();
  drawFace(ctx,x,y-2,11);ctx.fillStyle='white';ctx.font='bold 11px sans-serif';ctx.textAlign='center';ctx.fillText(label,x,y+h/2+14);}
const scene={
  onEvent(event,player){if(event.type==='particle_burst'){const a=sample(player.config.tracks[0].x,event.fraction);
    const b=sample(player.config.tracks[1].x,event.fraction),t=player.coordinates();
    player.particles.burst((t.x(a)+t.x(b))/2,t.height-80,event.count,event.colors);}},
  draw(ctx,frame){const t=frame.transform,ground=t.height-60;drawBackground(ctx,t);
    const a=frame.tracks.car_a,b=frame.tracks.car_b,ax=t.x(a.x),bx=t.x(b.x);
    const trailA=frame.trails.get('car_a').map(point=>({px:t.x(point.x)}));
    const trailB=frame.trails.get('car_b').map(point=>({px:t.x(point.x)}));
    const impact=frame.config.impactFraction,since=Math.max(0,frame.fraction-impact)*frame.config.durationMs/1000;
    const squash=frame.state==='idle'||frame.fraction<impact?0:Math.exp(-since*12);
    if(frame.config.sticky&&frame.fraction>=impact&&frame.state!=='idle'){ctx.strokeStyle='#8D6E63';ctx.lineWidth=6;
      ctx.beginPath();ctx.moveTo(ax,ground-19);ctx.lineTo(bx,ground-19);ctx.stroke();}
    drawCar(ctx,ax,'#42A5F5','A',squash,ground,trailA);
    drawCar(ctx,bx,'#FF8A65','B',squash,ground,trailB);}
};
"""


def build_bumper_canvas(
    result: CollisionResult,
    *,
    final_message: str,
    autoplay: bool,
    nonce: int,
) -> str:
    animation = result.animation
    if animation is None:
        raise ValueError("Bumper Cars result has no animation data.")
    total_time = animation.time_s[-1]
    impact_fraction = (
        result.collision_time_s / total_time
        if result.collision_time_s is not None and total_time > 0
        else 2.0
    )
    config = {
        "durationMs": animation.duration_ms,
        "autoplay": autoplay,
        "seed": 20_260_710 + nonce,
        "trailLength": 14,
        "view": dict(animation.view),
        "tracks": [to_jsonable(track) for track in animation.tracks],
        "impactFraction": impact_fraction,
        "sticky": result.parameters.restitution == 0,
        "completionMessage": final_message,
        "events": (
            [{
                "id": "impact",
                "fraction": impact_fraction,
                "type": "particle_burst",
                "count": 20,
                "colors": ["#FFD54F", "#FF7043", "#FFEE58", "#FFFFFF"],
            }]
            if result.collided
            else []
        ),
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE_JAVASCRIPT,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Two bumper cars moving on a straight track; controls follow the animation.",
        idle_hint="Use Play below or tap CRASH! to launch",
    )


COMPARISON_SCENE_JAVASCRIPT = r"""
function comparisonBackground(ctx,t){ctx.clearRect(0,0,t.width,t.height);ctx.fillStyle='#FFF3E0';ctx.fillRect(0,0,t.width,t.height);
  ctx.strokeStyle='#BCAAA4';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,t.height/2);ctx.lineTo(t.width,t.height/2);ctx.stroke();
  ctx.fillStyle='#5D4037';ctx.font='bold 13px sans-serif';ctx.fillText('Run A',12,22);ctx.fillText('Run B',12,t.height/2+22);}
function comparisonCar(ctx,x,y,color,label){ctx.fillStyle='rgba(0,0,0,.15)';ctx.fillRect(x-24,y+15,48,5);ctx.fillStyle=color;
  ctx.beginPath();ctx.roundRect(x-23,y-15,46,30,8);ctx.fill();ctx.fillStyle='white';ctx.font='bold 10px sans-serif';
  ctx.textAlign='center';ctx.fillText(label,x,y+4);}
const scene={onEvent(event,player){if(event.type==='particle_burst'){const t=player.coordinates();
    const a=sample(player.config.tracks[event.trackA].x,event.fraction),b=sample(player.config.tracks[event.trackB].x,event.fraction);
    const lane=event.lane==='a'?t.height*.27:t.height*.75;player.particles.burst((t.x(a)+t.x(b))/2,lane,event.count,event.colors);}},
  draw(ctx,frame){const t=frame.transform;comparisonBackground(ctx,t);const tracks=frame.tracks;
    comparisonCar(ctx,t.x(tracks.run_a_car_a.x),t.height*.27,'#1E88E5','A');
    comparisonCar(ctx,t.x(tracks.run_a_car_b.x),t.height*.27,'#FB8C00','B');
    comparisonCar(ctx,t.x(tracks.run_b_car_a.x),t.height*.75,'#42A5F5','A');
    comparisonCar(ctx,t.x(tracks.run_b_car_b.x),t.height*.75,'#FFB74D','B');}};
"""


def build_bumper_comparison_canvas(
    baseline: CollisionResult,
    modified: CollisionResult,
    *,
    changed_variable: str,
    nonce: int,
    autoplay: bool,
) -> str:
    """Build a synchronized two-lane player for Run A and Run B."""

    if baseline.animation is None or modified.animation is None:
        raise ValueError("Both comparison results require animation data.")
    minimum = min(baseline.animation.view["minimum"], modified.animation.view["minimum"])
    maximum = max(baseline.animation.view["maximum"], modified.animation.view["maximum"])
    tracks = []
    for prefix, result in (("run_a", baseline), ("run_b", modified)):
        for track in result.animation.tracks:
            payload = to_jsonable(track)
            payload["id"] = f"{prefix}_{track.id}"
            payload["label"] = f"{prefix.replace('_', ' ').title()} {track.label}"
            tracks.append(payload)
    events = []
    for lane, result, offset in (("a", baseline, 0), ("b", modified, 1)):
        total = result.animation.time_s[-1]
        if result.collision_time_s is not None and total > 0:
            fraction = result.collision_time_s / total
            events.append({"id": f"impact_{lane}", "fraction": fraction, "type": "particle_burst",
                "lane": lane, "trackA": offset*2, "trackB": offset*2+1, "count": 14,
                "colors": ["#FFD54F", "#FF7043", "#FFFFFF"]})
    config = {"durationMs": 4_200, "autoplay": autoplay, "seed": 20_260_800+nonce,
        "trailLength": 0, "view": {"minimum": minimum, "maximum": maximum}, "tracks": tracks,
        "events": events, "completionMessage": f"Comparison complete: {changed_variable}"}
    return build_player_document(
        config=config,
        scene_javascript=COMPARISON_SCENE_JAVASCRIPT,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Synchronized comparison of Bumper Cars Run A and Run B.",
        idle_hint="Run A is shown above Run B",
    )
