"""Renderer-neutral ray geometry shared by geometric-optics simulations."""
from dataclasses import dataclass
@dataclass(frozen=True,slots=True)
class RaySegment:
    x1:float;y1:float;x2:float;y2:float;label:str;kind:str="ray"
    def to_dict(self):return {"x1":self.x1,"y1":self.y1,"x2":self.x2,"y2":self.y2,"label":self.label,"kind":self.kind}
