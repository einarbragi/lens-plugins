# XenoCam for Octane (v1.3): guide

XenoCam is one cinematic lens for Octane in Cinema 4D. It's a classic cine prime set, modelled on the Cooke S4/i family from 12 mm to 300 mm, and its character follows your camera's focal length. There are no presets: set the focal length like you would on a real camera and the lens behaves like that member of the set. A handful of dials shape the look from there.

---

## 1. Quick start

**Install (once)**
Put `XenoCam-1.3.pyp` in your Cinema 4D plugins folder (delete any older `XenoCam*.pyp` first) and restart. It appears under **Extensions > XenoCam 1.3** and as a tag under **Tags > Extensions > XenoCam**. It can sit next to CharacterLens; they don't share anything.

**Set up a camera**
Click **Extensions > XenoCam 1.3**. With a camera selected it sets that camera up; with nothing selected it makes a new camera from the current view. Adding **Tags > Extensions > XenoCam** to a camera does the same.

Setup switches the Octane tag to OSL, loads the XenoCam shader, makes the viewport look through the camera, puts the **XenoCam** tag first on the camera and (re)starts the Live Viewer, which compiles the shader. A short report appears in the status bar and the console.

Running setup again on the same camera updates the shader and keeps your settings, and replaces an old 1.x Python XenoCam tag with the new tag type (settings kept). If the image stops reacting to the tag, press **Compile shader** on the tag: it does the same.

**Use: everything is on the XenoCam tag.** Focal length and sensor size stay on the C4D camera, where you'd normally set them.

---

## 2. How the lens follows the focal length

The set is described at ten focal lengths (12, 18, 25, 35, 50, 75, 100, 135, 180 and 300 mm), and XenoCam blends smoothly between them. Below 12 mm or above 300 mm it holds the nearest end.

| | Wide (12–25 mm) | Normal (35–50 mm) | Long (75–300 mm) |
|---|---|---|---|
| **Distortion** | gentle barrel, a touch of mustache at 12 mm | almost none | faint pincushion |
| **Corners** | darker, softer (field curvature, coma, astigmatism) | mild | clean and even |
| **Bokeh** | cat-eye toward the corners | slight cat-eye | round, creamy, centre-bright |
| **Colour fringing** | red/cyan on edges toward the corners | low | purple/green on out-of-focus edges |
| **Glow** | little | gentle wide-open glow | gentle glow, a touch of haze at 300 mm |

All of it is relative to the frame, so a different sensor width keeps the same character, just like swapping camera bodies.

---

## 3. The controls

**Lens & focus**
- **Fisheye:** switches the lens to a fisheye projection (see below). The focal length on the camera keeps working.
- **F-stop:** your aperture. T2 is the set wide open, with its full character. Higher stops clean the character up, as with real glass. Below T2 you get a faster version of the same lens: shallower focus, still full character. The **Aperture** line under it says which of these you're in.
- **Focus:** set the **Focus Object** on the camera itself (Object tab), as usual, and XenoCam focuses on it. The tag's **Focus Object (if the camera has none)** is only a fallback; if neither is set, **Focus distance** is used as typed.
- **Focus breathing:** 0 by default (no framing change on focus pulls). 0.3–0.6 is a typical stills lens, 1 full breathing.

**Look**
- **Character:** everything at once. 0 = a perfect lens, 1 = the set as modelled, 2 = exaggerated.
- **Era:** 0 = clean modern glass (Master Prime territory), 0.5 = the classic set, 1 = vintage (more glow, swirl, cat-eye, haze, warmth and corner fall-off, like a 70s Speed Panchro).
- **Format:** Spherical or Anamorphic. Anamorphic gives oval bokeh, softer and more distorted edges, and **mumps**: at close focus the squeeze drops, so faces and products get a little fatter, as on real front-anamorphics. **Anamorphic squeeze** (2.0 classic; 1.33/1.5/1.8 modern) appears when it's on.
- **Reset look:** puts the Look, Bokeh, Glow & edges and Colour controls back to their defaults (Format and focus stay).

**Bokeh**
- **Aperture blades** (8, as on the Cooke; 0 = perfect circle) and **Blade roundness**.
- **Cat-eye:** how strongly bokeh turns lemon-shaped toward the corners (with the matching optical vignetting).
- **Bokeh rim:** negative = creamy, centre-bright bokeh; positive = bright "soap bubble" rims.

**Glow & edges** (all 1 = as modelled)
- **Glow:** spherical aberration, the soft halo around highlights wide open.
- **Haze:** low-contrast veiling glare.
- **Swirl:** rotating background bokeh toward the edges.
- **Edge softness:** field curvature, astigmatism and coma together.
- **Distortion:** barrel/pincushion amount (negative flips it). The horizontal field of view stays put.
- **Focus plane tilt:** tilts the focus plane top to bottom, to keep a long product sharp front to back, or for a miniature look.

**Colour**
- **Fringing:** red/cyan edges toward the corners (lateral CA).
- **Purple fringing:** colour fringes on out-of-focus edges (longitudinal CA, secondary spectrum, coloured bokeh rims).
- **Vignette:** natural corner fall-off.
- **Warmth:** added to the set's own gentle warmth (−1 cool, +1 warm). About −0.15 gives a neutral image if you need exact product colour.
- **Edge colour cast:** extra warmth toward the corners, like old coatings.

**Fisheye**
A real fisheye maps angles to the image differently from a normal (rectilinear) lens: XenoCam uses the equisolid mapping of most cine and stills fisheyes, with a 180° image circle. The field of view still comes from your focal length and sensor width, so the focal length slider stays your zoom:
- **8 mm** on a full-frame (36 mm) sensor: a round fisheye image with black around it.
- **10–12 mm:** close to a full-frame fisheye; the top and bottom of the circle are cropped by a 16:9 frame.
- **15 mm:** a frame-filling diagonal fisheye.
- **35 mm and longer:** a gentle curved warp, like a lens with strong barrel distortion.

Everything else keeps working with Fisheye on: bokeh, depth of field, glow, fringing, Era and anamorphic. The focus surface curves with the lens, like a real fisheye's. Focus plane tilt is ignored while Fisheye is on.

---

## 4. Good to know

- **The character values are hand-tuned** from the Cooke S4/i family's known traits (the gentle "Cooke look": warm, smooth focus fall-off, round 8-blade bokeh, low distortion that grows on the widest lenses). They aren't measured data.
- **Flares** (including anamorphic horizontal streaks) aren't in the camera; use Octane's imager glare or comp.
- **Spectral fringing:** XenoCam reads the wavelengths Octane samples, so fringing is true dispersion. If the shader won't compile, use **Save shader to a folder...** in the tag's Tools, set `#define USE_SPECTRAL 1` to `0` at the top, and paste it into the Octane tag.
- **Plugin IDs:** 1000004–1000006, from Maxon's free test range. Register free permanent IDs before sharing XenoCam widely.
