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

Polling interval is 30 seconds. Commands use the SDC 3.0 controller's
program endpoint, POST devices/{id}/v2/program, exactly like the app:
{"power_switch": bool} for on/off, otherwise a program body
{program, mode, v1, v2, t1, t2, start, program_preset} where v1 is the
speed %. (The older POST devices/{id}/status path accepts writes but the
SDC 3.0 pump ignores them.) The **Mode Control** select writes the same
endpoint: Constant Speed (program 1, mode 0), Night Mode (program 2), and
the wave modes Lagoonal Ripple, Sharp Break, Reef Crest, Slow Current,
Fast Current (program 1, modes 1 to 5). The **Icon Color** select sets the
pump's app icon color (the GET /colors palette: Yellow, Orange, Red,
Purple, Green, Blue, Dark Blue) via /v2/settings, as the app does.

**Pump model (optional):** the Sicce cloud does not report pump size, every
size identifies as the same platform model. Under the integration's
**Configure** button you can declare each pump's model (SDC 3.0 / 6.0 / 9.0).
The declaration sets the model label in Home Assistant and enables an
**Estimated Flow** sensor for that pump (live % of the model's rated max
flow at zero head: roughly 800 / 1,450 / 2,500 gph; an estimate, since real
flow depends on plumbing head height). Undeclared pumps behave as before.

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
