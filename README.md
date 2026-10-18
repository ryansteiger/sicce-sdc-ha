# Sicce SDC for Home Assistant

![Sicce Syncra SDC pump and controller](https://premiumaquatics.com/cdn/shop/files/21136.png?v=1740526175)

**Your return pump, finally in Home Assistant.** This unofficial integration
talks to the same cloud as Sicce's ContrAll app, so anything the app can do
with your Syncra SDC, your automations can do too. Feed the fish without
opening an app. Drop the flow at night. Get paged when the pump says
something is wrong, in words, not just "Problem."

No vendor key, no Sicce developer account, no waiting on Italy. Just your
ContrAll email and password, the same ones you already use in the app.

## What each pump gets

- **Fan control.** On/off and flow %, because it is basically a very
  expensive, very wet fan.
- **Flow slider.** The same control as a number, much nicer on a dashboard.
- **Mode Control dropdown.** Constant Speed, Night Mode, and the wave
  modes: Lagoonal Ripple, Sharp Break, Reef Crest, Slow Current, Fast
  Current.
- **Feed Mode button.** One press pauses the pump for feeding, about
  10 minutes, just like the app. Press again to end it early. The pump
  remembers its setpoint and picks up right where it left off. A matching
  sensor shows while a feed pause is running.
- **Pump Color dropdown.** Pick the app's color for the pump and the ring
  LED on the physical controller changes to match. Sicce's own color
  values are oddly pastel (their "red" is really a mauve), so this drives
  the LED with proper saturated colors: red looks red.
- **Temperature sensor.** The pump's own water temperature reading.
- **Alerts sensor.** Says what is actually wrong, in English: High
  Temperature, Low Temperature, Dry Run, Rotor Blocked, No Power, Temp
  Probe Open, Temp Probe Short, Communication Error, Reservoir Low,
  Reservoir Empty. Or just "OK," which is what we all want to read.
- **Problem binary sensor.** The simple on/off version of the above, for
  automations that just want a yes or no.
- **Temp Alert Low / High settings.** The pump's own alarm thresholds,
  adjustable from Home Assistant. The pump watches its temperature against
  these and raises the matching alert itself.

## The model thing (worth 30 seconds)

Sicce's cloud does not report which size your pump is. A 3.0, a 6.0, a 7.0
and a 9.0 all introduce themselves to the internet as the exact same
thing, because in Sicce's data "Syncra SDC 3.0" is the controller platform,
not the pump size. Yes, really.

So the integration asks you instead. Hit **Configure** on the integration,
pick each pump's real model, and two things happen: the pump gets its
correct name in Home Assistant, and an **Estimated Flow** sensor appears,
live % of that model's rated max flow (roughly 800, 1,450, 1,900 and
2,500 gph). It is an honest estimate, your plumbing's head height gets a
vote too. Never pick a model and nothing changes, no guessing, no fake
numbers.

## Good to know

- **It is a cloud integration.** If Sicce's cloud naps, so does this. The
  pumps keep running their last program either way, they are not that
  fragile.
- **The pump reports back on its own schedule,** about 10 seconds after a
  change. The integration holds the state you asked for until the pump
  confirms it, so toggles do not bounce while the cloud catches up.
- **Displayed flow is the pump's real live output,** read from its
  mainboard registers, not the setpoint field. A pump started from its
  physical dial can show a setpoint of 0 while actually pushing 74%, and
  this integration believes the water, not the paperwork.
- Everything here was reverse engineered from the ContrAll app and
  verified command by command on a real pump in a bucket, so the fish were
  never the test subjects.

## Install (HACS)

1. HACS, Integrations, top right menu, Custom repositories. Add this
   repo's URL, category Integration.
2. Install "Sicce SDC (ContrAll Cloud)" and restart Home Assistant.
3. Settings, Devices & Services, Add Integration, "Sicce SDC", enter your
   ContrAll email and password.

## Fine print

Unofficial and unaffiliated with Sicce. Built by a reef keeper who wanted
his return pump in his automations. Product photo from the Premium
Aquatics listing for the Syncra SDC 9.0.
