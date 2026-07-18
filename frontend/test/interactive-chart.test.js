import { describe, expect, it } from "vitest";

import {
  domain,
  nearestPoint,
  zoomedDomain,
} from "../src/interactive-chart.js";

describe("interactive scientific chart geometry", () => {
  it("finds domains and the nearest sampled value deterministically", () => {
    expect(domain([2, 4, 8])).toEqual([2, 8]);
    const nearest = nearestPoint(
      [{ id: "a", label: "Run A", x: [0, 2, 4], y: [0, 3, 1] }],
      2.2,
    );
    expect(nearest).toMatchObject({ index: 1, x: 2, y: 3 });
  });

  it("zooms around the learner-selected coordinate", () => {
    expect(zoomedDomain([0, 100], 40, 0.5)).toEqual([15, 65]);
  });
});
