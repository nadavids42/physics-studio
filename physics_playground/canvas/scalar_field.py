"""Reusable responsive player adapter for precomputed one-dimensional scalar fields."""
from physics_playground.canvas.player import build_player_document
SCENE=r"""
const scene={draw(ctx,s){const w=s.transform.width,h=s.transform.height,frames=s.config.fieldFrames||[],xs=s.config.fieldX||[];ctx.clearRect(0,0,w,h);ctx.fillStyle='#F8FAFC';ctx.fillRect(0,0,w,h);ctx.strokeStyle='#64748B';ctx.beginPath();ctx.moveTo(35,h/2);ctx.lineTo(w-25,h/2);ctx.stroke();if(!frames.length)return;const fi=Math.min(frames.length-1,Math.round(s.fraction*(frames.length-1))),ys=frames[fi],limit=Math.max(.001,s.config.fieldLimit||1);ctx.strokeStyle='#0072B2';ctx.lineWidth=3;ctx.beginPath();for(let i=0;i<ys.length;i++){const px=35+i/(ys.length-1)*(w-60),py=h/2-ys[i]/limit*(h*.38);if(i)ctx.lineTo(px,py);else ctx.moveTo(px,py)}ctx.stroke();ctx.fillStyle='#111';ctx.font='13px sans-serif';ctx.fillText(`Time ${(s.fraction*(s.config.fieldDurationS||1)).toFixed(2)} s`,42,24);}};
"""
def build_scalar_field_document(*,x:tuple[float,...],frames:tuple[tuple[float,...],...],duration_s:float,accessible_label:str,completion_message:str,seed:int,autoplay:bool=False)->str:
    limit=max((abs(value) for frame in frames for value in frame),default=1.)
    config={"durationMs":max(1000,int(duration_s*2500)),"fieldDurationS":duration_s,"autoplay":autoplay,"seed":seed,"tracks":[{"id":"field-clock","label":"Wave field","x":[0,1]}],"events":[],"completionMessage":completion_message,"fieldX":x,"fieldFrames":frames,"fieldLimit":limit,"view":{"minimum":0,"maximum":1}}
    return build_player_document(config=config,scene_javascript=SCENE,logical_width=820,logical_height=390,accessible_label=accessible_label,idle_hint="Press Play to animate the field")
