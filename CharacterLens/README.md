# CharacterLens

An Octane OSL camera for Cinema 4D that renders lens character and stylised cameras directly in the render.

- **22 real lenses**: Cooke Panchro, Helios 44-2, Petzval, Soap Bubble Trioplan, Canon 50 f0.95, anamorphic, fisheye and more, each with its own bokeh, swirl, glow, fringing, distortion and vignetting.
- **26 style cameras**: PS1, N64, VHS, Super 8, night vision, CCTV, Game Boy Camera, tiny planet, 360, isometric, tilt-shift and more.
- **Live film looks** for night vision, CCTV, webcam, Super 8, toy camera, VHS and disposable: colour grade, bloom and grain in the render, no post step.
- **Look sliders** (Character, Bokeh, Swirl, Softness, Fringing, Distortion, Vignette), **colour correction**, and **Advanced** per-lens values you can save as your own presets.

## Install and use

1. Copy `dist/CharacterLens.pyp` into your Cinema 4D plugins folder and restart.
2. Select a camera (or nothing) and click **Extensions > CharacterLens**. Or add the CharacterLens tag from the Object Manager's **Tags > Extensions** menu.
3. Start Octane's Live Viewer. Everything is on the tag's **Character Lens** tab.

See `dist/CharacterLens_Guide.pdf` (3 pages). `CharacterLens_Reference_full.md` has the full technical reference.

## Building

```
cd src
python3 assemble.py      # writes dist/CharacterLens.pyp
python3 compact.py       # optional: checks the compact shader
cd ../test && python3 mock8.py   # offline test of every preset
```

`template.osl` is the shader, `tag_template.py` the tag logic, `looks.py` the presets, `builder.py` the tag layout and `plugin_template.pyp` the Cinema 4D plugin.

Requires Cinema 4D 2027 and Octane 2026.
