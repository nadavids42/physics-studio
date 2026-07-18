(() => {
  // src/physics-visuals.js
  var token = (state, group, name, fallback) => state.config.visualTokens?.[group]?.[name] ?? fallback;
  function applyText(context, state, role = "label") {
    const type = state.config.visualTokens?.typography || {};
    const sizes = {
      heading: type.heading_small || 19,
      label: type.label || 14,
      annotation: type.annotation || 13,
      helper: type.helper || 12,
      axis: type.graph_axis || 12,
      tooltip: type.tooltip || 13
    };
    const weight = role === "heading" ? type.weight_semibold || 650 : role === "label" ? type.weight_medium || 550 : type.weight_regular || 400;
    context.font = `${weight} ${sizes[role] || sizes.label}px ${type.family_ui || "system-ui, sans-serif"}`;
    context.fillStyle = token(state, "colors", "text", "#152536");
    context.textBaseline = "alphabetic";
  }
  function background(context, state, options = {}) {
    const { width, height } = state.transform;
    context.clearRect(0, 0, width, height);
    context.fillStyle = options.color || token(state, "colors", "canvas", "#F7FAFC");
    context.fillRect(0, 0, width, height);
  }
  function roundedPanel(context, state, x, y, width, height, options = {}) {
    const radius = options.radius ?? token(state, "shape", "radius_large", 16);
    context.beginPath();
    context.roundRect(x, y, width, height, radius);
    context.fillStyle = options.fill || token(state, "colors", "surface", "#FFF");
    context.fill();
    context.strokeStyle = options.stroke || token(state, "colors", "border", "#B8C5D1");
    context.lineWidth = options.lineWidth || token(state, "shape", "line_regular", 1.5);
    context.stroke();
  }
  function arrow(context, state, from, to, options = {}) {
    const color = options.color || token(state, "colors", options.role || "net_force", "#C2410C");
    const width = options.width || token(state, "shape", "line_vector", 3);
    const angle = Math.atan2(to.y - from.y, to.x - from.x);
    const head = options.head || Math.max(9, width * 4);
    context.save();
    context.strokeStyle = color;
    context.fillStyle = color;
    context.lineWidth = width;
    context.lineCap = "round";
    context.lineJoin = "round";
    if (options.dashed) context.setLineDash([7, 5]);
    context.beginPath();
    context.moveTo(from.x, from.y);
    context.lineTo(to.x, to.y);
    context.stroke();
    context.setLineDash([]);
    context.beginPath();
    context.moveTo(to.x, to.y);
    context.lineTo(
      to.x - head * Math.cos(angle - 0.45),
      to.y - head * Math.sin(angle - 0.45)
    );
    context.lineTo(
      to.x - head * Math.cos(angle + 0.45),
      to.y - head * Math.sin(angle + 0.45)
    );
    context.closePath();
    context.fill();
    if (options.label) {
      applyText(context, state, "label");
      context.fillStyle = color;
      context.fillText(
        options.label,
        to.x + (options.labelDx ?? 8),
        to.y + (options.labelDy ?? -8)
      );
    }
    context.restore();
  }
  function grid(context, state, box, options = {}) {
    const step = options.step || 40;
    context.save();
    context.strokeStyle = options.color || token(state, "colors", "grid", "#526577");
    context.globalAlpha = options.opacity ?? token(state, "shape", "grid_opacity", 0.16);
    context.lineWidth = token(state, "shape", "line_hairline", 1);
    context.beginPath();
    for (let x = box.x; x <= box.x + box.width; x += step) {
      context.moveTo(x, box.y);
      context.lineTo(x, box.y + box.height);
    }
    for (let y = box.y; y <= box.y + box.height; y += step) {
      context.moveTo(box.x, y);
      context.lineTo(box.x + box.width, y);
    }
    context.stroke();
    context.restore();
  }
  function trail(context, state, points, map, options = {}) {
    if (points.length < 2) return;
    context.save();
    context.strokeStyle = options.color || token(state, "colors", "trajectory", "#1769AA");
    context.lineWidth = options.width || token(state, "shape", "line_regular", 1.5);
    context.lineCap = "round";
    context.globalAlpha = options.opacity ?? token(state, "shape", "trail_opacity", 0.24);
    if (options.dashed) context.setLineDash([7, 5]);
    context.beginPath();
    points.forEach((point, index) => {
      const mapped = map(point);
      if (index) context.lineTo(mapped.x, mapped.y);
      else context.moveTo(mapped.x, mapped.y);
    });
    context.stroke();
    context.restore();
  }
  function responsive(state) {
    const width = state.transform.width;
    const responsiveTokens = state.config.visualTokens?.responsive || {};
    if (width <= (responsiveTokens.mobile_max_px || 480)) return "mobile";
    if (width <= (responsiveTokens.tablet_max_px || 820)) return "tablet";
    return "desktop";
  }
  var PhysicsVisuals = {
    token,
    applyText,
    background,
    roundedPanel,
    arrow,
    grid,
    trail,
    responsive
  };
  globalThis.PhysicsVisuals = PhysicsVisuals;
})();
