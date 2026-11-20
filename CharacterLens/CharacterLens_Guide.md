# CharacterLens for Octane: quick guide

CharacterLens is an Octane camera that renders real lens character (bokeh shape, glow, swirl, fringing, distortion) and stylised cameras (PS1, VHS, Super 8, fisheyes and more) directly in the render.

---

## Install and set up

1. Put `CharacterLens.pyp` in your Cinema 4D plugins folder and restart. It writes a small `characterlens_res` folder next to itself on first start (resources and the looks' colour grades); leave it there.
2. Click **Extensions > CharacterLens**. With a camera selected, it sets that camera up; with nothing selected, it makes a new camera from your current view. There's no window: a summary appears in the status bar. You can drag the command into any toolbar for one-click access.
   Or add the **CharacterLens** tag to a camera from the Object Manager's **Tags > Extensions** menu: it sets its camera up by itself.
3. Start the **Live Viewer**. If the controls don't change the render, press **Compile shader** on the tag (Octane only compiles while the Live Viewer is running).

Everything is on the **CharacterLens** tag's **Character Lens** tab, with Colour correction at the top. Don't edit the shader inputs on the Octane tag: the CharacterLens tag overwrites them.

Clicking CharacterLens again on a camera keeps all its settings and updates it to the installed version. Older scenes with the Python version of the tag are converted when you do.

## The controls

| Control | What it does |
|---|---|
| **Lens** | 22 real lenses, 26 `[Style]` cameras, then your own `[Saved]` lenses. Doesn't change your focal length or F-stop. |
| **F-stop** | Lower = more blur. Stopping down cleans up the lens like real glass. |
| **Full character at** | The lens's widest aperture, where its character is strongest. |
| **Focus Object** | Drag in any object to focus on it. |
| **Character** | All character at once. 0 = perfect lens, 1 = as designed, 2 = exaggerated. |
| **Bokeh, Swirl, Softness, Fringing, Distortion, Vignette** | Each changes only its own part of the look. Below 1 tones the lens down; above 1 adds more, even on a lens that has none of it. Only Vignette darkens the corners. **Reset look** sets them all back to 1. |
| **Style** | Pixel lines, wobble and 3D eye distance; only shown for `[Style]` cameras. |
| **Film look (grade, bloom, grain)** | For Night vision, CCTV, 2000s webcam, Super 8, Toy camera, VHS and the Pocket Dispo lens: a colour grade, glow and grain, live in the render. 0 = off, 1 = as designed, 2 = stronger. |
| **Colour correction** | Exposure (stops), Saturation and Gamma, using this camera's Octane imager. No render cost. |
| **Advanced** | Every value of the current lens, for fine-tuning. **Save as preset...** adds your version to the Lens list. |

## Getting more depth of field

Set a **Focus Object**, then lower the **F-stop**. You can go below the lens's widest aperture, down to f/0.02. The blur keeps growing, but the lens character stays at its wide-open look.

Wide shots focused far away need very low values (f/0.1 or less). Long lenses focused close need much less.

## Lenses

| Lens | Look |
|---|---|
| Sigma 15 f2.8 Diagonal Fisheye | real fisheye (circular at 10 mm or below) |
| Lensbaby Obscura 16 f90 | very soft, heavy haze, deep focus |
| Nikon Nikkor 20 f4 | vintage wide, barrel distortion, edge fringing |
| Blackwing7 20.7 T1.9 X-Tuned | modern cine, warm with soft glow |
| Cooke Panchro Classic 21 T2.2 | warm, gentle cine (default) |
| Canon FD 24 f1.4 SSC Aspherical | fast vintage wide, coma in corners |
| LOMO Illumina 25 T1.3 | Soviet cine, cool cast, glow, cat-eye bokeh |
| Pocket Dispo 28 f10 | disposable camera |
| Pinhole f150 | no lens character, near-infinite depth of field |
| Deakinizer #2A 32 T2.1 | heavy swirl |
| Civil War detuned | extreme swirl, fringing and glow |
| 7Artisans Floral Bloom 37 T2.9 | dreamy bloom |
| Voigtlander Nokton Classic 40 f1.4 | classic fast-lens glow |
| Zeiss Ultra Prime 50 T1.9 | clean modern reference |
| Anamorphic 2x 50 T2 | oval bokeh, anamorphic squeeze |
| Canon 50 f0.95 Dream Lens | very shallow and dreamy |
| Angenieux 10x25 zoom 55 T3.7 | warm, hazy 70s zoom |
| Petzval Pro 55 T1.8 | sharp centre, swirling edges |
| Helios 44-2 58 f2 | Soviet swirl |
| Soap Bubble 100 f2.8 (Trioplan) | bright-rimmed bubble bokeh |
| Vivitar Series 1 135 f2.3 | vintage tele, colour fringing in the bokeh |
| Leica Telyt-S 800 f6.3 | extreme tele compression, slight haze |

## Style cameras

PS1, N64, Doom / Build engine, Game Boy Camera, CRT TV, VHS camcorder, Toy camera (Holga), Super 8, Skate fisheye (VX1000), CCTV security, Peephole, 2000s webcam, Night vision, Anaglyph 3D, Prism filter, Kaleidoscope, Compound eye, Frosted glass, Ribbed glass, Underwater (flat port), Tilt-shift miniature, Tiny planet, Mirror ball, 360 equirectangular, Isometric, Reverse perspective.

**Film looks are live.** Night vision, CCTV, 2000s webcam, Super 8, Toy camera, VHS and the Pocket Dispo lens finish themselves in the render: a colour grade (a LUT), bloom and grain, set by **Film look**. These use the camera's own Octane Imager and Post processing settings while the look is on, and put your settings back when you switch to another lens. Looks that need the finished frames, such as PS1 palettes, timestamps or rolling shutter, are best done in your compositor.

For PS1 wobbly geometry, select objects and press **Add PS1 snap to selected** on the tag.

Render-size tips: Tiny planet and Mirror ball at 1:1, 360 at 2:1. For true Isometric, rotate the camera H 45°, P −35.26°.

## Troubleshooting

- **Controls don't change the render:** start the Live Viewer and press **Compile shader**.
- **Black frame right after starting the Live Viewer:** the shader is still compiling; it clears within a few seconds.
- **No visible blur:** see *Getting more depth of field* above.
- **Won't compile on a new Octane version:** press **Save shader to a folder...** in the tag's Tools, change `#define USE_SPECTRAL 1` to `0` at the top of `CharacterLens.osl`, and paste that code into the Octane tag's OSL Code field.
