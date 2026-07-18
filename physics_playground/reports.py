"""Simulation-independent lab-report models, builder, and export renderers."""

from __future__ import annotations

import base64
import csv
import html
from collections.abc import Mapping
from dataclasses import dataclass
from io import BytesIO, StringIO
from typing import Protocol

import matplotlib.pyplot as plt

from physics_playground.model_metadata import MODEL_METADATA
from physics_playground.notebook import ExperimentNotebook, TrialRecord
from physics_playground.registry import SIMULATIONS_BY_ID
from physics_playground.serialization import dumps

# Compatibility mapping for callers that previously imported ASSUMPTIONS.
ASSUMPTIONS = {key: value.assumption_statements for key, value in MODEL_METADATA.items()}


@dataclass(frozen=True, slots=True)
class ReportTrial:
    trial_number: int
    prediction: str | None
    parameters: Mapping[str, object]
    model_used: str
    result_summary: str
    measurements: Mapping[str, float]
    earned_badges: tuple[str, ...]
    learner_observation: str | None


@dataclass(frozen=True, slots=True)
class LabReport:
    scientist_name: str
    simulation_id: str
    simulation_title: str
    question: str
    trials: tuple[ReportTrial, ...]
    changed_parameters: Mapping[str, tuple[object, object]]
    measurement_deltas: Mapping[str, float]
    assumptions: tuple[str, ...]
    conclusion_prompt: str
    chart_svg_base64: str


@dataclass(frozen=True, slots=True)
class ReportBundle:
    report: LabReport
    html: str
    markdown: str
    csv: str
    json: str


class ReportRenderer(Protocol):
    def render(self, report: LabReport) -> str: ...


def _chart(trials: tuple[TrialRecord, ...]) -> str:
    names = sorted({name for trial in trials for name in trial.metrics})[:10]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    width = 0.8 / max(1, len(trials))
    positions = list(range(len(names)))
    colors = ("#0072B2", "#D55E00", "#009E73", "#CC79A7")
    hatches = ("//", "\\\\", "xx", "..")
    for index, trial in enumerate(trials):
        values = [trial.metrics.get(name, 0) for name in names]
        offset = (index - (len(trials) - 1) / 2) * width
        ax.bar(
            [x + offset for x in positions],
            values,
            width,
            label=f"Trial {trial.trial_number}",
            color=colors[index % len(colors)],
            hatch=hatches[index % len(hatches)],
            edgecolor="black",
        )
    ax.set_xticks(positions, names, rotation=30, ha="right")
    ax.set_ylabel("Stored measurement value")
    ax.set_title("Important measurements by trial")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    output = BytesIO()
    fig.savefig(
        output, format="svg", metadata={"Title": "Important measurements by selected trial"}
    )
    plt.close(fig)
    return base64.b64encode(output.getvalue()).decode("ascii")


def build_report(
    notebook: ExperimentNotebook, trial_ids: list[str], scientist_name: str
) -> LabReport:
    if not trial_ids:
        raise ValueError("Select at least one trial.")
    trials = tuple(notebook.get(item) for item in trial_ids)
    simulation_ids = {item.simulation_id for item in trials}
    if len(simulation_ids) != 1:
        raise ValueError("A lab report must contain trials from one simulation.")
    simulation_id = trials[0].simulation_id
    definition = SIMULATIONS_BY_ID[simulation_id]
    changed = {}
    deltas = {}
    if len(trials) >= 2:
        comparison = notebook.compare(trials[0].id, trials[-1].id)
        changed = dict(comparison.changed_parameters)
        deltas = dict(comparison.metric_deltas)
    report_trials = tuple(
        ReportTrial(
            t.trial_number,
            t.prediction,
            dict(t.parameters),
            t.model_version,
            t.result_summary,
            dict(t.metrics),
            t.earned_badges,
            t.learner_observation,
        )
        for t in trials
    )
    return LabReport(
        scientist_name.strip() or "Scientist",
        simulation_id,
        definition.title,
        definition.central_question,
        report_trials,
        changed,
        deltas,
        ASSUMPTIONS.get(simulation_id, ()),
        "What conclusion does the evidence support? Explain how the changed variables affected the outcome and identify one limitation of the model.",
        _chart(trials),
    )


def _table_rows(mapping):
    return "\n".join(f"| {key} | {value} |" for key, value in mapping.items()) or "| — | None |"


