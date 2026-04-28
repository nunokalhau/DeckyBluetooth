![](./assets/preview.png)

# Bluetooth plugin  
Formerly known as `SDH-Bluetooth`, this plugin allows you to quickly connect to already paired bluetooth devices.  
  
This saves one (yes ONE 1!) click instead of going trough the settings menu, but this should be faster when you're already in-game.  
If you can't see your device make sure you paired it once via the settings menu first, then it should appear.  
  
Under the hood it's just using bluetoothctl.  

## Features
- Quick Bluetooth device connection/disconnection
- Bluetooth power toggle
- **Audio Codec Switching** - Change between different audio codecs (aptX, LDAC, SBC, etc.) for connected audio devices directly in Gaming Mode

## Installation  
Install it via https://plugins.deckbrew.xyz/  

## Audio Codec Management
For audio devices (headsets, headphones), you can now switch between available audio codecs without leaving Gaming Mode:
- Select a connected audio device
- A codec dropdown will appear below the device
- Choose your preferred codec/profile (e.g., aptX, LDAC, SBC)
- The codec will be applied immediately via `pactl`

This feature requires `pactl` to be available on your system (typically included with PulseAudio).

## Planned features  
Additional device management features and enhanced codec profiles display.