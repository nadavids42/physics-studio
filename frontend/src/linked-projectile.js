import { mountPlayer, sample } from "./player-runtime.js";
import { scene as cannonballScene } from "./scenes/mechanics/cannonball.js";

export const QUANTITY_COLORS = Object.freeze({
  position: "#0072B2",
  velocity: "#D55E00",
  acceleration: "#00875A",
  horizontal: "#6F4E7C",
  vertical: "#C43C39",
});

export function nearestIndex(times, time) {
  if (!times.length) return 0;
  let best = 0;
  for (let index = 1; index < times.length; index += 1) {
    if (Math.abs(times[index] - time) < Math.abs(times[best] - time))
      best = index;
  }
  return best;
}

export function stateAt(run, fraction) {
  const time = sample(run.time_s, fraction);
  const index = nearestIndex(run.time_s, time);
  return {
    index,
    time,
    x: run.x_m[index],
    y: run.y_m[index],
    vx: run.vx_m_s[index],
    vy: run.vy_m_s[index],
    ax: run.ax_m_s2[index],
    ay: run.ay_m_s2[index],
  };
}

export function sharedDomains(runs) {
  const values = (key) => runs.flatMap((run) => run[key]);
  const extent = (items, includeZero = true) => {
    const low = Math.min(...items, ...(includeZero ? [0] : []));
    const high = Math.max(...items, ...(includeZero ? [0] : []));
    const padding = Math.max((high - low) * 0.08, 0.1);
    return [low - padding, high + padding];
  };
  return {
    time: [0, Math.max(...values("time_s"))],
    position: extent([...values("x_m"), ...values("y_m")]),
    velocity: extent([...values("vx_m_s"), ...values("vy_m_s")]),
    acceleration: extent([...values("ax_m_s2"), ...values("ay_m_s2")]),
  };
}

export function fractionFromGraphPointer(clientX, left, width) {
  return Math.min(1, Math.max(0, (clientX - left) / Math.max(width, 1)));
}

export function keyboardFraction(fraction, key, frameCount) {
  if (key === "Home") return 0;
  if (key === "End") return 1;
  const step = 1 / Math.max(frameCount - 1, 1);
  if (key === "ArrowRight") return Math.min(1, fraction + step);
  if (key === "ArrowLeft") return Math.max(0, fraction - step);
  return fraction;
}

export function accessibleReadout(runs, fraction) {
  return runs
    .map((run) => {
      const state = stateAt(run, fraction);
      return `${run.label}: t ${state.time.toFixed(2)} s; position x ${state.x.toFixed(2)} m, y ${state.y.toFixed(2)} m; velocity vx ${state.vx.toFixed(2)} m/s, vy ${state.vy.toFixed(2)} m/s; acceleration ax ${state.ax.toFixed(2)} m/s², ay ${state.ay.toFixed(2)} m/s².`;
    })
    .join(" ");
}

function svg(name, attrs = {}) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", name);
  Object.entries(attrs).forEach(([key, value]) =>
    node.setAttribute(key, value),
  );
  return node;
}

export class LinkedProjectileRuntime {
  constructor(config, environment = globalThis) {
    this.config = config;
    this.environment = environment;
    this.runs = config.representations.runs;
    this.domains = sharedDomains(this.runs);
    this.selectedQuantity = null;
    this.graphs = [...document.querySelectorAll("svg.linked-graph")];
    this.readout = document.getElementById("linked-readout");
    this.drawGraphs();
    this.player = mountPlayer(config, cannonballScene, environment);
    const originalRender = this.player.render.bind(this.player);
    this.player.render = (fraction) => {
      originalRender(fraction);
      this.update(fraction);
    };
    this.bind();
    this.update(0);
  }

