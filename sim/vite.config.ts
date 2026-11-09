import { defineConfig } from "vite";
import { execSync } from "node:child_process";
// relative base so the build works from https://<user>.github.io/<repo>/ without knowing the repo name
let commit = "unknown";
try { commit = execSync("git rev-parse --short HEAD", { cwd: __dirname }).toString().trim(); } catch {}
export default defineConfig({ base: "./", build: { target: "es2022" }, define: { __BUILD__: JSON.stringify(`${commit} ${new Date().toISOString().slice(0, 16)}Z`) } });
