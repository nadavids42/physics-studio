import { build } from "esbuild";
import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const output = resolve(
  root,
  "../physics_playground/static/js/physics-visuals.js",
);
const result = await build({
  entryPoints: [resolve(root, "src/physics-visuals.js")],
  bundle: true,
  format: "iife",
  platform: "browser",
  target: ["es2020"],
  write: false,
  legalComments: "none",
});
const generated = new TextDecoder().decode(result.outputFiles[0].contents);

if (process.argv.includes("--check")) {
  const current = await readFile(output, "utf8").catch(() => "");
  if (current !== generated) {
    throw new Error(
      "Built frontend asset is stale. Run `npm run build` in frontend/.",
    );
  }
} else {
  await writeFile(output, generated);
}
