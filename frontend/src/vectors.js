import { PhysicsAssets } from "./assets.js";
import { PhysicsVisuals } from "./physics-visuals.js";

export const PhysicsAnnotations = (() => {
  const V = PhysicsVisuals;
  const p = (x, y) => ({ x, y });
  const disclosureText = {
    normalized: "Vector lengths normalized for visibility",
    schematic: "Schematic vectors — not drawn to scale",
  };
  function endpoint(spec, progress = 1) {
    const mag = Math.hypot(spec.dx || 0, spec.dy || 0),
      ux = mag ? spec.dx / mag : 0,
      uy = mag ? -spec.dy / mag : 0;
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
    const pad = 8,
      h = 26,
      w = Math.min(
        s.transform.width - 24,
        ctx.measureText(value).width + pad * 2,
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
  function vector(ctx, s, spec, progress = 1, showDisclosure = true) {
    const end = endpoint(spec, progress),
      role = spec.role || "net_force";
    V.arrow(ctx, s, p(spec.x, spec.y), end, {
      role,
      color: spec.color,
      label: spec.label,
      dashed: spec.dashed || false,
      width: spec.line_width,
    });
    if (showDisclosure)
      disclosure(ctx, s, spec.scale_mode, spec.scale_disclosure);
  }
  function vectorSet(
    ctx,
    s,
    specs,
    progress = 1,
    originDisclosure = p(12, 12),
  ) {
    const modes = new Set();
    for (const spec of specs || []) {
      vector(ctx, s, spec, progress, false);
      if (spec.scale_mode !== "physical") modes.add(spec.scale_mode);
    }
    if (modes.size) {
      const mode = modes.has("schematic") ? "schematic" : "normalized";
      disclosure(ctx, s, mode, "", originDisclosure.x, originDisclosure.y);
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
    const a = p(o.x, o.y),
      b = o.end || p(o.x + (o.width || 100), o.y),
      color = o.color || V.token(s, "colors", "text_muted", "#526577"),
      tick = o.tick || 8;
    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.stroke();
    const angle = Math.atan2(b.y - a.y, b.x - a.x),
      nx = (-Math.sin(angle) * tick) / 2,
      ny = (Math.cos(angle) * tick) / 2;
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
        (a.y + b.y) / 2 + ny * 1.8,
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
    points.forEach((q, i) => (i ? ctx.lineTo(q.x, q.y) : ctx.moveTo(q.x, q.y)));
    ctx.stroke();
    ctx.restore();
  }
  function normalLine(ctx, s, o = {}) {
    const length = o.length || 70,
      angle = (o.surface_angle || 0) - Math.PI / 2;
    pathGuide(ctx, s, {
      points: [
        p(
          o.x - (Math.cos(angle) * length) / 2,
          o.y - (Math.sin(angle) * length) / 2,
        ),
        p(
          o.x + (Math.cos(angle) * length) / 2,
          o.y + (Math.sin(angle) * length) / 2,
        ),
      ],
      color: o.color,
      dashes: [5, 5],
    });
    if (o.label) {
      ctx.save();
      V.applyText(ctx, s, "annotation");
      ctx.fillText(
        o.label,
        o.x + Math.cos(angle) * length * 0.58,
        o.y + Math.sin(angle) * length * 0.58,
      );
      ctx.restore();
    }
  }
  function centerOfMass(ctx, s, o = {}) {
    const r = o.radius || 10,
      color = o.color || V.token(s, "colors", "selected", "#7C3AED");
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
      dashed: o.dashed,
    });
    if (o.direction !== false && points.length > 1) {
      const b = points.at(-1),
        a = points[Math.max(0, points.length - 3)];
      V.arrow(ctx, s, a, b, {
        color: o.color || V.token(s, "colors", "velocity", "#087EA4"),
        width: 2,
        head: 8,
      });
    }
  }
  function motionDirection(ctx, s, o = {}) {
    const end = o.end || p(o.x + (o.length || 44), o.y),
      dx = end.x - o.x,
      dy = -(end.y - o.y);
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
        scale_disclosure:
          o.scale_disclosure || "Motion-direction indicator is schematic",
      },
      1,
      o.show_disclosure !== false,
    );
  }
  return {
    endpoint,
    disclosure,
    vector,
    vectorSet,
    forceDiagram,
    angleArc,
    dimensionLine,
    pathGuide,
    normalLine,
    centerOfMass,
    velocityTrail,
    motionDirection,
  };
})();

globalThis.PhysicsAnnotations = PhysicsAnnotations;
