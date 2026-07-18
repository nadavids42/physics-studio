"""Bumper Cars scene adapter for the shared browser-side animation player."""

from physics_playground.canvas.player import build_player_document
from physics_playground.serialization import to_jsonable
from physics_playground.subjects.mechanics.bumper_cars.physics import CollisionResult

CANVAS_W, CANVAS_H = 680, 260
PLAYER_HEIGHT = 350

SCENE_JAVASCRIPT = r"""
function drawBackground(ctx,t,frame){const W=t.width,H=t.height,ground=H-60,mode=PhysicsExperience.context(ctx,frame,'collisionTrack');if(!mode.environment){ctx.fillStyle=PhysicsVisuals.token(frame,'colors','surface_muted','#EAF0F6');ctx.fillRect(0,ground,W,H-ground)}ctx.strokeStyle='rgba(255,255,255,.6)';
  ctx.lineWidth=3;ctx.setLineDash([14,10]);ctx.beginPath();ctx.moveTo(0,ground+30);ctx.lineTo(W,ground+30);ctx.stroke();ctx.setLineDash([]);}
function drawCar(ctx,frame,x,color,label,ground,trail){PhysicsAnimation.fadingTrail(ctx,trail,p=>({x:p.px,y:ground-15}),{color,width:5,opacity:.22});PhysicsAssets.cart(ctx,frame,{x,y:ground-24,width:52,height:28,fill:color,highlight:true,shadow:true,label});}
const scene={
  onEvent(event,player){if(event.type==='particle_burst'){const a=sample(player.config.tracks[0].x,event.fraction);
    const b=sample(player.config.tracks[1].x,event.fraction),t=player.coordinates();
    player.particles.burst((t.x(a)+t.x(b))/2,t.height-80,event.count,event.colors);}},
  draw(ctx,frame){const t=frame.transform,ground=t.height-60;drawBackground(ctx,t,frame);
    const a=frame.tracks.car_a,b=frame.tracks.car_b,ax=t.x(a.x),bx=t.x(b.x);
    const trailA=frame.trails.get('car_a').map(point=>({px:t.x(point.x)}));
    const trailB=frame.trails.get('car_b').map(point=>({px:t.x(point.x)}));
    const impact=frame.config.impactFraction,since=Math.max(0,frame.fraction-impact)*frame.config.durationMs/1000;
    if(frame.config.sticky&&frame.fraction>=impact&&frame.state!=='idle'){ctx.strokeStyle=PhysicsVisuals.token(frame,'colors','uncertainty','#64748B');ctx.lineWidth=6;
      ctx.beginPath();ctx.moveTo(ax,ground-19);ctx.lineTo(bx,ground-19);ctx.stroke();}
    drawCar(ctx,frame,ax,PhysicsVisuals.token(frame,'colors','graph_1','#0072B2'),'A',ground,trailA);
    drawCar(ctx,frame,bx,PhysicsVisuals.token(frame,'colors','graph_2','#D55E00'),'B',ground,trailB);
    if(frame.fraction>=impact&&since<.7){const x=(ax+bx)/2,y=ground-25,p=Math.min(1,since/.7);PhysicsAnimation.impactRipple(ctx,x,y,p,{reducedMotion:frame.reducedMotion,color:PhysicsVisuals.token(frame,'colors','warning','#9A5B00')});PhysicsAnimation.collisionFlash(ctx,x,y,p,{reducedMotion:frame.reducedMotion,config:frame.config});}}
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
            [
                {
                    "id": "impact",
                    "fraction": impact_fraction,
                    "type": "particle_burst",
                    "count": 20,
                    "colors": ["#FFD54F", "#FF7043", "#FFEE58", "#FFFFFF"],
                }
            ]
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
function comparisonBackground(ctx,t,frame){PhysicsExperience.context(ctx,frame,'collisionTrack');
  ctx.strokeStyle=PhysicsVisuals.token(frame,'colors','border','#B8C5D1');ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,t.height/2);ctx.lineTo(t.width,t.height/2);ctx.stroke();
  ctx.fillStyle=PhysicsVisuals.token(frame,'colors','text','#152536');PhysicsVisuals.applyText(ctx,frame,'label');ctx.fillText('Run A',12,22);ctx.fillText('Run B',12,t.height/2+22);}
function comparisonCar(ctx,frame,x,y,color,label){PhysicsAssets.cart(ctx,frame,{x,y,width:46,height:25,fill:color,highlight:true,shadow:true,label});}
const scene={onEvent(event,player){if(event.type==='particle_burst'){const t=player.coordinates();
    const a=sample(player.config.tracks[event.trackA].x,event.fraction),b=sample(player.config.tracks[event.trackB].x,event.fraction);
    const lane=event.lane==='a'?t.height*.27:t.height*.75;player.particles.burst((t.x(a)+t.x(b))/2,lane,event.count,event.colors);}},
  draw(ctx,frame){const t=frame.transform;comparisonBackground(ctx,t,frame);const tracks=frame.tracks,c1=PhysicsVisuals.token(frame,'colors','graph_1','#0072B2'),c2=PhysicsVisuals.token(frame,'colors','graph_2','#D55E00');
    comparisonCar(ctx,frame,t.x(tracks.run_a_car_a.x),t.height*.27,c1,'A');
    comparisonCar(ctx,frame,t.x(tracks.run_a_car_b.x),t.height*.27,c2,'B');
    comparisonCar(ctx,frame,t.x(tracks.run_b_car_a.x),t.height*.75,c1,'A');
    comparisonCar(ctx,frame,t.x(tracks.run_b_car_b.x),t.height*.75,c2,'B');}};
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
            events.append(
                {
                    "id": f"impact_{lane}",
                    "fraction": fraction,
                    "type": "particle_burst",
                    "lane": lane,
                    "trackA": offset * 2,
                    "trackB": offset * 2 + 1,
                    "count": 14,
                    "colors": ["#FFD54F", "#FF7043", "#FFFFFF"],
                }
            )
    config = {
        "durationMs": 4_200,
        "autoplay": autoplay,
        "seed": 20_260_800 + nonce,
        "trailLength": 0,
        "view": {"minimum": minimum, "maximum": maximum},
        "tracks": tracks,
        "events": events,
        "completionMessage": f"Comparison complete: {changed_variable}",
    }
    return build_player_document(
        config=config,
        scene_javascript=COMPARISON_SCENE_JAVASCRIPT,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Synchronized comparison of Bumper Cars Run A and Run B.",
        idle_hint="Run A is shown above Run B",
    )
