# XenoCam

A simple, preset-free cinematic lens for Octane in Cinema 4D: one classic cine prime set (modelled on the Cooke S4/i family, 12–300 mm) whose character follows the camera's focal length, with an Era dial, a Super 8 slider and a fisheye switch. Built from CharacterLens's lens code.

## Install and use

1. Copy `dist/XenoCam.pyp` into your Cinema 4D plugins folder and restart.
2. Select a camera and choose **Extensions > XenoCam > Set up XenoCam on selected camera**.
3. Start Octane's Live Viewer and press **Compile shader** on the XenoCam tag.

See `dist/XenoCam_Guide.pdf`.

## Building

```
cd src
python3 assemble.py      # writes dist/XenoCam.pyp
```

Requires Cinema 4D 2027 and Octane 2026.
