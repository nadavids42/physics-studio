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
      c = s.config,
      frames = c.wavefrontFrames || [],
      pad = 52,
      axisY = h * 0.58,
      min = c.worldMin,
      max = c.worldMax,
      map = (x) => pad + ((x - min) / (max - min)) * (w - pad * 2),
      metersToPixels = (r) => Math.abs(map(r) - map(0));
    PhysicsExperience.context(ctx, s, "laboratory");
    PhysicsAssets.ruler(ctx, s, {
      x: pad,
      y: axisY + 48,
      width: w - pad * 2,
      divisions: 10,
      maximum: max - min,
      showValues: PhysicsVisuals.responsive(s) !== "mobile",
    });
    ctx.save();
    ctx.strokeStyle = PhysicsVisuals.token(s, "colors", "text", "#152536");
    ctx.beginPath();
    ctx.moveTo(pad, axisY);
    ctx.lineTo(w - pad, axisY);
    ctx.stroke();
    PhysicsVisuals.applyText(ctx, s, "annotation");
    ctx.fillStyle = PhysicsVisuals.token(s, "colors", "text", "#152536");
    ctx.fillText("+x → right; medium stationary", pad, axisY + 72);
    ctx.restore();
    if (!frames.length) return;
    const frame =
      frames[
        Math.min(
          frames.length - 1,
          Math.round(s.fraction * (frames.length - 1)),
        )
      ];
    for (let i = 0; i < frame.centers.length; i++) {
      const center = map(frame.centers[i]),
        radius = metersToPixels(frame.radii[i]);
      PhysicsAssets.wavefront(ctx, s, {
        x: center,
        y: axisY,
        radius,
        count: 1,
        startAngle: 0,
        endAngle: Math.PI * 2,
        lineWidth: 1.6,
        opacity: 0.48,
      });
      ctx.save();
      ctx.fillStyle = PhysicsVisuals.token(
        s,
        "colors",
        "trajectory",
        "#1769AA",
      );
      ctx.beginPath();
      ctx.arc(center, axisY, 2.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
      if (i === frame.centers.length - 1) {
        ctx.save();
        PhysicsVisuals.applyText(ctx, s, "annotation");
        ctx.fillStyle = PhysicsVisuals.token(
          s,
          "colors",
          "text_muted",
          "#526577",
        );
        ctx.fillText(
          `r=${frame.radii[i].toFixed(1)} m`,
          Math.min(w - 92, center + radius + 4),
          axisY - 8,
        );
        ctx.restore();
      }
    }
    const sx = map(frame.source),
      ox = map(frame.observer);
    PhysicsAssets.source(ctx, s, {
      x: sx,
      y: axisY,
      radius: 16,
      label: "sound source",
    });
    PhysicsAssets.observer(ctx, s, {
      x: ox,
      y: axisY,
      radius: 15,
      label: "observer",
    });
    if (Math.abs(c.sourceVelocityMps) > 1e-9)
      PhysicsAnnotations.vector(
        ctx,
        s,
        {
          x: sx,
          y: axisY - 34,
          dx: c.sourceVelocityMps,
          dy: 0,
          role: "velocity",
          label: `source ${c.sourceVelocityMps.toFixed(0)} m/s`,
          scale_mode: "normalized",
          fixed_length_px: 48,
          scale_disclosure:
            "Motion-arrow direction is physical; length is normalized",
        },
        s.progress,
        true,
      );
    if (Math.abs(c.observerVelocityMps) > 1e-9)
      PhysicsAnnotations.vector(
        ctx,
        s,
        {
          x: ox,
          y: axisY - 34,
          dx: c.observerVelocityMps,
          dy: 0,
          role: "displacement",
          label: `observer ${c.observerVelocityMps.toFixed(0)} m/s`,
          scale_mode: "normalized",
          fixed_length_px: 48,
          scale_disclosure:
            "Motion-arrow direction is physical; length is normalized",
        },
        s.progress,
        false,
      );
    const ahead =
        c.sourceVelocityMps > 0
          ? "compressed ahead"
          : c.sourceVelocityMps < 0
            ? "expanded ahead"
            : "equal spacing ahead",
      behind =
        c.sourceVelocityMps > 0
          ? "expanded behind"
          : c.sourceVelocityMps < 0
            ? "compressed behind"
            : "equal spacing behind";
    PhysicsAssets.callout(ctx, s, {
      x: Math.max(10, sx - 215),
      y: 30,
      width: 190,
      height: 50,
      text: `${behind}\nλ = ${c.wavelengthBehindM.toFixed(2)} m`,
    });
    PhysicsAssets.callout(ctx, s, {
      x: Math.min(w - 200, sx + 25),
      y: 30,
      width: 190,
      height: 50,
      text: `${ahead}\nλ = ${c.wavelengthAheadM.toFixed(2)} m`,
    });
    ctx.save();
    PhysicsVisuals.applyText(ctx, s, "label");
    ctx.fillStyle = PhysicsVisuals.token(s, "colors", "text", "#152536");
    ctx.fillText(`${c.motionLabel} · positions and radii physical`, pad, 25);
    ctx.restore();
    PhysicsAnnotations.disclosure(
      ctx,
      s,
      "schematic",
      "Wavefront position and radius are physical; line thickness is decorative",
      12,
      h - 34,
    );
  },
};

export { scene };
globalThis.scene = scene;
