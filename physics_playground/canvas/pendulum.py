from physics_playground.canvas.player import build_player_document
from physics_playground.models.pendulum import PendulumResult
from physics_playground.serialization import to_jsonable
CANVAS_W,CANVAS_H,PLAYER_HEIGHT=500,440,520
SCENE=r"""
const scene={draw(ctx,f){const t=f.transform,W=t.width,H=t.height,pivot={x:W/2,y:32};ctx.clearRect(0,0,W,H);const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#E1F5FE');g.addColorStop(1,'#F3F9FF');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);ctx.fillStyle='#78909C';ctx.fillRect(pivot.x-30,pivot.y-12,60,10);
 const scale=Math.min((W/2-25)/f.config.maxLength,(H-pivot.y-25)/f.config.maxLength);for(const track of Object.values(f.tracks)){const x=pivot.x+track.x*scale,y=pivot.y-track.y*scale;ctx.strokeStyle=track.style.color;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(pivot.x,pivot.y);ctx.lineTo(x,y);ctx.stroke();const trail=f.trails.get(track.id);for(let i=0;i<trail.length;i++){ctx.globalAlpha=i/trail.length*.25;ctx.fillStyle=track.style.color;ctx.beginPath();ctx.arc(pivot.x+trail[i].x*scale,pivot.y-(trail[i].y||0)*scale,5,0,Math.PI*2);ctx.fill();}ctx.globalAlpha=1;ctx.fillStyle=track.style.color;ctx.beginPath();ctx.arc(x,y,17,0,Math.PI*2);ctx.fill();}}
};
"""
def _doc(items,seed,autoplay,message):
    tracks=[]
    for i,(label,r,color) in enumerate(items):q=to_jsonable(r.animation.tracks[0]);q["id"]=f"bob_{i}";q["label"]=label;q["style"]={"color":color};tracks.append(q)
    config={"durationMs":4800,"autoplay":autoplay,"seed":seed,"trailLength":18,"view":{"minimum":-1,"maximum":1},"maxLength":max(r.parameters.length_m for _,r,_ in items),"tracks":tracks,"events":[],"completionMessage":message}
    return build_player_document(config=config,scene_javascript=SCENE,logical_width=CANVAS_W,logical_height=CANVAS_H,accessible_label="Pendulum bob motion with rope length shown to scale.",idle_hint="Use Play or press SWING!")
def build_pendulum_canvas(r,*,seed,autoplay):return _doc([("Pendulum",r,"#66BB6A")],seed,autoplay,"Swing complete")
def build_pendulum_comparison_canvas(a,b,*,labels,seed,autoplay):return _doc([(labels[0],a,"#1565C0"),(labels[1],b,"#E65100")],seed,autoplay,"Comparison complete")
