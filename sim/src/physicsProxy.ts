import type { Spec, Controls } from "./physics";

/** The page's end of the physics worker (physicsWorker.ts): the same fields the HUD and the render loop read from RoverPhysics, filled from the worker's latest snapshot.
 *  advance() only sends the controls: the worker keeps its own clock. */
export interface BodyView { translation(): { x: number; y: number; z: number }; rotation(): { x: number; y: number; z: number; w: number }; linvel(): { x: number; y: number; z: number }; }
export interface PhysicsView {
  bodies: Record<string, BodyView>; gravity: number;
  linkAngle: { L: number; R: number }; panAngle: number; tiltAngle: number;
  wheelCurrent: Record<string, number>; wheelRate: Record<string, number>; soilState: Record<string, { load: number; slip: number; sinkage: number }>;
  motorPackAmps: number; servoMoving: boolean; tiltCut: boolean; stepMs?: number; snapHz?: number;
  advance(seconds: number, c: Controls): void; resetUpright(): void;
}

export class PhysicsProxy implements PhysicsView {
  bodies: Record<string, BodyView> = {};
  readonly gravity = 1.62;
  linkAngle = { L: 0, R: 0 }; panAngle = 0; tiltAngle = 0;
  wheelCurrent: Record<string, number> = {}; wheelRate: Record<string, number> = {}; soilState: Record<string, { load: number; slip: number; sinkage: number }> = {};
  motorPackAmps = 0; servoMoving = false; tiltCut = false;
  stepMs = 0; snapHz = 0; private snaps = 0; private snapT = performance.now();      // the worker's smoothed tick time and the snapshot rate seen here
  private worker: Worker; private names: string[]; private buf = new Float32Array(0); private linv = [0, 0, 0];
  private constructor(worker: Worker, spec: Spec) {
    this.worker = worker; this.names = Object.keys(spec.bodies);
    this.names.forEach((n, i) => {
      const t = { x: 0, y: 0, z: 0 }, r = { x: 0, y: 0, z: 0, w: 1 }, v = { x: 0, y: 0, z: 0 };
      this.bodies[n] = {
        translation: () => { const b = this.buf, k = i * 7; if (b.length) { t.x = b[k]; t.y = b[k + 1]; t.z = b[k + 2]; } return t; },
        rotation: () => { const b = this.buf, k = i * 7; if (b.length) { r.x = b[k + 3]; r.y = b[k + 4]; r.z = b[k + 5]; r.w = b[k + 6]; } return r; },
        linvel: () => { v.x = this.linv[0]; v.y = this.linv[1]; v.z = this.linv[2]; return v; },
      };
    });
    worker.onmessage = (e) => {
      const m = e.data;
      if (m.type !== "state") return;
      this.buf = m.buf; this.linv = m.linvel;
      this.snaps++; const now = performance.now(); if (now - this.snapT > 1000) { this.snapHz = Math.round(this.snaps * 1000 / (now - this.snapT)); this.snaps = 0; this.snapT = now; }
      Object.assign(this, m.tel);
    };
  }

  static async create(spec: Spec, opts: { spawnHeight: number; terrainBase?: string; terrainOpts?: object; rocks: boolean; soil: boolean; mastRateDeg?: number }): Promise<PhysicsProxy> {
    const worker = new Worker(new URL("./physicsWorker.ts", import.meta.url), { type: "module" });
    const ready = new Promise<void>((res, rej) => { worker.onmessage = (e) => { if (e.data.type === "ready") res(); }; worker.onerror = (e) => rej(new Error("physics worker: " + e.message)); });
    worker.postMessage({ type: "init", spec, ...opts });
    await ready;
    return new PhysicsProxy(worker, spec);
  }
  advance(_seconds: number, c: Controls) { this.worker.postMessage({ type: "controls", controls: c }); }
  resetUpright() { this.worker.postMessage({ type: "reset" }); }
}
