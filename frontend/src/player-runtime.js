import { PhysicsVisuals } from "./physics-visuals.js";
import { PhysicsAssets } from "./assets.js";
import { PhysicsAnnotations } from "./vectors.js";
import { PhysicsAnimation } from "./animation.js";
import { PhysicsExperience } from "./experience.js";

export function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

export function lerp(a, b, amount) {
  return a + (b - a) * amount;
}

export function sample(values, fraction) {
  if (!Array.isArray(values) || values.length === 0) return 0;
  const index = clamp(fraction, 0, 1) * (values.length - 1);
  const lower = Math.floor(index);
  const upper = Math.min(values.length - 1, lower + 1);
  return lerp(values[lower], values[upper], index - lower);
}

export function validatePlayerConfig(config) {
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new TypeError("Player payload must be an object.");
  }
  if (!Number.isFinite(config.durationMs) || config.durationMs <= 0) {
    throw new TypeError("Player payload requires a positive durationMs.");
  }
  if (!Array.isArray(config.tracks)) {
    throw new TypeError("Player payload requires a tracks array.");
  }
  for (const track of config.tracks) {
    if (!track || typeof track.id !== "string" || !Array.isArray(track.x)) {
      throw new TypeError(
        "Each player track requires a string id and x array.",
      );
    }
  }
  return config;
}

export function resolveVisualTheme(config, media = globalThis.matchMedia) {
  const requested = config.theme || "auto";
  const prefersDark =
    requested === "auto" &&
    typeof media === "function" &&
    media("(prefers-color-scheme: dark)").matches;
  const dark = requested === "dark" || prefersDark;
  config.resolvedTheme = dark ? "dark" : "light";
  config.visualTokens =
    (config.visualThemes || {})[config.resolvedTheme] ||
    config.visualTokens ||
    {};
  if (globalThis.document?.documentElement) {
    document.documentElement.dataset.psTheme = config.resolvedTheme;
  }
  return config.resolvedTheme;
}

