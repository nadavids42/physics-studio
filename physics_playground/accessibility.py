"""Shared accessibility preferences and rendering utilities."""
from dataclasses import asdict,dataclass
@dataclass(frozen=True,slots=True)
class AccessibilitySettings:
    reduced_motion:bool=False
    high_contrast:bool=False
    large_text:bool=False
    def to_dict(self):return asdict(self)
    @classmethod
    def from_dict(cls,data):return cls(bool(data.get("reduced_motion",False)),bool(data.get("high_contrast",False)),bool(data.get("large_text",False)))
