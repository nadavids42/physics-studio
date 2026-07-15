import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from physics_playground.contracts import PlotData
from physics_playground.models.spring import resonance_sweep


def plot_figure(plot:PlotData,overlays:tuple[PlotData,...]=())->Figure:
    fig,ax=plt.subplots()
    for item in (plot,*overlays):
        for series in item.series:ax.plot(series.x,series.y,label=series.label)
    ax.set_xlabel(plot.x_label);ax.set_ylabel(plot.y_label);ax.set_title(plot.title);ax.grid(True)
    if overlays:ax.legend()
    return fig


def resonance_figure(mass:float,stiffness:float,damping:float,drive_force:float)->Figure:
    ratios,amplitudes=resonance_sweep(mass,stiffness,damping,drive_force)
    fig,ax=plt.subplots();ax.plot(ratios,amplitudes);ax.axvline(1,color="crimson",linestyle="--",label="Natural frequency")
    ax.set_xlabel("Driving frequency ÷ natural frequency");ax.set_ylabel("Late response amplitude (m)");ax.set_title("Resonance response");ax.grid(True);ax.legend();return fig