class MarkdownRenderer:
    def render(self, r):
        sections = [
            f"# Lab Report: {r.simulation_title}",
            f"**Scientist:** {r.scientist_name}",
            f"## Question\n{r.question}",
        ]
        for t in r.trials:
            sections.extend(
                (
                    f"## Trial {t.trial_number}",
                    f"**Prediction:** {t.prediction or 'Not recorded'}",
                    f"**Model:** {t.model_used}",
                    "### Parameters\n| Parameter | Value |\n|---|---|\n"
                    + _table_rows(t.parameters),
                    f"### Result summary\n{t.result_summary}",
                    "### Important measurements\n| Measurement | Value |\n|---|---:|\n"
                    + _table_rows(t.measurements),
                    f"**Earned badges:** {', '.join(t.earned_badges) or 'None'}",
                    f"**Observation:** {t.learner_observation or 'Not recorded'}",
                )
            )
        if r.changed_parameters:
            sections.append(
                "## Comparison between trials\n### Changed parameters\n"
                + "\n".join(f"- **{k}:** {a} → {b}" for k, (a, b) in r.changed_parameters.items())
                + "\n### Measurement changes\n"
                + "\n".join(f"- **{k}:** {v:+.4g}" for k, v in r.measurement_deltas.items())
            )
        sections.extend(
            (
                "## Measurement chart",
                f"![Important measurements](data:image/svg+xml;base64,{r.chart_svg_base64})",
                "## Model assumptions\n" + "\n".join(f"- {item}" for item in r.assumptions),
                f"## Conclusion prompt\n{r.conclusion_prompt}",
            )
        )
        return "\n\n".join(sections) + "\n"


class HtmlRenderer:
    def render(self, r):
        trial_html = ""
        for t in r.trials:
            rows = "".join(
                f"<tr><th>{html.escape(str(k))}</th><td>{html.escape(str(v))}</td></tr>"
                for k, v in t.parameters.items()
            )
            metrics = "".join(
                f"<tr><th>{html.escape(str(k))}</th><td>{v:.6g}</td></tr>"
                for k, v in t.measurements.items()
            )
            trial_html += f"<section><h2>Trial {t.trial_number}</h2><p><strong>Prediction:</strong> {html.escape(t.prediction or 'Not recorded')}</p><p><strong>Model:</strong> {html.escape(t.model_used)}</p><h3>Parameters</h3><table>{rows}</table><h3>Result</h3><p>{html.escape(t.result_summary)}</p><h3>Measurements</h3><table>{metrics}</table><p><strong>Badges:</strong> {html.escape(', '.join(t.earned_badges) or 'None')}</p><p><strong>Observation:</strong> {html.escape(t.learner_observation or 'Not recorded')}</p></section>"
        comparison = ""
        if r.changed_parameters:
            comparison = (
                "<section><h2>Comparison between trials</h2><ul>"
                + "".join(
                    f"<li><strong>{html.escape(k)}</strong>: {html.escape(str(a))} → {html.escape(str(b))}</li>"
                    for k, (a, b) in r.changed_parameters.items()
                )
                + "</ul></section>"
            )
        assumptions = "".join(f"<li>{html.escape(item)}</li>" for item in r.assumptions)
        return f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{html.escape(r.simulation_title)} Lab Report</title><style>body{{font-family:Arial,sans-serif;max-width:900px;margin:auto;padding:24px;color:#111}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #555;padding:7px;text-align:left}}img{{max-width:100%}}@media print{{button{{display:none}}body{{padding:0}}section{{break-inside:avoid}}}}</style></head><body><button onclick='window.print()'>Print report</button><h1>{html.escape(r.simulation_title)} Lab Report</h1><p><strong>Scientist:</strong> {html.escape(r.scientist_name)}</p><h2>Question</h2><p>{html.escape(r.question)}</p>{trial_html}{comparison}<section><h2>Important measurements chart</h2><img alt='Bar chart comparing important stored measurements across selected trials' src='data:image/svg+xml;base64,{r.chart_svg_base64}'></section><section><h2>Model assumptions</h2><ul>{assumptions}</ul></section><section><h2>Conclusion prompt</h2><p>{html.escape(r.conclusion_prompt)}</p></section></body></html>"


class CsvRenderer:
    def render(self, r):
        params = sorted({k for t in r.trials for k in t.parameters})
        metrics = sorted({k for t in r.trials for k in t.measurements})
        fields = (
            [
                "scientist",
                "simulation",
                "question",
                "trial",
                "prediction",
                "model",
                "result",
                "badges",
                "observation",
            ]
            + [f"parameter.{k}" for k in params]
            + [f"measurement.{k}" for k in metrics]
        )
        out = StringIO()
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        for t in r.trials:
            row = {
                "scientist": r.scientist_name,
                "simulation": r.simulation_title,
                "question": r.question,
                "trial": t.trial_number,
                "prediction": t.prediction or "",
                "model": t.model_used,
                "result": t.result_summary,
                "badges": ";".join(t.earned_badges),
                "observation": t.learner_observation or "",
            }
            row.update({f"parameter.{k}": t.parameters.get(k, "") for k in params})
            row.update({f"measurement.{k}": t.measurements.get(k, "") for k in metrics})
            writer.writerow(row)
        return out.getvalue()


class JsonRenderer:
    def render(self, r):
        return dumps(r, indent=2)


def generate_report_bundle(notebook, trial_ids, scientist_name):
    report = build_report(notebook, trial_ids, scientist_name)
    return ReportBundle(
        report,
        HtmlRenderer().render(report),
        MarkdownRenderer().render(report),
        CsvRenderer().render(report),
        JsonRenderer().render(report),
    )
