# Sicce SDC for Home Assistant

<p align="center">
  <img src="https://premiumaquatics.com/cdn/shop/files/21136.png?v=1740526175" width="340" alt="Sicce Syncra SDC pump and controller">
</p>

<p align="center"><b>Your Sicce Syncra SDC pump, controlled from Home Assistant.</b><br>
Same cloud as the ContrAll app, so if the app can do it, your automations can too.</p>

## What you get

| | |
|---|---|
| **Pump control** | On/off and flow %, plus a dashboard-friendly flow slider |
| **Wave modes** | Constant Speed, Night Mode, Lagoonal Ripple, Sharp Break, Reef Crest, Slow Current, Fast Current |
| **Feed Mode button** | Pauses the pump for feeding (about 10 min), then it resumes on its own |
| **Pump Color** | Sets the color in the app and the ring LED on the real controller |
| **Temperature** | The pump's own water temperature reading |
| **Alerts in plain English** | "High Temperature", "Dry Run", "Rotor Blocked", or just "OK" |
| **Alarm thresholds** | Set the pump's high/low temperature alarms from Home Assistant |

## Setup

1. Add this repo in HACS (Integrations, top right menu, Custom repositories).
2. Install **Sicce SDC (ContrAll Cloud)** and restart Home Assistant.
3. Add the integration and sign in with your ContrAll email and password.

That is it. No developer account, no vendor key, nothing to request from Sicce.

## One last thing: tell it which pump you have

Sicce's cloud never says whether a pump is a 3.0, 6.0, 7.0 or 9.0, they all
report as the same model. So open the integration's **Configure** button,
pick each pump's real model, and it gets the right name in Home Assistant
plus an **Estimated Flow** sensor in gph. Skip it and everything still
works, you just do not get the flow estimate.

## Questions people ask

**Is it safe for my pump?** Yes. Every command is one the app itself sends,
and if the cloud ever goes down your pump simply keeps running its last
program.

**Why does the flow take a few seconds to update after I change it?** The
pump reports back about 10 seconds later. The integration shows the value
you set right away and lets the pump confirm it, so nothing flickers.

**Does it work without the internet?** No, this is a cloud integration,
same as the app. Your pump does not care, it keeps pumping either way.

<details>
<summary><b>For the nerds: how it actually works</b></summary>

<br>

Reverse engineered from the ContrAll app (a React Native app by Zepping)
and verified command by command on a real pump in a bucket of water.

- **Login:** email and password to `sicce.thingscloud.it/api`, returns a
  Bearer token. The app has no vendor key and no MQTT; that key belongs to
  a separate partner API you do not need.
- **Commands:** `POST devices/{id}/v2/program`. `{"power_switch": bool}`
  for on/off, otherwise a program body `{program, mode, v1, v2, t1, t2,
  start, program_preset}` where `v1` is speed %. Constant is program 1
  mode 0, Night is program 2, wave modes are program 1 with mode 1 to 5.
  Feed mode is the same body plus `"pause_mode": true`. (The older
  `/status` full-object write returns success but the SDC pump ignores
  it. Ask us how we know.)
- **Live values** come from the pump's mainboard registers in its status
  report: `mb_status[0]` running, `mb_status[2]` temperature x10,
  `mb_status[5]` live flow %. The setpoint field lies for dial-started
  pumps, the registers do not.
- **Color and thresholds** live in a settings record the pump syncs:
  `POST devices/{id}/v2/settings`. `color_id` sets the app icon, and the
  ring LED follows the `led_r/g/b` percentages in that record. Sicce's
  palette hexes are pastel UI swatches, so the integration converts each
  color to a saturated equivalent for the LED.
- **Alarms** are evaluated by the pump itself against its thresholds and
  reported as flags (`alert_temp_high` and friends). The Alerts sensor
  just gives them their names.
- **Pump size** is genuinely absent from the API: every size carries
  DeviceModel id 9, the controller platform. Hence the model picker.
- **Local control:** the pump's LAN port is only awake during WiFi
  provisioning, and its cloud address is not delivered by DNS, so there
  is no local API to talk to. Cloud is the honest route for now.

</details>

---

Unofficial, not affiliated with Sicce. Built by a reef keeper who wanted
his return pump in his automations. Product photo: Premium Aquatics.
