# Process

## Starting idea

For SD5913 Assignment 3, I wanted to turn a camera portrait into a playful ASCII keepsake. Week 5's brightness-to-character exercises provided the starting concept. The project adds live camera input, physical-style controls, capture/resume, camera switching, copying and PNG export.

## Decisions and revisions

- Replaced the initial countdown with immediate capture. Take photo freezes the live image; pressing it again resumes. Power stays on until explicitly switched off or the page is hidden/closed.
- Kept a 1970s-inspired enclosure and permanent controls. Removed redundant demo, retake and stop buttons. Feedback appears inside the CRT rather than as changing labels on the casing.
- Corrected preview/export aspect ratios and single-camera switching: requesting another facing must not merely mirror the same device.
- Fixed state-dependent machine resizing and separated stationary knob lighting from the rotating grip and marker.

## Classmate trial and response

Two classmates tried the experience. The feedback below was reported by the project owner; it is paraphrased, not a verbatim quotation. No names or recordings are retained. Both classmates tried the experience independently before asking the owner for help; no instructions were given before their initial attempts.

| Participant | Observation | Adopted change |
| --- | --- | --- |
| A | The density knob was too sensitive. | Reduced pointer-drag sensitivity to 60% of the previous mapping, retaining 40–160 columns and the existing keyboard steps. |
| B | It was unclear how to start; Take photo should turn on the camera. | Take photo now starts camera permission and live preview when off. A subsequent press captures; repeated pending clicks do not duplicate requests. |

Both changes are implemented and covered by automated checks. Neither participant has yet been reported to have retried the revised version; follow-up testing remains pending.

## AI assistance

Claude Code assisted with implementation, CSS, tests and documentation under my direction.

- **Kept:** local Canvas conversion and processing without uploading camera images.
- **Changed or rejected:** decorative non-interactive controls, buttons disappearing or greying out, and switching that only mirrored a single camera. I requested functional physical controls and accurate device feedback instead.

## Verification and limitations

The latest reported regression passed 10 unit tests, 2 launcher tests and 79 browser checks (91 total). Browser camera tests use synthetic streams, not physical hardware. They do not establish real-camera latency or Safari/iOS compatibility. Classmate feedback is separate from those automated checks.

Photos remain in browser memory unless explicitly copied or saved. Frozen output still keeps the camera active; power off, leaving/hiding the page or interruption ends the session. Real-device follow-up, updated screenshots and final course-submission checks remain to be completed.

Detailed historical iterations are retained in [DEVLOG](DEVLOG/process-history-before-summary.md); superseded behaviour there is not the current specification.
