# Tapster Valet

Valet is a plug-and-play automation tool designed for mobile devices.

Valet is a Raspberry Pi that plugs into a smartphone and turns it into something your automation
scripts can drive. It sends the phone real touch, mouse and keyboard input over USB, captures what's
on the screen, and gives the phone its network connection. Your scripts control the phone through
Valet, much like a container manager controls a container.

**Documentation:** [valetnet.dev](https://valetnet.dev/)

## Features

- **Authentic inputs:** taps, clicks and typing are sent over USB as a real keyboard, mouse and
  touchscreen (USB OTG HID), so the phone sees ordinary input devices.
- **Vision testing:** OpenCV and Tesseract OCR are preinstalled for finding buttons and reading text
  on screen, and you can use other image detection or machine learning libraries.
- **Network control:** Valet gives the connected phone an IP address and internet access over USB,
  and the phone's Bluetooth, Wi-Fi and mobile data can be switched on and off.
- **Drive any smartphone:** iOS and Android phones are supported, and you can switch between apps
  and native features.
- **Raspberry Pi-powered:** built on the versatile Pi platform and its large community.

## Models

| | Valet Vision | Valet Link |
|---|---|---|
| Screen capture | Camera pointed at the phone's screen | HDMI video capture from the phone |
| Status display | Built-in TFT display | — |
| Set-up flag | `--vision` | `--link` |

## How it works

A client automation script talks to the servers running on Valet, which control the phone:

```
Automation script ──HTTP──▶ Checkbox server ──▶ camera / HDMI capture  (screenshots)
       │                          └───────────▶ USB keyboard, mouse, touch ──▶ 📱 Phone
       └──────HTTP──▶ Checkbox display server ──▶ TFT display  (Valet Vision)
```

For a step-by-step example, see the [architecture overview](https://valetnet.dev/overview/).

Valet's software is made of these parts:

| Component | What it does |
|---|---|
| [checkbox-server](https://github.com/tapsterbot/checkbox-server) | Web server for screenshots, video and phone input |
| [checkbox-client-python](https://github.com/tapsterbot/checkbox-client-python) | Python client for writing automation scripts |
| [checkbox-display-server](https://github.com/tapsterbot/checkbox-display-server) | Shows status messages on Valet Vision's TFT display |
| [zero-hid](https://github.com/tapsterbot/zero-hid/tree/touch-support) | Makes Valet appear to the phone as a USB keyboard, mouse, touchscreen and network adapter |
| [Comitup](https://github.com/davesteele/comitup) | *(Optional)* Wi-Fi hotspot on first boot, for connecting Valet to your Wi-Fi network |

## Getting started

You'll need a Raspberry Pi 4 (4GB RAM minimum, 8GB recommended) and a MicroSD card (64GB recommended).

1. [Install Raspberry Pi OS](https://valetnet.dev/install-os/) on the SD card with Raspberry Pi Imager.
2. [Configure the OS](https://valetnet.dev/config-os/) by running the set-up script on Valet:
   ```bash
   cd ~/Documents
   curl -sL https://raw.githubusercontent.com/tapsterbot/valet/main/source/machine-setup.py -o machine-setup.py
   python machine-setup.py --vision    # or --link for Valet Link
   ```
   Add `--nohotspot` to skip the Wi-Fi hotspot, or `--noreboot` to review the output before rebooting.

## Repository layout

| Path | Contents |
|---|---|
| `source/machine-setup.py` | Set-up script that installs and configures Valet's software on Raspberry Pi OS |
| `docs/source/` | Documentation site source ([Sphinx](https://www.sphinx-doc.org/) with Markdown) |
| `docs/tools/imager-screenshots/` | Tools for making the Raspberry Pi Imager screenshots in the docs |
| `.github/workflows/documentation.yml` | Builds the docs and publishes them to GitHub Pages on every push to `main` |

## Building the docs

```bash
pip install sphinx sphinx-copybutton sphinx-design sphinxcontrib-mermaid myst-parser shibuya
sphinx-build -b dirhtml docs/source docs/build
python -m http.server 8000 --directory docs/build
```

Then open http://localhost:8000/.

## License

[MIT](LICENSE) © Tapster Robotics, Inc.
