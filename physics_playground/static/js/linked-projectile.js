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

  // src/vectors.js
  var PhysicsAnnotations = /* @__PURE__ */ (() => {
    const V = PhysicsVisuals;
    const p = (x, y) => ({ x, y });
    const disclosureText = {
      normalized: "Vector lengths normalized for visibility",
      schematic: "Schematic vectors \u2014 not drawn to scale"
    };
    function endpoint(spec, progress = 1) {
      const mag = Math.hypot(spec.dx || 0, spec.dy || 0), ux = mag ? spec.dx / mag : 0, uy = mag ? -spec.dy / mag : 0;
      let length = 0;
      if (spec.scale_mode === "physical")
        length = mag * (spec.pixels_per_unit || 1);
      else length = spec.fixed_length_px || 72;
      return p(spec.x + ux * length * progress, spec.y + uy * length * progress);
    }
    function disclosure(ctx, s, mode, text, x = 12, y = 12) {
      if (mode === "physical") return;
      const value = text || disclosureText[mode];
      if (!value) return;
      ctx.save();
      V.applyText(ctx, s, "helper");
      const pad = 8, h = 26, w = Math.min(
        s.transform.width - 24,
        ctx.measureText(value).width + pad * 2
      );
      ctx.fillStyle = V.token(s, "colors", "surface_raised", "#FFF");
      ctx.strokeStyle = V.token(s, "colors", "border", "#B8C5D1");
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(x, y, w, h, 8);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = V.token(s, "colors", "text_muted", "#526577");
      ctx.fillText(value, x + pad, y + 17);
      ctx.restore();
    }
    function scaleLegend(ctx, s, specs, x = 12, y = 12) {
      const physical = (specs || []).filter(
        (spec) => spec.scale_mode === "physical" && Number.isFinite(spec.pixels_per_unit) && spec.pixels_per_unit > 0 && spec.units
      );
      if (!physical.length) return;
      const scale = physical[0].pixels_per_unit, units = physical[0].units;
      if (physical.some(
        (spec) => spec.pixels_per_unit !== scale || spec.units !== units
      ))
        return;
      const target2 = 40 / scale, power = 10 ** Math.floor(Math.log10(target2)), reference = [1, 2, 5, 10].map((value) => value * power).reduce(
        (best, value) => Math.abs(value - target2) < Math.abs(best - target2) ? value : best
      ), length = reference * scale, quantity = units === "N" ? "Force" : "Vector", text = `${quantity} scale (linear): ${reference} ${units}`;
      ctx.save();
      V.applyText(ctx, s, "helper");
      const pad = 8, boxWidth = Math.min(
        s.transform.width - 24,
        Math.max(ctx.measureText(text).width + pad * 2, length + pad * 2)
      ), boxHeight = 48;
      ctx.fillStyle = V.token(s, "colors", "surface_raised", "#FFF");
      ctx.strokeStyle = V.token(s, "colors", "border", "#B8C5D1");
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(x, y, boxWidth, boxHeight, 8);
      ctx.fill();
      ctx.stroke();
      ctx.strokeStyle = V.token(s, "colors", "net_force", "#B3261E");
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x + pad, y + 18);
      ctx.lineTo(x + pad + length, y + 18);
      ctx.stroke();
      ctx.fillStyle = V.token(s, "colors", "text_muted", "#526577");
      ctx.fillText(text, x + pad, y + 39);
      ctx.restore();
    }
    function vector(ctx, s, spec, progress = 1, showDisclosure = true) {
      const end = endpoint(spec, progress), role = spec.role || "net_force";
      V.arrow(ctx, s, p(spec.x, spec.y), end, {
        role,
        color: spec.color,
        label: spec.label,
        dashed: spec.dashed || false,
        width: spec.line_width
      });
      if (showDisclosure)
        disclosure(
          ctx,
          s,
          spec.scale_mode,
          spec.scale_disclosure,
          spec.disclosure_x || 12,
          spec.disclosure_y || 12
        );
    }
    function vectorSet(ctx, s, specs, progress = 1, originDisclosure = p(12, 12)) {
      const modes = /* @__PURE__ */ new Set();
      for (const spec of specs || []) {
        vector(ctx, s, spec, progress, false);
        if (spec.scale_mode !== "physical") modes.add(spec.scale_mode);
      }
      scaleLegend(ctx, s, specs, originDisclosure.x, originDisclosure.y);
      if (modes.size) {
        const mode = modes.has("schematic") ? "schematic" : "normalized";
        const hasPhysical = (specs || []).some(
          (spec) => spec.scale_mode === "physical"
        );
        disclosure(
          ctx,
          s,
          mode,
          "",
          originDisclosure.x,
          originDisclosure.y + (hasPhysical ? 54 : 0)
        );
      }
    }
    function forceDiagram(ctx, s, diagram, progress = 1) {
      ctx.save();
      ctx.fillStyle = V.token(s, "colors", "surface", "#FFF");
      ctx.strokeStyle = V.token(s, "colors", "text", "#152536");
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(diagram.x, diagram.y, 10, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.restore();
      vectorSet(ctx, s, diagram.vectors, progress);
      if (diagram.title) {
        ctx.save();
        V.applyText(ctx, s, "label");
        ctx.textAlign = "center";
        ctx.fillText(diagram.title, diagram.x, diagram.y + 30);
        ctx.restore();
      }
    }
    function angleArc(ctx, s, o = {}) {
      PhysicsAssets.angleMarker(ctx, s, { ...o, label: o.label || "" });
    }
    function dimensionLine(ctx, s, o = {}) {
      const a = p(o.x, o.y), b = o.end || p(o.x + (o.width || 100), o.y), color = o.color || V.token(s, "colors", "text_muted", "#526577"), tick = o.tick || 8;
      ctx.save();
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
      const angle = Math.atan2(b.y - a.y, b.x - a.x), nx = -Math.sin(angle) * tick / 2, ny = Math.cos(angle) * tick / 2;
      for (const q of [a, b]) {
        ctx.beginPath();
        ctx.moveTo(q.x - nx, q.y - ny);
        ctx.lineTo(q.x + nx, q.y + ny);
        ctx.stroke();
      }
      if (o.label) {
        V.applyText(ctx, s, "annotation");
        ctx.fillStyle = color;
        ctx.textAlign = "center";
        ctx.fillText(
          o.label,
          (a.x + b.x) / 2 + nx * 1.8,
          (a.y + b.y) / 2 + ny * 1.8
        );
      }
      ctx.restore();
    }
    function pathGuide(ctx, s, o = {}) {
      const points = o.points || [];
      ctx.save();
      ctx.strokeStyle = o.color || V.token(s, "colors", "trajectory", "#1769AA");
      ctx.globalAlpha = o.opacity ?? 0.45;
      ctx.lineWidth = o.line_width || 1.5;
      ctx.setLineDash(o.dashes || [6, 6]);
      ctx.beginPath();
      points.forEach((q, i) => i ? ctx.lineTo(q.x, q.y) : ctx.moveTo(q.x, q.y));
      ctx.stroke();
      ctx.restore();
    }
    function normalLine(ctx, s, o = {}) {
      const length = o.length || 70, angle = (o.surface_angle || 0) - Math.PI / 2;
      pathGuide(ctx, s, {
        points: [
          p(
            o.x - Math.cos(angle) * length / 2,
            o.y - Math.sin(angle) * length / 2
          ),
          p(
            o.x + Math.cos(angle) * length / 2,
            o.y + Math.sin(angle) * length / 2
          )
        ],
        color: o.color,
        dashes: [5, 5]
      });
      if (o.label) {
        ctx.save();
        V.applyText(ctx, s, "annotation");
        ctx.fillText(
          o.label,
          o.x + Math.cos(angle) * length * 0.58,
          o.y + Math.sin(angle) * length * 0.58
        );
        ctx.restore();
      }
    }
    function centerOfMass(ctx, s, o = {}) {
      const r = o.radius || 10, color = o.color || V.token(s, "colors", "selected", "#7C3AED");
      ctx.save();
      ctx.translate(o.x, o.y);
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(-r, 0);
      ctx.lineTo(r, 0);
      ctx.moveTo(0, -r);
      ctx.lineTo(0, r);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
      if (o.label) {
        ctx.save();
        V.applyText(ctx, s, "label");
        ctx.fillStyle = color;
        ctx.fillText(o.label, o.x + r + 5, o.y - r - 3);
        ctx.restore();
      }
    }
    function velocityTrail(ctx, s, o = {}) {
      const points = o.points || [];
      V.trail(ctx, s, points, (q) => q, {
        color: o.color || V.token(s, "colors", "velocity", "#087EA4"),
        opacity: o.opacity,
        width: o.line_width || 2,
        dashed: o.dashed
      });
      if (o.direction !== false && points.length > 1) {
        const b = points.at(-1), a = points[Math.max(0, points.length - 3)];
        V.arrow(ctx, s, a, b, {
          color: o.color || V.token(s, "colors", "velocity", "#087EA4"),
          width: 2,
          head: 8
        });
      }
    }
    function motionDirection(ctx, s, o = {}) {
      const end = o.end || p(o.x + (o.length || 44), o.y), dx = end.x - o.x, dy = -(end.y - o.y);
      vector(
        ctx,
        s,
        {
          ...o,
          dx,
          dy,
          role: "velocity",
          label: o.label || "motion",
          scale_mode: o.scale_mode || "schematic",
          fixed_length_px: o.fixed_length_px || Math.max(1, Math.hypot(dx, dy)),
          scale_disclosure: o.scale_disclosure || "Motion-direction indicator is schematic"
        },
        1,
        o.show_disclosure !== false
      );
    }
    return {
      endpoint,
      disclosure,
      scaleLegend,
      vector,
      vectorSet,
      forceDiagram,
      angleArc,
      dimensionLine,
      pathGuide,
      normalLine,
      centerOfMass,
      velocityTrail,
      motionDirection
    };
  })();
  globalThis.PhysicsAnnotations = PhysicsAnnotations;

  // src/assets.js
  var PhysicsAssets = (() => {
    const V = PhysicsVisuals;
    const point = (x, y) => ({ x, y });
    function setup(ctx, s, o = {}) {
      ctx.save();
      ctx.translate(o.x || 0, o.y || 0);
      ctx.rotate(o.rotation || 0);
      ctx.scale(o.scale || 1, o.scale || 1);
      ctx.globalAlpha = (o.opacity ?? 1) * (o.disabled ? 0.45 : 1);
      ctx.lineWidth = o.outlineWidth || V.token(s, "shape", "object_outline", 2);
      ctx.lineJoin = "round";
      ctx.lineCap = "round";
      if (o.shadow) {
        ctx.shadowColor = "rgba(15,23,42,.18)";
        ctx.shadowBlur = 8;
        ctx.shadowOffsetY = 3;
      }
      if (o.glow) {
        ctx.shadowColor = o.fill || V.token(s, "colors", "accent", "#1769AA");
        ctx.shadowBlur = 14;
        ctx.shadowOffsetY = 0;
      }
    }
    function finish(ctx, s, o = {}) {
      ctx.restore();
      if (o.selected) {
        ctx.save();
        ctx.strokeStyle = V.token(s, "colors", "selected", "#7C3AED");
        ctx.lineWidth = 3;
        ctx.setLineDash([6, 4]);
        ctx.beginPath();
        ctx.arc(
          o.x || 0,
          o.y || 0,
          Math.max(o.width || 40, o.height || 40) * 0.7 * (o.scale || 1),
          0,
          Math.PI * 2
        );
        ctx.stroke();
        ctx.restore();
      }
      if (o.label) {
        ctx.save();
        V.applyText(ctx, s, "label");
        ctx.textAlign = "center";
        ctx.fillText(
          o.label,
          o.x || 0,
          (o.y || 0) + (o.height || 40) * (o.scale || 1) * 0.72 + 16
        );
        ctx.restore();
      }
    }
    function colors(s, o, fill = "accent") {
      return {
        fill: o.fill || V.token(s, "colors", fill, "#1769AA"),
        outline: o.outline || V.token(s, "colors", "text", "#152536")
      };
    }
    function gradient(ctx, c, r, base, highlight = true) {
      const g = ctx.createRadialGradient(
        c.x - r * 0.35,
        c.y - r * 0.4,
        r * 0.08,
        c.x,
        c.y,
        r
      );
      g.addColorStop(0, highlight ? "#FFFFFF" : base);
      g.addColorStop(0.22, base);
      g.addColorStop(1, base);
      return g;
    }
    function body(ctx, s, o = {}, role = "accent") {
      const r = o.radius || Math.min(o.width || 40, o.height || 40) / 2, c = colors(s, o, role), depth = PhysicsExperience.profile(s).depth;
      setup(ctx, s, {
        ...o,
        shadow: depth && o.shadow !== false,
        glow: depth && o.glow
      });
      ctx.fillStyle = gradient(
        ctx,
        point(0, 0),
        r,
        c.fill,
        depth && o.highlight !== false
      );
      ctx.strokeStyle = c.outline;
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      if (depth) {
        ctx.globalAlpha *= 0.22;
        ctx.fillStyle = "#FFF";
        ctx.beginPath();
        ctx.ellipse(
          -r * 0.25,
          -r * 0.32,
          r * 0.34,
          r * 0.16,
          -0.5,
          0,
          Math.PI * 2
        );
        ctx.fill();
      }
      finish(ctx, s, o);
    }
    function sphere(ctx, s, o = {}) {
      body(ctx, s, o, "accent");
    }
    function mass(ctx, s, o = {}) {
      body(ctx, s, o, "displacement");
    }
    function block(ctx, s, o = {}) {
      const w = o.width || 54, h = o.height || 42, c = colors(s, o, "energy"), depth = PhysicsExperience.profile(s).depth;
      setup(ctx, s, { ...o, shadow: depth && o.shadow !== false });
      const g = ctx.createLinearGradient(0, -h / 2, 0, h / 2);
      g.addColorStop(0, depth && o.highlight ? "#FFF" : c.fill);
      g.addColorStop(0.18, c.fill);
      g.addColorStop(1, c.fill);
      ctx.fillStyle = depth ? g : c.fill;
      ctx.strokeStyle = c.outline;
      ctx.beginPath();
      ctx.roundRect(-w / 2, -h / 2, w, h, Math.min(8, h * 0.18));
      ctx.fill();
      ctx.stroke();
      if (depth) {
        ctx.globalAlpha *= 0.18;
        ctx.fillStyle = "#FFF";
        ctx.fillRect(-w * 0.36, -h * 0.34, w * 0.72, h * 0.12);
      }
      finish(ctx, s, o);
    }
    function wheel(ctx, s, o = {}) {
      const r = o.radius || Math.min(o.width || 34, o.height || 34) / 2, c = colors(s, o, "uncertainty");
      setup(ctx, s, o);
      ctx.fillStyle = c.fill;
      ctx.strokeStyle = c.outline;
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = V.token(s, "colors", "surface", "#FFF");
      ctx.beginPath();
      ctx.arc(0, 0, r * 0.28, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      for (let i = 0; i < 6; i++) {
        const a = i * Math.PI / 3;
        ctx.beginPath();
        ctx.moveTo(Math.cos(a) * r * 0.3, Math.sin(a) * r * 0.3);
        ctx.lineTo(Math.cos(a) * r * 0.82, Math.sin(a) * r * 0.82);
        ctx.stroke();
      }
      finish(ctx, s, o);
    }
    function cart(ctx, s, o = {}) {
      const w = o.width || 72, h = o.height || 38;
      block(ctx, s, {
        ...o,
        y: (o.y || 0) - 8,
        width: w,
        height: h,
        label: "",
        shadow: o.shadow
      });
      wheel(ctx, s, {
        ...o,
        x: (o.x || 0) - w * 0.28,
        y: (o.y || 0) + h * 0.38,
        width: 20,
        height: 20,
        label: "",
        shadow: false
      });
      wheel(ctx, s, {
        ...o,
        x: (o.x || 0) + w * 0.28,
        y: (o.y || 0) + h * 0.38,
        width: 20,
        height: 20,
        label: "",
        shadow: false
      });
      if (o.label) finish(ctx, s, { ...o, shadow: false });
    }
    function pendulumBob(ctx, s, o = {}) {
      body(ctx, s, { ...o, radius: o.radius || 18 }, "displacement");
    }
    function pivot(ctx, s, o = {}) {
      const w = o.width || 34, h = o.height || 28, c = colors(s, o, "uncertainty");
      setup(ctx, s, o);
      ctx.fillStyle = c.fill;
      ctx.strokeStyle = c.outline;
      ctx.beginPath();
      ctx.moveTo(0, -h * 0.45);
      ctx.lineTo(w / 2, h / 2);
      ctx.lineTo(-w / 2, h / 2);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = V.token(s, "colors", "surface", "#FFF");
      ctx.beginPath();
      ctx.arc(0, -h * 0.32, 4, 0, Math.PI * 2);
      ctx.fill();
      finish(ctx, s, o);
    }
    function segment(ctx, s, o = {}, role = "tension") {
      const end = o.end || point(o.width || 80, 0), c = colors(s, o, role);
      setup(ctx, s, o);
      ctx.strokeStyle = c.fill;
      ctx.lineWidth = o.lineWidth || V.token(s, "shape", "line_emphasis", 2.5);
      if (o.dashed) ctx.setLineDash([7, 5]);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(end.x, end.y);
      ctx.stroke();
      finish(ctx, s, o);
    }
    function cable(ctx, s, o = {}) {
      segment(ctx, s, o, "tension");
    }
    function rod(ctx, s, o = {}) {
      segment(ctx, s, { ...o, lineWidth: o.lineWidth || 6 }, "uncertainty");
    }
    function spring(ctx, s, o = {}) {
      const end = o.end || point(o.width || 100, 0), turns = o.turns || 12, amp = o.amplitude || 9, c = colors(s, o, "acceleration");
      setup(ctx, s, o);
      ctx.strokeStyle = c.fill;
      ctx.lineWidth = o.lineWidth || 2.5;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      for (let i = 1; i < turns * 2; i++) {
        const t = i / (turns * 2), x = end.x * t, y = end.y * t + (i % 2 ? amp : -amp);
        ctx.lineTo(x, y);
      }
      ctx.lineTo(end.x, end.y);
      ctx.stroke();
      finish(ctx, s, o);
    }
    function ramp(ctx, s, o = {}) {
      const w = o.width || 150, h = o.height || 80, c = colors(s, o, "uncertainty");
      setup(ctx, s, o);
      ctx.fillStyle = o.fill || V.token(s, "colors", "surface_muted", "#EAF0F6");
      ctx.strokeStyle = c.outline;
      ctx.beginPath();
      if (o.descending) {
        ctx.moveTo(-w / 2, -h / 2);
        ctx.lineTo(-w / 2, h / 2);
        ctx.lineTo(w / 2, h / 2);
      } else {
        ctx.moveTo(-w / 2, h / 2);
        ctx.lineTo(w / 2, h / 2);
        ctx.lineTo(w / 2, -h / 2);
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      finish(ctx, s, o);
    }
    function pulley(ctx, s, o = {}) {
      wheel(ctx, s, {
        ...o,
        width: o.width || 48,
        height: o.height || 48,
        fill: o.fill || V.token(s, "colors", "surface_muted", "#EAF0F6")
      });
    }
    function lever(ctx, s, o = {}) {
      rod(ctx, s, {
        ...o,
        x: o.x - (o.width || 160) / 2,
        y: o.y,
        end: point(o.width || 160, 0),
        lineWidth: o.height || 9,
        label: ""
      });
      pivot(ctx, s, { ...o, width: 32, height: 28, label: "", shadow: false });
      if (o.label) finish(ctx, s, { ...o, shadow: false });
    }
    function track(ctx, s, o = {}) {
      const pts = o.points || [], color = o.outline || V.token(s, "colors", "text", "#152536");
      if (pts.length < 2) return;
      ctx.save();
      ctx.strokeStyle = color;
      ctx.globalAlpha = o.opacity ?? 1;
      ctx.lineWidth = o.lineWidth || 5;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      if (o.dashed) ctx.setLineDash([8, 7]);
      ctx.beginPath();
      pts.forEach((q, i) => i ? ctx.lineTo(q.x, q.y) : ctx.moveTo(q.x, q.y));
      ctx.stroke();
      if (!o.dashed && o.ties !== false) {
        ctx.lineWidth = 1.5;
        ctx.globalAlpha *= 0.55;
        for (let i = 1; i < pts.length; i++) {
          const a = pts[i - 1], b = pts[i], length = Math.hypot(b.x - a.x, b.y - a.y), count = Math.max(1, Math.floor(length / 24)), ux = (b.x - a.x) / length, uy = (b.y - a.y) / length, nx = -uy * 7, ny = ux * 7;
          for (let j = 0; j <= count; j++) {
            const q = {
              x: a.x + (b.x - a.x) * j / count,
              y: a.y + (b.y - a.y) * j / count
            };
            ctx.beginPath();
            ctx.moveTo(q.x - nx, q.y - ny);
            ctx.lineTo(q.x + nx, q.y + ny);
            ctx.stroke();
          }
        }
      }
      ctx.restore();
    }
    function planet(ctx, s, o = {}) {
      body(
        ctx,
        s,
        { ...o, radius: o.radius || Math.min(o.width || 72, o.height || 72) / 2 },
        "electric_field"
      );
    }
    function moon(ctx, s, o = {}) {
      body(
        ctx,
        s,
        {
          ...o,
          radius: o.radius || Math.min(o.width || 34, o.height || 34) / 2,
          highlight: false
        },
        "uncertainty"
      );
    }
    function star(ctx, s, o = {}) {
      const r = o.radius || Math.min(o.width || 70, o.height || 70) / 2, c = colors(s, o, "energy");
      setup(ctx, s, { ...o, glow: o.glow !== false });
      ctx.fillStyle = c.fill;
      ctx.strokeStyle = c.outline;
      ctx.beginPath();
      for (let i = 0; i < 20; i++) {
        const a = -Math.PI / 2 + i * Math.PI / 10, rr = i % 2 ? r * 0.72 : r;
        ctx.lineTo(Math.cos(a) * rr, Math.sin(a) * rr);
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      finish(ctx, s, o);
    }
    function satellite(ctx, s, o = {}) {
      const c = colors(s, o, "uncertainty");
      setup(ctx, s, o);
      ctx.fillStyle = c.fill;
      ctx.strokeStyle = c.outline;
      ctx.fillRect(-14, -11, 28, 22);
      ctx.strokeRect(-14, -11, 28, 22);
      ctx.fillStyle = V.token(s, "colors", "electric_field", "#006D77");
      for (const x of [-37, 17]) {
        ctx.fillRect(x, -10, 20, 20);
        ctx.strokeRect(x, -10, 20, 20);
      }
      ctx.beginPath();
      ctx.moveTo(0, -11);
      ctx.lineTo(0, -25);
      ctx.stroke();
      finish(ctx, s, o);
    }
    function projectile(ctx, s, o = {}) {
      body(
        ctx,
        s,
        { ...o, radius: o.radius || 9, shadow: o.shadow !== false },
        "trajectory"
      );
    }
    function cannon2(ctx, s, o = {}) {
      const c = colors(s, o, "uncertainty");
      setup(ctx, s, o);
      ctx.fillStyle = c.fill;
      ctx.strokeStyle = c.outline;
      ctx.beginPath();
      ctx.roundRect(-8, -9, o.width || 58, 18, 6);
      ctx.fill();
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(-8, 8, 14, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      finish(ctx, s, o);
    }
    function source(ctx, s, o = {}) {
      const r = o.radius || 17;
      body(ctx, s, { ...o, radius: r, label: "" }, "energy");
      ctx.save();
      ctx.strokeStyle = o.outline || V.token(s, "colors", "energy", "#B45309");
      ctx.lineWidth = 2;
      for (let i = 1; i <= 2; i++) {
        ctx.beginPath();
        ctx.arc(o.x + r * 0.45, o.y, r + i * 7, -0.7, 0.7);
        ctx.stroke();
      }
      ctx.restore();
      if (o.label) finish(ctx, s, { ...o, height: r * 2, shadow: false });
    }
    function observer(ctx, s, o = {}) {
      const r = o.radius || 15, c = colors(s, o, "accent");
      setup(ctx, s, o);
      ctx.fillStyle = c.fill;
      ctx.strokeStyle = c.outline;
      ctx.beginPath();
      ctx.arc(0, -r * 0.55, r * 0.42, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.beginPath();
      ctx.roundRect(-r * 0.6, -r * 0.05, r * 1.2, r * 1.25, r * 0.35);
      ctx.fill();
      ctx.stroke();
      finish(ctx, s, o);
    }
    function fluidContainer(ctx, s, o = {}) {
      const w = o.width || 130, h = o.height || 150, c = colors(s, o, "text");
      setup(ctx, s, o);
      ctx.strokeStyle = c.outline;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(-w / 2, -h / 2);
      ctx.lineTo(-w / 2, h / 2);
      ctx.lineTo(w / 2, h / 2);
      ctx.lineTo(w / 2, -h / 2);
      ctx.stroke();
      finish(ctx, s, o);
    }
    function fluidSurface(ctx, s, o = {}) {
      const w = o.width || 130, h = o.height || 70, c = o.fill || V.token(s, "colors", "electric_field", "#006D77");
      setup(ctx, s, o);
      ctx.fillStyle = c;
      ctx.globalAlpha *= o.fluidOpacity ?? 0.26;
      ctx.fillRect(-w / 2, 0, w, h);
      ctx.globalAlpha = (o.opacity ?? 1) * (o.disabled ? 0.45 : 1);
      ctx.strokeStyle = c;
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let x = -w / 2; x <= w / 2; x += 8)
        ctx.lineTo(x, Math.sin(x * 0.16) * 2);
      ctx.stroke();
      finish(ctx, s, o);
    }
    function lens(ctx, s, o = {}) {
      const w = o.width || 30, h = o.height || 120, c = colors(s, o, "electric_field");
      setup(ctx, s, o);
      ctx.fillStyle = c.fill;
      ctx.globalAlpha *= 0.24;
      ctx.strokeStyle = c.outline;
      ctx.beginPath();
      ctx.moveTo(0, -h / 2);
      ctx.quadraticCurveTo(w, 0, 0, h / 2);
      ctx.quadraticCurveTo(-w, 0, 0, -h / 2);
      ctx.fill();
      ctx.stroke();
      finish(ctx, s, o);
    }
    function mirror(ctx, s, o = {}) {
      const h = o.height || 120;
      setup(ctx, s, o);
      ctx.strokeStyle = o.outline || V.token(s, "colors", "text", "#152536");
      ctx.lineWidth = 5;
      ctx.beginPath();
      ctx.moveTo(0, -h / 2);
      ctx.lineTo(0, h / 2);
      ctx.stroke();
      ctx.lineWidth = 1;
      for (let y = -h / 2; y < h / 2; y += 10) {
        ctx.beginPath();
        ctx.moveTo(3, y);
        ctx.lineTo(11, y + 8);
        ctx.stroke();
      }
      finish(ctx, s, o);
    }
    function ray(ctx, s, o = {}) {
      V.arrow(
        ctx,
        s,
        point(o.x, o.y),
        o.end || point(o.x + (o.width || 100), o.y),
        {
          ...o,
          color: o.fill || V.token(s, "colors", "energy", "#B45309"),
          width: o.lineWidth || 2,
          head: o.head || 9
        }
      );
    }
    function wavefront(ctx, s, o = {}) {
      setup(ctx, s, o);
      ctx.strokeStyle = o.outline || V.token(s, "colors", "trajectory", "#1769AA");
      ctx.lineWidth = o.lineWidth || 2;
      ctx.globalAlpha *= o.opacity ?? 0.7;
      const count = o.count ?? 3, spacing = o.spacing ?? 18;
      for (let i = 0; i < count; i++) {
        ctx.beginPath();
        ctx.arc(
          0,
          0,
          (o.radius || 20) + i * spacing,
          o.startAngle ?? -0.8,
          o.endAngle ?? 0.8
        );
        ctx.stroke();
      }
      finish(ctx, s, o);
    }
    function charge(ctx, s, o = {}) {
      const positive = (o.sign ?? 1) >= 0;
      body(
        ctx,
        s,
        {
          ...o,
          fill: o.fill || V.token(
            s,
            "colors",
            positive ? "net_force" : "accent",
            positive ? "#C2410C" : "#1769AA"
          ),
          label: ""
        },
        positive ? "net_force" : "accent"
      );
      ctx.save();
      V.applyText(ctx, s, "heading");
      ctx.fillStyle = V.token(s, "colors", "text_inverse", "#FFF");
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(positive ? "+" : "\u2212", o.x, o.y);
      ctx.restore();
      if (o.label) finish(ctx, s, { ...o, shadow: false });
    }
    function fieldLine(ctx, s, o = {}) {
      const pts = o.points || [
        point(o.x, o.y),
        o.end || point(o.x + (o.width || 100), o.y)
      ];
      ctx.save();
      ctx.strokeStyle = o.outline || V.token(s, "colors", "electric_field", "#006D77");
      ctx.lineWidth = o.lineWidth || 1.5;
      ctx.globalAlpha = o.opacity ?? 0.75;
      ctx.beginPath();
      pts.forEach((p, i) => i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y));
      ctx.stroke();
      if (o.direction !== false && pts.length > 1) {
        const i = Math.floor(pts.length / 2), a = pts[Math.max(0, i - 1)], b = pts[i];
        V.arrow(ctx, s, a, b, { color: ctx.strokeStyle, width: 1.5, head: 7 });
      }
      ctx.restore();
    }
    function semanticArrow(role) {
      return (ctx, s, o = {}) => {
        const end = o.end || point(o.x + (o.width || 80), o.y), dx = end.x - o.x, dy = -(end.y - o.y);
        PhysicsAnnotations.vector(
          ctx,
          s,
          {
            ...o,
            role,
            dx,
            dy,
            scale_mode: o.scale_mode || "schematic",
            fixed_length_px: o.fixed_length_px || Math.hypot(dx, dy),
            scale_disclosure: o.scale_disclosure
          },
          1,
          o.show_disclosure !== false
        );
      };
    }
    const forceArrow = semanticArrow("net_force"), velocityArrow = semanticArrow("velocity"), accelerationArrow = semanticArrow("acceleration");
    function torqueArc(ctx, s, o = {}) {
      const r = o.radius || 42, start = o.startAngle ?? -0.8, end = o.endAngle ?? 2.8, color = o.fill || V.token(s, "colors", "net_force", "#C2410C");
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = o.lineWidth || 3;
      ctx.beginPath();
      ctx.arc(o.x, o.y, r, start, end, o.counterclockwise || false);
      ctx.stroke();
      const a = end, tip = point(o.x + Math.cos(a) * r, o.y + Math.sin(a) * r), back = point(o.x + Math.cos(a - 0.14) * r, o.y + Math.sin(a - 0.14) * r);
      V.arrow(ctx, s, back, tip, { color, width: 3, head: 10, label: o.label });
      ctx.restore();
    }
    function angleMarker(ctx, s, o = {}) {
      ctx.save();
      ctx.strokeStyle = o.outline || V.token(s, "colors", "accent", "#1769AA");
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(
        o.x,
        o.y,
        o.radius || 28,
        o.startAngle || 0,
        o.endAngle ?? Math.PI / 4
      );
      ctx.stroke();
      if (o.label) {
        V.applyText(ctx, s, "annotation");
        const a = ((o.startAngle || 0) + (o.endAngle ?? Math.PI / 4)) / 2;
        ctx.fillText(
          o.label,
          o.x + Math.cos(a) * (o.radius + 12),
          o.y + Math.sin(a) * (o.radius + 12)
        );
      }
      ctx.restore();
    }
    function ruler(ctx, s, o = {}) {
      const length = o.width || 160, div = o.divisions || 10;
      ctx.save();
      ctx.translate(o.x, o.y);
      ctx.rotate(o.rotation || 0);
      ctx.strokeStyle = o.outline || V.token(s, "colors", "text_muted", "#526577");
      ctx.fillStyle = ctx.strokeStyle;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(length, 0);
      ctx.stroke();
      V.applyText(ctx, s, "axis");
      for (let i = 0; i <= div; i++) {
        const x = i / div * length, h = i % 5 === 0 ? 10 : 6;
        ctx.beginPath();
        ctx.moveTo(x, -h / 2);
        ctx.lineTo(x, h / 2);
        ctx.stroke();
        if (o.showValues && i % 5 === 0)
          ctx.fillText(String(i / div * (o.maximum ?? length)), x - 4, 20);
      }
      ctx.restore();
    }
    function grid2(ctx, s, o = {}) {
      V.grid(
        ctx,
        s,
        { x: o.x, y: o.y, width: o.width || 200, height: o.height || 160 },
        { step: o.step, opacity: o.opacity }
      );
    }
    function trail2(ctx, s, o = {}) {
      V.trail(ctx, s, o.points || [], (p) => p, {
        color: o.fill,
        width: o.lineWidth,
        opacity: o.opacity,
        dashed: o.dashed
      });
    }
    function collisionFlash(ctx, s, o = {}) {
      const r = o.radius || 36, progress = o.progress ?? 1;
      ctx.save();
      ctx.translate(o.x, o.y);
      ctx.rotate(o.rotation || 0);
      ctx.fillStyle = o.fill || V.token(s, "colors", "warning", "#9A5B00");
      ctx.globalAlpha = (o.opacity ?? 1) * (1 - progress * 0.65);
      ctx.beginPath();
      for (let i = 0; i < 16; i++) {
        const a = i * Math.PI / 8, rr = i % 2 ? r * progress : r * 0.42 * progress;
        ctx.lineTo(Math.cos(a) * rr, Math.sin(a) * rr);
      }
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }
    function callout(ctx, s, o = {}) {
      const w = o.width || 180, h = o.height || 62, x = o.x, y = o.y;
      ctx.save();
      ctx.shadowColor = "rgba(15,23,42,.14)";
      ctx.shadowBlur = o.shadow === false ? 0 : 10;
      ctx.shadowOffsetY = 3;
      ctx.fillStyle = o.fill || V.token(s, "colors", "surface_raised", "#FFF");
      ctx.strokeStyle = o.outline || V.token(s, "colors", "border", "#B8C5D1");
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.roundRect(x, y, w, h, 12);
      ctx.fill();
      ctx.stroke();
      ctx.shadowColor = "transparent";
      if (o.target) {
        ctx.beginPath();
        ctx.moveTo(x + w * 0.2, y + h);
        ctx.lineTo(o.target.x, o.target.y);
        ctx.stroke();
      }
      V.applyText(ctx, s, "annotation");
      ctx.fillStyle = V.token(s, "colors", "text", "#152536");
      const lines = String(o.text || o.label || "").split("\n");
      lines.slice(0, 3).forEach((line, i) => ctx.fillText(line, x + 12, y + 22 + i * 17));
      ctx.restore();
    }
    const library = {
      sphere,
      mass,
      block,
      cart,
      pendulumBob,
      pivot,
      cable,
      rod,
      spring,
      ramp,
      pulley,
      lever,
      track,
      wheel,
      planet,
      moon,
      star,
      satellite,
      projectile,
      cannon: cannon2,
      source,
      observer,
      fluidContainer,
      fluidSurface,
      lens,
      mirror,
      ray,
      wavefront,
      charge,
      fieldLine,
      forceArrow,
      velocityArrow,
      accelerationArrow,
      torqueArc,
      angleMarker,
      ruler,
      grid: grid2,
      trail: trail2,
      collisionFlash,
      callout
    };
    function draw(ctx, s, spec) {
      const fn = library[spec.kind];
      if (!fn) throw new Error(`Unknown Physics Studio asset: ${spec.kind}`);
      fn(ctx, s, { ...spec, ...spec.style || {}, ...spec.options || {} });
    }
    function drawAll(ctx, s, specs) {
      for (const spec of specs || []) draw(ctx, s, spec);
    }
    return {
      ...library,
      draw,
      drawAll,
      kinds: Object.freeze(Object.keys(library))
    };
  })();
  globalThis.PhysicsAssets = PhysicsAssets;

  // src/animation.js
  var PhysicsAnimation = /* @__PURE__ */ (() => {
    const clamp2 = (value, min, max) => Math.min(max, Math.max(min, value));
    const smoothstep = (t) => {
      t = clamp2(t, 0, 1);
      return t * t * (3 - 2 * t);
    };
    class Camera {
      constructor(config = {}, reducedMotion = false) {
        this.reducedMotion = reducedMotion;
        this.current = { x: 0, y: 0, zoom: 1 };
        this.start = { ...this.current };
        this.target = { ...this.current };
        this.elapsed = 0;
        this.duration = 0;
        this.configure(config);
      }
      configure(config = {}) {
        this.current = {
          x: config.x || 0,
          y: config.y || 0,
          zoom: config.zoom || 1
        };
        this.start = { ...this.current };
        this.target = { ...this.current };
      }
      focus(target2 = {}, durationMs = 320) {
        this.start = { ...this.current };
        this.target = {
          x: target2.x ?? this.current.x,
          y: target2.y ?? this.current.y,
          zoom: clamp2(target2.zoom ?? this.current.zoom, 0.25, 8)
        };
        this.elapsed = 0;
        this.duration = this.reducedMotion ? 0 : Math.max(0, durationMs) / 1e3;
        if (!this.duration) this.current = { ...this.target };
      }
      update(seconds) {
        if (!this.duration) return;
        this.elapsed = Math.min(this.duration, this.elapsed + seconds);
        const t = smoothstep(this.elapsed / this.duration);
        for (const key of ["x", "y", "zoom"])
          this.current[key] = this.start[key] + (this.target[key] - this.start[key]) * t;
      }
      apply(ctx, width, height) {
        ctx.translate(width / 2, height / 2);
        ctx.scale(this.current.zoom, this.current.zoom);
        ctx.translate(-width / 2 - this.current.x, -height / 2 - this.current.y);
      }
      reset() {
        this.focus({ x: 0, y: 0, zoom: 1 }, 0);
      }
    }
    function withCamera(ctx, camera, width, height, draw) {
      ctx.save();
      camera.apply(ctx, width, height);
      draw();
      ctx.restore();
    }
    function fadingTrail(ctx, points, map, options = {}) {
      if (points.length < 2) return;
      ctx.save();
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      for (let i = 1; i < points.length; i++) {
        const a = map(points[i - 1]), b = map(points[i]), t = i / (points.length - 1);
        ctx.globalAlpha = (options.opacity ?? 0.3) * t * t;
        ctx.strokeStyle = options.color || "#1769AA";
        ctx.lineWidth = (options.width || 2) * (0.55 + 0.45 * t);
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }
      ctx.restore();
    }
    function subtleMotionBlur(ctx, positions, draw, options = {}) {
      const reduced = options.reducedMotion || false, count = reduced ? 0 : Math.min(options.samples ?? 3, 4);
      if (!count || positions.length < 2) {
        draw(positions.at(-1), 1);
        return;
      }
      const start = Math.max(0, positions.length - count - 1);
      for (let i = start; i < positions.length - 1; i++)
        draw(positions[i], (i - start + 1) / (positions.length - start) * 0.12);
      draw(positions.at(-1), 1);
    }
    function impactRipple(ctx, x, y, progress, options = {}) {
      if (options.reducedMotion) return;
      const t = clamp2(progress, 0, 1), radius = (options.radius || 46) * smoothstep(t);
      ctx.save();
      ctx.globalAlpha = (options.opacity ?? 0.5) * (1 - t);
      ctx.strokeStyle = options.color || "#9A5B00";
      ctx.lineWidth = options.width || 2;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
    function collisionFlash(ctx, x, y, progress, options = {}) {
      if (options.reducedMotion) return;
      PhysicsAssets.collisionFlash(
        ctx,
        { transform: { width: 0, height: 0 }, config: options.config || {} },
        {
          x,
          y,
          progress,
          radius: options.radius || 34,
          fill: options.color,
          opacity: options.opacity ?? 0.8,
          shadow: false
        }
      );
    }
    function focusTransition(camera, target2, options = {}) {
      camera.focus(
        target2,
        options.reducedMotion ? 0 : options.durationMs ?? 320
      );
    }
    return {
      Camera,
      withCamera,
      fadingTrail,
      subtleMotionBlur,
      impactRipple,
      collisionFlash,
      focusTransition,
      smoothstep
    };
  })();
  globalThis.PhysicsAnimation = PhysicsAnimation;

  // src/player-runtime.js
  function clamp(value, minimum, maximum) {
    return Math.min(maximum, Math.max(minimum, value));
  }
  function lerp(a, b, amount) {
    return a + (b - a) * amount;
  }
  function sample(values, fraction) {
    if (!Array.isArray(values) || values.length === 0) return 0;
    const index = clamp(fraction, 0, 1) * (values.length - 1);
    const lower = Math.floor(index);
    const upper = Math.min(values.length - 1, lower + 1);
    return lerp(values[lower], values[upper], index - lower);
  }
  function validatePlayerConfig(config) {
    if (!config || typeof config !== "object" || Array.isArray(config)) {
      throw new TypeError("Player payload must be an object.");
    }
    if (!Number.isFinite(config.durationMs) || config.durationMs <= 0) {
      throw new TypeError("Player payload requires a positive durationMs.");
    }
    if (!Array.isArray(config.tracks)) {
      throw new TypeError("Player payload requires a tracks array.");
    }
    for (const track of config.tracks) {
      if (!track || typeof track.id !== "string" || !Array.isArray(track.x)) {
        throw new TypeError(
          "Each player track requires a string id and x array."
        );
      }
    }
    return config;
  }
  function resolveVisualTheme(config, media = globalThis.matchMedia) {
    const requested = config.theme || "auto";
    const prefersDark = requested === "auto" && typeof media === "function" && media("(prefers-color-scheme: dark)").matches;
    const dark = requested === "dark" || prefersDark;
    config.resolvedTheme = dark ? "dark" : "light";
    config.visualTokens = (config.visualThemes || {})[config.resolvedTheme] || config.visualTokens || {};
    if (globalThis.document?.documentElement) {
      document.documentElement.dataset.psTheme = config.resolvedTheme;
    }
    return config.resolvedTheme;
  }
  function seededRandom(seed) {
    let state = seed >>> 0 || 1;
    return function random() {
      state += 1831565813;
      let value = state;
      value = Math.imul(value ^ value >>> 15, value | 1);
      value ^= value + Math.imul(value ^ value >>> 7, value | 61);
      return ((value ^ value >>> 14) >>> 0) / 4294967296;
    };
  }
  var PlaybackState = class {
    constructor(config) {
      this.config = validatePlayerConfig(config);
      this.fraction = 0;
      this.state = "idle";
      this.playbackRate = 1;
    }
    play() {
      if (this.state === "done") this.fraction = 0;
      this.state = "playing";
    }
    pause() {
      this.state = "paused";
    }
    seek(fraction) {
      this.fraction = clamp(fraction, 0, 1);
      if (this.fraction < 1 && this.state === "done") this.state = "paused";
      return this.fraction;
    }
    frameCount() {
      return Math.max(
        2,
        this.config.frameCount || 0,
        ...this.config.tracks.map(
          (track) => Math.max(track.x?.length || 0, track.y?.length || 0)
        )
      );
    }
    stepFrames(amount) {
      this.pause();
      const count = this.frameCount();
      const index = Math.round(this.fraction * (count - 1));
      return this.seek(clamp(index + amount, 0, count - 1) / (count - 1));
    }
    advance(seconds) {
      if (this.state !== "playing") return this.fraction;
      this.fraction = clamp(
        this.fraction + seconds * this.playbackRate / (this.config.durationMs / 1e3),
        0,
        1
      );
      if (this.fraction >= 1) this.state = "done";
      return this.fraction;
    }
  };
  var ParticleSystem = class {
    constructor(random, reducedMotion) {
      this.items = [];
      this.random = random;
      this.reducedMotion = reducedMotion;
    }
    burst(x, y, count, colors) {
      if (this.reducedMotion) return;
      for (let index = 0; index < count; index += 1) {
        const angle = this.random() * Math.PI * 2;
        const speed = 90 + this.random() * 210;
        this.items.push({
          x,
          y,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed - 80,
          life: 1,
          size: 2 + this.random() * 3,
          color: colors[Math.floor(this.random() * colors.length)]
        });
      }
    }
    reset() {
      this.items = [];
    }
    update(seconds) {
      for (const item of this.items) {
        item.x += item.vx * seconds;
        item.y += item.vy * seconds;
        item.vy += 320 * seconds;
        item.life -= 1.6 * seconds;
      }
      this.items = this.items.filter((item) => item.life > 0);
    }
    draw(ctx) {
      for (const item of this.items) {
        ctx.globalAlpha = Math.max(0, item.life);
        ctx.fillStyle = item.color;
        ctx.beginPath();
        ctx.arc(item.x, item.y, item.size, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
    }
  };
  var TrailStore = class {
    constructor(limit = 18) {
      this.limit = limit;
      this.items = /* @__PURE__ */ new Map();
    }
    reset() {
      this.items.clear();
    }
    push(id, point) {
      const points = this.items.get(id) || [];
      points.push(point);
      while (points.length > this.limit) points.shift();
      this.items.set(id, points);
    }
    get(id) {
      return this.items.get(id) || [];
    }
  };
  var AnimationPlayer = class {
    constructor(config, scene2, environment = globalThis) {
      this.environment = environment;
      this.config = validatePlayerConfig(config);
      this.scene = scene2;
      this.canvas = document.getElementById("animation-canvas");
      this.ctx = this.canvas?.getContext("2d");
      this.wrap = document.getElementById("canvas-wrap");
      this.playButton = document.getElementById("play-pause");
      this.replayButton = document.getElementById("replay");
      this.stepBackButton = document.getElementById("step-back");
      this.stepForwardButton = document.getElementById("step-forward");
      this.scrubber = document.getElementById("scrubber");
      this.speed = document.getElementById("speed");
      this.message = document.getElementById("message");
      this.hint = document.getElementById("hint");
      this.status = document.getElementById("status");
      this.reducedMotion = Boolean(config.reducedMotion) || Boolean(
        environment.matchMedia?.("(prefers-reduced-motion: reduce)").matches
      );
      document.body.classList.toggle(
        "high-contrast",
        Boolean(config.highContrast)
      );
      document.body.classList.toggle("large-text", Boolean(config.largeText));
      this.random = seededRandom(config.seed);
      this.particles = new ParticleSystem(this.random, this.reducedMotion);
      this.trails = new TrailStore(config.trailLength || 18);
      this.playback = new PlaybackState(config);
      this.lastTimestamp = null;
      this.fired = /* @__PURE__ */ new Set();
      this.frameRequest = null;
      this.cssWidth = 1;
      this.cssHeight = 1;
      this.lastTrailFraction = null;
      this.fixedStep = 1 / 60;
      this.accumulator = 0;
      this.camera = new PhysicsAnimation.Camera(
        config.camera || {},
        this.reducedMotion
      );
      this.boundPageHide = () => this.destroy();
      this.bind();
      this.resize();
      this.render(0);
      if (config.autoplay && !this.reducedMotion) this.play();
      else if (config.autoplay && this.reducedMotion) {
        this.status.textContent = "Reduced motion is enabled. Press Play to start the animation.";
      }
    }
    get fraction() {
      return this.playback.fraction;
    }
    set fraction(value) {
      this.playback.fraction = value;
    }
    get state() {
      return this.playback.state;
    }
    set state(value) {
      this.playback.state = value;
    }
    get playbackRate() {
      return this.playback.playbackRate;
    }
    set playbackRate(value) {
      this.playback.playbackRate = value;
    }
    bind() {
      this.onPlay = () => this.toggle();
      this.onReplay = () => this.replay();
      this.onStepBack = () => this.stepFrames(-1);
      this.onStepForward = () => this.stepFrames(1);
      this.onScrub = (event) => this.seek(Number(event.target.value) / 1e3);
      this.onSpeed = (event) => {
        this.playbackRate = Number(event.target.value);
      };
      this.playButton.addEventListener("click", this.onPlay);
      this.replayButton.addEventListener("click", this.onReplay);
      this.stepBackButton.addEventListener("click", this.onStepBack);
      this.stepForwardButton.addEventListener("click", this.onStepForward);
      this.scrubber.addEventListener("input", this.onScrub);
      this.speed.addEventListener("change", this.onSpeed);
      this.resizeObserver = new this.environment.ResizeObserver(
        () => this.resize()
      );
      this.resizeObserver.observe(this.wrap);
      this.onVisibility = () => {
        if (document.hidden && this.state === "playing") this.pause();
      };
      document.addEventListener("visibilitychange", this.onVisibility);
      this.onKeydown = (event) => {
        if (["INPUT", "SELECT", "BUTTON"].includes(document.activeElement.tagName))
          return;
        if (event.key === " ") {
          event.preventDefault();
          this.toggle();
        } else if (event.key.toLowerCase() === "r") this.replay();
        else if (event.key === "ArrowRight") this.seek(this.fraction + 0.02);
        else if (event.key === "ArrowLeft") this.seek(this.fraction - 0.02);
        else if (event.key === "." || event.key === ">") this.stepFrames(1);
        else if (event.key === "," || event.key === "<") this.stepFrames(-1);
      };
      document.addEventListener("keydown", this.onKeydown);
      this.environment.addEventListener("pagehide", this.boundPageHide, {
        once: true
      });
    }
    resize() {
      const box = this.wrap.getBoundingClientRect();
      const dpr = Math.min(
        this.config.maximumDpr || 2.5,
        Math.max(1, this.environment.devicePixelRatio || 1)
      );
      const nextWidth = Math.max(1, box.width);
      const nextHeight = Math.max(1, box.height);
      if (Math.abs(nextWidth - this.cssWidth) < 0.5 && Math.abs(nextHeight - this.cssHeight) < 0.5 && this.canvas.width === Math.round(nextWidth * dpr))
        return;
      this.cssWidth = nextWidth;
      this.cssHeight = nextHeight;
      this.canvas.width = Math.round(this.cssWidth * dpr);
      this.canvas.height = Math.round(this.cssHeight * dpr);
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.render(this.fraction);
    }
    coordinates() {
      const view = this.config.view || {};
      const xmin = view.minimum ?? 0;
      const xmax = view.maximum ?? 1;
      const left = 40;
      const right = this.cssWidth - 40;
      return {
        x: (value) => left + (value - xmin) / Math.max(1e-4, xmax - xmin) * (right - left),
        y: (value) => this.cssHeight - 60 - value,
        width: this.cssWidth,
        height: this.cssHeight
      };
    }
    snapshot(fraction) {
      const tracks = {};
      for (const track of this.config.tracks) {
        tracks[track.id] = {
          id: track.id,
          label: track.label,
          style: track.style || {},
          x: sample(track.x, fraction),
          y: track.y ? sample(track.y, fraction) : null,
          trail: this.trails.get(track.id)
        };
      }
      return tracks;
    }
    play() {
      if (this.state === "done") this.replay();
      this.playback.play();
      this.lastTimestamp = null;
      this.playButton.textContent = "\u23F8";
      this.playButton.setAttribute("aria-label", "Pause animation");
      this.hint.hidden = true;
      this.status.textContent = "Animation playing";
      this.ensureFrame();
    }
    pause() {
      this.playback.pause();
      this.playButton.textContent = "\u25B6";
      this.playButton.setAttribute("aria-label", "Play animation");
      this.status.textContent = "Animation paused";
    }
    resume() {
      this.play();
    }
    toggle() {
      this.state === "playing" ? this.pause() : this.play();
    }
    replay() {
      this.fraction = 0;
      this.fired.clear();
      this.trails.reset();
      this.particles.reset();
      this.camera.reset();
      this.lastTrailFraction = null;
      this.message.classList.remove("show");
      this.scrubber.value = "0";
      this.scrubber.setAttribute("aria-valuetext", "0 percent");
      this.state = "paused";
      this.play();
    }
    seek(fraction) {
      this.playback.seek(fraction);
      this.scrubber.value = String(Math.round(this.fraction * 1e3));
      this.scrubber.setAttribute(
        "aria-valuetext",
        `${Math.round(this.fraction * 100)} percent`
      );
      this.fired.clear();
      for (const event of this.config.events || []) {
        if (event.fraction <= this.fraction) this.fired.add(event.id);
      }
      this.trails.reset();
      this.particles.reset();
      this.lastTrailFraction = null;
      if (this.fraction < 1) this.message.classList.remove("show");
      this.render(this.fraction);
      this.status.textContent = `Animation at ${Math.round(this.fraction * 100)} percent`;
    }
    frameCount() {
      return this.playback.frameCount();
    }
    stepFrames(amount) {
      const fraction = this.playback.stepFrames(amount);
      this.seek(fraction);
      const count = this.frameCount();
      this.status.textContent = `Frame ${Math.round(this.fraction * (count - 1)) + 1} of ${count}`;
    }
    ensureFrame() {
      if (this.frameRequest === null) {
        this.frameRequest = this.environment.requestAnimationFrame(
          (timestamp) => this.tick(timestamp)
        );
      }
    }
    tick(timestamp) {
      this.frameRequest = null;
      const rawElapsed = this.lastTimestamp === null ? 0 : (timestamp - this.lastTimestamp) / 1e3;
      const elapsed = clamp(rawElapsed, 0, 0.25);
      this.lastTimestamp = timestamp;
      this.accumulator += elapsed;
      let stableElapsed = 0;
      let steps = 0;
      while (this.accumulator >= this.fixedStep && steps < 15) {
        stableElapsed += this.fixedStep;
        this.accumulator -= this.fixedStep;
        steps += 1;
      }
      if (this.state === "playing") {
        const previous = this.fraction;
        this.playback.advance(stableElapsed);
        this.fireEvents();
        this.scrubber.value = String(Math.round(this.fraction * 1e3));
        this.scrubber.setAttribute(
          "aria-valuetext",
          `${Math.round(this.fraction * 100)} percent`
        );
        if (previous < 1 && this.fraction >= 1) this.complete();
      }
      this.camera.update(stableElapsed);
      this.particles.update(stableElapsed);
      this.render(this.fraction);
      if (this.state === "playing" || this.particles.items.length)
        this.ensureFrame();
    }
    fireEvents() {
      for (const event of this.config.events || []) {
        if (this.fraction >= event.fraction && !this.fired.has(event.id)) {
          this.fired.add(event.id);
          if (this.scene.onEvent) this.scene.onEvent(event, this);
        }
      }
    }
    complete() {
      this.state = "done";
      this.playButton.textContent = "\u25B6";
      this.playButton.setAttribute("aria-label", "Replay animation");
      this.message.textContent = this.config.completionMessage || "";
      this.message.classList.toggle(
        "show",
        Boolean(this.config.completionMessage)
      );
      this.status.textContent = this.config.completionMessage || "Animation complete";
    }
    render(fraction) {
      if (!this.scene || !this.ctx) return;
      const transform = this.coordinates();
      const tracks = this.snapshot(fraction);
      if (this.lastTrailFraction === null || Math.abs(fraction - this.lastTrailFraction) > 1e-9) {
        for (const track of Object.values(tracks)) {
          this.trails.push(track.id, { x: track.x, y: track.y });
        }
        this.lastTrailFraction = fraction;
      }
      this.scene.draw(this.ctx, {
        fraction,
        state: this.state,
        tracks,
        transform,
        particles: this.particles,
        trails: this.trails,
        reducedMotion: this.reducedMotion,
        config: this.config,
        camera: this.camera,
        effects: PhysicsAnimation
      });
      this.particles.draw(this.ctx);
    }
    destroy() {
      if (this.frameRequest !== null) {
        this.environment.cancelAnimationFrame(this.frameRequest);
      }
      this.frameRequest = null;
      this.resizeObserver?.disconnect();
      this.playButton.removeEventListener("click", this.onPlay);
      this.replayButton.removeEventListener("click", this.onReplay);
      this.stepBackButton.removeEventListener("click", this.onStepBack);
      this.stepForwardButton.removeEventListener("click", this.onStepForward);
      this.scrubber.removeEventListener("input", this.onScrub);
      this.speed.removeEventListener("change", this.onSpeed);
      document.removeEventListener("visibilitychange", this.onVisibility);
      document.removeEventListener("keydown", this.onKeydown);
      this.environment.removeEventListener("pagehide", this.boundPageHide);
      this.particles.reset();
      this.trails.reset();
    }
  };
  function mountPlayer(config, scene2, environment = globalThis) {
    validatePlayerConfig(config);
    resolveVisualTheme(config, environment.matchMedia?.bind(environment));
    return new AnimationPlayer(config, scene2, environment);
  }
  Object.assign(globalThis, {
    AnimationPlayer,
    ParticleSystem,
    PhysicsAnimation,
    PhysicsAnnotations,
    PhysicsAssets,
    PhysicsExperience,
    PhysicsVisuals,
    TrailStore,
    clamp,
    lerp,
    mountPhysicsPlayer: mountPlayer,
    resolveVisualTheme,
    sample,
    seededRandom
  });

  // src/scenes/scene-api.js
  var PhysicsAnimation2 = globalThis.PhysicsAnimation;
  var PhysicsAnnotations2 = globalThis.PhysicsAnnotations;
  var PhysicsAssets2 = globalThis.PhysicsAssets;
  var PhysicsExperience2 = globalThis.PhysicsExperience;
  var PhysicsVisuals2 = globalThis.PhysicsVisuals;
  var sample2 = globalThis.sample;

  // src/scenes/mechanics/cannonball.js
  function mapPoint(x, y, view, t) {
    const left = 40, right = t.width - 25, ground = t.height - 46, top = 25;
    return {
      x: left + (x - view.xMin) / Math.max(1e-3, view.xMax - view.xMin) * (right - left),
      y: ground - (y - view.yMin) / Math.max(1e-3, view.yMax - view.yMin) * (ground - top)
    };
  }
  function sky(ctx, t, frame) {
    const ground = t.height - 46, mode = PhysicsExperience2.context(ctx, frame, "projectileField");
    if (!mode.environment) {
      ctx.fillStyle = PhysicsVisuals2.token(
        frame,
        "colors",
        "surface_muted",
        "#EAF0F6"
      );
      ctx.fillRect(0, ground, t.width, t.height - ground);
    }
  }
  function cannon(ctx, t, angle, frame) {
    const p = mapPoint(0, 0, t.config.view, t);
    PhysicsAssets2.cannon(ctx, frame, {
      x: p.x,
      y: p.y - 3,
      width: 48,
      rotation: -angle * Math.PI / 180,
      fill: PhysicsVisuals2.token(frame, "colors", "uncertainty", "#64748B"),
      highlight: true,
      shadow: true,
      label: PhysicsVisuals2.responsive(frame) === "mobile" ? "" : "Launcher"
    });
  }
  function target(ctx, t, frame) {
    const p = mapPoint(t.config.target, 0, t.config.view, t), surface = PhysicsVisuals2.token(frame, "colors", "surface", "#FFF"), accent = PhysicsVisuals2.token(frame, "colors", "net_force", "#C2410C");
    ctx.fillStyle = surface;
    ctx.beginPath();
    ctx.arc(p.x, p.y - 18, 17, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = accent;
    ctx.beginPath();
    ctx.arc(p.x, p.y - 18, 11, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = surface;
    ctx.beginPath();
    ctx.arc(p.x, p.y - 18, 5, 0, Math.PI * 2);
    ctx.fill();
  }
  var scene = {
    onEvent(event, player) {
      if (event.type === "impact") {
        const track = player.config.tracks[event.track];
        const t = player.coordinates();
        const p = mapPoint(
          sample2(track.x, event.fraction),
          sample2(track.y, event.fraction),
          player.config.view,
          t
        );
        player.particles.burst(p.x, p.y, event.count, event.colors);
      }
    },
    draw(ctx, frame) {
      const t = { ...frame.transform, config: frame.config };
      sky(ctx, t, frame);
      cannon(ctx, t, frame.config.angle, frame);
      target(ctx, t, frame);
      for (const track of Object.values(frame.tracks)) {
        const points = frame.trails.get(track.id);
        PhysicsAnimation2.fadingTrail(
          ctx,
          points,
          (q) => mapPoint(q.x, q.y || 0, frame.config.view, t),
          {
            color: track.style.color || PhysicsVisuals2.token(frame, "colors", "trajectory", "#1769AA"),
            width: 2.5,
            opacity: 0.42
          }
        );
        const p = mapPoint(track.x, track.y || 0, frame.config.view, t);
        PhysicsAssets2.projectile(ctx, frame, {
          x: p.x,
          y: p.y,
          radius: 8,
          fill: track.style.color || PhysicsVisuals2.token(frame, "colors", "trajectory", "#1769AA"),
          highlight: true,
          shadow: true,
          label: frame.config.tracks.length > 1 && PhysicsVisuals2.responsive(frame) !== "mobile" ? track.label : ""
        });
      }
    }
  };
  globalThis.scene = scene;

  // src/linked-projectile.js
  var QUANTITY_COLORS = Object.freeze({
    position: "#0072B2",
    velocity: "#D55E00",
    acceleration: "#00875A",
    horizontal: "#6F4E7C",
    vertical: "#C43C39"
  });
  var FRONTEND_PROTOCOL = "physics-studio.frontend";
  var FRONTEND_PROTOCOL_VERSION = 1;
  function validateFrontendEnvelope(envelope) {
    if (!envelope || typeof envelope !== "object" || Array.isArray(envelope))
      throw new TypeError("Frontend protocol envelope must be an object.");
    if (envelope.protocol !== FRONTEND_PROTOCOL || envelope.version !== FRONTEND_PROTOCOL_VERSION)
      throw new TypeError("Unsupported frontend protocol version.");
    if (!envelope.simulation?.id || !envelope.simulation?.modelVersion || envelope.representation?.kind !== "linked-projectile" || envelope.representation?.version !== 1)
      throw new TypeError("Invalid linked-projectile protocol metadata.");
    const config = envelope.payload;
    const runs = config?.representations?.runs;
    if (!Number.isFinite(config?.durationMs) || config.durationMs <= 0)
      throw new TypeError("Linked-projectile duration must be positive.");
    if (!Array.isArray(runs) || !runs.length || !Array.isArray(config.tracks))
      throw new TypeError("Linked-projectile runs and tracks are required.");
    if (runs.length !== config.tracks.length)
      throw new TypeError("Linked-projectile runs and tracks must correspond.");
    const keys = [
      "time_s",
      "x_m",
      "y_m",
      "vx_m_s",
      "vy_m_s",
      "ax_m_s2",
      "ay_m_s2"
    ];
    runs.forEach((run) => {
      const arrays = keys.map((key) => run[key]);
      if (!run.label || arrays.some(
        (values) => !Array.isArray(values) || !values.length || values.some((value) => !Number.isFinite(value))
      ) || new Set(arrays.map((values) => values.length)).size !== 1 || run.time_s.some(
        (time, index) => index > 0 && time <= run.time_s[index - 1]
      ))
        throw new TypeError("Linked-projectile run samples are invalid.");
    });
    return config;
  }
  function nearestIndex(times, time) {
    if (!times.length) return 0;
    let best = 0;
    for (let index = 1; index < times.length; index += 1) {
      if (Math.abs(times[index] - time) < Math.abs(times[best] - time))
        best = index;
    }
    return best;
  }
  function stateAt(run, fraction) {
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
      ay: run.ay_m_s2[index]
    };
  }
  function sharedDomains(runs) {
    const values = (key) => runs.flatMap((run) => run[key]);
    const extent = (items, includeZero = true) => {
      const low = Math.min(...items, ...includeZero ? [0] : []);
      const high = Math.max(...items, ...includeZero ? [0] : []);
      const padding = Math.max((high - low) * 0.08, 0.1);
      return [low - padding, high + padding];
    };
    return {
      time: [0, Math.max(...values("time_s"))],
      position: extent([...values("x_m"), ...values("y_m")]),
      velocity: extent([...values("vx_m_s"), ...values("vy_m_s")]),
      acceleration: extent([...values("ax_m_s2"), ...values("ay_m_s2")])
    };
  }
  function fractionFromGraphPointer(clientX, left, width) {
    return Math.min(1, Math.max(0, (clientX - left) / Math.max(width, 1)));
  }
  function keyboardFraction(fraction, key, frameCount) {
    if (key === "Home") return 0;
    if (key === "End") return 1;
    const step = 1 / Math.max(frameCount - 1, 1);
    if (key === "ArrowRight") return Math.min(1, fraction + step);
    if (key === "ArrowLeft") return Math.max(0, fraction - step);
    return fraction;
  }
  function accessibleReadout(runs, fraction) {
    return runs.map((run) => {
      const state = stateAt(run, fraction);
      return `${run.label}: t ${state.time.toFixed(2)} s; position x ${state.x.toFixed(2)} m, y ${state.y.toFixed(2)} m; velocity vx ${state.vx.toFixed(2)} m/s, vy ${state.vy.toFixed(2)} m/s; acceleration ax ${state.ax.toFixed(2)} m/s\xB2, ay ${state.ay.toFixed(2)} m/s\xB2.`;
    }).join(" ");
  }
  function svg(name, attrs = {}) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", name);
    Object.entries(attrs).forEach(
      ([key, value]) => node.setAttribute(key, value)
    );
    return node;
  }
  var LinkedProjectileRuntime = class {
    constructor(config, environment = globalThis) {
      this.config = config;
      this.environment = environment;
      this.runs = config.representations.runs;
      this.domains = sharedDomains(this.runs);
      this.selectedQuantity = null;
      this.graphs = [...document.querySelectorAll("svg.linked-graph")];
      this.readout = document.getElementById("linked-readout");
      this.announcement = document.getElementById("linked-announcement");
      this.equationButtons = [
        ...document.querySelectorAll("button.equation-term")
      ];
      this.destroyed = false;
      this.drawGraphs();
      this.player = mountPlayer(config, scene, environment);
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
        acceleration: ["ax_m_s2", "ay_m_s2", "Acceleration (m/s\xB2)"]
      };
      for (const graph of this.graphs) {
        const quantity = graph.dataset.quantity;
        const [xKey, yKey, label] = specifications[quantity];
        graph.setAttribute(
          "aria-label",
          `${label} versus time. Use arrow keys to inspect time values.`
        );
        const width = 420, height = 190, left = 46, right = 12, top = 18, bottom = 34;
        const [t0, t1] = this.domains.time;
        const [q0, q1] = this.domains[quantity];
        const X = (value) => left + (value - t0) / Math.max(t1 - t0, 1e-9) * (width - left - right);
        const Y = (value) => height - bottom - (value - q0) / Math.max(q1 - q0, 1e-9) * (height - top - bottom);
        graph.replaceChildren();
        graph.append(
          svg("line", {
            x1: left,
            x2: width - right,
            y1: Y(0),
            y2: Y(0),
            class: "zero"
          })
        );
        this.runs.forEach((run, runIndex) => {
          [
            [xKey, "horizontal"],
            [yKey, "vertical"]
          ].forEach(([key, component]) => {
            graph.append(
              svg("polyline", {
                points: run.time_s.map((time, index) => `${X(time)},${Y(run[key][index])}`).join(" "),
                class: `quantity-line ${component} run-${runIndex}`,
                "data-quantity": quantity
              })
            );
          });
        });
        const cursor = svg("line", {
          class: "graph-cursor",
          y1: top,
          y2: height - bottom
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
      this.seekFromGraph = (event, announce) => {
        const graph = event.currentTarget;
        const box = graph.getBoundingClientRect();
        const fraction = fractionFromGraphPointer(
          event.clientX,
          box.left,
          box.width
        );
        this.player.pause();
        this.player.seek(fraction);
        if (announce) this.announce(fraction);
      };
      this.onGraphPointer = (event) => this.seekFromGraph(event, false);
      this.onGraphSelect = (event) => this.seekFromGraph(event, true);
      this.onGraphKey = (event) => {
        if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) {
          event.preventDefault();
          this.player.pause();
          this.player.seek(
            keyboardFraction(
              this.player.fraction,
              event.key,
              this.player.frameCount()
            )
          );
          this.announce(this.player.fraction);
        }
      };
      this.graphs.forEach((graph) => {
        graph.addEventListener("pointermove", this.onGraphPointer);
        graph.addEventListener("click", this.onGraphSelect);
        graph.addEventListener("keydown", this.onGraphKey);
      });
      this.onEquation = (event) => {
        this.selectedQuantity = event.currentTarget.dataset.quantity;
        document.body.dataset.highlightQuantity = this.selectedQuantity;
        this.update(this.player.fraction);
      };
      this.equationButtons.forEach(
        (button) => button.addEventListener("click", this.onEquation)
      );
      this.onScrubberCommit = () => this.announce(this.player.fraction);
      this.player.scrubber.addEventListener("change", this.onScrubberCommit);
      this.onPageHide = () => this.destroy();
      this.environment.addEventListener("pagehide", this.onPageHide, {
        once: true
      });
    }
    update(fraction) {
      const time = sample(this.runs[0].time_s, fraction);
      this.graphs.forEach((graph) => {
        const left = Number(graph.dataset.left), right = Number(graph.dataset.right);
        const cursor = graph.querySelector(".graph-cursor");
        const x = left + fraction * (right - left);
        cursor.setAttribute("x1", x);
        cursor.setAttribute("x2", x);
      });
      const readout = accessibleReadout(this.runs, fraction);
      this.readout.textContent = readout;
      this.player.scrubber.setAttribute(
        "aria-valuetext",
        `Time ${time.toFixed(2)} seconds. ${readout}`
      );
    }
    announce(fraction) {
      this.announcement.textContent = `Selected state. ${accessibleReadout(this.runs, fraction)}`;
    }
    destroy() {
      if (this.destroyed) return;
      this.destroyed = true;
      this.graphs.forEach((graph) => {
        graph.removeEventListener("pointermove", this.onGraphPointer);
        graph.removeEventListener("click", this.onGraphSelect);
        graph.removeEventListener("keydown", this.onGraphKey);
      });
      this.equationButtons.forEach(
        (button) => button.removeEventListener("click", this.onEquation)
      );
      this.player.scrubber.removeEventListener("change", this.onScrubberCommit);
      this.environment.removeEventListener("pagehide", this.onPageHide);
      this.player.destroy();
    }
  };
  function mountLinkedProjectile(envelope, environment = globalThis) {
    return new LinkedProjectileRuntime(
      validateFrontendEnvelope(envelope),
      environment
    );
  }
  Object.assign(globalThis, { LinkedProjectileRuntime, mountLinkedProjectile });
})();
