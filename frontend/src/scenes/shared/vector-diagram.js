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
      c = s.config.vectorDiagram || {},
      cx = w / 2,
      cy = h / 2 - 15;
    PhysicsExperience.context(ctx, s, "laboratory");
    if (c.subjectKind === "charge")
      PhysicsAssets.charge(ctx, s, {
        x: cx,
        y: cy,
        radius: 13,
        sign: c.chargeSign,
        shadow: true,
        label: PhysicsVisuals.responsive(s) === "mobile" ? "" : "Test charge",
      });
    else
      PhysicsAssets.rod(ctx, s, {
        x: cx - 32,
        y: cy,
        end: { x: 64, y: 0 },
        rotation: -Math.atan2(c.vectors[0].dy, c.vectors[0].dx),
        fill: PhysicsVisuals.token(s, "colors", "uncertainty", "#64748B"),
        lineWidth: 7,
        shadow: true,
        label: PhysicsVisuals.responsive(s) === "mobile" ? "" : "Wire element",
      });
    const vectors = (c.vectors || []).map((v) => ({ ...v, x: cx, y: cy }));
    PhysicsAnnotations.vectorSet(
      ctx,
      s,
      vectors,
      s.reducedMotion ? 1 : s.fraction,
      { x: 12, y: 12 },
    );
    ctx.save();
    ctx.fillStyle = PhysicsVisuals.token(
      s,
      "colors",
      c.forceZ > 0
        ? "normal_force"
        : c.forceZ < 0
          ? "magnetic_field"
          : "text_muted",
      "#526577",
    );
    ctx.font =
      "650 58px " +
      PhysicsVisuals.token(s, "typography", "family_ui", "system-ui");
    ctx.textAlign = "center";
    ctx.fillText(c.forceZ > 0 ? "⊙" : c.forceZ < 0 ? "⊗" : "0", cx, cy + 105);
    PhysicsVisuals.applyText(ctx, s, "label");
    ctx.textAlign = "center";
    ctx.fillText(c.forceLabel, cx, cy + 135);
    ctx.restore();
    if (
      PhysicsExperience.level(s) !== "diagram" &&
      PhysicsVisuals.responsive(s) !== "mobile"
    )
      PhysicsAssets.callout(ctx, s, {
        x: w - 260,
        y: 18,
        width: 245,
        height: 62,
        text:
          "Right-hand rule\n" +
          (c.subjectKind === "charge"
            ? "Follows v × B; reverse for q < 0"
            : "Follows I × B; reverse for I < 0"),
        shadow: true,
      });
  },
};

export { scene };
globalThis.scene = scene;
