import {
  PhysicsAnimation,
  PhysicsAnnotations,
  PhysicsAssets,
  PhysicsExperience,
  PhysicsVisuals,
} from "../scene-api.js";

const scene = {
  draw(ctx, s) {
    const w = s.transform.width,
      h = s.transform.height,
      c = s.config.fluidContainer || {},
      left = w * 0.22,
      right = w * 0.78,
      top = h * 0.15,
      bottom = h * 0.82,
      width = right - left,
      height = bottom - top,
      waterline = top + 42;
    PhysicsExperience.context(ctx, s, "laboratory");
    if (c.kind === "buoyancy") {
      const progress = s.reducedMotion ? 1 : s.fraction,
        fraction = Math.max(0, Math.min(1, c.fraction)),
        objectH = 96,
        objectW = Math.min(116, width * 0.42);
      let cy;
      if (c.state === "Sinking") cy = bottom - objectH / 2 - 8;
      else if (c.state === "Neutral buoyancy")
        cy = waterline + (bottom - waterline) * 0.5;
      else cy = waterline + objectH * (fraction - 0.5) * progress;
      PhysicsAssets.fluidSurface(ctx, s, {
        x: (left + right) / 2,
        y: waterline,
        width,
        height: bottom - waterline,
        fill: PhysicsVisuals.token(s, "colors", "electric_field", "#006D77"),
        fluidOpacity: 0.22,
        shadow: false,
      });
      PhysicsAssets.fluidContainer(ctx, s, {
        x: (left + right) / 2,
        y: (top + bottom) / 2,
        width,
        height,
        shadow: true,
        label: "Fluid container",
      });
      PhysicsAssets.block(ctx, s, {
        x: w / 2,
        y: cy,
        width: objectW,
        height: objectH,
        fill: PhysicsVisuals.token(s, "colors", "energy", "#B45309"),
        highlight: true,
        shadow: true,
        label: c.state,
      });
      const submergedTop = Math.max(waterline, cy - objectH / 2),
        submergedBottom = Math.min(bottom, cy + objectH / 2);
      if (submergedBottom > submergedTop)
        PhysicsAnnotations.dimensionLine(ctx, s, {
          x: right + 22,
          y: submergedTop,
          end: { x: right + 22, y: submergedBottom },
          label: `${Math.round(fraction * 100)}% submerged`,
        });
      const maxForce = Math.max(c.weight, c.buoyant, 1),
        weightLength = 30 + (40 * c.weight) / maxForce,
        buoyantLength = 30 + (40 * c.buoyant) / maxForce,
        vectors = [
          {
            x: w / 2,
            y: cy,
            dx: 0,
            dy: -1,
            role: "gravity",
            label: "Weight",
            scale_mode: "normalized",
            fixed_length_px: weightLength,
          },
          {
            x: w / 2,
            y: cy,
            dx: 0,
            dy: 1,
            role: "normal_force",
            label: "Buoyancy",
            scale_mode: "normalized",
            fixed_length_px: buoyantLength,
          },
        ];
      PhysicsAnnotations.vectorSet(ctx, s, vectors, progress, { x: 12, y: 12 });
      if (!s.reducedMotion && progress < 1)
        PhysicsAnimation.impactRipple(ctx, w / 2, waterline, progress, {
          radius: 28,
          opacity: 0.22,
          color: PhysicsVisuals.token(s, "colors", "electric_field", "#006D77"),
        });
      if (PhysicsVisuals.responsive(s) !== "mobile")
        PhysicsAssets.callout(ctx, s, {
          x: 18,
          y: h - 105,
          width: 190,
          height: 82,
          text: `Object: ${c.objectDensity.toFixed(0)} kg/m³\nFluid: ${c.fluidDensity.toFixed(0)} kg/m³\nDisplaced: ${c.displacedVolume.toFixed(4)} m³`,
          shadow: false,
        });
    } else {
      const fluidColor = PhysicsVisuals.token(
        s,
        "colors",
        "electric_field",
        "#006D77",
      );
      PhysicsAssets.fluidSurface(ctx, s, {
        x: (left + right) / 2,
        y: top,
        width,
        height,
        fill: fluidColor,
        fluidOpacity: 0.18,
        shadow: false,
      });
      const gradient = ctx.createLinearGradient(0, top, 0, bottom);
      gradient.addColorStop(0, "transparent");
      gradient.addColorStop(1, fluidColor);
      ctx.save();
      ctx.globalAlpha = PhysicsExperience.level(s) === "diagram" ? 0.2 : 0.32;
      ctx.fillStyle = gradient;
      ctx.fillRect(left, top, width, height);
      ctx.restore();
      PhysicsAssets.fluidContainer(ctx, s, {
        x: (left + right) / 2,
        y: (top + bottom) / 2,
        width,
        height,
        shadow: true,
        label: "Hydrostatic column",
      });
      PhysicsAssets.ruler(ctx, s, {
        x: left - 28,
        y: top,
        width: height,
        rotation: Math.PI / 2,
        divisions: 10,
        maximum: c.maxDepth,
        showValues: PhysicsVisuals.responsive(s) !== "mobile",
      });
      const selectedY = top + height * (c.depth / c.maxDepth);
      PhysicsAnnotations.dimensionLine(ctx, s, {
        x: right + 22,
        y: top,
        end: { x: right + 22, y: selectedY },
        label: `Selected depth ${c.depth.toFixed(1)} m`,
      });
      const samples = c.pressureSamples || [];
      for (const sample of samples) {
        const y = top + height * (sample.depth / c.maxDepth),
          length = 18 + 54 * sample.ratio;
        PhysicsAnnotations.vector(
          ctx,
          s,
          {
            x: left + 8,
            y,
            dx: 1,
            dy: 0,
            role: "net_force",
            scale_mode: "normalized",
            fixed_length_px: length,
            scale_disclosure:
              "Pressure-arrow lengths are normalized for visibility",
          },
          1,
          false,
        );
      }
      PhysicsAnnotations.disclosure(
        ctx,
        s,
        "normalized",
        "Pressure-arrow lengths are normalized for visibility",
        12,
        12,
      );
      ctx.save();
      PhysicsVisuals.applyText(ctx, s, "label");
      ctx.fillText(
        `Surface: ${(c.surfacePressure / 1000).toFixed(2)} kPa`,
        left + 12,
        top + 24,
      );
      ctx.fillText(
        `Gauge: ${(c.gaugePressure / 1000).toFixed(2)} kPa`,
        left + 12,
        selectedY - 24,
      );
      ctx.fillText(
        `Absolute: ${(c.absolutePressure / 1000).toFixed(2)} kPa`,
        left + 12,
        selectedY - 8,
      );
      ctx.restore();
    }
  },
};

export { scene };
globalThis.scene = scene;
