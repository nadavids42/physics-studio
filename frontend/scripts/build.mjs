import { build } from "esbuild";
import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const targets = [
  ["physics-visuals.js", "physics-visuals.js"],
  ["assets.js", "physics-assets.js"],
  ["vectors.js", "physics-vectors.js"],
  ["animation.js", "physics-animation.js"],
  ["experience.js", "physics-experience.js"],
  ["player-runtime.js", "player-runtime.js"],
  ["interactive-chart.js", "interactive-chart.js"],
  ["linked-projectile.js", "linked-projectile.js"],
  ["scenes/shared/vector-diagram.js", "scene-vector-diagram.js"],
  ["scenes/shared/ray-diagram.js", "scene-ray-diagram.js"],
  ["scenes/shared/wavefronts.js", "scene-wavefronts.js"],
  ["scenes/shared/scalar-field.js", "scene-scalar-field.js"],
  ["scenes/shared/gas-container.js", "scene-gas-container.js"],
  ["scenes/shared/diffusion-player.js", "scene-diffusion-player.js"],
  ["scenes/shared/vector-field.js", "scene-vector-field.js"],
  ["scenes/shared/fluid-container.js", "scene-fluid-container.js"],
  ["scenes/mechanics/shared.js", "scene-mechanics.js"],
  ["scenes/mechanics/bumper-cars.js", "scene-bumper-cars.js"],
  [
    "scenes/mechanics/bumper-cars-comparison.js",
    "scene-bumper-cars-comparison.js",
  ],
  ["scenes/mechanics/orbital-gravity.js", "scene-orbital-gravity.js"],
  ["scenes/mechanics/earth-tunnel.js", "scene-earth-tunnel.js"],
  ["scenes/mechanics/cannonball.js", "scene-cannonball.js"],
  ["scenes/waves/pendulum.js", "scene-pendulum.js"],
  ["scenes/waves/double-pendulum.js", "scene-double-pendulum.js"],
  ["scenes/waves/boing.js", "scene-boing.js"],
];

async function generate(entry) {
  const result = await build({
    entryPoints: [resolve(root, `src/${entry}`)],
    bundle: true,
    format: "iife",
    platform: "browser",
    target: ["es2020"],
    write: false,
    legalComments: "none",
  });
  return new TextDecoder().decode(result.outputFiles[0].contents);
}

for (const [entry, outputName] of targets) {
  const output = resolve(root, `../physics_playground/static/js/${outputName}`);
  const generated = await generate(entry);
  if (process.argv.includes("--check")) {
    const current = await readFile(output, "utf8").catch(() => "");
    if (current !== generated) {
      throw new Error(
        `Built frontend asset ${outputName} is stale. Run \`npm run build\` in frontend/.`,
      );
    }
  } else {
    await writeFile(output, generated);
  }
}
