import { describe, expect, it } from "vitest";

import { PhysicsVisuals } from "../src/physics-visuals.js";
import { PhysicsAnnotations } from "../src/vectors.js";

describe("PhysicsVisuals", () => {
  it("executes responsive layout logic at runtime", () => {
    const state = { transform: { width: 420 }, config: { visualTokens: {} } };
    expect(PhysicsVisuals.responsive(state)).toBe("mobile");
    state.transform.width = 700;
    expect(PhysicsVisuals.responsive(state)).toBe("tablet");
    state.transform.width = 1200;
    expect(PhysicsVisuals.responsive(state)).toBe("desktop");
  });
});

describe("quantitative vector legends", () => {
  it("renders the declared linear force scale on canvas", () => {
    const operations = [];
    const ctx = new Proxy(
      { operations },
      {
        get(target, name) {
          if (name in target) return target[name];
          if (name === "measureText") return () => ({ width: 140 });
          return (...args) => operations.push([String(name), ...args]);
        },
        set(target, name, value) {
          target[name] = value;
          return true;
        },
      },
    );
    PhysicsAnnotations.scaleLegend(
      ctx,
      { transform: { width: 500 }, config: { visualTokens: {} } },
      [
        {
          scale_mode: "physical",
          pixels_per_unit: 4,
          units: "N",
        },
      ],
    );
    expect(
      operations.some(
        ([operation, text]) =>
          operation === "fillText" && text === "Force scale (linear): 10 N",
      ),
    ).toBe(true);
  });
});
