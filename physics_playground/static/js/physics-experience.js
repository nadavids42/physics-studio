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

  // src/experience.js
  var PhysicsExperience = /* @__PURE__ */ (() => {
    function level(s) {
      return s.config.presentationLevel || "illustrated";
    }
    function profile(s) {
      const name = level(s);
      return {
        level: name,
        depth: name !== "diagram",
        environment: name === "contextual",
        decorativeDetail: name !== "diagram",
        preserveScientificOverlays: true
      };
    }
    function context(ctx, s, kind) {
      const mode = profile(s), w = s.transform.width, h = s.transform.height;
      PhysicsVisuals.background(ctx, s, {
        color: PhysicsVisuals.token(
          s,
          "colors",
          mode.level === "diagram" ? "surface" : "canvas",
          "#F7FAFC"
        )
      });
      if (!mode.environment) return mode;
      ctx.save();
      if (kind === "projectileField") {
        const horizon = h * 0.7, g = ctx.createLinearGradient(0, 0, 0, horizon);
        g.addColorStop(0, "#B9DDF3");
        g.addColorStop(1, "#EDF7FC");
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, horizon);
        ctx.fillStyle = "#A7C98B";
        ctx.fillRect(0, horizon, w, h - horizon);
        ctx.strokeStyle = "rgba(255,255,255,.72)";
        ctx.lineWidth = 2;
        for (let x = 0; x < w; x += 70) {
          ctx.beginPath();
          ctx.moveTo(x, horizon);
          ctx.lineTo(x, h);
          ctx.stroke();
        }
      } else if (kind === "laboratory") {
        ctx.fillStyle = PhysicsVisuals.token(
          s,
          "colors",
          "surface_muted",
          "#EAF0F6"
        );
        ctx.fillRect(0, 0, w, h);
        ctx.strokeStyle = PhysicsVisuals.token(s, "colors", "grid", "#526577");
        ctx.globalAlpha = 0.12;
        for (let x = 0; x < w; x += 48) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, h);
          ctx.stroke();
        }
        ctx.globalAlpha = 1;
        ctx.fillStyle = PhysicsVisuals.token(
          s,
          "colors",
          "surface_raised",
          "#FFF"
        );
        ctx.fillRect(0, h * 0.8, w, h * 0.2);
      } else if (kind === "space") {
        const g = ctx.createRadialGradient(
          w * 0.5,
          h * 0.48,
          5,
          w * 0.5,
          h * 0.48,
          Math.max(w, h) * 0.7
        );
        g.addColorStop(0, "#182C4A");
        g.addColorStop(1, "#07101F");
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = "rgba(255,255,255,.7)";
        for (let i = 0; i < 36; i++) {
          const x = i * 83 % w, y = (i * i * 29 + 17) % h, r = i % 7 === 0 ? 1.5 : 0.7;
          ctx.beginPath();
          ctx.arc(x, y, r, 0, Math.PI * 2);
          ctx.fill();
        }
      } else if (kind === "opticsBench") {
        ctx.fillStyle = "#EEF3F7";
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = "#A9B6C2";
        ctx.fillRect(0, h * 0.76, w, 12);
        ctx.strokeStyle = "#738394";
        ctx.lineWidth = 2;
        for (let x = 30; x < w; x += 45) {
          ctx.beginPath();
          ctx.moveTo(x, h * 0.76);
          ctx.lineTo(x, h * 0.82);
          ctx.stroke();
        }
      } else if (kind === "rollerCoaster") {
        const g = ctx.createLinearGradient(0, 0, 0, h);
        g.addColorStop(0, "#C9E6F7");
        g.addColorStop(1, "#F6FAFC");
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = "#B7D59B";
        ctx.fillRect(0, h * 0.72, w, h * 0.28);
      } else if (kind === "collisionTrack") {
        ctx.fillStyle = "#F2E8DC";
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = "#73655B";
        ctx.fillRect(0, h * 0.72, w, h * 0.28);
        ctx.strokeStyle = "rgba(255,255,255,.65)";
        ctx.lineWidth = 3;
        ctx.setLineDash([14, 10]);
        ctx.beginPath();
        ctx.moveTo(0, h * 0.86);
        ctx.lineTo(w, h * 0.86);
        ctx.stroke();
        ctx.setLineDash([]);
      }
      ctx.restore();
      return mode;
    }
    function scientificOverlay(ctx, s, draw) {
      ctx.save();
      draw();
      ctx.restore();
    }
    return { level, profile, context, scientificOverlay };
  })();
  globalThis.PhysicsExperience = PhysicsExperience;
})();