  drawGraphs() {
    const specifications = {
      position: ["x_m", "y_m", "Position (m)"],
      velocity: ["vx_m_s", "vy_m_s", "Velocity (m/s)"],
      acceleration: ["ax_m_s2", "ay_m_s2", "Acceleration (m/s²)"],
    };
    for (const graph of this.graphs) {
      const quantity = graph.dataset.quantity;
      const [xKey, yKey, label] = specifications[quantity];
      graph.setAttribute(
        "aria-label",
        `${label} versus time. Use arrow keys to inspect time values.`,
      );
      const width = 420,
        height = 190,
        left = 46,
        right = 12,
        top = 18,
        bottom = 34;
      const [t0, t1] = this.domains.time;
      const [q0, q1] = this.domains[quantity];
      const X = (value) =>
        left +
        ((value - t0) / Math.max(t1 - t0, 1e-9)) * (width - left - right);
      const Y = (value) =>
        height -
        bottom -
        ((value - q0) / Math.max(q1 - q0, 1e-9)) * (height - top - bottom);
      graph.replaceChildren();
      graph.append(
        svg("line", {
          x1: left,
          x2: width - right,
          y1: Y(0),
          y2: Y(0),
          class: "zero",
        }),
      );
      this.runs.forEach((run, runIndex) => {
        [
          [xKey, "horizontal"],
          [yKey, "vertical"],
        ].forEach(([key, component]) => {
          graph.append(
            svg("polyline", {
              points: run.time_s
                .map((time, index) => `${X(time)},${Y(run[key][index])}`)
                .join(" "),
              class: `quantity-line ${component} run-${runIndex}`,
              "data-quantity": quantity,
            }),
          );
        });
      });
      const cursor = svg("line", {
        class: "graph-cursor",
        y1: top,
        y2: height - bottom,
      });
      graph.append(cursor);
      graph.dataset.left = String(left);
      graph.dataset.right = String(width - right);
      const title = svg("text", { x: left, y: 13, class: "graph-title" });
      title.textContent = label;
      graph.append(title);
    }
  }

  bind() {
    this.onGraphPointer = (event) => {
      const graph = event.currentTarget;
      const box = graph.getBoundingClientRect();
      const fraction = fractionFromGraphPointer(
        event.clientX,
        box.left,
        box.width,
      );
      this.player.pause();
      this.player.seek(fraction);
    };
    this.onGraphKey = (event) => {
      if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) {
        event.preventDefault();
        this.player.pause();
        this.player.seek(
          keyboardFraction(
            this.player.fraction,
            event.key,
            this.player.frameCount(),
          ),
        );
      }
    };
    this.graphs.forEach((graph) => {
      graph.addEventListener("pointermove", this.onGraphPointer);
      graph.addEventListener("click", this.onGraphPointer);
      graph.addEventListener("keydown", this.onGraphKey);
    });
    this.onEquation = (event) => {
      this.selectedQuantity = event.currentTarget.dataset.quantity;
      document.body.dataset.highlightQuantity = this.selectedQuantity;
      this.update(this.player.fraction);
    };
    document
      .querySelectorAll("button.equation-term")
      .forEach((button) => button.addEventListener("click", this.onEquation));
  }

  update(fraction) {
    const time = sample(this.runs[0].time_s, fraction);
    this.graphs.forEach((graph) => {
      const left = Number(graph.dataset.left),
        right = Number(graph.dataset.right);
      const cursor = graph.querySelector(".graph-cursor");
      const x = left + fraction * (right - left);
      cursor.setAttribute("x1", x);
      cursor.setAttribute("x2", x);
    });
    const readout = accessibleReadout(this.runs, fraction);
    this.readout.textContent = readout;
    this.player.scrubber.setAttribute(
      "aria-valuetext",
      `Time ${time.toFixed(2)} seconds. ${readout}`,
    );
  }
}

export function mountLinkedProjectile(config, environment = globalThis) {
  return new LinkedProjectileRuntime(config, environment);
}

Object.assign(globalThis, { LinkedProjectileRuntime, mountLinkedProjectile });
