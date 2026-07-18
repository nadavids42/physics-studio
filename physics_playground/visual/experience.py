"""Presentation-level contracts, preferences, and optional contextual layers."""

from dataclasses import dataclass
from enum import StrEnum


class PresentationLevel(StrEnum):
    DIAGRAM = "diagram"
    ILLUSTRATED = "illustrated"
    CONTEXTUAL = "contextual"


class VisualTheme(StrEnum):
    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"


DEFAULT_PRESENTATION_LEVEL = PresentationLevel.ILLUSTRATED


@dataclass(frozen=True, slots=True)
class VisualPreferences:
    presentation_level: PresentationLevel = DEFAULT_PRESENTATION_LEVEL
    theme: VisualTheme = VisualTheme.AUTO

    def to_dict(self) -> dict[str, str]:
        return {"presentation_level": self.presentation_level.value, "theme": self.theme.value}

    @classmethod
    def from_dict(cls, data):
        data = data or {}
        try:
            level = PresentationLevel(
                data.get("presentation_level", DEFAULT_PRESENTATION_LEVEL.value)
            )
        except (ValueError, TypeError):
            level = DEFAULT_PRESENTATION_LEVEL
        try:
            theme = VisualTheme(data.get("theme", VisualTheme.AUTO.value))
        except (ValueError, TypeError):
            theme = VisualTheme.AUTO
        return cls(level, theme)


@dataclass(frozen=True, slots=True)
class ExperienceProfile:
    level: PresentationLevel
    depth: bool
    environment: bool
    decorative_detail: bool
    preserve_scientific_overlays: bool = True


EXPERIENCE_PROFILES = {
    PresentationLevel.DIAGRAM: ExperienceProfile(PresentationLevel.DIAGRAM, False, False, False),
    PresentationLevel.ILLUSTRATED: ExperienceProfile(
        PresentationLevel.ILLUSTRATED, True, False, True
    ),
    PresentationLevel.CONTEXTUAL: ExperienceProfile(PresentationLevel.CONTEXTUAL, True, True, True),
}


CANVAS_EXPERIENCE_JS = r"""
const PhysicsExperience=(()=>{
  function level(s){return s.config.presentationLevel||'illustrated'}
  function profile(s){const name=level(s);return {level:name,depth:name!=='diagram',environment:name==='contextual',decorativeDetail:name!=='diagram',preserveScientificOverlays:true}}
  function context(ctx,s,kind){const mode=profile(s),w=s.transform.width,h=s.transform.height;PhysicsVisuals.background(ctx,s,{color:PhysicsVisuals.token(s,'colors',mode.level==='diagram'?'surface':'canvas','#F7FAFC')});
    if(!mode.environment)return mode;ctx.save();
    if(kind==='projectileField'){const horizon=h*.7,g=ctx.createLinearGradient(0,0,0,horizon);g.addColorStop(0,'#B9DDF3');g.addColorStop(1,'#EDF7FC');ctx.fillStyle=g;ctx.fillRect(0,0,w,horizon);
      ctx.fillStyle='#A7C98B';ctx.fillRect(0,horizon,w,h-horizon);ctx.strokeStyle='rgba(255,255,255,.72)';ctx.lineWidth=2;for(let x=0;x<w;x+=70){ctx.beginPath();ctx.moveTo(x,horizon);ctx.lineTo(x,h);ctx.stroke()}}
    else if(kind==='laboratory'){ctx.fillStyle=PhysicsVisuals.token(s,'colors','surface_muted','#EAF0F6');ctx.fillRect(0,0,w,h);ctx.strokeStyle=PhysicsVisuals.token(s,'colors','grid','#526577');ctx.globalAlpha=.12;
      for(let x=0;x<w;x+=48){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke()}ctx.globalAlpha=1;ctx.fillStyle=PhysicsVisuals.token(s,'colors','surface_raised','#FFF');ctx.fillRect(0,h*.8,w,h*.2)}
    else if(kind==='space'){const g=ctx.createRadialGradient(w*.5,h*.48,5,w*.5,h*.48,Math.max(w,h)*.7);g.addColorStop(0,'#182C4A');g.addColorStop(1,'#07101F');ctx.fillStyle=g;ctx.fillRect(0,0,w,h);
      ctx.fillStyle='rgba(255,255,255,.7)';for(let i=0;i<36;i++){const x=(i*83)%w,y=(i*i*29+17)%h,r=i%7===0?1.5:.7;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill()}}
    else if(kind==='opticsBench'){ctx.fillStyle='#EEF3F7';ctx.fillRect(0,0,w,h);ctx.fillStyle='#A9B6C2';ctx.fillRect(0,h*.76,w,12);ctx.strokeStyle='#738394';ctx.lineWidth=2;for(let x=30;x<w;x+=45){ctx.beginPath();ctx.moveTo(x,h*.76);ctx.lineTo(x,h*.82);ctx.stroke()}}
    else if(kind==='rollerCoaster'){const g=ctx.createLinearGradient(0,0,0,h);g.addColorStop(0,'#C9E6F7');g.addColorStop(1,'#F6FAFC');ctx.fillStyle=g;ctx.fillRect(0,0,w,h);ctx.fillStyle='#B7D59B';ctx.fillRect(0,h*.72,w,h*.28)}
    else if(kind==='collisionTrack'){ctx.fillStyle='#F2E8DC';ctx.fillRect(0,0,w,h);ctx.fillStyle='#73655B';ctx.fillRect(0,h*.72,w,h*.28);ctx.strokeStyle='rgba(255,255,255,.65)';ctx.lineWidth=3;ctx.setLineDash([14,10]);ctx.beginPath();ctx.moveTo(0,h*.86);ctx.lineTo(w,h*.86);ctx.stroke();ctx.setLineDash([])}
    ctx.restore();return mode}
  function scientificOverlay(ctx,s,draw){ctx.save();draw();ctx.restore()}
  return {level,profile,context,scientificOverlay};
})();
"""
