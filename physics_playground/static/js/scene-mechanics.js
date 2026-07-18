(() => {
  // src/scenes/scene-api.js
  var PhysicsAnimation = globalThis.PhysicsAnimation;
  var PhysicsAnnotations = globalThis.PhysicsAnnotations;
  var PhysicsAssets = globalThis.PhysicsAssets;
  var PhysicsExperience = globalThis.PhysicsExperience;
  var PhysicsVisuals = globalThis.PhysicsVisuals;
  var sample = globalThis.sample;

  // src/scenes/mechanics/shared.js
  var scene = {
    draw(ctx, s) {
      const { width: w, height: h } = s.transform, c = s.config.mechanics || {}, kind = s.config.scene;
      PhysicsExperience.context(
        ctx,
        s,
        kind === "coaster" ? "rollerCoaster" : "laboratory"
      );
      if (kind === "ramp") {
        const theta = (c.angleDeg || 0) * Math.PI / 180, maxRun = w - 140, run = Math.min(maxRun, (h - 150) / Math.max(Math.tan(theta), 1e-3)), x0 = (w - run) / 2, y0 = 70, x1 = x0 + run, y1 = y0 + Math.tan(theta) * run;
        const rampHeight = Math.max(4, y1 - y0), progress = s.tracks.block?.x || 0, bx = x0 + (x1 - x0) * progress, by = y0 + (y1 - y0) * progress - 23;
        PhysicsAssets.ramp(ctx, s, {
          x: (x0 + x1) / 2,
          y: y0 + rampHeight / 2,
          width: x1 - x0,
          height: rampHeight,
          descending: true,
          fill: PhysicsVisuals.token(s, "colors", "surface_muted", "#EAF0F6")
        });
        PhysicsAnnotations.pathGuide(ctx, s, {
          points: [
            { x: x0, y: y0 - 28 },
            { x: x1, y: y1 - 28 }
          ],
          opacity: 0.45
        });
        PhysicsAnnotations.normalLine(ctx, s, {
          x: bx,
          y: by,
          length: 92,
          surface_angle: theta,
          label: "normal"
        });
        PhysicsAssets.block(ctx, s, {
          x: bx,
          y: by,
          rotation: theta,
          width: 52,
          height: 38,
          label: c.motionState || "block",
          highlight: true,
          selected: c.moving
        });
        PhysicsAnnotations.angleArc(ctx, s, {
          x: x0,
          y: y0,
          radius: 34,
          startAngle: 0,
          endAngle: theta,
          label: `${(c.angleDeg || 0).toFixed(0)}\xB0`
        });
        const vectors = (c.vectors || []).map((v) => ({ ...v, x: bx, y: by }));
        PhysicsAnnotations.vectorSet(ctx, s, vectors, s.progress, {
          x: 12,
          y: 12
        });
        if (c.moving)
          PhysicsAnnotations.motionDirection(ctx, s, {
            x: bx + 24 * Math.cos(theta),
            y: by + 24 * Math.sin(theta),
            end: { x: bx + 66 * Math.cos(theta), y: by + 66 * Math.sin(theta) },
            label: "motion",
            disclosure_y: 68
          });
        PhysicsAssets.callout(ctx, s, {
          x: w - 245,
          y: 24,
          width: 220,
          height: 76,
          text: `${c.motionState || ""} \xB7 ${c.frictionState || ""}
Slip threshold: ${(c.criticalAngleDeg || 0).toFixed(1)}\xB0
Max static friction: ${(c.staticFrictionLimitN || 0).toFixed(1)} N`,
          target: { x: bx, y: by }
        });
      } else if (kind === "lever") {
        const cx = w / 2, cy = h * 0.55, turn = (s.tracks.beam?.x || 0) * Math.PI / 180, half = Math.min(w * 0.37, 260), maxArm = Math.max(c.loadArmM || 1, c.effortArmM || 1), scale = half / maxArm;
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(turn);
        PhysicsAssets.rod(ctx, s, {
          x: -half,
          y: 0,
          end: { x: half * 2, y: 0 },
          lineWidth: 12,
          label: ""
        });
        const lx = -(c.loadArmM || 0) * scale, ex = (c.effortArmM || 0) * scale;
        PhysicsAssets.block(ctx, s, {
          x: lx,
          y: -29,
          width: 44,
          height: 36,
          label: "load"
        });
        PhysicsAssets.block(ctx, s, {
          x: ex,
          y: -29,
          width: 44,
          height: 36,
          label: "effort",
          fill: PhysicsVisuals.token(s, "colors", "selected", "#7C3AED")
        });
        PhysicsAnnotations.dimensionLine(ctx, s, {
          x: lx,
          y: 32,
          end: { x: 0, y: 32 },
          label: `${(c.loadArmM || 0).toFixed(1)} m`
        });
        PhysicsAnnotations.dimensionLine(ctx, s, {
          x: 0,
          y: 50,
          end: { x: ex, y: 50 },
          label: `${(c.effortArmM || 0).toFixed(1)} m`
        });
        ctx.restore();
        PhysicsAssets.pivot(ctx, s, { x: cx, y: cy + 18, label: "pivot" });
        PhysicsAnnotations.centerOfMass(ctx, s, {
          x: cx,
          y: cy,
          label: "beam COM",
          radius: 7
        });
        PhysicsAnnotations.vectorSet(
          ctx,
          s,
          [
            {
              x: cx - (c.loadArmM || 0) * scale,
              y: cy - 48,
              dx: 0,
              dy: -1,
              role: "gravity",
              label: `load ${(c.loadForceN || 0).toFixed(0)} N`,
              scale_mode: "normalized",
              fixed_length_px: 48
            },
            {
              x: cx + (c.effortArmM || 0) * scale,
              y: cy - 48,
              dx: 0,
              dy: -1,
              role: "net_force",
              label: `effort ${(c.effortForceN || 0).toFixed(0)} N`,
              scale_mode: "normalized",
              fixed_length_px: 48
            }
          ],
          s.progress
        );
        if ((c.loadTorqueNm || 0) > 0)
          PhysicsAssets.torqueArc(ctx, s, {
            x: cx,
            y: cy,
            radius: 62,
            startAngle: 3.6,
            endAngle: 1.7,
            counterclockwise: true,
            label: "load torque"
          });
        if ((c.effortTorqueNm || 0) > 0)
          PhysicsAssets.torqueArc(ctx, s, {
            x: cx,
            y: cy,
            radius: 82,
            startAngle: -0.5,
            endAngle: 1.35,
            label: "effort torque",
            fill: PhysicsVisuals.token(s, "colors", "selected", "#7C3AED")
          });
        if (Math.abs(c.netTorqueNm || 0) > 1e-9)
          PhysicsAssets.torqueArc(ctx, s, {
            x: cx,
            y: cy,
            radius: 105,
            startAngle: -0.4,
            endAngle: 1.1,
            counterclockwise: (c.netTorqueNm || 0) < 0,
            label: "net torque"
          });
      } else if (kind === "coaster") {
        const car = s.tracks.car, pad = 62, top = 48, bottom = h - 58, length = c.trackLengthM || 1, maxHeight = Math.max(1, ...(c.trackPoints || []).map((q) => q.height)), X = (d) => pad + d / length * (w - pad * 2), Y = (v) => bottom - v / maxHeight * (bottom - top), points = (c.trackPoints || []).map((q) => ({
          x: X(q.distance),
          y: Y(q.height)
        })), reachable = Math.max(
          0,
          Math.min(length, c.reachableDistanceM ?? length)
        );
        const heightAt = (d) => {
          for (let i = 1; i < (c.trackPoints || []).length; i++) {
            const a = c.trackPoints[i - 1], b = c.trackPoints[i];
            if (d <= b.distance) {
              const u = (d - a.distance) / (b.distance - a.distance);
              return a.height + (b.height - a.height) * u;
            }
          }
          return c.trackPoints?.at(-1)?.height || 0;
        };
        const reachablePoints = points.filter(
          (_, i) => c.trackPoints[i].distance <= reachable
        );
        if (reachable < length) {
          const hStop = heightAt(reachable), stop = { x: X(reachable), y: Y(hStop) };
          if (!reachablePoints.length || reachablePoints.at(-1).x !== stop.x)
            reachablePoints.push(stop);
          const unavailable = [
            stop,
            ...points.filter((_, i) => c.trackPoints[i].distance > reachable)
          ];
          PhysicsAssets.track(ctx, s, {
            points: unavailable,
            dashed: true,
            opacity: 0.42
          });
          PhysicsAssets.callout(ctx, s, {
            x: Math.min(w - 205, stop.x + 12),
            y: Math.max(22, stop.y - 82),
            width: 184,
            height: 52,
            text: "Unreachable with\ncurrent energy",
            target: stop
          });
        }
        PhysicsAssets.track(ctx, s, { points: reachablePoints });
        PhysicsAssets.ruler(ctx, s, {
          x: pad - 20,
          y: bottom,
          width: bottom - top,
          rotation: -Math.PI / 2,
          divisions: 5,
          maximum: maxHeight,
          showValues: PhysicsVisuals.responsive(s) !== "mobile"
        });
        const distance = (car?.x || 0) * length, height = heightAt(distance), speed = car?.y || 0, x = X(distance), y = Y(height) - 18, next = Math.min(length, distance + length * 0.01), slope = Math.atan2(
          Y(heightAt(next)) - Y(height),
          X(next) - X(distance)
        ), pe = (c.massKg || 0) * (c.gravityMps2 || 9.81) * height, ke = 0.5 * (c.massKg || 0) * speed * speed, lost = (c.lossPerMeterJ || 0) * distance;
        PhysicsAssets.cart(ctx, s, {
          x,
          y,
          rotation: slope,
          width: 56,
          height: 28,
          label: "coaster"
        });
        if (speed > 0)
          PhysicsAnnotations.motionDirection(ctx, s, {
            x: x + 18 * Math.cos(slope),
            y: y + 18 * Math.sin(slope),
            end: { x: x + 54 * Math.cos(slope), y: y + 54 * Math.sin(slope) },
            label: `${speed.toFixed(1)} m/s`
          });
        PhysicsAssets.callout(ctx, s, {
          x: 18,
          y: 20,
          width: 210,
          height: 68,
          text: `Height ${height.toFixed(1)} m
PE ${pe.toFixed(0)} J \xB7 KE ${ke.toFixed(0)} J
Lost ${lost.toFixed(0)} J`
        });
        if ((c.lossPerMeterJ || 0) > 0)
          PhysicsAnnotations.disclosure(
            ctx,
            s,
            "schematic",
            "Mechanical energy decreases by the modeled loss per meter",
            12,
            h - 34
          );
      } else if (kind === "rotation") {
        const cx = w / 2, cy = h * 0.52, total = s.tracks.body?.x || 0, angle = (total % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2), radius = Math.min(82, w * 0.16);
        PhysicsAnnotations.pathGuide(ctx, s, {
          points: [
            { x: cx - radius - 18, y: cy },
            { x: cx + radius + 18, y: cy }
          ],
          opacity: 0.35
        });
        if (c.shape === "Rod about center")
          PhysicsAssets.rod(ctx, s, {
            x: cx - radius,
            y: cy,
            rotation: angle,
            end: { x: radius * 2, y: 0 },
            lineWidth: 11
          });
        else if (c.shape === "Solid sphere")
          PhysicsAssets.sphere(ctx, s, {
            x: cx,
            y: cy,
            radius,
            rotation: angle,
            label: ""
          });
        else if (c.shape === "Point mass") {
          PhysicsAssets.rod(ctx, s, {
            x: cx,
            y: cy,
            rotation: angle,
            end: { x: radius, y: 0 },
            lineWidth: 4
          });
          PhysicsAssets.mass(ctx, s, {
            x: cx + Math.cos(angle) * radius,
            y: cy + Math.sin(angle) * radius,
            radius: 18,
            label: "point mass"
          });
        } else
          PhysicsAssets.wheel(ctx, s, {
            x: cx,
            y: cy,
            radius,
            rotation: angle,
            fill: c.shape === "Hoop" ? PhysicsVisuals.token(s, "colors", "surface_muted", "#EAF0F6") : PhysicsVisuals.token(s, "colors", "uncertainty", "#6B7280")
          });
        PhysicsAssets.pivot(ctx, s, {
          x: cx,
          y: cy + 5,
          width: 24,
          height: 22,
          label: "axis"
        });
        PhysicsAnnotations.angleArc(ctx, s, {
          x: cx,
          y: cy,
          radius: radius + 18,
          startAngle: 0,
          endAngle: Math.min(angle, Math.PI * 1.8),
          label: "\u03B8"
        });
        if (Math.abs(c.torqueNm || 0) > 1e-9)
          PhysicsAssets.torqueArc(ctx, s, {
            x: cx,
            y: cy,
            radius: radius + 38,
            counterclockwise: (c.torqueNm || 0) < 0,
            label: "\u03C4"
          });
        if (Math.abs(c.omegaRadS || 0) > 1e-9)
          PhysicsAssets.torqueArc(ctx, s, {
            x: cx,
            y: cy,
            radius: radius + 58,
            startAngle: -0.5,
            endAngle: 0.9,
            counterclockwise: (c.omegaRadS || 0) < 0,
            label: "\u03C9 (schematic)",
            fill: PhysicsVisuals.token(s, "colors", "velocity", "#087EA4")
          });
        PhysicsAnnotations.disclosure(
          ctx,
          s,
          "schematic",
          "Angular indicators are schematic; orientation uses recorded \u03B8",
          12,
          12
        );
        PhysicsAssets.callout(ctx, s, {
          x: w - 226,
          y: 24,
          width: 202,
          height: 62,
          text: `Total \u03B8: ${total.toFixed(2)} rad
${(Math.abs(total) / (Math.PI * 2)).toFixed(2)} turns`
        });
      } else {
        const left = 62, right = w - 62, y = h * 0.52, X = (x) => left + (x + 5) / 10 * (right - left), items = c.objects || [];
        PhysicsAnnotations.pathGuide(ctx, s, {
          points: [
            { x: left, y },
            { x: right, y }
          ],
          dashes: [1, 0],
          opacity: 0.8
        });
        PhysicsAssets.ruler(ctx, s, {
          x: left,
          y: y + 44,
          width: right - left,
          divisions: 10,
          maximum: 10,
          showValues: PhysicsVisuals.responsive(s) !== "mobile"
        });
        for (const o of items) {
          const x = X(o.position), radius = Math.max(
            11,
            Math.min(24, 10 + Math.sqrt(Math.max(0, o.mass)) * 4)
          );
          PhysicsAssets.mass(ctx, s, {
            x,
            y: y - 24,
            radius,
            label: `${o.label}: ${o.mass.toFixed(1)} kg`,
            fill: PhysicsVisuals.token(s, "colors", o.role, "#1769AA"),
            selected: o.selected
          });
          PhysicsAnnotations.dimensionLine(ctx, s, {
            x: X(0),
            y: y + 18,
            end: { x, y: y + 18 },
            label: `${o.position.toFixed(1)} m`
          });
        }
        PhysicsAnnotations.centerOfMass(ctx, s, {
          x: X(c.centerM || 0),
          y: y - 24,
          label: `center ${(c.centerM || 0).toFixed(2)} m`
        });
        PhysicsAnnotations.disclosure(
          ctx,
          s,
          "schematic",
          "Mass radii are bounded illustrations; positions and dimensions use the ruler scale",
          12,
          12
        );
      }
    }
  };
  globalThis.scene = scene;
})();
