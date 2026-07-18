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
    function cannon(ctx, s, o = {}) {
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
      cannon,
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
      const target = 40 / scale, power = 10 ** Math.floor(Math.log10(target)), reference = [1, 2, 5, 10].map((value) => value * power).reduce(
        (best, value) => Math.abs(value - target) < Math.abs(best - target) ? value : best
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
})();
