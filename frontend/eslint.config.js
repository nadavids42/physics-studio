import eslint from "@eslint/js";
import globals from "globals";

export default [
  { ignores: ["coverage/**", "dist/**"] },
  eslint.configs.recommended,
  {
    files: ["**/*.js", "**/*.mjs"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: { ...globals.browser, ...globals.node },
    },
  },
];
