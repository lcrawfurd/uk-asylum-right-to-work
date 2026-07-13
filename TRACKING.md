# Event Tracking

`interactive_name`: `uk-asylum-charge-figure1`

Tracking implemented per the [CGD Interactive Analytics Tracking Standard](https://github.com/Center-for-Global-Development/cgd-interactive-toolkit/blob/main/analytics-tracking-standard.md). The `CGDTracking` utility is inlined in `BOTEC-asylum-figure3.html` (single-file embed); the flat `postMessage` contract matches the standard.

## Tracked Events

| `action_type` | `action_label` | `action_value` | Notes |
|---|---|---|---|
| `navigate` | `scenario_step` | step button text (e.g. `2 · + £10,000 charge`) | Fired when the user clicks one of the three scenario-step buttons. Bounded set of 3 values. |
| `view_control` | `replay` | — | Fired when the user clicks "Replay" to restart the build-up animation. |

`interactive_view` fires once when the interactive loads / enters the viewport.

## Not Tracked

- **Autoplay step advances** — driven by the code, not the user, so not a user engagement.
- **Hover / focus** — no meaningful hover interactions; excluded per standard.
- **The "Show the numbers" `<details>` toggle** — could be `detail_open`/`detail_close`, but it's a minor accessibility affordance; left untracked to keep signal clean. Add it if drill-in interest becomes relevant.
