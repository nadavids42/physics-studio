"""Planet Launcher scene adapters for the shared player."""

from physics_playground.canvas.player import build_player_document
from physics_playground.serialization import to_jsonable

CANVAS_W, CANVAS_H, PLAYER_HEIGHT = 560, 560, 640
SCENE = r"""
const scene={draw(ctx,f){const t=f.transform,W=t.width,H=t.height,cx=W/2,cy=H/2,view=f.config.orbitView,scale=Math.min(W,H)*.43/view;PhysicsExperience.context(ctx,f,'space');PhysicsAssets.star(ctx,f,{x:cx,y:cy,radius:16,fill:PhysicsVisuals.token(f,'colors','energy','#B45309'),glow:true,shadow:false,label:'Central body'});
 for(const q of Object.values(f.tracks)){const color=q.style.color||PhysicsVisuals.token(f,'colors','trajectory','#1769AA');PhysicsAnimation.fadingTrail(ctx,f.trails.get(q.id),p=>({x:cx+p.x*scale,y:cy-(p.y||0)*scale}),{color,width:2.2,opacity:.48});
 PhysicsAssets.planet(ctx,f,{x:cx+q.x*scale,y:cy-(q.y||0)*scale,radius:8,fill:color,highlight:true,shadow:true,label:f.config.tracks.length>1&&PhysicsVisuals.responsive(f)!=='mobile'?q.label:''});}}
};
"""


def _doc(items, seed, autoplay, message):
    tracks = []
    for i, (label, r, color) in enumerate(items):
        q = to_jsonable(r.animation.tracks[0])
        q["id"] = f"planet_{i}"
        q["label"] = label
        q["style"] = {"color": color}
        tracks.append(q)
    view = max(r.animation.view["maximum"] for _, r, _ in items)
    config = {
        "durationMs": 5000,
        "autoplay": autoplay,
        "seed": seed,
        "trailLength": 180,
        "view": {"minimum": -view, "maximum": view},
        "orbitView": view,
        "tracks": tracks,
        "events": [],
        "completionMessage": message,
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Planet trajectories around a fixed central star.",
        idle_hint="Use Play or press LAUNCH!",
    )


def build_orbit_canvas(r, *, seed, autoplay):
    return _doc([("Planet", r, "#42A5F5")], seed, autoplay, r.outcome.value)


def build_orbit_comparison_canvas(a, b, *, labels, seed, autoplay):
    return _doc(
        [(labels[0], a, "#42A5F5"), (labels[1], b, "#FF8A65")],
        seed,
        autoplay,
        "Comparison complete",
    )
