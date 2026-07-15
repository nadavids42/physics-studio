from physics_playground.contracts import MissionEvaluation
from .physics import DiffusionResult,WalkDimension

def evaluate(r:DiffusionResult,comparison:bool=False)->tuple[MissionEvaluation,...]:
    return (
        MissionEvaluation("diffusion_unbiased",abs(r.parameters.bias_x)<1e-12 and abs(r.parameters.bias_y)<1e-12,"Ran an unbiased walk"),
        MissionEvaluation("diffusion_two_d",r.parameters.dimensions==WalkDimension.TWO_D,"Ran a two-dimensional walk"),
        MissionEvaluation("diffusion_bias",abs(r.parameters.bias_x)>.1 or abs(r.parameters.bias_y)>.1,"Created directed drift"),
        MissionEvaluation("diffusion_compare",comparison,"Compared drift and diffusion"),
    )
