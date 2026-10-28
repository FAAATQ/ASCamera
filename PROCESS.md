# Process

## Current baseline — read before the history

The sections below preserve the actual sequence of iteration decisions and reported tests; they are not all current behaviour. Current source supersedes countdown, public demo, stop-on-capture, fader, disabled controls and two-row panel descriptions.

- Current panel: Take photo, Switch camera, Copy and Save in one row; power and density knob horizontally together on the left. All controls remain enabled; state guards explain unavailable actions inside the CRT in English.
- Power stays ON while frozen. Take photo toggles live/frozen using the retained stream; OFF, hidden tab, pagehide and interruption release the session. No countdown or Retake/Stop keys.
- Density is 40–160, step 8, default 96, including OFF-state adjustment. The raised grip carries a lighter 3px marker with shared scale angles.
- Current fictional hardware retains warm shell, direct four-facet-to-glass recess, subtle whole-screen convex effect, green ASCII boot lettering, red rocker and orange capture key. PNG stays flat, with ASCamera - FATQ footer and local timestamp/millisecond filename.
- No tests were run in this documentation pass. Latest handoff reported 86 passing checks before subsequent source changes; current full-suite success is unconfirmed. The browser harness still expects phosphor-portrait.png rather than the timestamped output, so that assertion is expected to fail until reviewed.
- demo-1200.png and demo-400.png are early examples, not current certified screenshots. Genuine peer trial, real-camera/mobile validation and final acceptance remain pending.
- See [CURRENT](CURRENT.md), [verification boundaries](docs/technical/verification.md) and [TODO](TODO.md) for the current baseline. No runtime, test or style edits were made by this documentation initialization.

## Historical record — superseded decisions remain attributed to their iteration

## Intent and first-draft decisions

The user selected camera → three-second countdown → ASCII snapshot, framed as an original retro green-terminal computer. The interaction promise is: **When I take a photo, the booth turns one moment into characters, then releases the camera.** Density changes the character grid, not the source image or camera capture.

The assistant implemented this draft in plain HTML/CSS/JavaScript with a small standard-library Python launcher. The Week 5 brightness/character idea is conceptual credit, not a claim that this is independent of class learning. Existing practice files were left untouched. The original requested destination was inaccessible to this isolated agent; implementation was made in its permitted worktree for explicit later integration, not silently installed in the original checkout.

Choices made during implementation:

- Chose a physical-computer bezel, phosphor screen, static scanlines and plain control labels rather than an imitation of a named product.
- Rejected continuous ASCII camera rendering: one snapshot makes the transformation easier to notice and stops camera access sooner.
- Rejected automatic camera startup and persistent image history. Explicit permission and a synthetic demo keep the first encounter optional.
- Used weighted luminance, a ten-character ramp, and a 0.5 character-aspect factor. These are approximations; camera exposure and typeface affect recognisability.
- Kept preview and captured output mirrored consistently. Export is an ASCII print, not the original photograph.

## Actual verification record

8 pure conversion tests passed. The first browser verification attempt failed because the Python Playwright `wait_for_function` argument needed the keyword `arg=`; that test harness call was fixed. The next run passed all 16 initial browser/launcher checks. A final expanded run passed 20 checks, adding superseded permission requests, active pagehide, unavailable API and unready video recovery. The camera indicator was also updated to turn on as soon as a stream arrives, before playback readiness. Two dedicated launcher tests additionally passed: actual executable Run.command fallback with uv absent from PATH, launched from another directory; and automatic browser dispatch/loopback binding/cleanup using a mocked browser opener. All test servers were stopped. Tests exercised the real local HTML in headless Chrome, using generated Canvas streams instead of a physical camera. Demo PNG signature and download filename, 1200px/400px layout overflow, and lifecycle paths were checked. Demo screenshots were generated; image Read output was blank in this agent's interface, so no visual review is claimed. No real camera permission, Finder double-click, Safari/iOS or user usability trial was performed.

## Framing correction verification

After the environment explicitly permitted the original workspace, corrected the preview/result/export mismatch there. The outlined viewfinder follows the full source aspect ratio within stage width and a viewport-limited height; preview and capture remain mirrored without cropping. Canvas measures the actual 16px monospace advance. Grid rows use that advance against a nominal 20px line height, then share a source-aspect-preserving effective line height between the uniformly scaled on-screen text and PNG. Export uses measured ascent/descent for baseline placement; its margin/footer sits outside the photo geometry, and footer text size shrinks if needed rather than clipping.

