# Performance logs

Logs written by the sim's performance recorder go here (they are small JSON files, a few hundred kB).

- **Benchmark:** open the sim with `?bench=1` (add `&maxpx=2.1` etc. to test other settings). It drives a fixed 60 s route (settle, straight, turn, straight, mast sweeps with the camera view on) with the adaptive resolution switched off (`&adapt=1` leaves it on), then shows the figures and a **Download the log file** button. Keep the window in front and do not touch the keys during the run. `?benchsecs=` changes the length.
- **Free recording:** press **L** at any time to start recording, **L** again to stop and get the same download.
- **Reading a log:** `npm run bench:summary -- bench/<file>.json`.
- The file holds the browser, GPU name, screen and window sizes, build (git commit), the settings, a per-second summary and every frame (frame time, main-thread time, pixel ratio, draw calls, triangles, position, the physics worker's step time and snapshot rate). Nothing is sent anywhere by the sim.
