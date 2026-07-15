from physics_playground.canvas.player import build_player_document
from physics_playground.serialization import to_jsonable
CANVAS_W,CANVAS_H,PLAYER_HEIGHT=560,500,590
SCENE=r"""
const scene={draw(ctx,f){const t=f.transform,W=t.width,H=t.height,p={x:W/2,y:45},scale=Math.min(W,H)*.38/f.config.limit;ctx.clearRect(0,0,W,H);ctx.fillStyle='#F5F7FB';ctx.fillRect(0,0,W,H);
 for(const prefix of f.config.systems){const j=f.tracks[prefix+'_joint'],b=f.tracks[prefix+'_bob'];const jx=p.x+j.x*scale,jy=p.y-j.y*scale,bx=p.x+b.x*scale,by=p.y-b.y*scale;ctx.strokeStyle=j.style.color;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(jx,jy);ctx.lineTo(bx,by);ctx.stroke();const trail=f.trails.get(prefix+'_bob');ctx.beginPath();trail.forEach((q,i)=>{const x=p.x+q.x*scale,y=p.y-(q.y||0)*scale;i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.globalAlpha=.25;ctx.stroke();ctx.globalAlpha=1;ctx.fillStyle=b.style.color;ctx.beginPath();ctx.arc(jx,jy,8,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(bx,by,13,0,Math.PI*2);ctx.fill();}}
};
"""
def build_double_canvas(r,*,seed,autoplay):
    tracks=[to_jsonable(q) for q in r.animation.tracks];limit=r.parameters.length_1_m+r.parameters.length_2_m;config={"durationMs":6000,"autoplay":autoplay,"seed":seed,"trailLength":100,"view":{"minimum":-limit,"maximum":limit},"limit":limit,"systems":["a","b"],"tracks":tracks,"events":[],"completionMessage":"Chaos comparison complete"}
    return build_player_document(config=config,scene_javascript=SCENE,logical_width=CANVAS_W,logical_height=CANVAS_H,accessible_label="Two nearly identical double pendulums evolving together.",idle_hint="Use Play or press RELEASE!")
