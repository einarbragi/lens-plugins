# Lens plugins for Cinema 4D + Octane

Two Octane OSL camera plugins for Cinema 4D 2027, by Einar Bragi.

| Plugin | What it is | Install |
|---|---|---|
| [**CharacterLens**](CharacterLens/) | 22 real-lens presets with their character (bokeh, swirl, glow, fringing, distortion), 26 style cameras (PS1, VHS, Super 8, night vision, fisheyes, tiny planet, ...) with live film looks, colour correction. | `CharacterLens/dist/CharacterLens.pyp` |
| [**XenoCam**](XenoCam/) | One preset-free cinematic lens (a Cooke-style prime set, 12–300 mm) whose character follows the focal length, with an Era dial, Super 8 slider and fisheye switch. | `XenoCam/dist/XenoCam.pyp` |

**Install:** copy the `.pyp` into your Cinema 4D plugins folder (Edit > Preferences > Open Preferences Folder... > plugins) and restart Cinema 4D. Each plugin's guide (PDF) is next to it in `dist/`.

## Layout

```
CharacterLens/
  dist/   CharacterLens.pyp + guide PDF      <- what you install
  src/    shader, tag logic, presets, build scripts
  test/   offline test of the tag logic (no Cinema 4D needed)
XenoCam/
  dist/   XenoCam.pyp + guide PDF
  src/    shader, tag logic, build script
```

Each plugin is a single `.pyp` built from `src/` with `python3 assemble.py`.
