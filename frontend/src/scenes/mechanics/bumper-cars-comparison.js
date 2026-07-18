function comparisonBackground(ctx, t, frame) {
  PhysicsExperience.context(ctx, frame, "collisionTrack");
  ctx.strokeStyle = PhysicsVisuals.token(frame, "colors", "border", "#B8C5D1");
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, t.height / 2);
  ctx.lineTo(t.width, t.height / 2);
  ctx.stroke();
  ctx.fillStyle = PhysicsVisuals.token(frame, "colors", "text", "#152536");
  PhysicsVisuals.applyText(ctx, frame, "label");
  ctx.fillText("Run A", 12, 22);
  ctx.fillText("Run B", 12, t.height / 2 + 22);
}
function comparisonCar(ctx, frame, x, y, color, label) {
  PhysicsAssets.cart(ctx, frame, {
    x,
    y,
    width: 46,
    height: 25,
    fill: color,
    highlight: true,
    shadow: true,
    label,
  });
}
import {
  PhysicsAssets,
  PhysicsExperience,
  PhysicsVisuals,
  sample,
} from "../scene-api.js";

const scene = {
  onEvent(event, player) {
    if (event.type === "particle_burst") {
      const t = player.coordinates();
      const a = sample(player.config.tracks[event.trackA].x, event.fraction),
        b = sample(player.config.tracks[event.trackB].x, event.fraction);
      const lane = event.lane === "a" ? t.height * 0.27 : t.height * 0.75;
      player.particles.burst(
        (t.x(a) + t.x(b)) / 2,
        lane,
        event.count,
        event.colors,
      );
    }
  },
  draw(ctx, frame) {
    const t = frame.transform;
    comparisonBackground(ctx, t, frame);
    const tracks = frame.tracks,
      c1 = PhysicsVisuals.token(frame, "colors", "graph_1", "#0072B2"),
      c2 = PhysicsVisuals.token(frame, "colors", "graph_2", "#D55E00");
    comparisonCar(
      ctx,
      frame,
      t.x(tracks.run_a_car_a.x),
      t.height * 0.27,
      c1,
      "A",
    );
    comparisonCar(
      ctx,
      frame,
      t.x(tracks.run_a_car_b.x),
      t.height * 0.27,
      c2,
      "B",
    );
    comparisonCar(
      ctx,
      frame,
      t.x(tracks.run_b_car_a.x),
      t.height * 0.75,
      c1,
      "A",
    );
    comparisonCar(
      ctx,
      frame,
      t.x(tracks.run_b_car_b.x),
      t.height * 0.75,
      c2,
      "B",
    );
  },
};

export { scene };
globalThis.scene = scene;
