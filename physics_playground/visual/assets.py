"""Typed asset contracts and the shared Canvas scientific asset library.

Physics remains renderer-neutral: an ``AssetSpec`` can be serialized into a
scene payload, described as text, or drawn by ``PhysicsAssets`` in the browser.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class AssetKind(StrEnum):
    SPHERE="sphere"; MASS="mass"; BLOCK="block"; CART="cart"; PENDULUM_BOB="pendulumBob"
    PIVOT="pivot"; CABLE="cable"; ROD="rod"; SPRING="spring"; RAMP="ramp"; PULLEY="pulley"
    LEVER="lever"; WHEEL="wheel"; PLANET="planet"; MOON="moon"; STAR="star"; SATELLITE="satellite"
    PROJECTILE="projectile"; CANNON="cannon"; FLUID_CONTAINER="fluidContainer"; FLUID_SURFACE="fluidSurface"
    LENS="lens"; MIRROR="mirror"; RAY="ray"; WAVEFRONT="wavefront"; CHARGE="charge"
    FIELD_LINE="fieldLine"; FORCE_ARROW="forceArrow"; VELOCITY_ARROW="velocityArrow"
    ACCELERATION_ARROW="accelerationArrow"; TORQUE_ARC="torqueArc"; ANGLE_MARKER="angleMarker"
    RULER="ruler"; GRID="grid"; TRAIL="trail"; COLLISION_FLASH="collisionFlash"; CALLOUT="callout"


@dataclass(frozen=True, slots=True)
class AssetStyle:
    fill: str | None = None; outline: str | None = None; opacity: float = 1
    selected: bool = False; disabled: bool = False; highlight: bool = False
    shadow: bool = True; glow: bool = False


@dataclass(frozen=True, slots=True)
class AssetSpec:
    kind: AssetKind; x: float; y: float
    width: float = 40; height: float = 40; scale: float = 1; rotation: float = 0
    label: str = ""; description: str = ""; style: AssetStyle = field(default_factory=AssetStyle)
    options: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload=asdict(self);payload["kind"]=self.kind.value;return payload

    @property
    def accessible_description(self) -> str:
        if self.description:return self.description
        name=self.label or self.kind.value.replace("Arrow"," arrow").replace("Line"," line")
        return f"{name} at ({self.x:g}, {self.y:g})."


CANVAS_ASSET_JS = r"""
const PhysicsAssets=(()=>{
  const V=PhysicsVisuals;
  const point=(x,y)=>({x,y});
  function setup(ctx,s,o={}){ctx.save();ctx.translate(o.x||0,o.y||0);ctx.rotate(o.rotation||0);ctx.scale(o.scale||1,o.scale||1);
    ctx.globalAlpha=(o.opacity??1)*(o.disabled ? .45 : 1);ctx.lineWidth=o.outlineWidth||V.token(s,'shape','object_outline',2);
    ctx.lineJoin='round';ctx.lineCap='round';if(o.shadow){ctx.shadowColor='rgba(15,23,42,.18)';ctx.shadowBlur=8;ctx.shadowOffsetY=3}
    if(o.glow){ctx.shadowColor=o.fill||V.token(s,'colors','accent','#1769AA');ctx.shadowBlur=14;ctx.shadowOffsetY=0}}
  function finish(ctx,s,o={}){ctx.restore();if(o.selected){ctx.save();ctx.strokeStyle=V.token(s,'colors','selected','#7C3AED');ctx.lineWidth=3;
    ctx.setLineDash([6,4]);ctx.beginPath();ctx.arc(o.x||0,o.y||0,Math.max(o.width||40,o.height||40)*.7*(o.scale||1),0,Math.PI*2);ctx.stroke();ctx.restore()}
    if(o.label){ctx.save();V.applyText(ctx,s,'label');ctx.textAlign='center';ctx.fillText(o.label,o.x||0,(o.y||0)+(o.height||40)*(o.scale||1)*.72+16);ctx.restore()}}
  function colors(s,o,fill='accent'){return {fill:o.fill||V.token(s,'colors',fill,'#1769AA'),outline:o.outline||V.token(s,'colors','text','#152536')}}
  function gradient(ctx,c,r,base,highlight=true){const g=ctx.createRadialGradient(c.x-r*.35,c.y-r*.4,r*.08,c.x,c.y,r);g.addColorStop(0,highlight?'#FFFFFF':base);g.addColorStop(.22,base);g.addColorStop(1,base);return g}
  function body(ctx,s,o={},role='accent'){const r=(o.radius||Math.min(o.width||40,o.height||40)/2),c=colors(s,o,role);setup(ctx,s,o);
    ctx.fillStyle=gradient(ctx,point(0,0),r,c.fill,o.highlight!==false);ctx.strokeStyle=c.outline;ctx.beginPath();ctx.arc(0,0,r,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.globalAlpha*=.22;ctx.fillStyle='#FFF';ctx.beginPath();ctx.ellipse(-r*.25,-r*.32,r*.34,r*.16,-.5,0,Math.PI*2);ctx.fill();finish(ctx,s,o)}
  function sphere(ctx,s,o={}){body(ctx,s,o,'accent')} function mass(ctx,s,o={}){body(ctx,s,o,'displacement')}
  function block(ctx,s,o={}){const w=o.width||54,h=o.height||42,c=colors(s,o,'energy');setup(ctx,s,o);const g=ctx.createLinearGradient(0,-h/2,0,h/2);
    g.addColorStop(0,o.highlight?'#FFF':c.fill);g.addColorStop(.18,c.fill);g.addColorStop(1,c.fill);ctx.fillStyle=g;ctx.strokeStyle=c.outline;
    ctx.beginPath();ctx.roundRect(-w/2,-h/2,w,h,Math.min(8,h*.18));ctx.fill();ctx.stroke();ctx.globalAlpha*=.18;ctx.fillStyle='#FFF';ctx.fillRect(-w*.36,-h*.34,w*.72,h*.12);finish(ctx,s,o)}
  function wheel(ctx,s,o={}){const r=o.radius||Math.min(o.width||34,o.height||34)/2,c=colors(s,o,'uncertainty');setup(ctx,s,o);ctx.fillStyle=c.fill;ctx.strokeStyle=c.outline;
    ctx.beginPath();ctx.arc(0,0,r,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle=V.token(s,'colors','surface','#FFF');ctx.beginPath();ctx.arc(0,0,r*.28,0,Math.PI*2);ctx.fill();ctx.stroke();
    for(let i=0;i<6;i++){const a=i*Math.PI/3;ctx.beginPath();ctx.moveTo(Math.cos(a)*r*.3,Math.sin(a)*r*.3);ctx.lineTo(Math.cos(a)*r*.82,Math.sin(a)*r*.82);ctx.stroke()}finish(ctx,s,o)}
  function cart(ctx,s,o={}){const w=o.width||72,h=o.height||38;block(ctx,s,{...o,y:(o.y||0)-8,width:w,height:h,label:'',shadow:o.shadow});
    wheel(ctx,s,{...o,x:(o.x||0)-w*.28,y:(o.y||0)+h*.38,width:20,height:20,label:'',shadow:false});wheel(ctx,s,{...o,x:(o.x||0)+w*.28,y:(o.y||0)+h*.38,width:20,height:20,label:'',shadow:false});
    if(o.label)finish(ctx,s,{...o,shadow:false})}
  function pendulumBob(ctx,s,o={}){body(ctx,s,{...o,radius:o.radius||18},'displacement')}
  function pivot(ctx,s,o={}){const w=o.width||34,h=o.height||28,c=colors(s,o,'uncertainty');setup(ctx,s,o);ctx.fillStyle=c.fill;ctx.strokeStyle=c.outline;
    ctx.beginPath();ctx.moveTo(0,-h*.45);ctx.lineTo(w/2,h/2);ctx.lineTo(-w/2,h/2);ctx.closePath();ctx.fill();ctx.stroke();ctx.fillStyle=V.token(s,'colors','surface','#FFF');ctx.beginPath();ctx.arc(0,-h*.32,4,0,Math.PI*2);ctx.fill();finish(ctx,s,o)}
  function segment(ctx,s,o={},role='tension'){const end=o.end||point((o.width||80),0),c=colors(s,o,role);setup(ctx,s,o);ctx.strokeStyle=c.fill;ctx.lineWidth=o.lineWidth||V.token(s,'shape','line_emphasis',2.5);
    if(o.dashed)ctx.setLineDash([7,5]);ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(end.x,end.y);ctx.stroke();finish(ctx,s,o)}
  function cable(ctx,s,o={}){segment(ctx,s,o,'tension')} function rod(ctx,s,o={}){segment(ctx,s,{...o,lineWidth:o.lineWidth||6},'uncertainty')}
  function spring(ctx,s,o={}){const end=o.end||point(o.width||100,0),turns=o.turns||12,amp=o.amplitude||9,c=colors(s,o,'acceleration');setup(ctx,s,o);ctx.strokeStyle=c.fill;ctx.lineWidth=o.lineWidth||2.5;
    ctx.beginPath();ctx.moveTo(0,0);for(let i=1;i<turns*2;i++){const t=i/(turns*2),x=end.x*t,y=end.y*t+(i%2?amp:-amp);ctx.lineTo(x,y)}ctx.lineTo(end.x,end.y);ctx.stroke();finish(ctx,s,o)}
  function ramp(ctx,s,o={}){const w=o.width||150,h=o.height||80,c=colors(s,o,'uncertainty');setup(ctx,s,o);ctx.fillStyle=o.fill||V.token(s,'colors','surface_muted','#EAF0F6');ctx.strokeStyle=c.outline;
    ctx.beginPath();ctx.moveTo(-w/2,h/2);ctx.lineTo(w/2,h/2);ctx.lineTo(w/2,-h/2);ctx.closePath();ctx.fill();ctx.stroke();finish(ctx,s,o)}
  function pulley(ctx,s,o={}){wheel(ctx,s,{...o,width:o.width||48,height:o.height||48,fill:o.fill||V.token(s,'colors','surface_muted','#EAF0F6')})}
  function lever(ctx,s,o={}){rod(ctx,s,{...o,x:o.x-(o.width||160)/2,y:o.y,end:point(o.width||160,0),lineWidth:o.height||9,label:''});pivot(ctx,s,{...o,width:32,height:28,label:'',shadow:false});if(o.label)finish(ctx,s,{...o,shadow:false})}
  function planet(ctx,s,o={}){body(ctx,s,{...o,radius:o.radius||Math.min(o.width||72,o.height||72)/2},'electric_field')}
  function moon(ctx,s,o={}){body(ctx,s,{...o,radius:o.radius||Math.min(o.width||34,o.height||34)/2,highlight:false},'uncertainty')}
  function star(ctx,s,o={}){const r=o.radius||Math.min(o.width||70,o.height||70)/2,c=colors(s,o,'energy');setup(ctx,s,{...o,glow:o.glow!==false});ctx.fillStyle=c.fill;ctx.strokeStyle=c.outline;ctx.beginPath();
    for(let i=0;i<20;i++){const a=-Math.PI/2+i*Math.PI/10,rr=i%2?r*.72:r;ctx.lineTo(Math.cos(a)*rr,Math.sin(a)*rr)}ctx.closePath();ctx.fill();ctx.stroke();finish(ctx,s,o)}
  function satellite(ctx,s,o={}){const c=colors(s,o,'uncertainty');setup(ctx,s,o);ctx.fillStyle=c.fill;ctx.strokeStyle=c.outline;ctx.fillRect(-14,-11,28,22);ctx.strokeRect(-14,-11,28,22);
    ctx.fillStyle=V.token(s,'colors','electric_field','#006D77');for(const x of [-37,17]){ctx.fillRect(x,-10,20,20);ctx.strokeRect(x,-10,20,20)}ctx.beginPath();ctx.moveTo(0,-11);ctx.lineTo(0,-25);ctx.stroke();finish(ctx,s,o)}
  function projectile(ctx,s,o={}){body(ctx,s,{...o,radius:o.radius||9,shadow:o.shadow!==false},'trajectory')}
  function cannon(ctx,s,o={}){const c=colors(s,o,'uncertainty');setup(ctx,s,o);ctx.fillStyle=c.fill;ctx.strokeStyle=c.outline;ctx.beginPath();ctx.roundRect(-8,-9,o.width||58,18,6);ctx.fill();ctx.stroke();ctx.beginPath();ctx.arc(-8,8,14,0,Math.PI*2);ctx.fill();ctx.stroke();finish(ctx,s,o)}
  function fluidContainer(ctx,s,o={}){const w=o.width||130,h=o.height||150,c=colors(s,o,'text');setup(ctx,s,o);ctx.strokeStyle=c.outline;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(-w/2,-h/2);ctx.lineTo(-w/2,h/2);ctx.lineTo(w/2,h/2);ctx.lineTo(w/2,-h/2);ctx.stroke();finish(ctx,s,o)}
  function fluidSurface(ctx,s,o={}){const w=o.width||130,h=o.height||70,c=o.fill||V.token(s,'colors','electric_field','#006D77');setup(ctx,s,o);ctx.fillStyle=c;ctx.globalAlpha*=o.fluidOpacity??.26;ctx.fillRect(-w/2,0,w,h);
    ctx.globalAlpha=(o.opacity??1)*(o.disabled ? .45 : 1);ctx.strokeStyle=c;ctx.lineWidth=2;ctx.beginPath();for(let x=-w/2;x<=w/2;x+=8)ctx.lineTo(x,Math.sin(x*.16)*2);ctx.stroke();finish(ctx,s,o)}
  function lens(ctx,s,o={}){const w=o.width||30,h=o.height||120,c=colors(s,o,'electric_field');setup(ctx,s,o);ctx.fillStyle=c.fill;ctx.globalAlpha*=.24;ctx.strokeStyle=c.outline;ctx.beginPath();
    ctx.moveTo(0,-h/2);ctx.quadraticCurveTo(w,0,0,h/2);ctx.quadraticCurveTo(-w,0,0,-h/2);ctx.fill();ctx.stroke();finish(ctx,s,o)}
  function mirror(ctx,s,o={}){const h=o.height||120;setup(ctx,s,o);ctx.strokeStyle=o.outline||V.token(s,'colors','text','#152536');ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(0,-h/2);ctx.lineTo(0,h/2);ctx.stroke();
    ctx.lineWidth=1;for(let y=-h/2;y<h/2;y+=10){ctx.beginPath();ctx.moveTo(3,y);ctx.lineTo(11,y+8);ctx.stroke()}finish(ctx,s,o)}
  function ray(ctx,s,o={}){V.arrow(ctx,s,point(o.x,o.y),o.end||point(o.x+(o.width||100),o.y),{...o,color:o.fill||V.token(s,'colors','energy','#B45309'),width:o.lineWidth||2,head:o.head||9})}
  function wavefront(ctx,s,o={}){setup(ctx,s,o);ctx.strokeStyle=o.outline||V.token(s,'colors','trajectory','#1769AA');ctx.lineWidth=o.lineWidth||2;ctx.globalAlpha*=o.opacity??.7;
    const count=o.count||3,spacing=o.spacing||18;for(let i=1;i<=count;i++){ctx.beginPath();ctx.arc(0,0,(o.radius||20)+i*spacing,o.startAngle??-.8,o.endAngle??.8);ctx.stroke()}finish(ctx,s,o)}
  function charge(ctx,s,o={}){const positive=(o.sign??1)>=0;body(ctx,s,{...o,fill:o.fill||V.token(s,'colors',positive?'net_force':'accent',positive?'#C2410C':'#1769AA'),label:''},positive?'net_force':'accent');
    ctx.save();V.applyText(ctx,s,'heading');ctx.fillStyle=V.token(s,'colors','text_inverse','#FFF');ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(positive?'+':'−',o.x,o.y);ctx.restore();if(o.label)finish(ctx,s,{...o,shadow:false})}
  function fieldLine(ctx,s,o={}){const pts=o.points||[point(o.x,o.y),o.end||point(o.x+(o.width||100),o.y)];ctx.save();ctx.strokeStyle=o.outline||V.token(s,'colors','electric_field','#006D77');ctx.lineWidth=o.lineWidth||1.5;ctx.globalAlpha=o.opacity??.75;
    ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.stroke();if(o.direction!==false&&pts.length>1){const i=Math.floor(pts.length/2),a=pts[Math.max(0,i-1)],b=pts[i];V.arrow(ctx,s,a,b,{color:ctx.strokeStyle,width:1.5,head:7})}ctx.restore()}
  function semanticArrow(role){return (ctx,s,o={})=>{const end=o.end||point(o.x+(o.width||80),o.y),dx=end.x-o.x,dy=-(end.y-o.y);
    PhysicsAnnotations.vector(ctx,s,{...o,role,dx,dy,scale_mode:o.scale_mode||'schematic',fixed_length_px:o.fixed_length_px||Math.hypot(dx,dy),scale_disclosure:o.scale_disclosure},1,o.show_disclosure!==false)}}
  const forceArrow=semanticArrow('net_force'),velocityArrow=semanticArrow('velocity'),accelerationArrow=semanticArrow('acceleration');
  function torqueArc(ctx,s,o={}){const r=o.radius||42,start=o.startAngle??-.8,end=o.endAngle??2.8,color=o.fill||V.token(s,'colors','net_force','#C2410C');ctx.save();ctx.strokeStyle=color;ctx.lineWidth=o.lineWidth||3;ctx.beginPath();ctx.arc(o.x,o.y,r,start,end,o.counterclockwise||false);ctx.stroke();
    const a=end,tip=point(o.x+Math.cos(a)*r,o.y+Math.sin(a)*r),back=point(o.x+Math.cos(a-.14)*r,o.y+Math.sin(a-.14)*r);V.arrow(ctx,s,back,tip,{color,width:3,head:10,label:o.label});ctx.restore()}
  function angleMarker(ctx,s,o={}){ctx.save();ctx.strokeStyle=o.outline||V.token(s,'colors','accent','#1769AA');ctx.lineWidth=2;ctx.beginPath();ctx.arc(o.x,o.y,o.radius||28,o.startAngle||0,o.endAngle??Math.PI/4);ctx.stroke();
    if(o.label){V.applyText(ctx,s,'annotation');const a=((o.startAngle||0)+(o.endAngle??Math.PI/4))/2;ctx.fillText(o.label,o.x+Math.cos(a)*(o.radius+12),o.y+Math.sin(a)*(o.radius+12))}ctx.restore()}
  function ruler(ctx,s,o={}){const length=o.width||160,div=o.divisions||10;ctx.save();ctx.translate(o.x,o.y);ctx.rotate(o.rotation||0);ctx.strokeStyle=o.outline||V.token(s,'colors','text_muted','#526577');ctx.fillStyle=ctx.strokeStyle;ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(length,0);ctx.stroke();V.applyText(ctx,s,'axis');
    for(let i=0;i<=div;i++){const x=i/div*length,h=i%5===0?10:6;ctx.beginPath();ctx.moveTo(x,-h/2);ctx.lineTo(x,h/2);ctx.stroke();if(o.showValues&&i%5===0)ctx.fillText(String(i/div*(o.maximum??length)),x-4,20)}ctx.restore()}
  function grid(ctx,s,o={}){V.grid(ctx,s,{x:o.x,y:o.y,width:o.width||200,height:o.height||160},{step:o.step,opacity:o.opacity})}
  function trail(ctx,s,o={}){V.trail(ctx,s,o.points||[],p=>p,{color:o.fill,width:o.lineWidth,opacity:o.opacity,dashed:o.dashed})}
  function collisionFlash(ctx,s,o={}){const r=o.radius||36,progress=o.progress??1;ctx.save();ctx.translate(o.x,o.y);ctx.rotate(o.rotation||0);ctx.fillStyle=o.fill||V.token(s,'colors','warning','#9A5B00');ctx.globalAlpha=(o.opacity??1)*(1-progress*.65);ctx.beginPath();
    for(let i=0;i<16;i++){const a=i*Math.PI/8,rr=i%2?r*progress:r*.42*progress;ctx.lineTo(Math.cos(a)*rr,Math.sin(a)*rr)}ctx.closePath();ctx.fill();ctx.restore()}
  function callout(ctx,s,o={}){const w=o.width||180,h=o.height||62,x=o.x,y=o.y;ctx.save();ctx.shadowColor='rgba(15,23,42,.14)';ctx.shadowBlur=o.shadow===false?0:10;ctx.shadowOffsetY=3;
    ctx.fillStyle=o.fill||V.token(s,'colors','surface_raised','#FFF');ctx.strokeStyle=o.outline||V.token(s,'colors','border','#B8C5D1');ctx.lineWidth=1.5;ctx.beginPath();ctx.roundRect(x,y,w,h,12);ctx.fill();ctx.stroke();ctx.shadowColor='transparent';
    if(o.target){ctx.beginPath();ctx.moveTo(x+w*.2,y+h);ctx.lineTo(o.target.x,o.target.y);ctx.stroke()}V.applyText(ctx,s,'annotation');ctx.fillStyle=V.token(s,'colors','text','#152536');
    const lines=String(o.text||o.label||'').split('\n');lines.slice(0,3).forEach((line,i)=>ctx.fillText(line,x+12,y+22+i*17));ctx.restore()}
  const library={sphere,mass,block,cart,pendulumBob,pivot,cable,rod,spring,ramp,pulley,lever,wheel,planet,moon,star,satellite,projectile,cannon,
    fluidContainer,fluidSurface,lens,mirror,ray,wavefront,charge,fieldLine,forceArrow,velocityArrow,accelerationArrow,torqueArc,angleMarker,ruler,grid,trail,collisionFlash,callout};
  function draw(ctx,s,spec){const fn=library[spec.kind];if(!fn)throw new Error(`Unknown Physics Studio asset: ${spec.kind}`);fn(ctx,s,{...spec,...(spec.style||{}),...(spec.options||{})})}
  function drawAll(ctx,s,specs){for(const spec of specs||[])draw(ctx,s,spec)}
  return {...library,draw,drawAll,kinds:Object.freeze(Object.keys(library))};
})();
"""