export function seededRandom(seed) {
  let state = seed >>> 0 || 1;
  return function random() {
    state += 0x6d2b79f5;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

export class PlaybackState {
  constructor(config) {
    this.config = validatePlayerConfig(config);
    this.fraction = 0;
    this.state = "idle";
    this.playbackRate = 1;
  }

  play() {
    if (this.state === "done") this.fraction = 0;
    this.state = "playing";
  }

  pause() {
    this.state = "paused";
  }

  seek(fraction) {
    this.fraction = clamp(fraction, 0, 1);
    if (this.fraction < 1 && this.state === "done") this.state = "paused";
    return this.fraction;
  }

  frameCount() {
    return Math.max(
      2,
      this.config.frameCount || 0,
      ...this.config.tracks.map((track) =>
        Math.max(track.x?.length || 0, track.y?.length || 0),
      ),
    );
  }

  stepFrames(amount) {
    this.pause();
    const count = this.frameCount();
    const index = Math.round(this.fraction * (count - 1));
    return this.seek(clamp(index + amount, 0, count - 1) / (count - 1));
  }

  advance(seconds) {
    if (this.state !== "playing") return this.fraction;
    this.fraction = clamp(
      this.fraction +
        (seconds * this.playbackRate) / (this.config.durationMs / 1000),
      0,
      1,
    );
    if (this.fraction >= 1) this.state = "done";
    return this.fraction;
  }
}

export class ParticleSystem {
  constructor(random, reducedMotion) {
    this.items = [];
    this.random = random;
    this.reducedMotion = reducedMotion;
  }
  burst(x, y, count, colors) {
    if (this.reducedMotion) return;
    for (let index = 0; index < count; index += 1) {
      const angle = this.random() * Math.PI * 2;
      const speed = 90 + this.random() * 210;
      this.items.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 80,
        life: 1,
        size: 2 + this.random() * 3,
        color: colors[Math.floor(this.random() * colors.length)],
      });
    }
  }
  reset() {
    this.items = [];
  }
  update(seconds) {
    for (const item of this.items) {
      item.x += item.vx * seconds;
      item.y += item.vy * seconds;
      item.vy += 320 * seconds;
      item.life -= 1.6 * seconds;
    }
    this.items = this.items.filter((item) => item.life > 0);
  }
  draw(ctx) {
    for (const item of this.items) {
      ctx.globalAlpha = Math.max(0, item.life);
      ctx.fillStyle = item.color;
      ctx.beginPath();
      ctx.arc(item.x, item.y, item.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }
}

export class TrailStore {
  constructor(limit = 18) {
    this.limit = limit;
    this.items = new Map();
  }
  reset() {
    this.items.clear();
  }
  push(id, point) {
    const points = this.items.get(id) || [];
    points.push(point);
    while (points.length > this.limit) points.shift();
    this.items.set(id, points);
  }
  get(id) {
    return this.items.get(id) || [];
  }
}

export class AnimationPlayer {
  constructor(config, scene, environment = globalThis) {
    this.environment = environment;
    this.config = validatePlayerConfig(config);
    this.scene = scene;
    this.canvas = document.getElementById("animation-canvas");
    this.ctx = this.canvas?.getContext("2d");
    this.wrap = document.getElementById("canvas-wrap");
    this.playButton = document.getElementById("play-pause");
    this.replayButton = document.getElementById("replay");
    this.stepBackButton = document.getElementById("step-back");
    this.stepForwardButton = document.getElementById("step-forward");
    this.scrubber = document.getElementById("scrubber");
    this.speed = document.getElementById("speed");
    this.message = document.getElementById("message");
    this.hint = document.getElementById("hint");
    this.status = document.getElementById("status");
    this.reducedMotion =
      Boolean(config.reducedMotion) ||
      Boolean(
        environment.matchMedia?.("(prefers-reduced-motion: reduce)").matches,
      );
    document.body.classList.toggle(
      "high-contrast",
      Boolean(config.highContrast),
    );
    document.body.classList.toggle("large-text", Boolean(config.largeText));
    this.random = seededRandom(config.seed);
    this.particles = new ParticleSystem(this.random, this.reducedMotion);
    this.trails = new TrailStore(config.trailLength || 18);
    this.playback = new PlaybackState(config);
    this.lastTimestamp = null;
    this.fired = new Set();
    this.frameRequest = null;
    this.cssWidth = 1;
    this.cssHeight = 1;
    this.lastTrailFraction = null;
    this.fixedStep = 1 / 60;
    this.accumulator = 0;
    this.camera = new PhysicsAnimation.Camera(
      config.camera || {},
      this.reducedMotion,
    );
    this.boundPageHide = () => this.destroy();
    this.bind();
    this.resize();
    this.render(0);
    if (config.autoplay && !this.reducedMotion) this.play();
    else if (config.autoplay && this.reducedMotion) {
      this.status.textContent =
        "Reduced motion is enabled. Press Play to start the animation.";
    }
  }

  get fraction() {
    return this.playback.fraction;
  }
  set fraction(value) {
    this.playback.fraction = value;
  }
  get state() {
    return this.playback.state;
  }
  set state(value) {
    this.playback.state = value;
  }
  get playbackRate() {
    return this.playback.playbackRate;
  }
  set playbackRate(value) {
    this.playback.playbackRate = value;
  }

  bind() {
    this.onPlay = () => this.toggle();
    this.onReplay = () => this.replay();
    this.onStepBack = () => this.stepFrames(-1);
    this.onStepForward = () => this.stepFrames(1);
    this.onScrub = (event) => this.seek(Number(event.target.value) / 1000);
    this.onSpeed = (event) => {
      this.playbackRate = Number(event.target.value);
    };
    this.playButton.addEventListener("click", this.onPlay);
    this.replayButton.addEventListener("click", this.onReplay);
    this.stepBackButton.addEventListener("click", this.onStepBack);
    this.stepForwardButton.addEventListener("click", this.onStepForward);
    this.scrubber.addEventListener("input", this.onScrub);
    this.speed.addEventListener("change", this.onSpeed);
    this.resizeObserver = new this.environment.ResizeObserver(() =>
      this.resize(),
    );
    this.resizeObserver.observe(this.wrap);
    this.onVisibility = () => {
      if (document.hidden && this.state === "playing") this.pause();
    };
    document.addEventListener("visibilitychange", this.onVisibility);
    this.onKeydown = (event) => {
      if (
        ["INPUT", "SELECT", "BUTTON"].includes(document.activeElement.tagName)
      )
        return;
      if (event.key === " ") {
        event.preventDefault();
        this.toggle();
      } else if (event.key.toLowerCase() === "r") this.replay();
      else if (event.key === "ArrowRight") this.seek(this.fraction + 0.02);
      else if (event.key === "ArrowLeft") this.seek(this.fraction - 0.02);
      else if (event.key === "." || event.key === ">") this.stepFrames(1);
      else if (event.key === "," || event.key === "<") this.stepFrames(-1);
    };
    document.addEventListener("keydown", this.onKeydown);
    this.environment.addEventListener("pagehide", this.boundPageHide, {
      once: true,
    });
  }

  resize() {
    const box = this.wrap.getBoundingClientRect();
    const dpr = Math.min(
      this.config.maximumDpr || 2.5,
      Math.max(1, this.environment.devicePixelRatio || 1),
    );
    const nextWidth = Math.max(1, box.width);
    const nextHeight = Math.max(1, box.height);
    if (
      Math.abs(nextWidth - this.cssWidth) < 0.5 &&
      Math.abs(nextHeight - this.cssHeight) < 0.5 &&
      this.canvas.width === Math.round(nextWidth * dpr)
    )
      return;
    this.cssWidth = nextWidth;
    this.cssHeight = nextHeight;
    this.canvas.width = Math.round(this.cssWidth * dpr);
    this.canvas.height = Math.round(this.cssHeight * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.render(this.fraction);
  }

  coordinates() {
    const view = this.config.view || {};
    const xmin = view.minimum ?? 0;
    const xmax = view.maximum ?? 1;
    const left = 40;
    const right = this.cssWidth - 40;
    return {
      x: (value) =>
        left +
        ((value - xmin) / Math.max(0.0001, xmax - xmin)) * (right - left),
      y: (value) => this.cssHeight - 60 - value,
      width: this.cssWidth,
      height: this.cssHeight,
    };
  }

  snapshot(fraction) {
    const tracks = {};
    for (const track of this.config.tracks) {
      tracks[track.id] = {
        id: track.id,
        label: track.label,
        style: track.style || {},
        x: sample(track.x, fraction),
        y: track.y ? sample(track.y, fraction) : null,
        trail: this.trails.get(track.id),
      };
    }
    return tracks;
  }

  play() {
    if (this.state === "done") this.replay();
    this.playback.play();
    this.lastTimestamp = null;
    this.playButton.textContent = "⏸";
    this.playButton.setAttribute("aria-label", "Pause animation");
    this.hint.hidden = true;
    this.status.textContent = "Animation playing";
    this.ensureFrame();
  }
  pause() {
    this.playback.pause();
    this.playButton.textContent = "▶";
    this.playButton.setAttribute("aria-label", "Play animation");
    this.status.textContent = "Animation paused";
  }
  resume() {
    this.play();
  }
  toggle() {
    this.state === "playing" ? this.pause() : this.play();
  }
  replay() {
    this.fraction = 0;
    this.fired.clear();
    this.trails.reset();
    this.particles.reset();
    this.camera.reset();
    this.lastTrailFraction = null;
    this.message.classList.remove("show");
    this.scrubber.value = "0";
    this.scrubber.setAttribute("aria-valuetext", "0 percent");
    this.state = "paused";
    this.play();
  }
  seek(fraction) {
    this.playback.seek(fraction);
    this.scrubber.value = String(Math.round(this.fraction * 1000));
    this.scrubber.setAttribute(
      "aria-valuetext",
      `${Math.round(this.fraction * 100)} percent`,
    );
    this.fired.clear();
    for (const event of this.config.events || []) {
      if (event.fraction <= this.fraction) this.fired.add(event.id);
    }
    this.trails.reset();
    this.particles.reset();
    this.lastTrailFraction = null;
    if (this.fraction < 1) this.message.classList.remove("show");
    this.render(this.fraction);
    this.status.textContent = `Animation at ${Math.round(this.fraction * 100)} percent`;
  }
  frameCount() {
    return this.playback.frameCount();
  }
  stepFrames(amount) {
    const fraction = this.playback.stepFrames(amount);
    this.seek(fraction);
    const count = this.frameCount();
    this.status.textContent = `Frame ${Math.round(this.fraction * (count - 1)) + 1} of ${count}`;
  }
  ensureFrame() {
    if (this.frameRequest === null) {
      this.frameRequest = this.environment.requestAnimationFrame((timestamp) =>
        this.tick(timestamp),
      );
    }
  }
  tick(timestamp) {
    this.frameRequest = null;
    const rawElapsed =
      this.lastTimestamp === null ? 0 : (timestamp - this.lastTimestamp) / 1000;
    const elapsed = clamp(rawElapsed, 0, 0.25);
    this.lastTimestamp = timestamp;
    this.accumulator += elapsed;
    let stableElapsed = 0;
    let steps = 0;
    while (this.accumulator >= this.fixedStep && steps < 15) {
      stableElapsed += this.fixedStep;
      this.accumulator -= this.fixedStep;
      steps += 1;
    }
    if (this.state === "playing") {
      const previous = this.fraction;
      this.playback.advance(stableElapsed);
      this.fireEvents();
      this.scrubber.value = String(Math.round(this.fraction * 1000));
      this.scrubber.setAttribute(
        "aria-valuetext",
        `${Math.round(this.fraction * 100)} percent`,
      );
      if (previous < 1 && this.fraction >= 1) this.complete();
    }
    this.camera.update(stableElapsed);
    this.particles.update(stableElapsed);
    this.render(this.fraction);
    if (this.state === "playing" || this.particles.items.length)
      this.ensureFrame();
  }
  fireEvents() {
    for (const event of this.config.events || []) {
      if (this.fraction >= event.fraction && !this.fired.has(event.id)) {
        this.fired.add(event.id);
        if (this.scene.onEvent) this.scene.onEvent(event, this);
      }
    }
  }
  complete() {
    this.state = "done";
    this.playButton.textContent = "▶";
    this.playButton.setAttribute("aria-label", "Replay animation");
    this.message.textContent = this.config.completionMessage || "";
    this.message.classList.toggle(
      "show",
      Boolean(this.config.completionMessage),
    );
    this.status.textContent =
      this.config.completionMessage || "Animation complete";
  }
  render(fraction) {
    if (!this.scene || !this.ctx) return;
    const transform = this.coordinates();
    const tracks = this.snapshot(fraction);
    if (
      this.lastTrailFraction === null ||
      Math.abs(fraction - this.lastTrailFraction) > 1e-9
    ) {
      for (const track of Object.values(tracks)) {
        this.trails.push(track.id, { x: track.x, y: track.y });
      }
      this.lastTrailFraction = fraction;
    }
    this.scene.draw(this.ctx, {
      fraction,
      state: this.state,
      tracks,
      transform,
      particles: this.particles,
      trails: this.trails,
      reducedMotion: this.reducedMotion,
      config: this.config,
      camera: this.camera,
      effects: PhysicsAnimation,
    });
    this.particles.draw(this.ctx);
  }

  destroy() {
    if (this.frameRequest !== null) {
      this.environment.cancelAnimationFrame(this.frameRequest);
    }
    this.frameRequest = null;
    this.resizeObserver?.disconnect();
    this.playButton.removeEventListener("click", this.onPlay);
    this.replayButton.removeEventListener("click", this.onReplay);
    this.stepBackButton.removeEventListener("click", this.onStepBack);
    this.stepForwardButton.removeEventListener("click", this.onStepForward);
    this.scrubber.removeEventListener("input", this.onScrub);
    this.speed.removeEventListener("change", this.onSpeed);
    document.removeEventListener("visibilitychange", this.onVisibility);
    document.removeEventListener("keydown", this.onKeydown);
    this.environment.removeEventListener("pagehide", this.boundPageHide);
    this.particles.reset();
    this.trails.reset();
  }
}

export function mountPlayer(config, scene, environment = globalThis) {
  validatePlayerConfig(config);
  resolveVisualTheme(config, environment.matchMedia?.bind(environment));
  return new AnimationPlayer(config, scene, environment);
}

Object.assign(globalThis, {
  AnimationPlayer,
  ParticleSystem,
  PhysicsAnimation,
  PhysicsAnnotations,
  PhysicsAssets,
  PhysicsExperience,
  PhysicsVisuals,
  TrailStore,
  clamp,
  lerp,
  mountPhysicsPlayer: mountPlayer,
  resolveVisualTheme,
  sample,
  seededRandom,
});
