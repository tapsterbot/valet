# How to Configure Raspberry Pi OS for Valet

## Connect to Valet
Use username and passwrd from [Raspberry Pi Imager settings](install-os.md#a-general-settings)
```bash
ssh tapster@valet-vision.local
```

## Once connected to Valet, run this script:
```bash
curl -sL https://raw.githubusercontent.com/tapsterbot/valet/main/source/machine-setup.py | python3
```

## What does the script do?
- Run raspi-config:
  - Enable VNC for remote desktop access
  - (*Valet Vision*): Enable SPI to control the TFT display
  - (*Valet Vision*): Enable I2C to control the TFT display
- Create Python virtual environment
- Install required Python libraries
- Install libcamera libraries
- Install OpenCV for computer vision
- Install Tesseract OCR and Pytesseract for text recognition
- Install [zero-hid](https://github.com/tapsterbot/zero-hid/tree/dev) library for mouse & keyboard control
- Install [Checkbox server](https://github.com/tapsterbot/checkbox-server)
- Install [Checkbox client](https://github.com/tapsterbot/checkbox-client-python)
- (*Optional*): Install [Comitup](https://github.com/davesteele/comitup) for easy Wi-Fi onboarding

### Valet Vision Only
- Install [Blinka](https://github.com/adafruit/Adafruit_Blinka) library (for controlling TFT display)
- Install [Checkbox display server](https://github.com/tapsterbot/checkbox-display-server)
- Install TFT display test script

### Valet Link Only
- Set required video capture settings