(() => {
  // src/scenes/scene-api.js
  var PhysicsAnimation = globalThis.PhysicsAnimation;
  var PhysicsAnnotations = globalThis.PhysicsAnnotations;
  var PhysicsAssets = globalThis.PhysicsAssets;
  var PhysicsExperience = globalThis.PhysicsExperience;
  var PhysicsVisuals = globalThis.PhysicsVisuals;
  var sample = globalThis.sample;

  // src/scenes/waves/boing.js
  var scene = {
    draw(ctx, s) {
      const t = s.transform, c = s.config.boing || {}, tracks = Object.values(s.tracks), count = tracks.length;
      PhysicsExperience.context(ctx, s, "laboratory");
      const wall = 48, span = Math.max(1, t.x(1) - t.x(0));
      tracks.forEach((track, index) => {
        const meta = c.oscillators[index] || {}, cy = (index + 1) * t.height / (count + 1), equilibrium = t.x(0), x = t.x(track.x), velocity = track.y || 0, displacement = track.x || 0;
        ctx.save();
        ctx.strokeStyle = PhysicsVisuals.token(
          s,
          "colors",
          "text_muted",
          "#526577"
        );
        ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.moveTo(wall, cy - 54);
        ctx.lineTo(wall, cy + 54);
        ctx.stroke();
        ctx.restore();
        PhysicsAnnotations.pathGuide(ctx, s, {
          points: [
            { x: equilibrium, y: cy - 54 },
            { x: equilibrium, y: cy + 54 }
          ],
          dashes: [5, 5],
          opacity: 0.7
        });
        const amplitude = Math.abs(meta.initialDisplacementM || 0), left = t.x(-amplitude), right = t.x(amplitude);
        PhysicsAnnotations.pathGuide(ctx, s, {
          points: [
            { x: left, y: cy - 38 },
            { x: left, y: cy + 38 }
          ],
          opacity: 0.3
        });
        PhysicsAnnotations.pathGuide(ctx, s, {
          points: [
            { x: right, y: cy - 38 },
            { x: right, y: cy + 38 }
          ],
          opacity: 0.3
        });
        if ((meta.dampingNsM || 0) > 0 && !meta.driven) {
          const envelope = amplitude * Math.exp(
            -(meta.dampingNsM || 0) * (meta.durationS || 0) * s.fraction / (2 * (meta.massKg || 1))
          ), elo = t.x(-envelope), ehi = t.x(envelope);
          PhysicsAnnotations.dimensionLine(ctx, s, {
            x: elo,
            y: cy - 46,
            end: { x: ehi, y: cy - 46 },
            label: `damping envelope \xB1${envelope.toFixed(2)} m`
          });
        }
        PhysicsAssets.spring(ctx, s, {
          x: wall,
          y: cy,
          end: { x: x - wall - 23, y: 0 },
          turns: 14,
          amplitude: 10,
          label: ""
        });
        const trail = track.trail || [];
        PhysicsAnnotations.velocityTrail(ctx, s, {
          points: trail.map((q) => ({ x: t.x(q.x), y: cy })),
          direction: false,
          opacity: 0.16,
          line_width: 5
        });
        PhysicsAssets.mass(ctx, s, {
          x,
          y: cy,
          radius: 22,
          label: track.label,
          fill: PhysicsVisuals.token(
            s,
            "colors",
            meta.role || "displacement",
            "#1769AA"
          ),
          selected: count > 1
        });
        const vectors = [];
        if (Math.abs(displacement) > 1e-8)
          vectors.push({
            x: equilibrium,
            y: cy,
            dx: displacement,
            dy: 0,
            role: "displacement",
            label: `x ${displacement.toFixed(2)} m`,
            scale_mode: "physical",
            pixels_per_unit: Math.abs(span),
            units: "m"
          });
        if (Math.abs(velocity) > 1e-8)
          vectors.push({
            x,
            y: cy - 8,
            dx: velocity,
            dy: 0,
            role: "velocity",
            label: `v ${velocity.toFixed(2)} m/s`,
            scale_mode: "normalized",
            fixed_length_px: 38
          });
        const restoring = -(meta.stiffnessNm || 0) * displacement;
        if (Math.abs(restoring) > 1e-8)
          vectors.push({
            x,
            y: cy + 8,
            dx: restoring,
            dy: 0,
            role: "net_force",
            label: `spring force ${restoring.toFixed(1)} N`,
            scale_mode: "normalized",
            fixed_length_px: 46
          });
        PhysicsAnnotations.vectorSet(ctx, s, vectors, s.progress, {
          x: 12,
          y: 12 + index * 28
        });
        ctx.save();
        PhysicsVisuals.applyText(ctx, s, "annotation");
        ctx.fillStyle = PhysicsVisuals.token(
          s,
          "colors",
          "text_muted",
          "#526577"
        );
        ctx.fillText("\u2212A", left - 9, cy + 58);
        ctx.fillText("equilibrium", equilibrium - 34, cy + 58);
        ctx.fillText("+A", right - 7, cy + 58);
        ctx.restore();
      });
    }
  };
  globalThis.scene = scene;
})();
