const SVG_NS = "http://www.w3.org/2000/svg";
const COLORS = ["#0072B2", "#D55E00", "#00875A", "#A23B72", "#8A5A00"];
const SEMANTIC_COLORS = {
  graph_1: "#0072B2",
  graph_2: "#D55E00",
  graph_3: "#00875A",
  graph_4: "#A23B72",
  graph_5: "#8A5A00",
};
const DARK_COLORS = {
  graph_1: "#56B4E9",
  graph_2: "#FF9F68",
  graph_3: "#63D6A0",
  graph_4: "#E69AC7",
  graph_5: "#FFD166",
};
const HIGH_CONTRAST_COLORS = [
  "#56B4E9",
  "#FFB000",
  "#63D6A0",
  "#E69AC7",
  "#FFFFFF",
];
const DASHES = { solid: "", dashed: "9 6", dotted: "2 5" };

export function domain(values) {
  const low = Math.min(...values),
    high = Math.max(...values);
  return low === high ? [low - 1, high + 1] : [low, high];
}

export function nearestPoint(series, xValue) {
  let best = null;
  for (const item of series) {
    item.x.forEach((x, index) => {
      const candidate = { series: item, index, x, y: item.y[index] };
      if (!best || Math.abs(x - xValue) < Math.abs(best.x - xValue))
        best = candidate;
    });
  }
  return best;
}

export function zoomedDomain(current, center, factor) {
  const half = ((current[1] - current[0]) * factor) / 2;
  return [center - half, center + half];
}

function svgElement(name, attributes = {}) {
  const element = document.createElementNS(SVG_NS, name);
  Object.entries(attributes).forEach(([key, value]) =>
    element.setAttribute(key, value),
  );
  return element;
}

