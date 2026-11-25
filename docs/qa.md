# Atomic Age Utility QA

Tested November 24, 2026 in the project’s local Dashboard Lab, running Home Assistant Container Core 2026.11.3 and Frontend 20261028.8. The dashboard was created from scratch and saved through the storage-mode editor at `/atomic-age-utility/home`. The theme was copied into the lab theme directory and loaded with `frontend.reload_themes`.

## Acceptance checklist

| Check | Result |
| --- | --- |
| Day and Night Console | Pass. Theme appeared in the picker. Lab Kitchen rendered both palettes. Computed text and card-surface tokens matched the Day and Night values. |
| First screen fits | Pass at the observed 1280 × 720 CSS viewport. All three zones and primary controls were visible. The requested 1280 × 800 viewport remains unverified. |
| Visible labels | Pass for primary lab controls. Native shortcut cards showed the action text and an icon. |
| One-tap quick programs | Pass for lab Bright and All Off. A single tap changed the light tile to On or Off. Household scenes require device testing. |
| Readable safety status | Pass for simulated status. Alarm, doors, windows, glass break, and camera availability had plain-language labels. Household entity mapping remains pending. |
| Consolidated advisory | Lab alert produced one Home shortcut to Maintenance, and the lab clear action removed the alert. Household unavailable-state recovery remains unverified. |
| Household view excludes diagnostics | Pass in the lab primary view. The room builder includes only configured and verified IDs. |
| Custom resource independence | Pass. Native shortcuts, headings, tiles, Markdown, gauge, conditional visibility, and history rendered. Custom resources required: zero. |
| Responsive reflow | Three columns observed at 1280 × 720. Browser viewport overrides did not change the measured viewport. Checks at 320, 700, 1050, 1280 × 800, portrait, and on a Fire tablet remain open. |
| Confirmation for sensitive actions | The lab simulation displayed its confirmation, with Cancel and OK available. The household dashboard carries read-only security status and has no alarm or lock actions. |
| Storage-mode API | Pass. Created a distinct hyphenated dashboard and saved through the raw editor, which uses the Lovelace storage API. |
| Original design | Pass. CSS surfaces and built-in iconography implement the spec without third-party art. |

## Additional checks

- Climate subview, native history chart, temperature more-info, keyboard slider operation, and explicit back navigation were exercised.
- At desktop size, the Security shortcut measured 56 CSS pixels high. The primary card grid used 8 px spacing. The lab view showed no card overlap or configuration errors.
- The packaged Day and Night colors achieved minimum contrast ratios of 4.73:1 and 4.75:1, respectively, across 22 tested combinations per mode. Contrast was calculated against the dashboard, primary-card, and alternate-surface swatches. This covers primary and secondary text, the focus token, and the chosen supporting action, warning, danger, security, and info foregrounds. Native controls outside the sampled view still need component-level contrast and keyboard-focus checks.
- Real cover, climate HVAC, media, alarm, and lock transition states, group partial activity, reduced-motion behavior, OS-driven mode switching, and error handling still need testing against appropriate fixtures or an authorized household test. The lab does not have those hardware integrations.
- Both console modes were captured in the browser at 1280 × 720. The 1280 × 800 viewport and standalone screenshot files remain pending.
- Clean Marketplace install, restart, update, and uninstall remain pending. No release was published.
