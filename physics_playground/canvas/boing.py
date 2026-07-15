"""Boing Machine adapters for the shared animation player."""

from physics_playground.canvas.player import build_player_document
from physics_playground.models.spring import SpringResult
from physics_playground.serialization import to_jsonable

CANVAS_W,CANVAS_H,PLAYER_HEIGHT=680,230,320
SCENE=r"""
function background(ctx,t){ctx.clearRect(0,0,t.width,t.height);const g=ctx.createLinearGradient(0,0,0,t.height);g.addColorStop(0,'#F3F6FB');g.addColorStop(1,'#E8ECF3');ctx.fillStyle=g;ctx.fillRect(0,0,t.width,t.height);}
function spring(ctx,from,to,y){ctx.strokeStyle='#5C6BC0';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(from,y);const n=22;for(let i=1;i<=n;i++){const x=from+i/n*(to-from);ctx.lineTo(x,y+(i%2?13:-13));}ctx.lineTo(to,y);ctx.stroke();}
const scene={draw(ctx,frame){const t=frame.transform,cy=t.height/2,wall=45,rest=t.x(0);background(ctx,t);ctx.fillStyle='#607D8B';ctx.fillRect(wall-10,cy-55,12,110);
  for(const track of Object.values(frame.tracks)){const x=t.x(track.x);spring(ctx,wall,x,cy);const trail=frame.trails.get(track.id);for(let i=0;i<trail.length;i++){ctx.globalAlpha=i/trail.length*.25;ctx.fillStyle=track.style.color||'#EF5350';ctx.beginPath();ctx.arc(t.x(trail[i].x),cy,7,0,Math.PI*2);ctx.fill();}ctx.globalAlpha=1;
  ctx.fillStyle=track.style.color||'#EF5350';ctx.beginPath();ctx.roundRect(x-20,cy-20,40,40,8);ctx.fill();ctx.fillStyle='white';ctx.beginPath();ctx.arc(x-7,cy-4,4,0,Math.PI*2);ctx.arc(x+7,cy-4,4,0,Math.PI*2);ctx.fill();}}
};
"""


def _document(results:list[tuple[str,SpringResult,str]],*,seed:int,autoplay:bool,message:str)->str:
    minimum=min(r.animation.view["minimum"] for _,r,_ in results);maximum=max(r.animation.view["maximum"] for _,r,_ in results)
    tracks=[]
    for i,(label,result,color) in enumerate(results):
        track=to_jsonable(result.animation.tracks[0]);track["id"]=f"mass_{i}";track["label"]=label;track["style"]={"color":color};tracks.append(track)
    config={"durationMs":4200,"autoplay":autoplay,"seed":seed,"trailLength":14,"view":{"minimum":minimum,"maximum":maximum},"tracks":tracks,"events":[],"completionMessage":message}
    return build_player_document(config=config,scene_javascript=SCENE,logical_width=CANVAS_W,logical_height=CANVAS_H,
        accessible_label="Masses oscillating horizontally on springs.",idle_hint="Use Play or press BOING!")


def build_boing_canvas(result:SpringResult,*,seed:int,autoplay:bool)->str:
    return _document([("Spring mass",result,"#EF5350")],seed=seed,autoplay=autoplay,message="Oscillation complete!")


def build_boing_comparison_canvas(a:SpringResult,b:SpringResult,*,labels:tuple[str,str],seed:int,autoplay:bool)->str:
    return _document([(labels[0],a,"#1565C0"),(labels[1],b,"#E65100")],seed=seed,autoplay=autoplay,message="Comparison complete")
