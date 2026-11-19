# CharacterLens for Octane (v0.8): guide and lens deep dive

`CharacterLens.osl` is an Octane OSL camera. It builds lens character inside the render: each camera ray starts and points exactly as it would in a lens with that personality. Bokeh, glow, fringing and swirl therefore react to real depth, real highlights and real reflections, which post tools can only approximate.

---

## 1. Quick start (Cinema 4D + Octane)

**Install (once)**
Put `CharacterLens.pyp` in your Cinema 4D plugins folder and restart. It appears under **Extensions > CharacterLens**, with the CharacterLens icon. That one file holds everything: the shader, the camera tag, the PS1 snap and the post tool.

**Set up a camera**
1. Select an Octane Camera (or a C4D camera with an Octane Camera tag).
2. **Extensions > CharacterLens > Set up CharacterLens on selected camera.** This switches the Octane tag to OSL, loads the shader, makes the viewport look through the camera and adds the **CharacterLens** tag.
3. Start the **Live Viewer**, then press **Compile shader** on the tag. Octane only compiles an OSL camera while the Live Viewer is rendering through it, so the Live Viewer has to be running first.

Running setup on a camera that already has a CharacterLens tag upgrades it and keeps everything on it: your values, Focus Object, Advanced edits and saved lenses. It also moves the tag in front of the Octane Camera tag, so focus follows the camera without lag.

**Use: everything is on the tag's Character Lens tab**

Select the CharacterLens tag and open its **Character Lens** tab. The tag's own code stays on the Tag tab as a short stub: the logic lives in the plugin, so every camera picks up plugin updates and the scene file stays small. A scene opened without the plugin keeps rendering with the camera's last settings.

| Group | Control | What it does |
|---|---|---|
| Lens & focus | **Lens** | 22 real lenses, 26 `[Style]` cameras, then your own `[Saved]` lenses. Picking one loads its character into the Advanced group. It doesn't touch your focal length or F-stop. |
| | **F-stop** | Yours to set. Stopping down cleans a real lens up, just like glass. Going below the lens's widest aperture (down to f/0.02) keeps adding blur. |
| | **Full character at** | The lens's widest aperture, and what your F-stop does with it (see below). |
| | **Focus Object** | Drag in any null or object. Empty = the camera's own Focus Object. If neither is set, Focus distance is used as typed. |
| | **Focus distance (cm)** | Filled in automatically while a Focus Object is set. |
| Look | **Character** | Everything at once, including style effects. 0 = perfect lens, 2 = exaggerated. |
| | **Bokeh, Swirl, Softness / glow, Fringing, Distortion, Vignette** | Scale groups of Advanced values (1 = as set there). Above 1, Vignette also darkens the frame edges directly, so it works on long lenses too. **Reset look** puts all of them back to 1 (and colour correction to neutral). |
| Style | **Pixel lines, Wobble / gate weave, Anaglyph eye distance** | Only shown when a `[Style]` camera is picked. Pixel lines 0 = the style's own grid. |
| Colour correction | *(folded)* | **Use colour correction**, **Exposure (stops)**, **Saturation**, **Gamma**. See below. |
| Advanced | *(folded)* | Every value a preset stores: 63 of them, in eight sub-groups. See **Advanced** below. |
| Tools | **Compile shader** | Recompiles the shader (Live Viewer must be running). |
| | **Add PS1 snap to selected** | Puts the selected objects under a *PS1 Vertex Snap* generator (see 4b). |

Focal length, sensor size and frame number come from the camera automatically. The shader's own inputs on the Octane tag are driven by the CharacterLens tag, so leave them alone: anything typed there is overwritten.

**F-stop and "Full character at".** Each lens has a widest aperture, where its character is strongest:
- **Wider than the lens** (f/0.1 on Super 8, whose zoom opens to f/3.7): the blur keeps growing like a faster lens would, but the character stays at its wide-open look. Use it to exaggerate depth of field on any lens.
- **At the lens's widest:** full character.
- **Slower than the lens** (f/5.6 on the Petzval): glow, swirl, cat-eye and fringing shrink, as they do on real glass.
- Style cameras without depth of field (PS1, N64, fisheyes, 360...) ignore F-stop. The line says so.

