import { FlatCompat } from "@eslint/eslintrc";
import { dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  {
    ignores: [
      ".next/",
      ".source/",
      ".wrangler/",
      "out/",
      "dist/",
      "node_modules/",
      "scripts/",
      "content/",
      "public/",
      "*.config.js",
      "*.config.ts",
      "*.config.mjs",
      "next-env.d.ts",
      "e2e/",
      "playwright-report/",
      "test-results/",
      ".open-next/",
      "bundled/",
    ],
  },
  ...compat.extends(
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
  ),
  {
    rules: {
      // ShipAny 模板既有代码暂降为 warn，后续逐步修复
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-empty-object-type": "warn",
      "@typescript-eslint/ban-ts-comment": "warn",
      "prefer-const": "warn",
      "react/display-name": "off",
      "react-hooks/rules-of-hooks": "warn",
      "@next/next/no-assign-module-variable": "warn",
    },
  },
];

export default eslintConfig;
