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
