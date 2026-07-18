import { beforeEach, describe, expect, it } from "vitest";

import { scene as cannonball } from "../src/scenes/mechanics/cannonball.js";
import { scene as rayDiagram } from "../src/scenes/shared/ray-diagram.js";
import { scene as pendulum } from "../src/scenes/waves/pendulum.js";

function contextRecorder() {
  const operations = [];
  const gradient = {
    addColorStop: (...args) => operations.push(["colorStop", ...args]),
  };
  const context = new Proxy(
    { operations },
    {
      get(target, name) {
        if (name in target) return target[name];
        if (name === "measureText") return () => ({ width: 40 });
        if (
          name === "createLinearGradient" ||
          name === "createRadialGradient"
        ) {
          return () => gradient;
        }
        return (...args) => operations.push([String(name), ...args]);
      },
      set(target, name, value) {
        target[name] = value;
        operations.push([`set:${String(name)}`, value]);
        return true;
      },
    },
  );
  return context;
}

function calls(kind) {
  return globalThis.__sceneCalls.filter((entry) => entry.kind === kind);
}

beforeEach(() => {
  globalThis.__sceneCalls.length = 0;
});

describe("representative scene adapters", () => {
  it("renders a mechanics trajectory with launcher, trail, and projectile", () => {
    const ctx = contextRecorder();
    const trails = new Map([
      [
        "ball",
        [
          { x: 0, y: 0 },
          { x: 2, y: 1 },
        ],
      ],
    ]);
    cannonball.draw(ctx, {
      fraction: 0.5,
      reducedMotion: false,
      transform: { width: 680, height: 360 },
      config: {
        angle: 45,
        target: 8,
        view: { xMin: 0, xMax: 10, yMin: 0, yMax: 5 },
        tracks: [{ id: "ball" }],
      },
      tracks: { ball: { id: "ball", x: 2, y: 1, style: {} } },
      trails: { get: (id) => trails.get(id) || [] },
    });
    expect(calls("assets.cannon")).toHaveLength(1);
    expect(calls("assets.projectile")).toHaveLength(1);
    expect(calls("animation.fadingTrail")).toHaveLength(1);
    expect(ctx.operations.some(([operation]) => operation === "arc")).toBe(
      true,
    );
  });

  it("renders an oscillation with a pivot, cable, bob, and bounded trail", () => {
    const ctx = contextRecorder();
    pendulum.draw(ctx, {
      reducedMotion: false,
      transform: { width: 500, height: 440 },
      config: { maxLength: 2, tracks: [{ id: "bob" }] },
      tracks: { bob: { id: "bob", x: 0.5, y: -1.8, style: {} } },
      trails: {
        get: () => [
          { x: 0, y: -2 },
          { x: 0.5, y: -1.8 },
        ],
      },
    });
    expect(calls("assets.pivot")).toHaveLength(1);
    expect(calls("assets.cable")).toHaveLength(1);
    expect(calls("assets.pendulumBob")).toHaveLength(1);
    expect(calls("animation.fadingTrail")).toHaveLength(1);
  });

  it("renders an optics lens and physical ray geometry", () => {
    const ctx = contextRecorder();
    rayDiagram.draw(ctx, {
      fraction: 1,
      reducedMotion: true,
      transform: { width: 640, height: 360 },
      config: {
        presentationLevel: "diagram",
        rayConfig: {
          xmin: -5,
          xmax: 5,
          ymin: -3,
          ymax: 3,
          lens: true,
          lensSign: 1,
          rays: [{ x1: -4, y1: 1, x2: 4, y2: -1, label: "principal" }],
        },
      },
    });
    expect(calls("assets.lens")).toHaveLength(1);
    expect(calls("assets.ray")).toHaveLength(1);
    expect(calls("experience.context")[0].args[2]).toBe("opticsBench");
  });
});

const allSceneModules = import.meta.glob(
  "../src/scenes/{mechanics,shared,waves}/*.js",
);

it("loads every extracted scene as an executable adapter", async () => {
  expect(Object.keys(allSceneModules)).toHaveLength(17);
  for (const load of Object.values(allSceneModules)) {
    const module = await load();
    expect(module.scene).toBeTypeOf("object");
    expect(module.scene.draw).toBeTypeOf("function");
  }
});