**Getting more blur.** Real depth of field can be subtle: a 30 mm lens focused 5 m away barely softens the background even at f/1.4, which is correct but easy to mistake for no depth of field at all. Set a Focus Object, then keep lowering the F-stop past the lens's limit until the background melts. Wide shots focused far away may need f/0.1 or lower; long lenses focused close need much less. Older scenes that used the v0.8 Depth of field slider are converted to the matching F-stop when you run Set up again.

**Colour correction.** Ticking **Use colour correction** switches on this camera's own Octane imager (the Imager tab on the Octane Camera tag) and drives its Exposure (in stops: +1 = twice as bright), Saturation and Gamma. While it's on, the camera's imager replaces the global imager from Octane's settings, including its response curve; set the response on the Imager tab if you rely on one. Unticking switches the camera imager off again, if CharacterLens switched it on. Octane applies the imager after rendering, so it costs no render time. There's no histogram: Octane doesn't hand the Live Viewer image to plugins, and any workaround would slow rendering.

**Advanced.** Unfold it to edit any value of the current lens. The sub-groups (§3 explains each value):
- **Aperture & bokeh:** blades, blade roundness, cat-eye, cat-eye rim radius, bokeh rim brightness, onion rings, widest aperture, anamorphic squeeze.
- **Sharpness & glow:** spherical aberration, coma, astigmatism, field curvature, swirl strength, haze and haze spread.
- **Distortion & breathing:** distortion K1 and K2, focus breathing.
- **Colour fringing & vignetting:** the four kinds of chromatic aberration, natural vignetting, edge colour cast and its warmth.
- **Style: projection & optics:** projection (lens, three fisheyes, 360, tiny planet, mirror ball, orthographic, Doom shear, reverse perspective), field of view override, fisheye image circle, Tiny planet zoom, ortho view width, reverse perspective strength, focus plane tilt, aperture size multiplier, lens character amount, no depth of field, underwater port, anaglyph 3D, extra distortion / field curvature / vignette, minimum haze.
- **Style: pixels & screen:** pixel grid lines, pixel aspect and softness, scanlines, phosphor mask, screen curvature, convergence error, chroma smear, tint.
- **Style: motion & gate:** VHS wobble, film gate weave, rounded gate corners, round tube mask.
- **Style: filters & glass:** prism copies and spread, kaleidoscope segments, compound eye cells, glass in front (frosted, ribbed, shower door) and its amount.
- *Aperture size multiplier* enlarges the aperture like a lower F-stop does; the Tilt-shift style sets it to 4.

The style values work on real lenses too: scanlines on a Helios, or a tilted focus plane on the Cooke.

Buttons at the top of Advanced:
- **Use preset values:** puts every Advanced value back to the current lens's preset.
- **Save as preset...:** asks for a name and adds the current setup to the Lens list as `[Saved] name`. Saving under an existing name updates that lens. Saved lenses are stored on the tag, so they travel with the camera (copy the tag to reuse them on another camera).
- **Delete saved preset:** removes the `[Saved]` lens that's picked. The values stay on the tag.

If it won't compile: in the plugin window use **Save shader + post tool to a folder**, set `#define USE_SPECTRAL 1` to `0` at the top of `CharacterLens.osl`, and paste that code into the Octane tag.

---

## 2. How a lens makes an image (the model this shader uses)

**Thin lens.** A lens of focal length *f* focused at distance *D* places its image at
`v = f·D / (D − f)` behind the lens. A point at a different distance focuses in front of or behind the sensor and spreads into a disc: the bokeh. That disc is a **projected image of the aperture**, so whatever shape the light passes through (blades, a clipped cat-eye, an oval) is the bokeh shape.

**Entrance pupil and f-number.** The opening the scene "sees" has diameter `f / N`. The shader sends each ray from a random point on this pupil toward the point on the focus plane that the pixel looks at. At infinite resolution that alone is a perfect lens.

