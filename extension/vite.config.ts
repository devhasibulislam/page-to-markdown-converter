import {
  copyFileSync,
  mkdirSync,
  cpSync,
  renameSync,
  existsSync,
  rmSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { resolve } from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
  base: "",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        popup: resolve(__dirname, "src/popup.html"),
        background: resolve(__dirname, "src/background.ts"),
        content: resolve(__dirname, "src/content.ts"),
      },
      output: {
        entryFileNames: "[name].js",
        chunkFileNames: "chunks/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
    target: "es2022",
    minify: false,
  },
  plugins: [
    {
      name: "copy-manifest-and-flatten",
      closeBundle() {
        const dist = resolve(__dirname, "dist");
        mkdirSync(dist, { recursive: true });
        copyFileSync(resolve(__dirname, "src/manifest.json"), resolve(dist, "manifest.json"));
        cpSync(resolve(__dirname, "src/icons"), resolve(dist, "icons"), { recursive: true });

        const nested = resolve(dist, "src", "popup.html");
        if (existsSync(nested)) {
          const target = resolve(dist, "popup.html");
          const html = readFileSync(nested, "utf8").replace(/(["'])\.\.\//g, "$1./");
          writeFileSync(target, html);
          rmSync(resolve(dist, "src"), { recursive: true, force: true });
        }
      },
    },
  ],
});
