(() => {
  // src/scenes/scene-api.js
  var PhysicsAnimation = globalThis.PhysicsAnimation;
  var PhysicsAnnotations = globalThis.PhysicsAnnotations;
  var PhysicsAssets = globalThis.PhysicsAssets;
  var PhysicsExperience = globalThis.PhysicsExperience;
  var PhysicsVisuals = globalThis.PhysicsVisuals;
  var sample = globalThis.sample;

  // src/scenes/mechanics/earth-tunnel.js
  var scene = {
    draw(ctx, f) {
      const t = f.transform, W = t.width, H = t.height, c = f.config.earthTunnel || {}, cx = W / 2, cy = H / 2, R = Math.min(W, H) * 0.34, X = (km) => cx + km / f.config.radiusKm * R;
      PhysicsExperience.context(ctx, f, "space");
      PhysicsAssets.planet(ctx, f, {
        x: cx,
        y: cy,
        radius: R,
        label: "idealized spherical planet",
        shadow: false
      });
      PhysicsAnnotations.pathGuide(ctx, f, {
        points: [
          { x: cx - R, y: cy },
          { x: cx + R, y: cy }
        ],
        dashes: [8, 7],
        opacity: 0.75
      });
      PhysicsAnnotations.centerOfMass(ctx, f, {
        x: cx,
        y: cy,
        label: "center",
        radius: 9
      });
      PhysicsAnnotations.dimensionLine(ctx, f, {
        x: cx,
        y: cy - R - 18,
        end: { x: cx + R, y: cy - R - 18 },
        label: `planet radius ${f.config.radiusKm.toFixed(0)} km`
      });
      for (const [index, track] of Object.values(f.tracks).entries()) {
        const meta = c.travelers[index] || {}, x = X(track.x), acceleration = track.y || 0, turn = X(meta.turningPointKm || 0), trail = f.trails.get(track.id) || [], dashed = index % 2 === 1;
        PhysicsAnnotations.pathGuide(ctx, f, {
          points: [
            { x: turn, y: cy - 23 },
            { x: turn, y: cy + 23 },
            { x: X(-(meta.turningPointKm || 0)), y: cy + 23 },
            { x: X(-(meta.turningPointKm || 0)), y: cy - 23 }
          ],
          dashes: dashed ? [4, 4] : [1, 0],
          opacity: 0.55
        });
        PhysicsAnnotations.velocityTrail(ctx, f, {
          points: trail.map((q) => ({ x: X(q.x), y: cy })),
          direction: false,
          opacity: index ? 0.18 : 0.28,
          line_width: index ? 3 : 5,
          dashed
        });
        PhysicsAssets.mass(ctx, f, {
          x,
          y: cy,
          radius: index ? 11 : 14,
          label: `${meta.label} \u2014 ${dashed ? "dashed" : "solid"}`,
          fill: PhysicsVisuals.token(f, "colors", meta.role, "#1769AA"),
          outline: PhysicsVisuals.token(f, "colors", "text", "#152536"),
          selected: index > 0
        });
        PhysicsAnnotations.dimensionLine(ctx, f, {
          x: cx,
          y: cy + 36 + index * 18,
          end: { x, y: cy + 36 + index * 18 },
          label: `r = ${track.x.toFixed(0)} km`
        });
        if (Math.abs(acceleration) > 1e-8)
          PhysicsAnnotations.vector(
            ctx,
            f,
            {
              x,
              y: cy - 8,
              dx: acceleration,
              dy: 0,
              role: "acceleration",
              label: `a ${acceleration.toFixed(2)} m/s\xB2`,
              scale_mode: "normalized",
              fixed_length_px: 46,
              scale_disclosure: "Acceleration direction is physical; length is normalized"
            },
            f.progress,
            index === 0
          );
      }
      ctx.save();
      PhysicsVisuals.applyText(ctx, f, "annotation");
      ctx.fillStyle = PhysicsVisuals.token(f, "colors", "text", "#152536");
      ctx.fillText(c.modelSummary || "", 18, 28);
      ctx.restore();
    }
  };
  globalThis.scene = scene;
})();
