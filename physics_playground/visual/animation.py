"""Browser-side presentation helpers for immutable simulation trajectories."""

CANVAS_ANIMATION_JS = r"""
const PhysicsAnimation=(()=>{
  const clamp=(value,min,max)=>Math.min(max,Math.max(min,value));
  const smoothstep=t=>{t=clamp(t,0,1);return t*t*(3-2*t)};
  class Camera {
    constructor(config={},reducedMotion=false){this.reducedMotion=reducedMotion;this.current={x:0,y:0,zoom:1};this.start={...this.current};this.target={...this.current};this.elapsed=0;this.duration=0;this.configure(config)}
    configure(config={}){this.current={x:config.x||0,y:config.y||0,zoom:config.zoom||1};this.start={...this.current};this.target={...this.current}}
    focus(target={},durationMs=320){this.start={...this.current};this.target={x:target.x??this.current.x,y:target.y??this.current.y,zoom:clamp(target.zoom??this.current.zoom,.25,8)};
      this.elapsed=0;this.duration=this.reducedMotion?0:Math.max(0,durationMs)/1000;if(!this.duration)this.current={...this.target}}
    update(seconds){if(!this.duration)return;this.elapsed=Math.min(this.duration,this.elapsed+seconds);const t=smoothstep(this.elapsed/this.duration);
      for(const key of ['x','y','zoom'])this.current[key]=this.start[key]+(this.target[key]-this.start[key])*t}
    apply(ctx,width,height){ctx.translate(width/2,height/2);ctx.scale(this.current.zoom,this.current.zoom);ctx.translate(-width/2-this.current.x,-height/2-this.current.y)}
    reset(){this.focus({x:0,y:0,zoom:1},0)}
  }
  function withCamera(ctx,camera,width,height,draw){ctx.save();camera.apply(ctx,width,height);draw();ctx.restore()}
  function fadingTrail(ctx,points,map,options={}){if(points.length<2)return;ctx.save();ctx.lineCap='round';ctx.lineJoin='round';
    for(let i=1;i<points.length;i++){const a=map(points[i-1]),b=map(points[i]),t=i/(points.length-1);ctx.globalAlpha=(options.opacity??.3)*t*t;ctx.strokeStyle=options.color||'#1769AA';ctx.lineWidth=(options.width||2)*(.55+.45*t);
      ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke()}ctx.restore()}
  function subtleMotionBlur(ctx,positions,draw,options={}){const reduced=options.reducedMotion||false,count=reduced?0:Math.min(options.samples??3,4);if(!count||positions.length<2){draw(positions.at(-1),1);return}
    const start=Math.max(0,positions.length-count-1);for(let i=start;i<positions.length-1;i++)draw(positions[i],(i-start+1)/(positions.length-start)*.12);draw(positions.at(-1),1)}
  function impactRipple(ctx,x,y,progress,options={}){if(options.reducedMotion)return;const t=clamp(progress,0,1),radius=(options.radius||46)*smoothstep(t);ctx.save();ctx.globalAlpha=(options.opacity??.5)*(1-t);
    ctx.strokeStyle=options.color||'#9A5B00';ctx.lineWidth=options.width||2;ctx.beginPath();ctx.arc(x,y,radius,0,Math.PI*2);ctx.stroke();ctx.restore()}
  function collisionFlash(ctx,x,y,progress,options={}){if(options.reducedMotion)return;PhysicsAssets.collisionFlash(ctx,{transform:{width:0,height:0},config:options.config||{}},{x,y,progress,
    radius:options.radius||34,fill:options.color,opacity:options.opacity??.8,shadow:false})}
  function focusTransition(camera,target,options={}){camera.focus(target,options.reducedMotion?0:(options.durationMs??320))}
  return {Camera,withCamera,fadingTrail,subtleMotionBlur,impactRipple,collisionFlash,focusTransition,smoothstep};
})();
"""
