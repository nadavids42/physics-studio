"""Reusable shared-player diagram for vector cross-product direction."""
from physics_playground.canvas.player import build_player_document
SCENE=r"""
const scene={draw(ctx,s){const w=s.transform.width,h=s.transform.height,c=s.config.vectorDiagram||{},cx=w/2,cy=h/2-15;
PhysicsVisuals.background(ctx,s);const vectors=(c.vectors||[]).map(v=>({...v,x:cx,y:cy}));PhysicsAnnotations.vectorSet(ctx,s,vectors,s.fraction,{x:12,y:12});
ctx.save();ctx.fillStyle=PhysicsVisuals.token(s,'colors',c.forceZ>0?'normal_force':(c.forceZ<0?'magnetic_field':'text_muted'),'#526577');
ctx.font='650 58px '+PhysicsVisuals.token(s,'typography','family_ui','system-ui');ctx.textAlign='center';ctx.fillText(c.forceZ>0?'⊙':(c.forceZ<0?'⊗':'0'),cx,cy+105);
PhysicsVisuals.applyText(ctx,s,'label');ctx.textAlign='center';ctx.fillText(c.forceLabel,cx,cy+135);ctx.restore();}};
"""
def build_vector_direction_document(*,motion:tuple[float,float],field:tuple[float,float],force_z:float,motion_label:str,message:str,seed:int)->str:
    vectors=[
        {"dx":motion[0],"dy":motion[1],"role":"velocity","label":motion_label,"scale_mode":"normalized","fixed_length_px":105},
        {"dx":field[0],"dy":field[1],"role":"magnetic_field","label":"Magnetic field B","scale_mode":"normalized","fixed_length_px":105},
    ]
    config={"durationMs":1400,"autoplay":False,"seed":seed,"tracks":[{"id":"vector-reveal","label":"Vector direction reveal","x":[0,1]}],"events":[],"completionMessage":message,"vectorDiagram":{"vectors":vectors,"forceZ":force_z,"forceLabel":"Force: out ⊙" if force_z>0 else ("Force: in ⊗" if force_z<0 else "Force: zero")},"view":{"minimum":0,"maximum":1}}
    return build_player_document(config=config,scene_javascript=SCENE,logical_width=720,logical_height=430,accessible_label="Magnetic cross-product vector diagram. "+message,idle_hint="Press Play to reveal the vectors and force direction")
