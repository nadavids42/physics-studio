import { describe, expect, it } from "vitest";

import { PhysicsVisuals } from "../src/physics-visuals.js";

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
