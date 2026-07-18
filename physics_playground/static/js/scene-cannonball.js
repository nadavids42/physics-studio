(() => {
  // src/scenes/scene-api.js
  var PhysicsAnimation = globalThis.PhysicsAnimation;
  var PhysicsAnnotations = globalThis.PhysicsAnnotations;
  var PhysicsAssets = globalThis.PhysicsAssets;
  var PhysicsExperience = globalThis.PhysicsExperience;
  var PhysicsVisuals = globalThis.PhysicsVisuals;
  var sample = globalThis.sample;

  // src/scenes/mechanics/cannonball.js
  function mapPoint(x, y, view, t) {
    const left = 40, right = t.width - 25, ground = t.height - 46, top = 25;
    return {
      x: left + (x - view.xMin) / Math.max(1e-3, view.xMax - view.xMin) * (right - left),
      y: ground - (y - view.yMin) / Math.max(1e-3, view.yMax - view.yMin) * (ground - top)
    };
  }
  function sky(ctx, t, frame) {
    const ground = t.height - 46, mode = PhysicsExperience.context(ctx, frame, "projectileField");
    if (!mode.environment) {
      ctx.fillStyle = PhysicsVisuals.token(
        frame,
        "colors",
        "surface_muted",
        "#EAF0F6"
      );
      ctx.fillRect(0, ground, t.width, t.height - ground);
    }
  }
  function cannon(ctx, t, angle, frame) {
    const p = mapPoint(0, 0, t.config.view, t);
    PhysicsAssets.cannon(ctx, frame, {
      x: p.x,
      y: p.y - 3,
      width: 48,
      rotation: -angle * Math.PI / 180,
      fill: PhysicsVisuals.token(frame, "colors", "uncertainty", "#64748B"),
      highlight: true,
      shadow: true,
      label: PhysicsVisuals.responsive(frame) === "mobile" ? "" : "Launcher"
    });
  }
  function target(ctx, t, frame) {
    const p = mapPoint(t.config.target, 0, t.config.view, t), surface = PhysicsVisuals.token(frame, "colors", "surface", "#FFF"), accent = PhysicsVisuals.token(frame, "colors", "net_force", "#C2410C");
    ctx.fillStyle = surface;
    ctx.beginPath();
    ctx.arc(p.x, p.y - 18, 17, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = accent;
    ctx.beginPath();
    ctx.arc(p.x, p.y - 18, 11, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = surface;
    ctx.beginPath();
    ctx.arc(p.x, p.y - 18, 5, 0, Math.PI * 2);
    ctx.fill();
  }
  var scene = {
    onEvent(event, player) {
      if (event.type === "impact") {
        const track = player.config.tracks[event.track];
        const t = player.coordinates();
        const p = mapPoint(
          sample(track.x, event.fraction),
          sample(track.y, event.fraction),
          player.config.view,
          t
        );
        player.particles.burst(p.x, p.y, event.count, event.colors);
      }
    },
    draw(ctx, frame) {
      const t = { ...frame.transform, config: frame.config };
      sky(ctx, t, frame);
      cannon(ctx, t, frame.config.angle, frame);
      target(ctx, t, frame);
      for (const track of Object.values(frame.tracks)) {
        const points = frame.trails.get(track.id);
        PhysicsAnimation.fadingTrail(
          ctx,
          points,
          (q) => mapPoint(q.x, q.y || 0, frame.config.view, t),
          {
            color: track.style.color || PhysicsVisuals.token(frame, "colors", "trajectory", "#1769AA"),
            width: 2.5,
            opacity: 0.42
          }
        );
        const p = mapPoint(track.x, track.y || 0, frame.config.view, t);
        PhysicsAssets.projectile(ctx, frame, {
          x: p.x,
          y: p.y,
          radius: 8,
          fill: track.style.color || PhysicsVisuals.token(frame, "colors", "trajectory", "#1769AA"),
          highlight: true,
          shadow: true,
          label: frame.config.tracks.length > 1 && PhysicsVisuals.responsive(frame) !== "mobile" ? track.label : ""
        });
      }
    }
  };
  globalThis.scene = scene;
})();
