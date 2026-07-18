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
      c = s.config.rayConfig || {},
      rays = c.rays || [],
      xmin = c.xmin ?? -5,
      xmax = c.xmax ?? 5,
      ymin = c.ymin ?? -4,
      ymax = c.ymax ?? 4,
      X = (x) => 35 + ((x - xmin) / (xmax - xmin)) * (w - 70),
      Y = (y) => h - 30 - ((y - ymin) / (ymax - ymin)) * (h - 60),
      origin = { x: X(0), y: Y(0) };
    PhysicsExperience.context(ctx, s, "opticsBench");
    if (c.interface) {
      ctx.save();
      ctx.globalAlpha = PhysicsExperience.level(s) === "diagram" ? 0.12 : 0.2;
      ctx.fillStyle = PhysicsVisuals.token(
        s,
        "colors",
        "accent_soft",
        "#DCEEFF",
      );
      ctx.fillRect(35, 30, w - 70, origin.y - 30);
      ctx.fillStyle = PhysicsVisuals.token(
        s,
        "colors",
        "surface_muted",
        "#EAF0F6",
      );
      ctx.fillRect(35, origin.y, w - 70, h - 30 - origin.y);
      ctx.restore();
      ctx.strokeStyle = PhysicsVisuals.token(s, "colors", "text", "#152536");
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(X(xmin), origin.y);
      ctx.lineTo(X(xmax), origin.y);
      ctx.stroke();
      PhysicsAnnotations.normalLine(ctx, s, {
        x: origin.x,
        y: origin.y,
        length: h - 60,
        surface_angle: 0,
        label: "Normal",
      });
      ctx.save();
      PhysicsVisuals.applyText(ctx, s, "label");
      ctx.fillText(`Medium 1  n = ${c.medium1.toFixed(2)}`, 48, 52);
      ctx.fillText(`Medium 2  n = ${c.medium2.toFixed(2)}`, 48, h - 46);
      ctx.restore();
      const radius = Math.min(42, w * 0.07);
      PhysicsAnnotations.angleArc(ctx, s, {
        x: origin.x,
        y: origin.y,
        radius,
        startAngle: -Math.PI / 2 - (c.incidentAngle * Math.PI) / 180,
        endAngle: -Math.PI / 2,
        label: `${c.incidentAngle.toFixed(0)}°`,
      });
      PhysicsAnnotations.angleArc(ctx, s, {
        x: origin.x,
        y: origin.y,
        radius: radius + 15,
        startAngle: -Math.PI / 2,
        endAngle: -Math.PI / 2 + (c.incidentAngle * Math.PI) / 180,
        label: `${c.incidentAngle.toFixed(0)}°`,
      });
      if (c.refractionAngle !== null)
        PhysicsAnnotations.angleArc(ctx, s, {
          x: origin.x,
          y: origin.y,
          radius,
          startAngle: Math.PI / 2 - (c.refractionAngle * Math.PI) / 180,
          endAngle: Math.PI / 2,
          label: `${c.refractionAngle.toFixed(0)}°`,
        });
    } else {
      ctx.strokeStyle = PhysicsVisuals.token(
        s,
        "colors",
        "text_muted",
        "#526577",
      );
      ctx.beginPath();
      ctx.moveTo(X(xmin), origin.y);
      ctx.lineTo(X(xmax), origin.y);
      ctx.stroke();
    }
    if (c.lens)
      PhysicsAssets.lens(ctx, s, {
        x: origin.x,
        y: origin.y,
        width: Math.max(18, w * 0.035),
        height: (h - 60) * 0.75,
        fill: PhysicsVisuals.token(s, "colors", "electric_field", "#006D77"),
        shadow: true,
        label: c.lensSign > 0 ? "Converging lens" : "Diverging lens",
      });
    const visible = s.reducedMotion
      ? rays.length
      : Math.ceil(s.fraction * rays.length);
    for (let i = 0; i < visible; i++) {
      const r = rays[i],
        virtual = r.kind === "virtual",
        color = PhysicsVisuals.token(
          s,
          "colors",
          virtual ? "magnetic_field" : i === 0 ? "net_force" : "energy",
          "#B45309",
        );
      PhysicsAssets.ray(ctx, s, {
        x: X(r.x1),
        y: Y(r.y1),
        end: { x: X(r.x2), y: Y(r.y2) },
        fill: color,
        lineWidth: 2.5,
        dashed: virtual,
        label: PhysicsVisuals.responsive(s) === "mobile" ? "" : r.label || "",
        shadow: false,
      });
    }
    if (c.interface) {
      PhysicsAnnotations.disclosure(
        ctx,
        s,
        "schematic",
        "Ray directions and angles are physical; displayed ray lengths are schematic",
        12,
        12,
      );
      if (c.totalInternalReflection)
        PhysicsAssets.callout(ctx, s, {
          x: w - 235,
          y: h - 82,
          width: 220,
          height: 54,
          text: "Total internal reflection\nNo transmitted ray",
          shadow: true,
          target: origin,
        });
    }
  },
};

export { scene };
globalThis.scene = scene;
