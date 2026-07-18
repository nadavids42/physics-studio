"""Shared JavaScript primitives for model-driven scientific illustration."""

CANVAS_VISUAL_JS = r"""
const PhysicsVisuals=(()=>{
  const token=(s,group,name,fallback)=>s.config.visualTokens?.[group]?.[name]??fallback;
  function applyText(ctx,s,role='label'){
    const type=s.config.visualTokens?.typography||{},sizes={heading:type.heading_small||19,label:type.label||14,
      annotation:type.annotation||13,helper:type.helper||12,axis:type.graph_axis||12,tooltip:type.tooltip||13};
    const weight=role==='heading'?(type.weight_semibold||650):(role==='label'?(type.weight_medium||550):(type.weight_regular||400));
    ctx.font=`${weight} ${sizes[role]||sizes.label}px ${type.family_ui||'system-ui, sans-serif'}`;
    ctx.fillStyle=token(s,'colors','text','#152536');ctx.textBaseline='alphabetic';
  }
  function background(ctx,s,options={}){const {width,height}=s.transform;ctx.clearRect(0,0,width,height);
    ctx.fillStyle=options.color||token(s,'colors','canvas','#F7FAFC');ctx.fillRect(0,0,width,height);}
  function roundedPanel(ctx,s,x,y,w,h,options={}){const radius=options.radius??token(s,'shape','radius_large',16);
    ctx.beginPath();ctx.roundRect(x,y,w,h,radius);ctx.fillStyle=options.fill||token(s,'colors','surface','#FFF');ctx.fill();
    ctx.strokeStyle=options.stroke||token(s,'colors','border','#B8C5D1');ctx.lineWidth=options.lineWidth||token(s,'shape','line_regular',1.5);ctx.stroke();}
  function arrow(ctx,s,from,to,options={}){const color=options.color||token(s,'colors',options.role||'net_force','#C2410C'),
    width=options.width||token(s,'shape','line_vector',3),angle=Math.atan2(to.y-from.y,to.x-from.x),head=options.head||Math.max(9,width*4);
    ctx.save();ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=width;ctx.lineCap='round';ctx.lineJoin='round';
    if(options.dashed)ctx.setLineDash([7,5]);ctx.beginPath();ctx.moveTo(from.x,from.y);ctx.lineTo(to.x,to.y);ctx.stroke();
    ctx.setLineDash([]);ctx.beginPath();ctx.moveTo(to.x,to.y);ctx.lineTo(to.x-head*Math.cos(angle-.45),to.y-head*Math.sin(angle-.45));
    ctx.lineTo(to.x-head*Math.cos(angle+.45),to.y-head*Math.sin(angle+.45));ctx.closePath();ctx.fill();
    if(options.label){applyText(ctx,s,'label');ctx.fillStyle=color;ctx.fillText(options.label,to.x+(options.labelDx??8),to.y+(options.labelDy??-8));}ctx.restore();}
  function grid(ctx,s,box,options={}){const step=options.step||40;ctx.save();ctx.strokeStyle=options.color||token(s,'colors','grid','#526577');
    ctx.globalAlpha=options.opacity??token(s,'shape','grid_opacity',.16);ctx.lineWidth=token(s,'shape','line_hairline',1);ctx.beginPath();
    for(let x=box.x;x<=box.x+box.width;x+=step){ctx.moveTo(x,box.y);ctx.lineTo(x,box.y+box.height)}
    for(let y=box.y;y<=box.y+box.height;y+=step){ctx.moveTo(box.x,y);ctx.lineTo(box.x+box.width,y)}ctx.stroke();ctx.restore();}
  function trail(ctx,s,points,map,options={}){if(points.length<2)return;ctx.save();ctx.strokeStyle=options.color||token(s,'colors','trajectory','#1769AA');
    ctx.lineWidth=options.width||token(s,'shape','line_regular',1.5);ctx.lineCap='round';ctx.globalAlpha=options.opacity??token(s,'shape','trail_opacity',.24);
    if(options.dashed)ctx.setLineDash([7,5]);ctx.beginPath();points.forEach((p,i)=>{const q=map(p);i?ctx.lineTo(q.x,q.y):ctx.moveTo(q.x,q.y)});ctx.stroke();ctx.restore();}
  function responsive(s){const w=s.transform.width,r=s.config.visualTokens?.responsive||{};return w<=(r.mobile_max_px||480)?'mobile':w<=(r.tablet_max_px||820)?'tablet':'desktop';}
  return {token,applyText,background,roundedPanel,arrow,grid,trail,responsive};
})();
"""
