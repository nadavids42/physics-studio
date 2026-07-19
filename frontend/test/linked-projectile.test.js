import { describe, expect, it } from "vitest";

import {
  accessibleReadout,
  fractionFromGraphPointer,
  keyboardFraction,
  nearestIndex,
  sharedDomains,
  stateAt,
} from "../src/linked-projectile.js";

const run = {
  label: "Run A",
  time_s: [0, 1, 2],
  x_m: [0, 4, 8],
  y_m: [0, 3, 0],
  vx_m_s: [4, 4, 4],
  vy_m_s: [5, 0, -5],
  ax_m_s2: [0, 0, 0],
  ay_m_s2: [-5, -5, -5],
};

describe("linked projectile state", () => {
  it("samples one shared time for every representation", () => {
    expect(nearestIndex(run.time_s, 1.1)).toBe(1);
    expect(stateAt(run, 0.5)).toMatchObject({
      time: 1,
      x: 4,
      y: 3,
      vx: 4,
      vy: 0,
      ay: -5,
    });
  });

  it("uses shared comparison domains", () => {
    const second = { ...run, x_m: [0, 8, 16], vy_m_s: [8, 0, -8] };
    const domains = sharedDomains([run, second]);
    expect(domains.time).toEqual([0, 2]);
    expect(domains.position[1]).toBeGreaterThan(16);
    expect(domains.velocity[0]).toBeLessThan(-8);
  });
});

describe("linked projectile interactions", () => {
  it("maps graph pointing and keyboard steps onto the shared clock", () => {
    expect(fractionFromGraphPointer(150, 50, 200)).toBe(0.5);
    expect(fractionFromGraphPointer(10, 50, 200)).toBe(0);
    expect(keyboardFraction(0, "ArrowRight", 3)).toBe(0.5);
    expect(keyboardFraction(0.5, "End", 3)).toBe(1);
  });

  it("provides equivalent time and all vector values as text", () => {
    const readout = accessibleReadout([run], 0.5);
    expect(readout).toContain("t 1.00 s");
    expect(readout).toContain("position x 4.00 m, y 3.00 m");
    expect(readout).toContain("velocity vx 4.00 m/s, vy 0.00 m/s");
    expect(readout).toContain("acceleration ax 0.00 m/s², ay -5.00 m/s²");
  });
});
