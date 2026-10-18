# Sicce SDC for Home Assistant (ContrAll cloud)

Unofficial integration for Sicce Syncra SDC WiFi pumps. It signs in to the
same cloud the ContrAll app uses (sicce.thingscloud.it) with your ContrAll
email and password. No vendor key needed.

## Entities per pump

- **Fan** — pump control. Percentage is flow %, on/off is the power switch.
  Turning on from 0% starts at 50%.
- **Flow number** — a 0-100 slider with the same control, friendlier on
  dashboards than the fan popup.
- **Mode sensor** — current operating mode (read-only for now).
- **Temperature sensor** — the pump's water temperature reading (`real_temp`).
- **Problem binary sensor** — on when the pump raises an alert (dry run,
  rotor, no power, temperature high/low, comms, reservoir). Individual
  flags are exposed as attributes.

Polling interval is 30 seconds. Commands are desired-state writes, exactly
like the app: the full device object is posted back with `power` and
`power_switch` changed.

Displayed flow is the pump's LIVE output, read from its mainboard status
registers (`mb_status[5]`), not the app's setpoint field: a pump set from
its physical dial reports a stale 0 in the setpoint field while actually
running, e.g. at 74%. On/off likewise follows the running flag
(`mb_status[0]`). The **Mode sensor** reports the operating mode label
(Constant Speed, Night Mode, Lagoonal Ripple, Sharp Break, Reef Crest,
Slow Current, Fast Current) read-only in v0.3; mode writing lands in a
later version once its write path is verified on a bench unit.

## Install (HACS)

1. HACS → Integrations → ⋮ → Custom repositories → add this repo URL,
   category Integration.
2. Install "Sicce SDC (ContrAll Cloud)", restart Home Assistant.
3. Settings → Devices & Services → Add Integration → "Sicce SDC" →
   enter your ContrAll email and password.

Cloud-dependent by design: if Sicce's cloud is down, so is this. Local
control research is tracked separately.
