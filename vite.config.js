import { defineConfig } from "vite";
import { resolve } from "node:path";

export default defineConfig({
    build: {
        outDir: "src/static/js",
        emptyOutDir: true,
        manifest: "manifest.json",

        rolldownOptions: {
            input: {
                "modules/login": resolve("src/dev/ts/modules/login.ts"),
                "modules/registration": resolve("src/dev/ts/modules/registration.ts"),
                "pages/login": resolve("src/dev/ts/pages/login.ts"),
            },

            output: {
                entryFileNames: "[name]-[hash].js",
                chunkFileNames: "chunks/[name]-[hash].js",
                assetFileNames: "asset/[name][extname]",
            }
        }
    }
})