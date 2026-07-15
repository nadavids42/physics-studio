from physics_playground.canvas.player import build_player_document
from physics_playground.serialization import to_jsonable
CANVAS_W,CANVAS_H,PLAYER_HEIGHT=640,350,430
SCENE=r"""
const scene={draw(ctx,f){const t=f.transform,W=t.width,H=t.height,cx=W/2,cy=H/2,R=Math.min(W,H)*.36;ctx.clearRect(0,0,W,H);ctx.fillStyle='#0b1224';ctx.fillRect(0,0,W,H);const g=ctx.createRadialGradient(cx-R*.3,cy-R*.3,R*.1,cx,cy,R);g.addColorStop(0,'#81D4FA');g.addColorStop(1,'#2E7D32');ctx.fillStyle=g;ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.fill();ctx.strokeStyle='rgba(255,255,255,.55)';ctx.setLineDash([8,8]);ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(cx-R,cy);ctx.lineTo(cx+R,cy);ctx.stroke();ctx.setLineDash([]);
 for(const q of Object.values(f.tracks)){const x=cx+(q.x/f.config.radiusKm)*R;const trail=f.trails.get(q.id);for(let i=0;i<trail.length;i++){ctx.globalAlpha=i/trail.length*.3;ctx.fillStyle=q.style.color;ctx.beginPath();ctx.arc(cx+(trail[i].x/f.config.radiusKm)*R,cy,7,0,Math.PI*2);ctx.fill();}ctx.globalAlpha=1;ctx.fillStyle=q.style.color;ctx.beginPath();ctx.arc(x,cy,15,0,Math.PI*2);ctx.fill();}}
};
"""
def _doc(items,seed,autoplay,message):
    tracks=[]
    for i,(label,r,color) in enumerate(items):q=to_jsonable(r.animation.tracks[0]);q["id"]=f"traveler_{i}";q["label"]=label;q["style"]={"color":color};tracks.append(q)
    radius=max(r.parameters.radius_m/1000 for _,r,_ in items);config={"durationMs":4500,"autoplay":autoplay,"seed":seed,"trailLength":18,"view":{"minimum":-radius,"maximum":radius},"radiusKm":radius,"tracks":tracks,"events":[],"completionMessage":message}
    return build_player_document(config=config,scene_javascript=SCENE,logical_width=CANVAS_W,logical_height=CANVAS_H,accessible_label="Traveler falling through a tunnel across a planet.",idle_hint="Use Play or press JUMP IN!")
def build_tunnel_canvas(r,*,seed,autoplay):return _doc([("Traveler",r,"#FF7043")],seed,autoplay,"Reached the opposite turning point")
def build_tunnel_comparison_canvas(items,*,seed,autoplay):return _doc([(label,r,color) for label,r,color in items],seed,autoplay,"Comparison complete")
