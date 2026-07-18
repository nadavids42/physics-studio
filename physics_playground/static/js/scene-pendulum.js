(() => {
  // src/scenes/scene-api.js
  var PhysicsAnimation = globalThis.PhysicsAnimation;
  var PhysicsAnnotations = globalThis.PhysicsAnnotations;
  var PhysicsAssets = globalThis.PhysicsAssets;
  var PhysicsExperience = globalThis.PhysicsExperience;
  var PhysicsVisuals = globalThis.PhysicsVisuals;
  var sample = globalThis.sample;

  // src/scenes/waves/pendulum.js
  var scene = {
    draw(ctx, f) {
      const t = f.transform, W = t.width, H = t.height, pivot = { x: W / 2, y: 38 };
      PhysicsExperience.context(ctx, f, "laboratory");
      PhysicsAssets.pivot(ctx, f, {
        x: pivot.x,
        y: pivot.y,
        width: 42,
        height: 30,
        fill: PhysicsVisuals.token(f, "colors", "uncertainty", "#64748B"),
        shadow: true,
        label: "Pivot"
      });
      const scale = Math.min(
        (W / 2 - 35) / f.config.maxLength,
        (H - pivot.y - 42) / f.config.maxLength
      );
      for (const track of Object.values(f.tracks)) {
        const x = pivot.x + track.x * scale, y = pivot.y - track.y * scale, color = track.style.color || PhysicsVisuals.token(f, "colors", "displacement", "#0F766E");
        PhysicsAnimation.fadingTrail(
          ctx,
          f.trails.get(track.id),
          (q) => ({ x: pivot.x + q.x * scale, y: pivot.y - (q.y || 0) * scale }),
          { color, width: 2.2, opacity: 0.35 }
        );
        PhysicsAssets.cable(ctx, f, {
          x: pivot.x,
          y: pivot.y,
          end: { x: x - pivot.x, y: y - pivot.y },
          fill: PhysicsVisuals.token(f, "colors", "tension", "#6D28D9"),
          shadow: false
        });
        PhysicsAssets.pendulumBob(ctx, f, {
          x,
          y,
          radius: 17,
          fill: color,
          highlight: true,
          shadow: true,
          label: f.config.tracks.length > 1 && PhysicsVisuals.responsive(f) !== "mobile" ? track.label : ""
        });
      }
    }
  };
  globalThis.scene = scene;
})();