**Aberrations.** Real lenses don't send every ray from a pupil point to the same focus point. Each ray lands slightly off, by an amount that depends on:
- where on the pupil it started (**ρ**: centre to rim)
- where in the frame it lands (**h**: centre to corner)

Optical designers describe this with the five **Seidel aberrations**, the third-order terms of a lens's error. The shader adds exactly these terms to each ray:

| Term | Grows with | What it looks like |
|---|---|---|
| Spherical aberration | ρ³ | glow / halo everywhere, bokeh brightness profile |
| Coma | ρ² · h | comet tails pointing out from the centre, worst in corners |
| Astigmatism | ρ · h² | points smear into radial or tangential lines at the edges |
| Field curvature | ρ · h² | corners focus at a different distance than the centre |
| Distortion | h³ | straight lines bow (barrel/pincushion) |

The pupil is measured against the **wide-open** aperture. Stopping down shrinks ρ, so a lens cleans up the way real glass does: spherical aberration drops fastest (ρ³), astigmatism and field curvature slowest (ρ). That's why an f/1.4 portrait lens glows at f/1.4 and is crisp at f/4, with no extra code.

---

## 3. Each characteristic: the physics, the lenses that show it, and the controls

**Controls** below are the names in the tag's **Advanced** group. The **Look** slider that scales each one is in brackets: Bokeh scales cat-eye, rim brightness and onion rings; Softness / glow scales spherical aberration, coma, astigmatism, field curvature and haze; Fringing scales the four CA values; Distortion scales K1 and K2; Swirl and Vignette scale their own value.

### 3.1 Aperture shape and bokeh outline
- **Physics:** the iris is made of blades. Fewer, straighter blades give polygon bokeh. Many rounded blades give circles. Stopped down, the polygon shows more, because the curved blade edges form less of the outline.
- **Lenses:** modern primes have 9–11 rounded blades. Older and budget lenses have 5–6 straight blades (pentagon/hexagon highlights). Old cine lenses and some vintage glass have up to 15–18 blades and look almost perfectly round.
- **Controls:** *Aperture blades (0 = round)*, *Blade roundness*. Polygon sampling is reweighted so polygons stay evenly lit.

