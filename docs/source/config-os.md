# How to Configure Raspberry Pi OS for Valet

## Connect to Valet
Use username and password from [Raspberry Pi Imager settings](install-os.md#a-general-settings)
```bash
ssh tapster@valet-vision.local
```

## Once connected, move to the Documents directory
```bash
cd ~/Documents
```

## Download the machine set-up script
```bash
curl -sL https://raw.githubusercontent.com/tapsterbot/valet/main/source/machine-setup.py -o machine-setup.py
```
## Run the set-up script:
**For Valet Link**:
```bash
python machine-setup.py --link
```
**For Valet Vision**:
```bash
python machine-setup.py --vision
```
***Note***: By default, Valet is set up as a Wi-Fi hotspot on first boot, to make it easier to connect to your main Wi-Fi network. If you want to disable this feature, include an additional flag:
```bash
python machine-setup.py --link --nohotspot
or
python machine-setup.py --vision --nohotspot
```


## What does the script do?
- Run raspi-config:
  - Enable VNC for remote desktop access
  - *(Valet Vision)*: Enable SPI to control the TFT display
  - *(Valet Vision)*: Enable I2C to control the TFT display
- Create Python virtual environment
- Install required Python libraries
- Install libcamera libraries
- Install OpenCV for computer vision
- Install Tesseract OCR and Pytesseract for text recognition
- Install [zero-hid](https://github.com/tapsterbot/zero-hid/tree/touch-support) library for mouse & keyboard control
- Install [Checkbox server](https://github.com/tapsterbot/checkbox-server)
- Install [Checkbox client](https://github.com/tapsterbot/checkbox-client-python)
- *(Optional)*: Install [Comitup](https://github.com/davesteele/comitup) for easy Wi-Fi onboarding

### Valet Vision Only
- Install [Blinka](https://github.com/adafruit/Adafruit_Blinka) library (for controlling TFT display)
- Install [Checkbox display server](https://github.com/tapsterbot/checkbox-display-server)
- Install TFT display test script

### Valet Link Only
- Set required video capture settings
