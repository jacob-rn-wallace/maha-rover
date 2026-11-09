import { defineConfig } from "vite";
// relative base so the build works from https://<user>.github.io/<repo>/ without knowing the repo name
export default defineConfig({ base: "./", build: { target: "es2022" } });