### 3.2 Cat-eye bokeh and optical vignetting (one phenomenon)
- **Physics:** off-axis, the light cone has to pass the iris **and** the front and rear lens barrels. Seen from the corner, the barrel rims slide across the iris, and the light gets through only where the openings overlap: a lemon (cat's-eye) shape. Less light gets through there, so the corners darken. That darkening is **optical vignetting**. It's the same cause as cat-eye, which is why the shader models them together.
- **Stopped down,** the iris gets smaller than the rims' overlap, and both cat-eye and optical vignetting disappear. The shader reproduces this automatically.
- **Lenses:** strongest in fast compact designs (50/1.4, 85/1.4, 35/1.4) and in long, narrow barrels. Weakest in big modern designs with oversized front elements.
- **Controls:** *Cat-eye* (how far the rims slide per unit of field) and *Cat-eye rim radius* (rim size relative to the wide-open pupil; above 1 means cat-eye only appears in the far corners). [Bokeh]

### 3.3 Swirl
- **Physics:** swirl isn't one aberration. It's the sum of three: **cat-eye** (bokeh squashed radially), **field curvature** (the edges are more defocused, so their bokeh is bigger) and **astigmatism** (bokeh stretched tangentially). All the edge bokeh gets stretched along circles around the centre, and the background seems to rotate.
- **Lenses:**
  - **Petzval** portraits (1840 design): huge field curvature, sharp centre, wild edges.
  - **Helios-44** (Soviet copy of the Zeiss Biotar double-Gauss).
  - **Biotar** itself (the Helios preset covers this look), and some early Planars.
- **Controls:** *Swirl strength* (extra radial pupil squash that grows with h²), together with *Cat-eye*, *Field curvature* and *Astigmatism*. The strong swirl presets (Petzval, Helios, Deakinizer, Civil War) push all four. [Swirl]
- **Seeing it:** swirl, cat-eye and onion rings live in the out-of-focus areas, so they need visible bokeh: a longer focal length, a closer focus, small bright highlights behind the subject, or an F-stop below the lens's widest.

### 3.4 Spherical aberration (SA): glow, focus shift, and bokeh texture
- **Physics:** rays through the rim of a spherical lens bend more than rays near the centre, so they focus at a different distance. In focus, this gives a sharp core inside a soft halo (the "dreamy wide-open glow"). Out of focus, it makes the **bokeh brightness uneven**, and the two sides of focus behave oppositely:
  - **Undercorrected** (most vintage lenses; **positive** values here): soft, centre-bright background bokeh (pleasing) and harsh, bright-edged foreground bokeh.
  - **Overcorrected** (**negative** values; Meyer Trioplan, some old triplets and mirror-like designs): background bokeh gets a bright rim, the "soap bubble" look. Foreground is soft.
- **Lenses:** strong in vintage fast lenses, portrait and soft-focus lenses (Petzval, Cooke Speed Panchro, Canon 50/0.95 "dream lens"). Modern aspherical lenses correct it almost completely.
- **Controls:** *Spherical aberration (glow)* (sign chooses under or over). *Bokeh rim brightness* is a separate artistic control that brightens the rim (+) or centre (−) without blurring anything in focus. *Haze / veiling glare* and *Haze spread* add the low-contrast wash of old uncoated glass. [Softness / glow; rim brightness is on Bokeh]

### 3.5 Coma
- **Physics:** for off-axis points, each ring of the pupil images to a circle that is shifted and sized differently. They stack into a comet with its tail pointing away from the centre (or toward it, if the sign flips). In point-like highlights this shows as "seagull" or "bird-wing" shapes in the corners (sagittal coma). Stars are the classic test.
- **Lenses:** fast wide-angles (24/1.4, 35/1.4), older double-Gauss lenses wide open. Strongest at the widest aperture, gone by about f/4.
- **Controls:** *Coma* (sign flips the direction of the tail). [Softness / glow]

### 3.6 Astigmatism and field curvature
- **Physics:**
  - **Field curvature:** the sharp "plane" is really a curved bowl (the Petzval surface). Focused on a centre subject, the corners are slightly out of focus.
  - **Astigmatism:** radial and tangential lines focus at different distances, so corner points become short lines.
- **Lenses:** Petzval (extreme), cheap or vintage lenses, wide-angles. Modern flat-field lenses (macro, apochromats) have almost none.
- **Controls:** *Field curvature*, *Astigmatism*. [Softness / glow]

### 3.7 Distortion
- **Physics:** magnification changes with distance from the centre. Barrel distortion (shrinking toward the edge) is typical of wide and retrofocus lenses. Pincushion is typical of telephotos and some 85s. **Mustache** distortion (barrel in the centre, pincushion at the edge) is common in modern compact wides.
- **In-render advantage:** distortion maps each pixel to a scene direction, so it never leaves empty edges and needs no auto-scaling. The horizontal field of view stays the same while you adjust it.
- **Controls:** *Distortion K1* (+ barrel / − pincushion). Add an opposite-signed *Distortion K2* for mustache. [Distortion]

### 3.8 Chromatic aberration (four flavours)
Glass bends blue light more than red (dispersion, measured as the Abbe number). Lens designers pair glasses to cancel most of it. What's left over is:

| Type | Physics | Look | Control |
|---|---|---|---|
| **Lateral (transverse) CA** | magnification differs per colour | red/cyan edges that grow toward the corners, even in focus | *Lateral CA* |
| **Longitudinal (axial) CA** | focus distance differs per colour | colour fringes on out-of-focus edges: green behind focus, magenta in front | *Longitudinal CA* |
| **Secondary spectrum** | an achromat brings red and blue to the same focus but leaves green out | the classic **purple/green fringing** on bright edges | *Secondary spectrum* |
| **Spherochromatism** | spherical aberration differs per colour | coloured rims on bokeh balls (green outside / magenta inside, or the reverse) | *Spherochromatism* |

All four are scaled by the **Fringing** slider.

- **Lenses:** fast achromatic primes (85/1.4, 50/1.2) show heavy longitudinal CA and purple fringing wide open. Wide-angles show lateral CA. APO lenses (low-dispersion glass) show almost none.
- **How the shader does it:** it reads the wavelengths Octane is sampling, traces one of them per ray with its own focus and magnification, and weights the ray to that wavelength. This is true dispersion. If spectral sampling isn't available (or `USE_SPECTRAL` is 0), it does the same per R/G/B channel instead, which is a little cleaner but less exact. Anaglyph always uses the RGB path.

### 3.9 Vignetting and colour cast
- **Natural vignetting:** light falling obliquely onto the sensor drops off as roughly cos⁴ of the angle. Strong on wide-angles, mild on teles. Control: *Natural vignetting* [Vignette]. (Optical vignetting comes from §3.2.)
- **Colour cast:**
  - Old coatings and yellowed (thoriated) glass warm the whole image.
  - Some lenses shift colour toward the edges because coatings perform differently at steep angles.
  - Controls: *Edge colour cast* (how strong, toward the edges) and *Cast warmth* (− cool / + warm). Keep a global tint in the imager for a clean split.

### 3.10 Focus breathing
- **Physics:** when a lens focuses by moving all its glass outward, the image distance *v* grows and the field of view narrows (the frame "breathes" during a focus pull). Internal-focus cine lenses compensate for this. Many anamorphics breathe heavily.
- **All presets ship with breathing at 0**, so a focus pull never changes your framing. Turn it up per lens in Advanced if you want the effect.
- **Control:** *Focus breathing*:
  - 0 = no breathing (compensated)
  - 1 = full unit-focus breathing
  - above 1 = exaggerated
  - negative = the frame widens when focusing closer

### 3.11 Anamorphic
- **Physics:** a cylindrical front group squeezes the horizontal field, usually by 2×, so a wide image fits on a narrower sensor. Its pupil is narrower horizontally, so after desqueeze the bokeh is a **vertical oval**. Other traits: more barrel distortion horizontally, heavier breathing, and the famous horizontal streak flares.
- **Control:** *Anamorphic squeeze* (2.0 = classic, 1.33/1.5/1.8 = modern). It works on any lens, so you can make an anamorphic Helios. **Streak flares are a post effect**: Octane imager glare with a horizontal streak, or comp.

### 3.12 Onion rings
- **Physics:** cheaply moulded or ground aspherical elements leave fine concentric ripples, which show up as rings inside the bokeh.
- **Lenses:** many modern lenses with moulded aspherical elements, especially zooms and budget primes.
- **Control:** *Onion rings* (strength; the ring count is fixed). [Bokeh]

### 3.13 Tilt
- **Tilt (Scheimpflug):** tilts the focus plane top to bottom, for the miniature look or for keeping a long product sharp front to back. Control: *Focus plane tilt (deg)* in *Style: projection & optics*. It works on every lens, not just the Tilt-shift style. The Tilt-shift style also sets *Aperture size multiplier* to 4 so the out-of-focus areas melt fast.
- Lens whack (decentred elements) and sensor shift aren't in this version.

### Effects deliberately left to Octane's imager / post
- **Bloom and glare:** imager bloom/glare, or comp. (Veiling haze is in the shader: *Haze / veiling glare*.)
- **Ghosts and flares:** imager or comp.
- **Lens dirt:** comp.

Some of the glow does come from spherical aberration, so use less imager bloom than usual.

---

## 4. The lens list

Matched by eye to the LensNode reference frames. These are hand-set starting points per lens, not measured data. **Widest** is where the lens shows its full character (the *Full character at* line). **Focal** is the real lens's focal length, as a starting point: picking a lens doesn't set it, so frame the shot however you like.

| # | Lens | Focal | Widest |
|---|---|---|---|
| 21 | Sigma 15 f2.8 Diagonal Fisheye | 15 mm | f/2.8 |
| 15 | Lensbaby Obscura 16 f90 | 16 mm | f/90 |
| 22 | Nikon Nikkor 20 f4 | 20 mm | f/4 |
| 8 | Blackwing7 20.7 T1.9 X-Tuned | 20.7 mm | f/1.9 |
| 6 | Cooke Panchro Classic 21 T2.2 | 21 mm | f/2.2 |
| 5 | Canon FD 24 f1.4 SSC Aspherical | 24 mm | f/1.4 |
| 7 | LOMO Illumina 25 T1.3 | 25 mm | f/1.3 |
| 14 | Pocket Dispo 28 f10 | 28 mm | f/10 |
| 19 | Pinhole f150 | 30 mm | f/150 |
| 12 | Deakinizer #2A 32 T2.1 | 32 mm | f/2.1 |
| 13 | Civil War detuned | 35 mm | f/2 |
| 16 | 7Artisans Floral Bloom 37 T2.9 | 37 mm | f/2.9 |
| 3 | Voigtlander Nokton Classic 40 f1.4 | 40 mm | f/1.4 |
| 1 | Zeiss Ultra Prime 50 T1.9 (clean) | 50 mm | f/1.9 |
| 18 | Anamorphic 2x 50 T2 | 50 mm | f/2 |
| 4 | Canon 50 f0.95 Dream Lens | 50 mm | f/0.95 |
| 9 | Angenieux 10x25 zoom 55 T3.7 | 55 mm | f/3.7 |
| 10 | Petzval Pro 55 T1.8 | 55 mm | f/1.8 |
| 11 | Helios 44-2 58 f2 | 58 mm | f/2 |
| 17 | Soap Bubble 100 f2.8 (Trioplan) | 100 mm | f/2.8 |
| 27 | Vivitar Series 1 135 f2.3 | 135 mm | f/2.3 |
| 29 | Leica Telyt-S 800 f6.3 | 800 mm | f/6.3 |

The list in Cinema 4D is in this order: shortest focal length first, and at the same focal length the cleaner lens before the more characterful one. The numbers are just IDs.

**Fisheye (Sigma 15).** It works like the real lens: the field of view comes from your focal length and the camera's sensor width (equisolid projection, 180° image circle). At 15 mm it fills a full-frame image corner to corner; at 10 mm or below it gives a round image with black around it. No depth of field, like real fisheyes at normal apertures.

**Fewer, more different presets (v0.8).** Presets that looked nearly alike were removed so every entry is a distinct look: the Samsung 10 fisheye (same as the Sigma now that focal length is yours), Jupiter-3 (close to the Nokton), Konica Hexanon 200 (close to the Vivitar 135), Zeiss Biotar (another swirl lens next to the Helios), Sirui 1.33x anamorphic (the 2x anamorphic with a different squeeze, which Advanced can set), and the Leica Elmarit 28 and Nikkor 85 (two more clean lenses next to the Zeiss Ultra Prime and Blackwing7). The default lens is now the Cooke Panchro. A camera that used a removed preset switches to the Cooke Panchro when its tag is upgraded; save your own version first if you want to keep it.

**To add your own lens:** pick the closest preset, change its Advanced values, and press **Save as preset...**. To make it a built-in lens for every scene, send me its values and I'll add it to the plugin.

---

## 4b. Stylized cameras

Three styles were removed in v0.8 because they repeated others: Disposable camera (the Pocket Dispo lens is the same look), Bodycam / dashcam (close to CCTV) and Shower door glass (close to frosted and ribbed glass; *Glass in front* in Advanced still has it).

Everything optical happens in the render: pixel grids, CRT curvature and scanlines, phosphor mask, VHS line wobble and chroma smear, fisheye and 360 projections, Doom-style look-up shear, anaglyph stereo, prism copies, kaleidoscope, compound eye, textured glass, underwater port refraction and tilt-shift.

Tiny planet and Isometric have their own zoom (*Tiny planet zoom*, *Ortho view width* in cm), so they look the same whatever focal length the camera has. Set either to 0 to zoom with the focal length instead.

**Reverse perspective (hypercentric).** Things farther away look bigger instead of smaller, so you see the front, sides and top of a product at once, as if it opens up towards you. Real hypercentric lenses inspect bottles and cylinders all the way round. Rays start spread over the camera plane and converge on a point behind the subject:
- **Focus on the subject** (Focus Object). The subject at the focus distance keeps the framing your focal length would give with a normal lens; everything behind it grows.
- *Reverse perspective strength* (Advanced, preset 0.5): 0 = orthographic, 1 = convergence point at twice the focus distance, higher = stronger. Anything beyond the convergence point turns upside down.
- Set *Ortho view width* to frame by a fixed width (cm, at the subject) instead of the focal length.
- No depth of field, like a real hypercentric lens at its usual small aperture.

What a camera can't do is handled by **`characterlens_post.py`** (colour depth, palettes, noise, overlays, light leaks) and the **PS1 vertex snap** generator.

| # | Style | Finishing pass |
|---|---|---|
| 101 | PS1 | `ps1` (15-bit colour + dither) + **PS1 vertex snap** generator |
| 102 | N64 | `n64` |
| 103 | Doom / Build engine | `doom` (256-colour palette) |
| 104 | Game Boy Camera | `gameboy` (4-tone palette; `--gray` for camera prints) |
| 105 | CRT TV | `crt` (phosphor bloom) |
| 106 | VHS camcorder | `vhs --timestamp` (chroma bleed, noise, tracking band) |
| 108 | Toy camera (Holga) | `toy` (cross-process, light leaks) |
| 109 | Super 8 | `super8` (grain, flicker, dust) |
| 110 | Skate fisheye (VX1000) | `grain` |
| 111 | CCTV security | `cctv` (camera ID + timestamp) |
| 113 | Peephole | - |
| 114 | 2000s webcam | `webcam` (JPEG blocks, noise) |
| 115 | Night vision | `nightvision` (mono green, grain) |
| 116 | Anaglyph 3D (red/cyan) | - (view with red/cyan glasses) |
| 117 | Prism filter | - |
| 118 | Kaleidoscope | - |
| 119 | Compound eye | - |
| 120 | Frosted glass | - |
| 121 | Ribbed glass | - |
| 123 | Underwater (flat port) | - (add an Octane medium for depth haze) |
| 124 | Tilt-shift miniature | `tiltshift` (saturation) |
| 125 | Tiny planet | - (render about 1:1; size the planet with *Tiny planet zoom*) |
| 126 | Mirror ball | - (render 1:1) |
| 127 | 360 equirectangular | - (render 2:1) |
| 128 | Isometric (orthographic) | - (rotate camera H 45 deg, P -35.26 deg for true isometric; frame it with *Ortho view width*) |
| 129 | Reverse perspective (hypercentric) | - (see below) |

### Post tool (`characterlens_post.py`)
In the plugin window, pick a look, the input frame(s) and an output folder, then press **Run post-process**. It opens in its own console window. The first time, press **Install numpy + Pillow** (it asks before installing). From a command line:
```
python characterlens_post.py --list
python characterlens_post.py ps1 renders/ out_ps1/
python characterlens_post.py vhs renders/ out_vhs/ --timestamp --start "1998-07-04 15:30:00"
python characterlens_post.py rolling subframes/ out/ --subframes 8     # rolling shutter
python characterlens_post.py slitscan frames/ slit.png                 # slit-scan
```
- Needs Python with numpy + Pillow. EXR input also needs `imageio`; otherwise render PNG/TIFF.
- `--lines` should match the shader's pixel grid, so dither cells line up with the pixels.
- **Rolling shutter / slit-scan:** a camera can't give each ray its own time, so these are built from frames:
  - **Rolling shutter:** render the shot at N× the frame rate (e.g. 8 sub-frames per frame). The tool takes each row from a progressively later sub-frame.
  - **Slit-scan:** each column comes from a later frame of a normal sequence.

### PS1 vertex snap
Select the objects, then click the CharacterLens tag and press **Add PS1 snap to selected** (or use the button in the plugin window). They go under a *PS1 Vertex Snap* Python Generator that snaps vertices to the render camera's 240-line screen grid every frame: the PS1 geometry wobble.
- *Grid lines*, *Depth steps* and *Strength* are on its User Data.
- **Not possible in Octane:** PS1 affine texture warping, because a path tracer always interpolates perspective-correctly. Use low-res textures to get closer.

---

## 5. Advanced value ranges (rule of thumb)

- **Spherical aberration, Coma, Astigmatism, Field curvature:** 1.0 means a blur of about **1% of frame width** (≈40 px at 4K) at the rim of a wide-open pupil, in the corner. Subtle 0.02–0.1, characterful 0.1–0.3, extreme 0.5+. The Petzval and Civil War presets go well past 1 on purpose.
- **Lateral CA:** 1.0 ≈ 0.1% magnification difference per ±150 nm (≈2 px of fringing in a 4K corner). Civil War uses 25.
- **Longitudinal CA / Secondary spectrum:** 1.0 ≈ one f/2 depth of focus. 1–2 is visible purple fringing.
- **Cat-eye:** 0.2–0.4 typical, 0.6+ vintage. **Cat-eye rim radius:** 1.0–1.2.
- **Swirl:** 0.2 noticeable, 0.5 Helios, 0.9 Petzval.
- **Distortion K1:** ±0.01–0.05 typical lens, 0.1+ fisheye-ish.
- **Focus breathing:** 0 none (every preset's default), 0.3–0.6 a typical stills lens, 1 full unit-focus breathing, 1.2 a heavy anamorphic.
- **Haze / veiling glare:** 0.02–0.07 subtle, 0.3+ Lensbaby / soft-focus.

---

## 6. Building and matching lenses (LensNode as reference)

1. **Render the test set** in Octane with a perfect lens (Character 0):
   - **Bokeh field:** a 7×4 grid of tiny emissive spheres far behind a focused card, at f/wide-open, and again stopped down 2 stops.
   - **Foreground bokeh:** the same grid in front of focus. This shows the sign of spherical aberration.
   - **Point lights in focus:** for glow and corner coma.
   - **Checkerboard filling the frame:** for distortion and lateral CA.
   - **Flat white card:** for vignetting and colour cast.
   - **High-contrast edges** (white bars on black) slightly out of focus: for longitudinal CA and fringing.
2. Run the plain renders through **LensNode** in Resolve with the lens you want. Ideally, also collect real photos of that lens.
3. Render the same scenes with CharacterLens, side by side, and tune the Advanced values in this order: blades/shape → cat-eye/rim radius → spherical aberration and rim brightness → coma/astigmatism/field curvature → distortion → CA → vignetting/cast.
4. Press **Save as preset...** (or send me the values, and I'll make it a built-in lens).

---

## 7. Checks for a new Octane build

Verified in Cinema 4D 2027 with Octane 2026.x (v0.6): the shader compiles with spectral mode on, `camera:dofrandom` arrives (real bokeh), `octane:throughput` colour tinting works, and the Focus Object, lens switching and buttons work on the tag. Also checked live in v0.7: the Advanced inputs, the aperture line and lens switching; depth of field matches real optics. The v0.8 changes (Character Lens tab, colour correction, the aperture and vignette fixes, the preset list, the icon) were checked live in v0.8.1; F-stop below the lens limit was checked in v0.8.2. If you move to another Octane version, these are the things to re-check:

1. **Bokeh:** a defocused highlight should be a disc, not a sharp point. A point means `camera:dofrandom` isn't arriving.
2. **Killed rays darken:** corners should darken as Vignette goes up. If they don't, Octane is discarding killed samples instead of counting them as black.
3. **Colour fringing:** pick *Civil War detuned* with Fringing at 2 and look for purple/green fringes on a defocused white edge. Grey, colourless noise means `octane:throughput` isn't applied.
4. **Spectral mode compiles** (`_spectrum`, `color:wavelengths`). If not, set `USE_SPECTRAL 0` (see Quick start).
5. **Units:** a card at 2 m with Focus distance 200 cm should be sharp.
6. **Render cost:** expect it to be slower than the native thin-lens camera. AOVs such as motion vectors may not match the new camera.
