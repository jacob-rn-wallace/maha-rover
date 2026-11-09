import * as THREE from "three";
import { Terrain } from "./terrain";
import { RockField } from "./rocks";
import { FJS1 } from "./soil";
import { RoverPhysics, type Spec, type Controls } from "./physics";

/** The physics on its own thread: Rapier, the heightfield patch and the rock hulls run here, at their own clock, and a snapshot goes to the page each tick.
 *  The worker loads its own copy of the terrain (the page keeps one for drawing); both are deterministic, so they agree. Protocol in physicsProxy.ts. */
let phys: RoverPhysics | undefined;
let controls: Controls = { throttle: 0, turn: 0, pan: 0, tilt: 0, brake: true };
let resetFlag = false;
let names: string[] = [];

(self as any).onmessage = async (e: MessageEvent) => {
  const m = e.data;
  if (m.type === "init") {
    const spec: Spec = m.spec;
    let terrain: Terrain | undefined;
    if (m.terrainBase) {
      terrain = await Terrain.load(m.terrainBase, m.terrainOpts);
      if (m.rocks) terrain.rocks = new RockField(terrain, new THREE.MeshBasicMaterial(), terrain.spawn);
    }
    phys = await RoverPhysics.create(spec, m.spawnHeight, terrain, m.soil ? FJS1 : undefined);
    if (typeof m.mastRateDeg === "number" && m.mastRateDeg > 0) phys.mastRate = m.mastRateDeg * Math.PI / 180;
    names = Object.keys(spec.bodies);
    (self as any).postMessage({ type: "ready" });
    let last = performance.now();
    setInterval(() => {
      const now = performance.now(), dt = (now - last) / 1000; last = now;
      if (resetFlag) { resetFlag = false; phys!.resetUpright(); }
      phys!.advance(dt, controls);
      const buf = new Float32Array(names.length * 7);
      names.forEach((n, i) => { const b = phys!.bodies[n], t = b.translation(), r = b.rotation(); buf.set([t.x, t.y, t.z, r.x, r.y, r.z, r.w], i * 7); });
      const v = phys!.bodies.chassis.linvel();
      (self as any).postMessage({
        type: "state", buf, linvel: [v.x, v.y, v.z],
        tel: { linkAngle: phys!.linkAngle, panAngle: phys!.panAngle, tiltAngle: phys!.tiltAngle, wheelCurrent: phys!.wheelCurrent, wheelRate: phys!.wheelRate, soilState: phys!.soilState, motorPackAmps: phys!.motorPackAmps, servoMoving: phys!.servoMoving, tiltCut: phys!.tiltCut },
      }, [buf.buffer]);
    }, 8);
  } else if (m.type === "controls") controls = m.controls;
  else if (m.type === "reset") resetFlag = true;
};