Final local regression: 9 pure tests, 28 browser checks, and 2 dedicated launcher tests passed. The browser suite uses synthetic Canvas streams only: colored edges and an interior fiducial at 640×480, 960×540, 480×640 and 540×960, each at 1200px and 400px viewport widths and 40/96/160 columns (24 PNG exports). Assertions cover source-aspect viewfinder bounds, unchanged preview/result framing, mirrored side edges, top/bottom preservation, fiducial retention, decoded PNG geometry, photo-margin bounds and separate footer content. Screenshots now go to the temporary directory rather than overwriting repository examples. No real camera or human visual/usability trial was performed; no global configuration, commit or push was made.

## Reported peer trial — feedback supplied by the project owner

Two classmates tried the experience. The owner supplied the following feedback; no names, recordings, exact trial date or verbatim quotations were provided. These are paraphrases, not assistant-observed sessions. Whether instructions were withheld before the trial has not been established.

| Participant | Reported observation | Decision and requested improvement |
| --- | --- | --- |
| A | The density knob felt too sensitive. | Accept: reduce pointer-drag sensitivity to 60% of the existing mapping. Preserve the 40–160-column range, step size and keyboard operation; use more physical travel for the same density change. |
| B | It was unclear how to begin; pressing Take photo should also turn on camera power. | Accept: a deliberate Take photo press while off starts the camera and switches power on. Once live preview is ready, the next press freezes the picture; further presses resume/freeze as before. Permission errors and repeated clicks must still receive clear feedback. |

Both decisions have now been implemented. Automated regression reported 10 pure tests, 2 launcher tests and 78 browser checks passing (90 total), using synthetic camera streams rather than a physical camera. A 40px pointer drag changes the default density from 96 to 120 with the reduced mapping. Off-state Take photo starts one camera request and enters live preview without immediately capturing; repeated clicks while permission is pending do not duplicate requests. The viewport correction also keeps idle/live/frozen enclosure dimensions stable at 1920×1080, 1680×898 and 390×844. Neither classmate has been reported to have retested the revised version; a follow-up trial is still needed. These changes have not yet been deployed or pushed.

## Remaining human trial checks

Ask a willing participant to use the current camera interaction with informed permission. No public demo is present. Do not retain their photo without explicit agreement. The earlier demo/countdown trial questions are superseded by these current questions.

- Can they identify Camera power as the initial entry and understand local-only handling?
- Can they freeze/resume with Take photo and understand that frozen output still uses an active camera?
- Does the density knob produce a recognisable portrait at both ends, including a preset while OFF?
- Can they copy text and find/open the timestamped, flat, signed PNG on desktop/mobile?
- Does Finder launch work, and does the real camera indicator switch off after power OFF or hiding/leaving the page?

The two owner-reported observations and adopted decisions are recorded above. Remaining device checks and follow-up trials are not yet verified. Record further observations and actual improvements without inventing quotations or claiming final acceptance, grades or complete course compliance.

## Live preview and camera switching iteration

The user subsequently requested live ASCII and deliberate mobile camera switching, superseding the initial frozen-only preview decision. Live conversion reuses one low-resolution Canvas sampling buffer and the existing measured-font text renderer. A single requestAnimationFrame chain gates work to at least 55ms between conversions (approximately 18 FPS target); conversion is synchronous, with no queued frame jobs or catch-up loop. Preview starts at 96 columns; density also updates live. Capture retains the three-second countdown, stops scheduling/tracks and freezes the full-resolution snapshot; retake explicitly resumes. Stop, pagehide, hidden tab, interruption and superseded requests retain cleanup/token guards.

Switch requests stop the old stream before requesting the opposite ideal facing, preserving density. Track-reported facing controls front mirroring/rear non-mirroring across live/frozen/export. Missing facing is explicitly unverified rather than claimed successful; orientation then follows the requested facing. A rejected switch attempts the prior facing (except permission denial), while a single-camera fallback reports the retained actual camera. Switching is hidden and guarded outside ready preview.

