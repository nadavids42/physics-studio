import { afterEach, describe, expect, it } from "vitest";

import {
  AnimationPlayer,
  ParticleSystem,
  PlaybackState,
  validatePlayerConfig,
} from "../src/player-runtime.js";

const validConfig = (overrides = {}) => ({
  durationMs: 1000,
  tracks: [{ id: "body", x: [0, 1, 2], y: [0, 1, 0] }],
  ...overrides,
});

class FakeTarget {
  constructor() {
    this.listeners = new Map();
    this.classList = { add() {}, remove() {}, toggle() {} };
    this.tagName = "BODY";
    this.value = "0";
    this.hidden = false;
    this.textContent = "";
    this.attributes = new Map();
  }
  addEventListener(type, listener) {
    const values = this.listeners.get(type) || new Set();
    values.add(listener);
    this.listeners.set(type, values);
  }
  removeEventListener(type, listener) {
    this.listeners.get(type)?.delete(listener);
  }
  setAttribute(name, value) {
    this.attributes.set(name, String(value));
  }
  getBoundingClientRect() {
    return { width: 640, height: 360 };
  }
}

function installFakeBrowser() {
  const ids = Object.fromEntries(
    [
      "animation-canvas",
      "canvas-wrap",
      "play-pause",
      "replay",
      "step-back",
      "step-forward",
      "scrubber",
      "speed",
      "message",
      "hint",
      "status",
    ].map((id) => [id, new FakeTarget()]),
  );
  ids["animation-canvas"].getContext = () => ({
    setTransform() {},
    globalAlpha: 1,
  });
  ids["animation-canvas"].width = 0;
  ids["animation-canvas"].height = 0;
  const documentTarget = new FakeTarget();
  globalThis.document = Object.assign(documentTarget, {
    body: new FakeTarget(),
    activeElement: new FakeTarget(),
    documentElement: { dataset: {} },
    getElementById: (id) => ids[id],
    hidden: false,
  });
  class FakeResizeObserver {
    observe() {}
    disconnect() {
      this.disconnected = true;
    }
  }
  const environment = new FakeTarget();
  Object.assign(environment, {
    ResizeObserver: FakeResizeObserver,
    devicePixelRatio: 2,
    matchMedia: () => ({ matches: false }),
    requestAnimationFrame: () => 41,
    cancelAnimationFrame: (id) => {
      environment.cancelledFrame = id;
    },
  });
  return { documentTarget, environment, ids };
}

afterEach(() => {
  delete globalThis.document;
});

describe("PlaybackState", () => {
  it("plays, pauses, advances, and completes deterministically", () => {
    const playback = new PlaybackState(validConfig());
    playback.play();
    expect(playback.advance(0.25)).toBeCloseTo(0.25);
    playback.pause();
    expect(playback.advance(0.25)).toBeCloseTo(0.25);
    playback.playbackRate = 2;
    playback.play();
    playback.advance(0.5);
    expect(playback.fraction).toBe(1);
    expect(playback.state).toBe("done");
  });

  it("supports bounded stepping and scrubbing", () => {
    const playback = new PlaybackState(validConfig());
    expect(playback.stepFrames(1)).toBeCloseTo(0.5);
    expect(playback.stepFrames(5)).toBe(1);
    expect(playback.seek(-1)).toBe(0);
    expect(playback.seek(2)).toBe(1);
  });
});

it("suppresses decorative particles under reduced motion", () => {
  const particles = new ParticleSystem(() => 0.5, true);
  particles.burst(10, 10, 8, ["#fff"]);
  expect(particles.items).toEqual([]);
});

it("rejects malformed payloads before mounting", () => {
  expect(() => validatePlayerConfig(null)).toThrow(/object/);
  expect(() => validatePlayerConfig({ tracks: [] })).toThrow(/durationMs/);
  expect(() =>
    validatePlayerConfig({ durationMs: 100, tracks: [{ id: 2, x: [] }] }),
  ).toThrow(/track/);
});

it("teardown cancels animation and removes lifecycle listeners", () => {
  const { documentTarget, environment, ids } = installFakeBrowser();
  const player = new AnimationPlayer(validConfig(), { draw() {} }, environment);
  player.play();
  expect(player.frameRequest).toBe(41);
  player.destroy();
  expect(environment.cancelledFrame).toBe(41);
  expect(player.resizeObserver.disconnected).toBe(true);
  expect(documentTarget.listeners.get("keydown").size).toBe(0);
  expect(documentTarget.listeners.get("visibilitychange").size).toBe(0);
  expect(ids["play-pause"].listeners.get("click").size).toBe(0);
});

it("keeps native keyboard behavior inside player controls", () => {
  const { documentTarget, environment, ids } = installFakeBrowser();
  const player = new AnimationPlayer(validConfig(), { draw() {} }, environment);
  globalThis.document.activeElement = ids.scrubber;
  ids.scrubber.tagName = "INPUT";
  let prevented = false;
  const keydown = [...documentTarget.listeners.get("keydown")][0];
  keydown({ key: " ", preventDefault: () => (prevented = true) });
  expect(player.state).toBe("idle");
  expect(prevented).toBe(false);
  player.destroy();
});

it("exposes meaningful scrubber percentages", () => {
  const { environment, ids } = installFakeBrowser();
  const player = new AnimationPlayer(validConfig(), { draw() {} }, environment);
  player.seek(0.375);
  expect(ids.scrubber.attributes.get("aria-valuetext")).toBe("38 percent");
  player.stepFrames(1);
  expect(ids.scrubber.attributes.get("aria-valuetext")).toBe("100 percent");
  player.destroy();
});
