import {
  PhysicsAnimation,
  PhysicsAssets,
  PhysicsExperience,
  PhysicsVisuals,
} from "../scene-api.js";

const scene = {
  draw(ctx, f) {
    const t = f.transform,
      W = t.width,
      H = t.height,
      cx = W / 2,
      cy = H / 2,
      view = f.config.orbitView,
      scale = (Math.min(W, H) * 0.43) / view;
    PhysicsExperience.context(ctx, f, "space");
    PhysicsAssets.star(ctx, f, {
      x: cx,
      y: cy,
      radius: 16,
      fill: PhysicsVisuals.token(f, "colors", "energy", "#B45309"),
      glow: true,
      shadow: false,
      label: "Central body",
    });
    for (const q of Object.values(f.tracks)) {
      const color =
        q.style.color ||
        PhysicsVisuals.token(f, "colors", "trajectory", "#1769AA");
      PhysicsAnimation.fadingTrail(
        ctx,
        f.trails.get(q.id),
        (p) => ({ x: cx + p.x * scale, y: cy - (p.y || 0) * scale }),
        { color, width: 2.2, opacity: 0.48 },
      );
      PhysicsAssets.planet(ctx, f, {
        x: cx + q.x * scale,
        y: cy - (q.y || 0) * scale,
        radius: 8,
        fill: color,
        highlight: true,
        shadow: true,
        label:
          f.config.tracks.length > 1 &&
          PhysicsVisuals.responsive(f) !== "mobile"
            ? q.label
            : "",
      });
    }
  },
};

export { scene };
globalThis.scene = scene;