Final verification: 9 pure tests + 40 browser checks + 2 launcher tests passed (51 total, including all prior 39 checks). Added synthetic real-frame progression, live density, cancel continuity, freeze/save, resumed/closed scheduling, hidden-tab cleanup, dual-facing orientation, single-camera fallback, unreported facing, rejected-switch restoration and close during pending switch. The first switching-test run read an intermediate requesting state too early; waiting for preview readiness fixed the test, then all checks passed. Synthetic sample measured 23 rendered text updates across 1464.6ms: 15.02 updates/second, minimum interval 64.2ms. These figures measure synthetic local DOM update cadence only, not real camera latency, mobile capability or hardware FPS. Real phone/Safari front/rear switching, orientation and download verification remain pending. Run.command is unchanged. No real camera, upload/storage, global edits, commit or push.

## References

See README.md and CREDITS.md for sources and assistance attribution.

## Single-camera bug correction and text copy

User reported that a laptop switch merely flipped the same camera. Corrected the earlier requested-facing fallback: a switch request alone never changes effective mirroring. After permission, enumerate video inputs; disable switch when exactly one is reported. Compare actual track device IDs, with changed explicit facing as fallback only when IDs are absent. Returning the same ID cannot change orientation even if facing reports conflict. Unverified results retain effective identity/orientation; request failures still restore the previous device ID where available. Added explicit Copy ASCII text for live/frozen click-time content, secure Clipboard API success/failure feedback and manual-selection fallback.

Final tests: 9 pure + 45 browser + 2 launcher = 56 passed. Updated synthetic camera mocks now provide stable physical device IDs and enumeration; tests cover one-device disabled/no request/no flip, same-device contradictory facing, real two-ID transition, restoration and pending-switch cleanup. Clipboard tests cover exact frozen/live contents, no automatic writes, denial and unavailable API. Final synthetic update cadence: 23 updates across 1465.5ms (15.01 updates/second, minimum interval 64.5ms); not a hardware latency measurement. No real camera accessed. Phone/Safari checks remain pending. No global edits, commit or push.

## Warm hardware visual iteration

Implemented the requested fictional 1970s instrument treatment: warm off-white/light gray enclosure, thick rounded CRT bezel, edge-only glass reflection/scanlines, dimensional keycaps and a rotary density indicator bound to the native labeled range. No curvature transform, crop or aspect distortion is applied to ASCII/photo content. The density slider remains pointer/keyboard accessible; its rotation reflects actual columns. Added a keyboard-operable Camera power switch that starts only on deliberate activation and stops/clears active or pending sessions. It is labeled separately from Switch camera. No continuous decorative animation; reduced-motion rules remain.

Regression: 9 pure tests, 47 browser checks and 2 launcher tests passed (58 total). Added keyboard density/grid/rotary indicator and power start/stop assertions; all earlier camera identity, clipboard, framing and cleanup checks retained. Generated synthetic demo screenshots at 1200px/400px in the system temporary directory; no horizontal page overflow at either width. Screenshot Read produced blank interface output, so no visual review is claimed. No real camera, phone/Safari validation, external publishing, global edit, commit or push.

## Actual curved picture and mechanical fader correction

User rejected the earlier static glass-only curvature and decorative knob. Replaced the knob with a native draggable linear range, a rectangular brushed-aluminum cap with machined grooves, highlights and a recessed rail (explicit WebKit/Firefox thumb overrides). Kept the liked power switch appearance/function and moved it to the machine top. Replaced the large serif welcome with monospaced terminal boot/status typography. Meaningful action buttons now use tall ivory sculpted ABS-like tops, sloped sidewalls, dished shading, narrow corners and a dark recessed key well; capture/save use contrasting charcoal keys. No copied branding or dummy keyboard.

Added crt.js: 16×12 triangle mesh geometry paints genuine static spherical/barrel distortion through Canvas drawImage transforms, not CPU per-pixel processing. Edge midpoint bow is 8.8% of frame height relative to its corners; 10% corner guard space retains the entire source. The same paintCRT function renders live/frozen display and PNG photo area; footer stays outside. Clipboard is intentionally unwarped text. Canvas display replaces visible pre text while retaining its copy/selection contents.

