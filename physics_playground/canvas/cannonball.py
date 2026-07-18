"""Cannonball scene adapters for the shared animation player."""

from physics_playground.canvas.player import build_player_document
from physics_playground.models.projectile import ProjectileResult
from physics_playground.serialization import to_jsonable

CANVAS_W, CANVAS_H, PLAYER_HEIGHT = 680, 360, 440

SCENE = r"""
function mapPoint(x,y,view,t){const left=40,right=t.width-25,ground=t.height-46,top=25;
  return {x:left+(x-view.xMin)/Math.max(.001,view.xMax-view.xMin)*(right-left),
          y:ground-(y-view.yMin)/Math.max(.001,view.yMax-view.yMin)*(ground-top)};}
function sky(ctx,t,frame){const ground=t.height-46,mode=PhysicsExperience.context(ctx,frame,'projectileField');if(!mode.environment){ctx.fillStyle=PhysicsVisuals.token(frame,'colors','surface_muted','#EAF0F6');ctx.fillRect(0,ground,t.width,t.height-ground)}}
function cannon(ctx,t,angle,frame){const p=mapPoint(0,0,t.config.view,t);PhysicsAssets.cannon(ctx,frame,{x:p.x,y:p.y-3,width:48,rotation:-angle*Math.PI/180,fill:PhysicsVisuals.token(frame,'colors','uncertainty','#64748B'),highlight:true,shadow:true,label:PhysicsVisuals.responsive(frame)==='mobile'?'':'Launcher'});}
function target(ctx,t,frame){const p=mapPoint(t.config.target,0,t.config.view,t),surface=PhysicsVisuals.token(frame,'colors','surface','#FFF'),accent=PhysicsVisuals.token(frame,'colors','net_force','#C2410C');ctx.fillStyle=surface;ctx.beginPath();ctx.arc(p.x,p.y-18,17,0,Math.PI*2);ctx.fill();
  ctx.fillStyle=accent;ctx.beginPath();ctx.arc(p.x,p.y-18,11,0,Math.PI*2);ctx.fill();ctx.fillStyle=surface;ctx.beginPath();ctx.arc(p.x,p.y-18,5,0,Math.PI*2);ctx.fill();}
const scene={onEvent(event,player){if(event.type==='impact'){const track=player.config.tracks[event.track];const t=player.coordinates();
  const p=mapPoint(sample(track.x,event.fraction),sample(track.y,event.fraction),player.config.view,t);player.particles.burst(p.x,p.y,event.count,event.colors);}},
draw(ctx,frame){const t={...frame.transform,config:frame.config};sky(ctx,t,frame);cannon(ctx,t,frame.config.angle,frame);target(ctx,t,frame);
  for(const track of Object.values(frame.tracks)){const points=frame.trails.get(track.id);PhysicsAnimation.fadingTrail(ctx,points,q=>mapPoint(q.x,q.y||0,frame.config.view,t),{color:track.style.color||PhysicsVisuals.token(frame,'colors','trajectory','#1769AA'),width:2.5,opacity:.42});
    const p=mapPoint(track.x,track.y||0,frame.config.view,t);PhysicsAssets.projectile(ctx,frame,{x:p.x,y:p.y,radius:8,fill:track.style.color||PhysicsVisuals.token(frame,'colors','trajectory','#1769AA'),highlight:true,shadow:true,label:frame.config.tracks.length>1&&PhysicsVisuals.responsive(frame)!=='mobile'?track.label:''});}}
};
"""


def _config(results: list[tuple[str, ProjectileResult, str]], target_m: float, seed: int, message: str, autoplay: bool) -> dict:
    tracks=[]; events=[]; x_max=max(target_m, *(result.range_m for _,result,_ in results))*1.15+3
    y_max=max(1.0, *(result.maximum_height_m for _,result,_ in results))*1.25+1
    for index,(label,result,color) in enumerate(results):
        track=to_jsonable(result.animation.tracks[0]); track["id"]=f"projectile_{index}"; track["label"]=label; track["style"]={"color":color}; tracks.append(track)
        if result.landed: events.append({"id":f"impact_{index}","fraction":1.0,"type":"impact","track":index,"count":24,
                                         "colors":["#FFD54F",color,"#FFFFFF"]})
    return {"durationMs":3_200,"autoplay":autoplay,"seed":seed,"trailLength":22,
            "view":{"xMin":0.0,"xMax":x_max,"yMin":0.0,"yMax":y_max},"tracks":tracks,"events":events,
            "target":target_m,"angle":results[0][1].parameters.launch_angle_deg,"completionMessage":message}


def build_cannon_canvas(result: ProjectileResult, *, target_m: float, message: str, seed: int, autoplay: bool) -> str:
    return build_player_document(config=_config([("Cannonball",result,"#37474F")],target_m,seed,message,autoplay),
        scene_javascript=SCENE,logical_width=CANVAS_W,logical_height=CANVAS_H,
        accessible_label="Animated cannonball trajectory and target.",idle_hint="Use Play or press FIRE!")


def build_cannon_comparison_canvas(run_a: ProjectileResult, run_b: ProjectileResult, *, target_m: float,
                                    labels: tuple[str,str], seed: int, autoplay: bool) -> str:
    config=_config([(labels[0],run_a,"#1565C0"),(labels[1],run_b,"#E65100")],target_m,seed,"Comparison complete",autoplay)
    return build_player_document(config=config,scene_javascript=SCENE,logical_width=CANVAS_W,logical_height=CANVAS_H,
        accessible_label=f"Overlaid cannonball trajectories comparing {labels[0]} and {labels[1]}.",idle_hint="Run A is blue; Run B is orange")
