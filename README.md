# Phosphor

A local ASCII photo booth for SD5913 Assignment 3. Live camera frames become green characters inside a fictional retro instrument. This is an evolving prototype, not a claim of completed submission or verified course compliance.

## Run

On macOS, double-click **Run.command** with [uv](https://docs.astral.sh/uv/) installed. Keep its Terminal open; Ctrl-C stops the server. Finder/security behaviour still needs a real-machine trial.

Alternatively, from this folder:

```sh
uv run start.py
uv run start.py --port 8766 --no-browser
```

The server binds to 127.0.0.1 (default port 8765). Use localhost, not file://. No frontend build, CDN, API key or application package installation is needed. uv may provision Python on first use. Browser APIs require a supported secure context.

## Current interaction

- **Camera power** is the only initial camera entry. It requests video, never audio. Power OFF cancels pending work, stops tracks and clears the session image.
- **Take photo** freezes the current frame immediately, without a countdown. Power stays ON and the camera remains active. Press it again to resume live ASCII using the same healthy stream.
- **Switch camera** works from live preview. One-device setups report unavailability without another media request. A request alone never flips the same camera; actual device identity/facing determines verified switching and mirroring.
- **Copy** copies the exact live/frozen ASCII text at click time, including whitespace. Clipboard denial/unavailability reports failure and attempts manual text selection.
- **Save** downloads the frozen ASCII as a flat PNG. Its separate footer reads `ASCamera - FATQ`; filename format is `ascamera-portrait-YYYYMMDD-HHMMSS-mmm.png`, using local time.
- **Density** uses a draggable, keyboard-accessible knob: 40–160 columns, step 8, default 96. It works while OFF, live or frozen. The numeric readout is inside the CRT.

The four action keys stay enabled and visible in one row; unavailable actions explain why without requesting permission. Power and knob sit horizontally together on the left. Narrow layouts can wrap the instrument/key groups. There is no public demo, Retake or Stop/Clear key.

## Visual direction

Warm off-white housing, four sloping recess faces meeting gently bowed glass, sculpted keys, orange capture key, red mechanical power switch and a raised density grip with a subtle 3px marker. Boot lettering is real ASCII. English status and density feedback remain inside the green CRT.

One shared subtle SVG displacement curves the whole screen interior, including boot text, status and picture—not the physical controls. PNG and copied text stay unwarped. The earlier crt.js picture mesh is a legacy/test utility, not a runtime dependency. The full source frame is preserved rather than cropped.

## Privacy and recovery

- No automatic camera start, audio recording, upload, analytics, cookies, localStorage or automatic photo history.
- Freezing pauses conversion, **not** the camera. Turn power OFF to release it.
- Hiding the tab, pagehide or camera interruption closes the session. Returning does not restart it automatically.
- Late results from cancelled permission requests are stopped. The browser's permission prompt itself cannot be dismissed by the app.
- Permission denial, missing/busy cameras and unsupported/insecure contexts have recovery feedback. Browser site settings control permissions.
- This is a private local tool, not a hardened public server. Save/copy only when you intend to create an external copy.

Some runtime messages still mention removed Close/Stop controls or disabled switching. These are documented follow-up issues, not additional current controls.

## Verification status

This documentation pass did **not** run tests, use a real camera or visually certify screenshots. Earlier iterations reported passing suites; the latest handoff reported 86 tests, but source changed afterwards. **The current full suite is not confirmed passing.** In particular, tests/browser.py still expects `phosphor-portrait.png`, conflicting with the current timestamped filename and likely failing that assertion.

Commands for a later authorized verification pass:

```sh
node --test tests/ascii.test.js
uv run tests/browser.py
uv run tests/launcher.py
zsh -n Run.command
```

Browser fixtures use synthetic Canvas MediaStreams, not physical cameras. Historical approximately 15 FPS observations describe synthetic DOM updates, not hardware latency. Safari/iOS, real front/rear switching, Finder launch, current visual quality and genuine peer testing remain pending. `demo-1200.png` and `demo-400.png` are early examples, not certified current screenshots.

## Documentation and delivery

- [AI documentation index](docs/INDEX.md), [current state](CURRENT.md), [pending work](TODO.md).
- [Process history](PROCESS.md): earlier countdown, fader, stop-on-capture and two-row layouts are historical and superseded.
- [Credits and AI assistance](CREDITS.md): review and disclose assistance under current course policy.
- A later private GitHub development repository was requested but is not yet confirmed or created. The assignment requires a public repository at delivery; resolve visibility and publication scope before submission. No repository publication is claimed here.

## References

- [SD5913 Week 5](https://github.com/sd5913/pfad/tree/2026/week05): brightness-to-character and interactive-parameter concepts. Existing classroom work remains untouched.
- Browser reference entry points: [getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia), [Canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API). These links are not a claim of live retrieval during this documentation pass.