Latest verification: 10 pure tests + 49 browser checks + 2 launcher tests = 61 passed. Added native pointer-drag density check, synthetic colored-edge raster warp check and 10,201-point mapped bounds/center/bow test. Existing 24 PNG exports and lifecycle/camera-identity/clipboard regressions pass; shared-renderer architecture is checked indirectly, not claimed as pixel-perfect PNG/display comparison. Synthetic cadence after final keycap styling: 23 updates across 1464.9ms, 15.02 updates/second, minimum interval 61.2ms. The mesh coordinates are regenerated per paint; sampling buffers are reused. No real-camera latency claim. Desktop/400px generated demo screenshots refreshed in system temp directory with no page overflow; previous image Read was blank so no visual inspection claim. Phone Safari/Firefox rendering and physical camera validation remain pending. No real camera/global changes/commit/push.

## Whole-screen subtle curvature correction

The latest user request supersedes the previous picture-only mesh. Added one screen-content wrapper around welcome, both status bars and the picture; a generated static 128×128 calibrated red/green displacement map feeds one SVG feDisplacementMap at scale 12. Maximum axis displacement is approximately 4.7 CSS pixels, substantially gentler than the prior 8.8%-height bow. Seven pixels of inner safe padding plus existing screen margins protect content. Physical keycaps, fader and top power switch remain outside the filter. The photo canvas is flat before the common filter, avoiding double warping. PNG deliberately exports the clean flat ASCII print; clipboard is plain text. The old crt.js mesh is retained only as a legacy tested utility, not imported by the running app.

Actual regression: 10 pure tests, 50 browser checks and 2 launcher tests passed (62 total). New structural checks verify the common filter/map/strength, welcome/status/picture inclusion, controls exclusion and no canvas-local filter. Existing legacy mesh tests still pass but do not validate the new on-screen raster effect; no new pixel-diff or physical Safari validation is claimed. Existing live/frozen framing, 400/1200 overflow, keyboard/fader, camera identity, clipboard and 24 PNG exports passed. Synthetic DOM cadence: 15.01 updates/second over 1465.9ms, not display GPU timing or real camera latency. No real camera, external writes, global changes, commit or push.

## Convex direction and immediate capture

Inverted the common screen displacement map channels: feDisplacementMap samples SourceGraphic at output + displacement, so negative red on the right and positive red on the left move visible source landmarks outward. This corrects the prior inward/concave direction; scale remains 12 with safe padding. Removed countdown/cancel state, timer and controls: capture now synchronously freezes a ready frame and releases tracks. Removed both branding blocks and duplicate initial Start camera button; the liked power switch is now bottom-left beneath the action keys. Added an external accessible LED: off/live and a nonrepeating 1.2s capture indication (reduced motion disables animation).

Revised browser regression passed 50 checks, replacing obsolete countdown tests, including immediate capture, sole power entry, outside-screen LED states and calibrated map pixel direction. Screenshot raster grid direction has not yet been measured; channel sampling is mathematical evidence, not a screenshot pixel comparison. Synthetic cadence 15.02 updates/second. No real camera, global config, commit or push. Earlier process sections are historical, not current countdown behavior.

## Sculpted monitor enclosure

Added directional warm-shell bevels, a substantially sloping conic-gradient recess, upper/left cavity shadows, lower lip catchlights, a separate dark gasket and a polygonal bowed glass aperture (bowed top/bottom and sides rather than repeated rounded rectangles). Screen content remains inside safe padding with the existing common subtle outward displacement; physical controls remain outside. No reference image or branding is shipped. Reading the supplied reference image returned blank in this interface, so no direct image inspection is claimed.

Browser suite passed 51 checks, including new funnel/gasket/aperture/inset structure assertions and existing 400/1200 overflow, full framing and all functional regression. With the previously passing 10 pure and 2 launcher tests, total is 63. Demo screenshots refreshed in system temporary directory. Structural tests do not establish subjective depth quality or raster curvature direction; the outstanding screenshot-grid direction check remains incomplete. No real camera, global config, commit or push.

## Smooth aperture and four planar recess faces

Replaced the segmented polygon glass clip with a responsive objectBoundingBox SVG contour using four cubic Bézier spans with matching tangent directions at joins. Added four explicit planar top/bottom/left/right SVG recess faces and four diagonal inward miter seams, independently lit; decorative SVG ignores pointer events. No reference photo or watermark/brand asset is shipped. All camera/control behavior is unchanged.

