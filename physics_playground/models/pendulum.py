"""Pure small-angle and nonlinear simple-pendulum models."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from enum import StrEnum
import math
import numpy as np
from physics_playground.contracts import AnimationData,AnimationKind,AnimationTrack,ContractResult,EventKind,ModelAssumption,PlotData,PlotKind,PlotSeries,SimulationEvent,SummaryMetric
from physics_playground.serialization import to_jsonable
from physics_playground.validation import PhysicsValidationError,require_positive
from physics_playground.performance import MAX_TRAJECTORY_SAMPLES,enforce_budget,validate_finite_parameters

class PendulumModel(StrEnum):SMALL_ANGLE="Small-angle approximation";NONLINEAR="Nonlinear pendulum"

@dataclass(frozen=True,slots=True)
class PendulumParameters:
    length_m:float
    gravity_m_s2:float
    release_angle_deg:float
    model:PendulumModel=PendulumModel.SMALL_ANGLE
    duration_periods:float=4.0
    samples:int=800
    def validate(self):
        validate_finite_parameters(self)
        require_positive("Rope length",self.length_m);require_positive("Gravity",self.gravity_m_s2);require_positive("Duration",self.duration_periods)
        if not 0<abs(self.release_angle_deg)<179:raise PhysicsValidationError("Release angle must be between 0° and 179°.")
        if self.samples<4:raise PhysicsValidationError("Samples must be at least 4.")
        enforce_budget("Pendulum samples",self.samples,MAX_TRAJECTORY_SAMPLES)
    @property
    def small_angle_period_s(self):return 2*math.pi*math.sqrt(self.length_m/self.gravity_m_s2)
    def to_dict(self):
        data=to_jsonable(asdict(self));data["model"]=self.model.value;return data

@dataclass(frozen=True,slots=True)
class PendulumResult(ContractResult[PendulumParameters]):
    period_s:float=0.0
    maximum_speed_m_s:float=0.0
    energy_drift_fraction:float=0.0

def nonlinear_period_series(length:float,gravity:float,angle_deg:float)->float:
    """Large-angle period series through theta^6; accurate for playground angles."""
    t=math.radians(angle_deg);ratio=1+t*t/16+11*t**4/3072+173*t**6/737280
    return 2*math.pi*math.sqrt(length/gravity)*ratio

def _result(p,t,theta,omega,period,method):
    x=p.length_m*np.sin(theta);y=-p.length_m*np.cos(theta);speed=np.abs(p.length_m*omega)
    energy=.5*(p.length_m*omega)**2+p.gravity_m_s2*p.length_m*(1-np.cos(theta));e0=max(abs(float(energy[0])),1e-12);drift=float(np.max(np.abs(energy-energy[0]))/e0)
    plots=(PlotData("angle_time","Angle versus time","Time (s)","Angle (degrees)",(PlotSeries("angle",method,tuple(t),tuple(np.degrees(theta))),)),
        PlotData("angular_velocity_time","Angular velocity versus time","Time (s)","Angular velocity (rad/s)",(PlotSeries("omega","ω(t)",tuple(t),tuple(omega)),)),
        PlotData("energy_time","Mechanical energy versus time","Time (s)","Energy per unit mass (J/kg)",(PlotSeries("energy","E(t)",tuple(t),tuple(energy)),)),
        PlotData("phase_space","Pendulum phase space","Angle (rad)","Angular velocity (rad/s)",(PlotSeries("phase","(θ,ω)",tuple(theta),tuple(omega)),),PlotKind.PHASE))
    return PendulumResult(simulation_id="pendulum",parameters=p,metrics=(SummaryMetric("period","Period",period,"s",f"{period:.2f} s"),
        SummaryMetric("maximum_speed","Maximum bob speed",float(np.max(speed)),"m/s",f"{np.max(speed):.2f} m/s"),SummaryMetric("energy_drift","Energy drift",drift*100,"%",f"{drift*100:.4f}%")),
        events=(SimulationEvent("release",EventKind.START,0,"Bob released"),SimulationEvent("complete",EventKind.COMPLETION,float(t[-1]),"Pendulum trial complete")),plots=plots,
        animation=AnimationData(AnimationKind.TWO_DIMENSIONAL,tuple(t),(AnimationTrack("bob","Pendulum bob",tuple(x),tuple(y),{"color":"#66BB6A"}),),4800,
            {"length":p.length_m,"minimum":-p.length_m,"maximum":p.length_m}),
        assumptions=(ModelAssumption("point_mass","The bob is a point mass."),ModelAssumption("rigid_rope","The rope is massless, rigid, and never stretches."),ModelAssumption("no_drag","There is no air resistance or pivot friction.")),
        period_s=period,maximum_speed_m_s=float(np.max(speed)),energy_drift_fraction=drift)

def simulate_small_angle(p:PendulumParameters)->PendulumResult:
    p.validate();period=p.small_angle_period_s;w0=math.sqrt(p.gravity_m_s2/p.length_m);t=np.linspace(0,p.duration_periods*period,p.samples);a=math.radians(p.release_angle_deg)
    return _result(p,t,a*np.cos(w0*t),-a*w0*np.sin(w0*t),period,"Small-angle")

def simulate_nonlinear(p:PendulumParameters)->PendulumResult:
    p.validate();period=nonlinear_period_series(p.length_m,p.gravity_m_s2,p.release_angle_deg);t=np.linspace(0,p.duration_periods*period,p.samples);dt=t[1]-t[0];s=np.zeros((p.samples,2));s[0]=(math.radians(p.release_angle_deg),0)
    def rhs(q):return np.array((q[1],-(p.gravity_m_s2/p.length_m)*math.sin(q[0])))
    for i in range(1,p.samples):
        q=s[i-1];k1=rhs(q);k2=rhs(q+dt*k1/2);k3=rhs(q+dt*k2/2);k4=rhs(q+dt*k3);s[i]=q+dt*(k1+2*k2+2*k3+k4)/6
    return _result(p,t,s[:,0],s[:,1],period,"Nonlinear RK4")

def simulate_pendulum(p:PendulumParameters)->PendulumResult:
    return simulate_small_angle(p) if p.model==PendulumModel.SMALL_ANGLE else simulate_nonlinear(p)

def approximation_error_curve(length:float,gravity:float,max_angle:int=85):
    angles=tuple(range(1,max_angle+1));t0=2*math.pi*math.sqrt(length/gravity);errors=tuple((nonlinear_period_series(length,gravity,a)/t0-1)*100 for a in angles);return angles,errors
