"""Every per-preset value the shader uses, as editable Advanced controls.

Each entry: (key, pin, label, kind, min, max, slider_min, slider_max, step, group, cycle)
  key   - field name in looks.py (lens fields, then style fields; style haze is "s:haze")
  pin   - OSL input name on the shader
  kind  - "real", "int", "bool" or "cycle"
"""

PROJ = [(0, "Lens"), (1, "Fisheye (equidistant)"), (2, "Fisheye (stereographic)"), (3, "Fisheye (equisolid)"),
        (4, "360 equirectangular"), (5, "Tiny planet"), (6, "Mirror ball"), (7, "Orthographic"),
        (8, "Doom look-up shear"), (9, "Reverse perspective")]
GLASS = [(0, "None"), (1, "Frosted"), (2, "Ribbed"), (3, "Shower door")]

G_AP = "Aperture & bokeh"
G_SH = "Sharpness & glow"
G_DI = "Distortion & breathing"
G_CO = "Colour fringing & vignetting"
G_PR = "Style: projection & optics"
G_PX = "Style: pixels & screen"
G_MO = "Style: motion & gate"
G_FX = "Style: filters & glass"

ADV = [
    # ---------------- lens character ----------------
    ("blades",     "A_blades",     "Aperture blades (0 = round)",        "int",  0, 32, 0, 16, 1, G_AP, None),
    ("roundness",  "A_roundness",  "Blade roundness",                    "real", 0, 1, 0, 1, 0.01, G_AP, None),
    ("catEye",     "A_catEye",     "Cat-eye",                            "real", 0, 3, 0, 1, 0.01, G_AP, None),
    ("rimRadius",  "A_rimRadius",  "Cat-eye rim radius",                 "real", 0.5, 5, 1, 2, 0.01, G_AP, None),
    ("rimBias",    "A_rimBias",    "Bokeh rim brightness (- centre / + rim)", "real", -2, 2, -1, 1, 0.01, G_AP, None),
    ("onion",      "A_onion",      "Onion rings",                        "real", 0, 1, 0, 0.2, 0.005, G_AP, None),
    ("maxF",       "A_maxF",       "Widest aperture (f-number)",         "real", 0.5, 256, 0.95, 22, 0.05, G_AP, None),
    ("squeeze",    "A_squeeze",    "Anamorphic squeeze",                 "real", 0.5, 3, 1, 2, 0.01, G_AP, None),

    ("sa",         "A_sa",         "Spherical aberration (glow)",        "real", -5, 5, -1, 3, 0.01, G_SH, None),
    ("coma",       "A_coma",       "Coma",                               "real", -3, 3, -1, 1, 0.01, G_SH, None),
    ("astig",      "A_astig",      "Astigmatism",                        "real", 0, 10, 0, 4, 0.01, G_SH, None),
    ("fc",         "A_fc",         "Field curvature",                    "real", 0, 5, 0, 2, 0.01, G_SH, None),
    ("swirl",      "A_swirl",      "Swirl strength",                              "real", 0, 3, 0, 1, 0.01, G_SH, None),
    ("haze",       "A_haze",       "Haze / veiling glare",               "real", 0, 2, 0, 0.5, 0.005, G_SH, None),
    ("hazeSpread", "A_hazeSpread", "Haze spread",                        "real", 0, 1, 0, 0.25, 0.005, G_SH, None),

    ("k1",         "A_k1",         "Distortion K1 (+ barrel / - pincushion)", "real", -1, 1, -0.1, 0.1, 0.001, G_DI, None),
    ("k2",         "A_k2",         "Distortion K2 (opposite sign = mustache)", "real", -1, 1, -0.05, 0.05, 0.001, G_DI, None),
    ("breathing",  "A_breathing",  "Focus breathing",                    "real", -3, 3, 0, 1.5, 0.01, G_DI, None),

    ("latCA",      "A_latCA",      "Lateral CA (edge fringes)",          "real", 0, 100, 0, 25, 0.1, G_CO, None),
    ("longCA",     "A_longCA",     "Longitudinal CA (out-of-focus fringes)", "real", 0, 20, 0, 5, 0.01, G_CO, None),
    ("secCA",      "A_secCA",      "Secondary spectrum (purple fringe)", "real", 0, 10, 0, 2, 0.01, G_CO, None),
    ("sphCA",      "A_sphCA",      "Spherochromatism (coloured bokeh rims)", "real", 0, 10, 0, 2, 0.01, G_CO, None),
    ("natVig",     "A_natVig",     "Natural vignetting",                 "real", 0, 3, 0, 1.5, 0.01, G_CO, None),
    ("castAmt",    "A_castAmt",    "Edge colour cast",                   "real", 0, 1, 0, 0.3, 0.005, G_CO, None),
    ("warmth",     "A_warmth",     "Cast warmth (- cool / + warm)",      "real", -1, 1, -1, 1, 0.01, G_CO, None),

    # ---------------- stylized camera ----------------
    ("proj",       "A_proj",       "Projection",                         "cycle", 0, 9, 0, 9, 1, G_PR, PROJ),
    ("fov",        "A_fov",        "Field of view override (deg, 0 = camera)", "real", 0, 360, 0, 220, 0.5, G_PR, None),
    ("circle",     "A_circle",     "Fisheye image circle (0 = full frame)", "real", 0, 2, 0, 1, 0.01, G_PR, None),
    ("zoom",       "A_zoom",       "Tiny planet zoom (0 = from focal length)", "real", 0, 10, 0, 2, 0.01, G_PR, None),
    ("orthoWidth", "A_orthoWidth", "Ortho view width (cm, 0 = from focal length)", "real", 0, 100000, 0, 1000, 1, G_PR, None),
    ("revStrength", "A_revStrength", "Reverse perspective strength",    "real", 0, 20, 0, 3, 0.01, G_PR, None),
    ("tilt",       "A_tilt",       "Focus plane tilt (deg)",             "real", -45, 45, -10, 10, 0.1, G_PR, None),
    ("apBoost",    "A_apBoost",    "Aperture size multiplier",           "real", 0.05, 10, 0.25, 4, 0.01, G_PR, None),
    ("lensAmt",    "A_lensAmt",    "Lens character amount",              "real", 0, 3, 0, 2, 0.01, G_PR, None),
    ("noDOF",      "A_noDOF",      "No depth of field",                  "bool", 0, 1, 0, 1, 1, G_PR, None),
    ("port",       "A_port",       "Flat underwater port",               "bool", 0, 1, 0, 1, 1, G_PR, None),
    ("stereo",     "A_stereo",     "Anaglyph 3D (red/cyan)",             "bool", 0, 1, 0, 1, 1, G_PR, None),
    ("extraK1",    "A_extraK1",    "Extra distortion",                   "real", -1, 1, 0, 0.3, 0.001, G_PR, None),
    ("extraFC",    "A_extraFC",    "Extra field curvature",              "real", 0, 3, 0, 1, 0.01, G_PR, None),
    ("extraVig",   "A_extraVig",   "Extra vignette",                     "real", 0, 5, 0, 2, 0.01, G_PR, None),
    ("s:haze",     "A_sHaze",      "Minimum haze",                       "real", 0, 2, 0, 0.3, 0.005, G_PR, None),
    ("s:hazeSpread", "A_sHazeSpread", "Haze spread override (0 = lens)", "real", 0, 1, 0, 0.3, 0.005, G_PR, None),

    ("pixLines",   "A_pixLines",   "Pixel grid lines (0 = off)",         "int",  0, 2160, 0, 720, 1, G_PX, None),
    ("pixAspect",  "A_pixAspect",  "Pixel aspect",                       "real", 0.25, 4, 0.5, 2, 0.01, G_PX, None),
    ("pixSoft",    "A_pixSoft",    "Pixel softness",                     "real", 0, 1, 0, 1, 0.01, G_PX, None),
    ("scan",       "A_scan",       "Scanlines",                          "real", 0, 1, 0, 1, 0.01, G_PX, None),
    ("mask",       "A_mask",       "Phosphor mask",                      "real", 0, 1, 0, 1, 0.01, G_PX, None),
    ("curve",      "A_curve",      "Screen curvature",                   "real", 0, 0.5, 0, 0.15, 0.001, G_PX, None),
    ("conv",       "A_conv",       "Convergence error",                  "real", 0, 5, 0, 2, 0.01, G_PX, None),
    ("chromaSmear", "A_chromaSmear", "Chroma smear",                     "real", 0, 3, 0, 1, 0.01, G_PX, None),
    ("tint:0",     "A_tintR",      "Tint red",                           "real", 0, 3, 0, 2, 0.01, G_PX, None),
    ("tint:1",     "A_tintG",      "Tint green",                         "real", 0, 3, 0, 2, 0.01, G_PX, None),
    ("tint:2",     "A_tintB",      "Tint blue",                          "real", 0, 3, 0, 2, 0.01, G_PX, None),

    ("wobble",     "A_wobble",     "VHS wobble",                         "real", 0, 3, 0, 1, 0.01, G_MO, None),
    ("weave",      "A_weave",      "Film gate weave",                    "real", 0, 3, 0, 1, 0.01, G_MO, None),
    ("gate",       "A_gate",       "Rounded gate corners",               "real", 0, 0.5, 0, 0.2, 0.001, G_MO, None),
    ("tube",       "A_tube",       "Round tube mask (0 = off)",          "real", 0, 2, 0, 1, 0.01, G_MO, None),

    ("copies",     "A_copies",     "Prism copies (0 = off)",             "int",  0, 16, 0, 8, 1, G_FX, None),
    ("prismOffset", "A_prismOffset", "Prism spread",                     "real", 0, 0.5, 0, 0.2, 0.001, G_FX, None),
    ("kaleido",    "A_kaleido",    "Kaleidoscope segments (0 = off)",    "int",  0, 24, 0, 12, 1, G_FX, None),
    ("cells",      "A_cells",      "Compound eye cells (0 = off)",       "int",  0, 40, 0, 16, 1, G_FX, None),
    ("glass",      "A_glass",      "Glass in front",                     "cycle", 0, 3, 0, 3, 1, G_FX, GLASS),
    ("glassAmt",   "A_glassAmt",   "Glass amount",                       "real", 0, 3, 0, 1, 0.01, G_FX, None),
]

LENS_GROUPS = [G_AP, G_SH, G_DI, G_CO]
STYLE_GROUPS = [G_PR, G_PX, G_MO, G_FX]
OSL_INT = {"blades", "proj", "glass", "stereo", "port", "noDOF"}   # int pins in the shader
