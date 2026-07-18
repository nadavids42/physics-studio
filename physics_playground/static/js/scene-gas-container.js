(() => {
  // src/scenes/scene-api.js
  var PhysicsAnimation = globalThis.PhysicsAnimation;
  var PhysicsAnnotations = globalThis.PhysicsAnnotations;
  var PhysicsAssets = globalThis.PhysicsAssets;
  var PhysicsExperience = globalThis.PhysicsExperience;
  var PhysicsVisuals = globalThis.PhysicsVisuals;
  var sample = globalThis.sample;

  // src/scenes/shared/gas-container.js
  var scene = {
    draw(ctx, s) {
      const w = s.transform.width, h = s.transform.height, c = s.config.gasContainer || {}, progress = s.reducedMotion ? 1 : s.fraction, left = w * 0.25, right = w * 0.75, outerTop = h * 0.16, bottom = h * 0.82, outerHeight = bottom - outerTop, maxV = Math.max(c.volumeA, c.volumeB, 1e-3), v = c.volumeA + (c.volumeB - c.volumeA) * progress, gasH = 80 + v / maxV * outerHeight * 0.72, top = bottom - gasH, pressure = c.pressureA + (c.pressureB - c.pressureA) * progress, temp = c.tempA + (c.tempB - c.tempA) * progress;
      PhysicsExperience.context(ctx, s, "laboratory");
      ctx.save();
      ctx.globalAlpha = 0.16;
      ctx.fillStyle = PhysicsVisuals.token(s, "colors", "energy", "#B45309");
      ctx.fillRect(left, top, right - left, bottom - top);
      ctx.restore();
      PhysicsAssets.fluidContainer(ctx, s, {
        x: (left + right) / 2,
        y: (outerTop + bottom) / 2,
        width: right - left,
        height: outerHeight,
        shadow: true,
        label: "Ideal-gas cylinder"
      });
      ctx.save();
      ctx.strokeStyle = PhysicsVisuals.token(s, "colors", "border", "#B8C5D1");
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(left - 18, outerTop);
      ctx.lineTo(left - 18, bottom);
      ctx.moveTo(right + 18, outerTop);
      ctx.lineTo(right + 18, bottom);
      ctx.stroke();
      ctx.restore();
      PhysicsAssets.block(ctx, s, {
        x: (left + right) / 2,
        y: top,
        width: right - left + 24,
        height: 18,
        fill: PhysicsVisuals.token(s, "colors", "uncertainty", "#64748B"),
        highlight: true,
        shadow: true,
        label: "Piston"
      });
      const limit = PhysicsExperience.level(s) === "diagram" ? Math.min(12, c.particleLayout.length) : c.particleLayout.length;
      for (let i = 0; i < limit; i++) {
        const particle = c.particleLayout[i], x = left + 12 + particle.u * (right - left - 24), y = top + 12 + particle.v * Math.max(8, bottom - top - 24);
        ctx.fillStyle = PhysicsVisuals.token(s, "colors", "graph_2", "#D55E00");
        ctx.globalAlpha = 0.78;
        ctx.beginPath();
        ctx.arc(x, y, particle.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      const arrowRatio = pressure / Math.max(c.pressureA, c.pressureB, 1), arrowLength = 24 + 28 * arrowRatio;
      for (const x of [
        left + (right - left) * 0.25,
        left + (right - left) * 0.5,
        left + (right - left) * 0.75
      ])
        PhysicsAnnotations.vector(
          ctx,
          s,
          {
            x,
            y: top - arrowLength - 12,
            dx: 0,
            dy: -1,
            role: "net_force",
            scale_mode: "normalized",
            fixed_length_px: arrowLength,
            scale_disclosure: "Pressure indicators are normalized for visibility"
          },
          1,
          false
        );
      ctx.save();
      PhysicsVisuals.applyText(ctx, s, "label");
      const compact = PhysicsVisuals.responsive(s) === "mobile";
      ctx.fillText(`P ${pressure.toFixed(1)} kPa`, compact ? 16 : left, 32);
      ctx.fillText(
        `V ${(v * 1e3).toFixed(1)} L`,
        compact ? 16 : left + 150,
        compact ? 52 : 32
      );
      ctx.fillText(
        `T ${temp.toFixed(1)} K`,
        compact ? 16 : left + 285,
        compact ? 72 : 32
      );
      ctx.fillText(
        `n ${c.amount.toFixed(2)} mol`,
        compact ? 16 : left + 430,
        compact ? 92 : 32
      );
      ctx.restore();
      PhysicsAnnotations.disclosure(
        ctx,
        s,
        "normalized",
        "Pressure indicators are normalized for visibility",
        12,
        h - 64
      );
      if (PhysicsVisuals.responsive(s) !== "mobile")
        PhysicsAssets.callout(ctx, s, {
          x: w - 245,
          y: h - 104,
          width: 230,
          height: 58,
          text: "Particles are illustrative\nCount and motion are not molecular scale",
          shadow: false
        });
    }
  };
  globalThis.scene = scene;
})();
