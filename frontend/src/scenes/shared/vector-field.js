import {
  PhysicsAnnotations,
  PhysicsAssets,
  PhysicsExperience,
  PhysicsVisuals,
} from "../scene-api.js";

const scene = {
  draw(ctx, s) {
    const w = s.transform.width,
      h = s.transform.height,
      c = s.config.vectorField || {},
      n = c.gridSize || 1,
      pad = 38,
      cellW = (w - 2 * pad) / Math.max(1, n - 1),
      cellH = (h - 2 * pad) / Math.max(1, n - 1),
      X = (x) => pad + ((x + c.extent) / (2 * c.extent)) * (w - 2 * pad),
      Y = (y) => h - pad - ((y + c.extent) / (2 * c.extent)) * (h - 2 * pad);
    PhysicsExperience.context(ctx, s, "laboratory");
    PhysicsAssets.grid(ctx, s, {
      x: pad,
      y: pad,
      width: w - 2 * pad,
      height: h - 2 * pad,
      step: Math.max(24, (w - 2 * pad) / 8),
      opacity: PhysicsExperience.level(s) === "diagram" ? 0.2 : 0.12,
    });
    for (const p of c.samples) {
      const ratio = Math.min(1, Math.abs(p.v) / c.potentialLimit),
        color = PhysicsVisuals.token(
          s,
          "colors",
          p.v >= 0 ? "graph_2" : "graph_1",
          p.v >= 0 ? "#D55E00" : "#0072B2",
        );
      ctx.save();
      ctx.globalAlpha = 0.06 + 0.22 * ratio;
      ctx.fillStyle = color;
      ctx.fillRect(
        X(p.x) - cellW / 2,
        Y(p.y) - cellH / 2,
        cellW + 1,
        cellH + 1,
      );
      ctx.restore();
    }
    for (const p of c.excluded) {
      const x = X(p.x),
        y = Y(p.y);
      ctx.save();
      ctx.strokeStyle = PhysicsVisuals.token(s, "colors", "warning", "#9A5B00");
      ctx.globalAlpha = 0.7;
      ctx.lineWidth = 1;
      for (let d = -cellW / 2; d < cellW / 2; d += 5) {
        ctx.beginPath();
        ctx.moveTo(x + d, y - cellH / 2);
        ctx.lineTo(x + d + cellH, y + cellH / 2);
        ctx.stroke();
      }
      ctx.restore();
    }
    const reveal = s.reducedMotion ? 1 : Math.max(0.05, s.fraction);
    for (const p of c.samples) {
      const mag = Math.hypot(p.ex, p.ey);
      if (!mag) continue;
      const relative = Math.min(
          1,
          Math.log10(1 + mag) / Math.log10(1 + c.fieldMagnitudeLimit),
        ),
        len = (5 + 14 * relative) * reveal,
        x = X(p.x),
        y = Y(p.y);
      PhysicsAnnotations.vector(
        ctx,
        s,
        {
          x,
          y,
          dx: p.ex,
          dy: p.ey,
          role: "electric_field",
          scale_mode: "normalized",
          fixed_length_px: len,
          scale_disclosure:
            "Field directions are physical; arrow lengths are normalized for visibility using logarithmic magnitude",
        },
        1,
        false,
      );
    }
    for (const q of c.charges)
      PhysicsAssets.charge(ctx, s, {
        x: X(q.x),
        y: Y(q.y),
        radius: 12,
        sign: q.q,
        shadow: true,
        label:
          PhysicsVisuals.responsive(s) === "mobile"
            ? ""
            : q.q > 0
              ? "+ source"
              : "− source",
      });
    PhysicsAssets.charge(ctx, s, {
      x: X(c.testX),
      y: Y(c.testY),
      radius: 7,
      sign: c.testCharge,
      fill: PhysicsVisuals.token(s, "colors", "selected", "#7C3AED"),
      shadow: true,
      label: "test",
    });
    PhysicsAnnotations.dimensionLine(ctx, s, {
      x: pad,
      y: h - pad + 12,
      end: { x: w - pad, y: h - pad + 12 },
      label: `${(2 * c.extent).toFixed(1)} m field width`,
    });
    PhysicsAnnotations.disclosure(
      ctx,
      s,
      "normalized",
      "Field directions are physical; arrow lengths are normalized for visibility using logarithmic magnitude",
      12,
      12,
    );
    if (PhysicsVisuals.responsive(s) !== "mobile")
      PhysicsAssets.callout(ctx, s, {
        x: w - 220,
        y: 42,
        width: 205,
        height: 72,
        text: `Potential bands\nWarm: positive  Cool: negative\nHatched: singularity excluded`,
        shadow: false,
      });
  },
};

export { scene };
globalThis.scene = scene;