export function mountInteractiveChart(config) {
  document.body.classList.toggle(
    "high-contrast",
    Boolean(config.high_contrast),
  );
  const svg = document.getElementById("chart"),
    tableHost = document.getElementById("table"),
    tooltip = document.getElementById("tooltip"),
    reset = document.getElementById("zoom-reset");
  if (!svg || !config?.series?.length)
    throw new TypeError("Interactive chart payload is invalid.");
  const margin = { left: 72, right: 24, top: 34, bottom: 58 },
    width = 720,
    height = 390,
    allX = config.series.flatMap((item) => item.x),
    allY = config.series.flatMap((item) => item.y),
    originalX = domain(allX),
    yDomain = domain(allY);
  let xDomain = [...originalX];
  const dark =
    config.theme === "dark" ||
    (config.theme === "auto" &&
      globalThis.matchMedia?.("(prefers-color-scheme: dark)").matches);
  const draw = () => {
    svg.querySelectorAll("g.chart-data").forEach((node) => node.remove());
    const group = svgElement("g", { class: "chart-data" }),
      X = (x) =>
        margin.left +
        ((x - xDomain[0]) / (xDomain[1] - xDomain[0])) *
          (width - margin.left - margin.right),
      Y = (y) =>
        height -
        margin.bottom -
        ((y - yDomain[0]) / (yDomain[1] - yDomain[0])) *
          (height - margin.top - margin.bottom);
    for (let tick = 0; tick <= 5; tick++) {
      const x = margin.left + (tick / 5) * (width - margin.left - margin.right),
        y = margin.top + (tick / 5) * (height - margin.top - margin.bottom);
      group.append(
        svgElement("line", {
          x1: x,
          x2: x,
          y1: margin.top,
          y2: height - margin.bottom,
          class: "grid",
        }),
      );
      const xTick = svgElement("text", {
        x,
        y: height - margin.bottom + 18,
        "text-anchor": "middle",
      });
      xTick.textContent = (
        xDomain[0] +
        (tick / 5) * (xDomain[1] - xDomain[0])
      ).toPrecision(3);
      const yTick = svgElement("text", {
        x: margin.left - 10,
        y: y + 4,
        "text-anchor": "end",
      });
      yTick.textContent = (
        yDomain[1] -
        (tick / 5) * (yDomain[1] - yDomain[0])
      ).toPrecision(3);
      group.append(xTick, yTick);
      group.append(
        svgElement("line", {
          x1: margin.left,
          x2: width - margin.right,
          y1: y,
          y2: y,
          class: "grid",
        }),
      );
    }
    config.series.forEach((item, seriesIndex) => {
      const palette = dark ? DARK_COLORS : SEMANTIC_COLORS,
        color = config.high_contrast
          ? HIGH_CONTRAST_COLORS[seriesIndex % HIGH_CONTRAST_COLORS.length]
          : palette[item.semantic_color] || COLORS[seriesIndex % COLORS.length],
        visible = item.x
          .map((x, i) => ({ x, y: item.y[i] }))
          .filter((point) => point.x >= xDomain[0] && point.x <= xDomain[1]);
      const path = svgElement("polyline", {
        class: `series series-${item.id}`,
        points: visible.map((point) => `${X(point.x)},${Y(point.y)}`).join(" "),
        stroke: color,
        "stroke-dasharray": DASHES[item.line_style] || "",
      });
      group.append(path);
      visible.forEach((point, index) => {
        if (index % Math.max(1, Math.floor(visible.length / 12)) !== 0) return;
        const common = {
          class: `point series-${item.id}`,
          fill: "white",
          stroke: color,
        };
        if (item.marker === "square")
          group.append(
            svgElement("rect", {
              ...common,
              x: X(point.x) - 4,
              y: Y(point.y) - 4,
              width: 8,
              height: 8,
            }),
          );
        else if (item.marker === "triangle")
          group.append(
            svgElement("polygon", {
              ...common,
              points: `${X(point.x)},${Y(point.y) - 5} ${X(point.x) - 5},${Y(point.y) + 4} ${X(point.x) + 5},${Y(point.y) + 4}`,
            }),
          );
        else
          group.append(
            svgElement("circle", {
              ...common,
              cx: X(point.x),
              cy: Y(point.y),
              r: 4,
            }),
          );
      });
      const legendX = margin.left + seriesIndex * 170;
      group.append(
        svgElement("line", {
          x1: legendX,
          x2: legendX + 28,
          y1: 18,
          y2: 18,
          stroke: color,
          "stroke-width": 2.5,
          "stroke-dasharray": DASHES[item.line_style] || "",
        }),
      );
      const legendLabel = svgElement("text", {
        x: legendX + 34,
        y: 22,
        class: `series-${item.id}`,
      });
      legendLabel.textContent = `${item.label} (${item.line_style}, ${item.marker})`;
      group.append(legendLabel);
    });
    group.append(
      svgElement("line", {
        x1: margin.left,
        x2: width - margin.right,
        y1: height - margin.bottom,
        y2: height - margin.bottom,
        class: "axis",
      }),
    );
    group.append(
      svgElement("line", {
        x1: margin.left,
        x2: margin.left,
        y1: margin.top,
        y2: height - margin.bottom,
        class: "axis",
      }),
    );
    const xLabel = svgElement("text", {
      x: width / 2,
      y: height - 12,
      "text-anchor": "middle",
    });
    xLabel.textContent = config.x_axis.display_label;
    const yLabel = svgElement("text", {
      x: 18,
      y: height / 2,
      transform: `rotate(-90 18 ${height / 2})`,
      "text-anchor": "middle",
    });
    yLabel.textContent = config.y_axis.display_label;
    group.append(xLabel, yLabel);
    svg.append(group);
    svg.onpointermove = config.hover
      ? (event) => {
          const rect = svg.getBoundingClientRect(),
            px = ((event.clientX - rect.left) / rect.width) * width,
            value =
              xDomain[0] +
              ((px - margin.left) / (width - margin.left - margin.right)) *
                (xDomain[1] - xDomain[0]),
            nearest = nearestPoint(config.series, value);
          if (!nearest) return;
          tooltip.style.display = "block";
          tooltip.style.left = `${event.offsetX + 12}px`;
          tooltip.style.top = `${event.offsetY + 12}px`;
          tooltip.textContent = `${nearest.series.label}: ${nearest.x.toFixed(3)} ${config.x_axis.unit}, ${nearest.y.toFixed(3)} ${config.y_axis.unit}`;
          highlight(nearest.series.id);
        }
      : null;
    svg.onpointerleave = () => {
      tooltip.style.display = "none";
      highlight(null);
    };
    if (config.zoom)
      svg.onwheel = (event) => {
        event.preventDefault();
        const rect = svg.getBoundingClientRect(),
          center =
            xDomain[0] +
            ((event.clientX - rect.left) / rect.width) *
              (xDomain[1] - xDomain[0]);
        xDomain = zoomedDomain(xDomain, center, event.deltaY < 0 ? 0.8 : 1.25);
        draw();
      };
  };
  const highlight = (id) => {
    if (!config.linked_highlight) return;
    svg
      .querySelectorAll(".series,.point")
      .forEach((node) =>
        node.classList.toggle(
          "muted",
          Boolean(id) && !node.classList.contains(`series-${id}`),
        ),
      );
    tableHost
      .querySelectorAll("tr[data-series]")
      .forEach((row) =>
        row.classList.toggle("muted", Boolean(id) && row.dataset.series !== id),
      );
  };
  if (config.table) {
    const rows = config.series
      .flatMap((item) =>
        item.x.map(
          (x, i) =>
            `<tr tabindex="0" data-series="${item.id}"><td>${item.label}</td><td>${x.toFixed(4)}</td><td>${item.y[i].toFixed(4)}</td></tr>`,
        ),
      )
      .join("");
    tableHost.innerHTML = `<details><summary>Data table</summary><table><caption>${config.title}</caption><thead><tr><th>Series</th><th>${config.x_axis.display_label}</th><th>${config.y_axis.display_label}</th></tr></thead><tbody>${rows}</tbody></table></details>`;
    tableHost.querySelectorAll("tr[data-series]").forEach((row) => {
      row.onfocus = () => highlight(row.dataset.series);
      row.onblur = () => highlight(null);
    });
  }
  reset.hidden = !config.zoom;
  reset.onclick = () => {
    xDomain = [...originalX];
    draw();
  };
  draw();
}

globalThis.mountInteractiveChart = mountInteractiveChart;
