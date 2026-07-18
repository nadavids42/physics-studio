from physics_playground.canvas.player import build_player_document
from physics_playground.models.pendulum import PendulumResult
from physics_playground.serialization import to_jsonable
CANVAS_W,CANVAS_H,PLAYER_HEIGHT=500,440,520
SCENE=r"""
const scene={draw(ctx,f){const t=f.transform,W=t.width,H=t.height,pivot={x:W/2,y:38};PhysicsExperience.context(ctx,f,'laboratory');PhysicsAssets.pivot(ctx,f,{x:pivot.x,y:pivot.y,width:42,height:30,fill:PhysicsVisuals.token(f,'colors','uncertainty','#64748B'),shadow:true,label:'Pivot'});
 const scale=Math.min((W/2-35)/f.config.maxLength,(H-pivot.y-42)/f.config.maxLength);for(const track of Object.values(f.tracks)){const x=pivot.x+track.x*scale,y=pivot.y-track.y*scale,color=track.style.color||PhysicsVisuals.token(f,'colors','displacement','#0F766E');
 PhysicsAnimation.fadingTrail(ctx,f.trails.get(track.id),q=>({x:pivot.x+q.x*scale,y:pivot.y-(q.y||0)*scale}),{color,width:2.2,opacity:.35});PhysicsAssets.cable(ctx,f,{x:pivot.x,y:pivot.y,end:{x:x-pivot.x,y:y-pivot.y},fill:PhysicsVisuals.token(f,'colors','tension','#6D28D9'),shadow:false});
 PhysicsAssets.pendulumBob(ctx,f,{x,y,radius:17,fill:color,highlight:true,shadow:true,label:f.config.tracks.length>1&&PhysicsVisuals.responsive(f)!=='mobile'?track.label:''});}}
};
"""
def _doc(items,seed,autoplay,message):
    tracks=[]
    for i,(label,r,color) in enumerate(items):q=to_jsonable(r.animation.tracks[0]);q["id"]=f"bob_{i}";q["label"]=label;q["style"]={"color":color};tracks.append(q)
    config={"durationMs":4800,"autoplay":autoplay,"seed":seed,"trailLength":18,"view":{"minimum":-1,"maximum":1},"maxLength":max(r.parameters.length_m for _,r,_ in items),"tracks":tracks,"events":[],"completionMessage":message}
    return build_player_document(config=config,scene_javascript=SCENE,logical_width=CANVAS_W,logical_height=CANVAS_H,accessible_label="Pendulum bob motion with rope length shown to scale.",idle_hint="Use Play or press SWING!")
def build_pendulum_canvas(r,*,seed,autoplay):return _doc([("Pendulum",r,"#66BB6A")],seed,autoplay,"Swing complete")
def build_pendulum_comparison_canvas(a,b,*,labels,seed,autoplay):return _doc([(labels[0],a,"#1565C0"),(labels[1],b,"#E65100")],seed,autoplay,"Comparison complete")
