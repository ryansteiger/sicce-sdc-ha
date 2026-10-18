# Sicce SDC for Home Assistant (ContrAll cloud)

Unofficial integration for Sicce Syncra SDC WiFi pumps. It signs in to the
same cloud the ContrAll app uses (sicce.thingscloud.it) with your ContrAll
email and password. No vendor key needed.

## Entities per pump

- **Fan** — pump control. Percentage is flow %, on/off is the power switch.
  Turning on from 0% starts at 50%.
- **Temperature sensor** — the pump's water temperature reading (`real_temp`).
- **Problem binary sensor** — on when the pump raises an alert (dry run,
  rotor, no power, temperature high/low, comms, reservoir). Individual
  flags are exposed as attributes.

Polling interval is 30 seconds. Commands are desired-state writes, exactly
like the app: the full device object is posted back with `power` and
`power_switch` changed.

## Install (HACS)

1. HACS → Integrations → ⋮ → Custom repositories → add this repo URL,
   category Integration.
2. Install "Sicce SDC (ContrAll Cloud)", restart Home Assistant.
3. Settings → Devices & Services → Add Integration → "Sicce SDC" →
   enter your ContrAll email and password.

Cloud-dependent by design: if Sicce's cloud is down, so is this. Local
control research is tracked separately.
