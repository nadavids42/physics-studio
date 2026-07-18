"""Shared chart styling for analysis views across simulation families."""
from __future__ import annotations
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from physics_playground.visual.experience import PresentationLevel
from physics_playground.visual.tokens import LIGHT_THEME,SHAPE,TYPOGRAPHY


def style_figure(figure:Figure,level:PresentationLevel=PresentationLevel.ILLUSTRATED)->Figure:
    """Apply the scientific visual language without changing plotted data."""
    background=LIGHT_THEME.surface if level is PresentationLevel.DIAGRAM else LIGHT_THEME.canvas
    figure.patch.set_facecolor(background)
    for axis in figure.axes:
        axis.set_facecolor(LIGHT_THEME.surface)
        axis.title.set_color(LIGHT_THEME.text);axis.title.set_fontsize(TYPOGRAPHY.heading_small);axis.title.set_fontweight(TYPOGRAPHY.weight_semibold)
        axis.xaxis.label.set_color(LIGHT_THEME.text);axis.yaxis.label.set_color(LIGHT_THEME.text)
        axis.tick_params(colors=LIGHT_THEME.text_muted,labelsize=TYPOGRAPHY.graph_axis)
        for spine in axis.spines.values():spine.set_color(LIGHT_THEME.border);spine.set_linewidth(SHAPE.line_hairline)
        axis.grid(True,color=LIGHT_THEME.grid,alpha=SHAPE.grid_opacity,linewidth=SHAPE.line_hairline)
        legend=axis.get_legend()
        if legend:
            legend.get_frame().set_facecolor(LIGHT_THEME.surface_raised);legend.get_frame().set_edgecolor(LIGHT_THEME.border)
            for text in legend.get_texts():text.set_color(LIGHT_THEME.text)
    figure.tight_layout();return figure


def series_figure(*,x:list[float],series:dict[str,list[float]],x_label:str,y_label:str,title:str)->Figure:
    figure,axis=plt.subplots()
    for label,values in series.items():axis.plot(x,values,label=label)
    axis.set_xlabel(x_label);axis.set_ylabel(y_label);axis.set_title(title)
    if len(series)>1:axis.legend()
    return style_figure(figure)
