"""Shared browser-player scene adapter for mechanics diagrams."""
from physics_playground.canvas.player import build_player_document

SCENE=r"""
const scene={draw(ctx,s){const {width:w,height:h}=s.transform;PhysicsExperience.context(ctx,s,s.config.scene==='coaster'?'rollerCoaster':'laboratory');ctx.strokeStyle=PhysicsVisuals.token(s,'colors','text','#152536');ctx.lineWidth=4;
if(s.config.scene==='ramp'){ctx.beginPath();ctx.moveTo(35,h-35);ctx.lineTo(w-35,h-35);ctx.lineTo(35,40);ctx.closePath();ctx.stroke();const b=s.tracks.block;ctx.fillStyle='#FB8C00';ctx.fillRect(35+b.x*(w-100),35+b.x*(h-95),34,34);}
else if(s.config.scene==='lever'){ctx.translate(w/2,h/2);ctx.rotate((s.tracks.beam.x||0)*Math.PI/180);ctx.strokeStyle='#1565C0';ctx.lineWidth=12;ctx.beginPath();ctx.moveTo(-w*.4,0);ctx.lineTo(w*.4,0);ctx.stroke();ctx.fillStyle='#455A64';ctx.beginPath();ctx.moveTo(-18,28);ctx.lineTo(18,28);ctx.lineTo(0,0);ctx.fill();ctx.fillStyle='#D32F2F';ctx.fillRect(-w*.34,-35,42,34);ctx.fillStyle='#2E7D32';ctx.fillRect(w*.28,-35,42,34);}
else if(s.config.scene==='coaster'){const car=s.tracks.car;ctx.strokeStyle='#37474F';ctx.beginPath();for(let i=0;i<80;i++){const x=30+i*(w-60)/79,y=h*.72-Math.sin(i/79*Math.PI*2)*h*.25;if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y)}ctx.stroke();ctx.fillStyle='#E53935';ctx.fillRect(22+car.x*(w-70),h*.68-Math.sin(car.x*Math.PI*2)*h*.25,36,22);}
else if(s.config.scene==='rotation'){ctx.translate(w/2,h/2);ctx.rotate(s.tracks.body.x||0);ctx.fillStyle='#5E35B1';ctx.beginPath();ctx.arc(0,0,75,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#FFF';ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(70,0);ctx.stroke();}
else{ctx.strokeStyle='#546E7A';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(35,h/2);ctx.lineTo(w-35,h/2);ctx.stroke();for(const t of Object.values(s.tracks)){const x=55+(t.x+5)/10*(w-110);ctx.fillStyle=t.style.color||'#1976D2';ctx.beginPath();ctx.arc(x,h/2,Math.max(8,t.style.radius||12),0,Math.PI*2);ctx.fill();ctx.fillStyle='#111';ctx.fillText(t.label,x-18,h/2+35);}}}};
"""
def document(scene:str,tracks:list[dict],*,message:str,seed:int,autoplay:bool=True)->str:
    return build_player_document(config={"durationMs":2200,"autoplay":autoplay,"seed":seed,"scene":scene,"tracks":tracks,"events":[],"completionMessage":message,"view":{"minimum":0,"maximum":1}},scene_javascript=SCENE,logical_width=760,logical_height=360,accessible_label=f"{scene.title()} mechanics animation. {message}",idle_hint="Press Play to run the experiment")
