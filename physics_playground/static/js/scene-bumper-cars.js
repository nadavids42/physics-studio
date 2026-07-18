(() => {
  // src/scenes/scene-api.js
  var PhysicsAnimation = globalThis.PhysicsAnimation;
  var PhysicsAnnotations = globalThis.PhysicsAnnotations;
  var PhysicsAssets = globalThis.PhysicsAssets;
  var PhysicsExperience = globalThis.PhysicsExperience;
  var PhysicsVisuals = globalThis.PhysicsVisuals;
  var sample = globalThis.sample;

  // src/scenes/mechanics/bumper-cars.js
  function drawBackground(ctx, t, frame) {
    const W = t.width, H = t.height, ground = H - 60, mode = PhysicsExperience.context(ctx, frame, "collisionTrack");
    if (!mode.environment) {
      ctx.fillStyle = PhysicsVisuals.token(
        frame,
        "colors",
        "surface_muted",
        "#EAF0F6"
      );
      ctx.fillRect(0, ground, W, H - ground);
    }
    ctx.strokeStyle = "rgba(255,255,255,.6)";
    ctx.lineWidth = 3;
    ctx.setLineDash([14, 10]);
    ctx.beginPath();
    ctx.moveTo(0, ground + 30);
    ctx.lineTo(W, ground + 30);
    ctx.stroke();
    ctx.setLineDash([]);
  }
  function drawCar(ctx, frame, x, color, label, ground, trail) {
    PhysicsAnimation.fadingTrail(
      ctx,
      trail,
      (p) => ({ x: p.px, y: ground - 15 }),
      { color, width: 5, opacity: 0.22 }
    );
    PhysicsAssets.cart(ctx, frame, {
      x,
      y: ground - 24,
      width: 52,
      height: 28,
      fill: color,
      highlight: true,
      shadow: true,
      label
    });
  }
  var scene = {
    onEvent(event, player) {
      if (event.type === "particle_burst") {
        const a = sample(player.config.tracks[0].x, event.fraction);
        const b = sample(player.config.tracks[1].x, event.fraction), t = player.coordinates();
        player.particles.burst(
          (t.x(a) + t.x(b)) / 2,
          t.height - 80,
          event.count,
          event.colors
        );
      }
    },
    draw(ctx, frame) {
      const t = frame.transform, ground = t.height - 60;
      drawBackground(ctx, t, frame);
      const a = frame.tracks.car_a, b = frame.tracks.car_b, ax = t.x(a.x), bx = t.x(b.x);
      const trailA = frame.trails.get("car_a").map((point) => ({ px: t.x(point.x) }));
      const trailB = frame.trails.get("car_b").map((point) => ({ px: t.x(point.x) }));
      const impact = frame.config.impactFraction, since = Math.max(0, frame.fraction - impact) * frame.config.durationMs / 1e3;
      if (frame.config.sticky && frame.fraction >= impact && frame.state !== "idle") {
        ctx.strokeStyle = PhysicsVisuals.token(
          frame,
          "colors",
          "uncertainty",
          "#64748B"
        );
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(ax, ground - 19);
        ctx.lineTo(bx, ground - 19);
        ctx.stroke();
      }
      drawCar(
        ctx,
        frame,
        ax,
        PhysicsVisuals.token(frame, "colors", "graph_1", "#0072B2"),
        "A",
        ground,
        trailA
      );
      drawCar(
        ctx,
        frame,
        bx,
        PhysicsVisuals.token(frame, "colors", "graph_2", "#D55E00"),
        "B",
        ground,
        trailB
      );
      if (frame.fraction >= impact && since < 0.7) {
        const x = (ax + bx) / 2, y = ground - 25, p = Math.min(1, since / 0.7);
        PhysicsAnimation.impactRipple(ctx, x, y, p, {
          reducedMotion: frame.reducedMotion,
          color: PhysicsVisuals.token(frame, "colors", "warning", "#9A5B00")
        });
        PhysicsAnimation.collisionFlash(ctx, x, y, p, {
          reducedMotion: frame.reducedMotion,
          config: frame.config
        });
      }
    }
  };
  globalThis.scene = scene;
})();