Verification: 10 pure + 52 browser + 2 launcher tests passed (64 total). Updated aperture assertion and added four cubic/four face/four seam checks; desktop/400px overflow, inset, all framing and functional checks pass. Generated demo screenshots refreshed in system temp. These structural checks do not substitute for subjective visual review; screenshot-grid curvature-direction measurement remains outstanding. No real camera, global edits, commit or push.

## Repair excessive aperture bow

Root cause: four long cubic spans produced an oval-like opening, while fixed gasket/facet percentages diverged from responsive padding. Replaced with eight quadratic spans defining a near-rectangle, 1–2% side bow and small corners. Removed the conflicting late enclosure override blocks, rebuilt one coordinated recess CSS section, removed the oversized pseudo-gasket and aligned all four face inner edges/seams to measured glass bounds using ResizeObserver. Content retains safe inset and common subtle convex filter.

54 browser checks passed, including actual screenshot PNG decoding: four injected magenta corner landmarks at status-region bounds each retain at least 30 pixels in all quadrants at 1200px and 400px. This is rendered occlusion evidence, not merely DOM bounds or subjective aesthetic approval, and does not establish every text glyph's visibility. With existing 10 pure and 2 launcher tests total is 66. Screenshots saved as phosphor-repaired-1200.png and phosphor-repaired-400.png in system temp. No real camera, commit, push or global edits.

## Direct slope-to-glass contact

Removed the remaining dark recess backing and glass inset rim shadow. Four facet inner paths now use the same normalized quadratic control points as the actual glass clip, transformed into responsive bezel coordinates; corner seams terminate at the curved aperture joins rather than the rectangular screen box. No separate gasket band is generated. Existing geometry, content inset and physical controls are otherwise retained.

Final unit 10 / launcher 2 / browser 54 checks passed (66 total). First browser run failed a transient minimum DOM update interval assertion (overall cadence still 15.01 FPS); unchanged rerun passed at 15.03 FPS with 62.8ms minimum interval. Desktop/mobile rendered four-corner visibility screenshots refreshed. A dedicated pixel classifier for absence of a thick ring is not implemented, so no such measurement is claimed. No real camera, global edit, commit or push.

## Fixed physical controls and functional rotary density

User superseded the linear fader request. All existing action buttons and density panel now remain visible in fixed grid slots; unavailable actions are disabled with state-specific title feedback. Fixed status-region heights prevent camera source/status wording from reflowing the physical panel. Replaced exposed linear range with a visually circular machined knob/ribbed scale and rotating notch, backed by the same native accessible range (40–160, default 96). Pointer capture maps right/up drag to increasing density, left/down decreasing; touch-action is restricted only on the knob gesture surface. Keyboard arrows/Home/End retain native range operation. No new buttons were added.

Latest verification: 10 pure, 2 launcher and 56 browser checks passed (68 total). Existing tests adapted from hidden actions to disabled actions. Added document-coordinate fixed button bounds across idle/live/frozen and actual Home/End density/grid assertions; pointer dragging and all earlier geometry/camera/clipboard regression passed. Initial bounds test incorrectly compared viewport positions after automatic scrolling; document coordinates fixed that harness issue. Dedicated touch-emulation and requesting/error bounding-box checks remain unimplemented; do not infer those from the existing checks. No real camera, globals, commit or push.

## Always-operable physical controls, demo removal

Removed public Try demo portrait button without adding a replacement. Remaining buttons/range are always enabled and visible; JS state guards provide external fixed-height feedback. Off-state actions show “Turn on camera power first.” without a media request. Off-state density actually changes stored value; requesting actions explain waiting without duplicate requests. Power cancels pending work; valid frozen copy/save remain functional after capture stops tracks.

Migrated browser demo calls to explicit power→synthetic camera→capture fixtures, and readiness waits from disabled flags to actual live-preview status. Final full run: 10 pure + 2 launcher + 60 browser = 72 passed. New checks click every off-state action and change knob while asserting zero media calls; pending-request actions remain enabled with one request and late-stream cleanup. Existing live/frozen copy/export, single/dual-device truthfulness, all geometry, screenshots and keyboard/drag tests passed. No real camera, global config, commit or push.

Latest correction: runtime feedback is inside the CRT screen-content, not below the screen. All runtime UI text uses English; no language selector was added. Always-operable controls and off-state density adjustment remain unchanged.
