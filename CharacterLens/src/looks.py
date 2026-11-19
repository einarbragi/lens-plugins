"""Single source of truth for CharacterLens lenses and stylized cameras.
Generates the OSL tables and the C4D tag table (see build.py).
Values are hand-set by lens family / reference frames, not measured data."""

LENS_DEFAULT = dict(
    blades=9, roundness=0.8, rimBias=0.0, onion=0.0, catEye=0.3, rimRadius=1.1, swirl=0.0,
    sa=0.05, coma=0.05, astig=0.03, fc=0.03, k1=0.0, k2=0.0,
    latCA=0.5, longCA=0.8, secCA=0.4, sphCA=0.5, natVig=0.7, castAmt=0.0, warmth=0.0,
    breathing=0.0, maxF=1.4, squeeze=1.0, haze=0.0, hazeSpread=0.05, focal=50)

# id: (name, overrides)
LENSES = {
    1: ("Zeiss Ultra Prime 50 T1.9 (clean)", dict(focal=50, maxF=1.9, roundness=0.9, catEye=0.2, rimRadius=1.2,
        sa=0.02, coma=0.02, astig=0.01, fc=0.01, k1=0.005, latCA=0.2, longCA=0.3, secCA=0.15, sphCA=0.2,
        natVig=0.4, breathing=0.0)),
    3: ("Voigtlander Nokton Classic 40 f1.4", dict(focal=40, blades=10, roundness=0.7, rimBias=-0.1, catEye=0.45,
        rimRadius=1.05, swirl=0.15, sa=0.5, coma=0.15, astig=0.08, fc=0.10, k1=0.01, latCA=0.6, longCA=1.4,
        secCA=0.8, sphCA=1.0, natVig=0.9, castAmt=0.1, warmth=0.2, haze=0.06, hazeSpread=0.04, breathing=0.0)),
    4: ("Canon 50 f0.95 Dream Lens", dict(focal=50, maxF=0.95, blades=10, roundness=0.5, rimBias=-0.2, catEye=0.6,
        rimRadius=1.0, swirl=0.25, sa=0.7, coma=0.25, astig=0.15, fc=0.2, k1=0.01, latCA=0.8, longCA=2.0,
        secCA=1.2, sphCA=1.2, natVig=1.0, castAmt=0.15, warmth=0.3, haze=0.14, hazeSpread=0.06, breathing=0.0)),
    5: ("Canon FD 24 f1.4 SSC Aspherical", dict(focal=24, blades=8, roundness=0.5, catEye=0.45, rimRadius=1.05,
        onion=0.05, sa=0.06, coma=0.2, astig=0.1, fc=0.08, k1=0.03, k2=-0.005, latCA=1.0, natVig=1.0,
        breathing=0.0)),
    6: ("Cooke Panchro Classic 21 T2.2", dict(focal=21, maxF=2.2, blades=11, roundness=0.9, rimBias=-0.1,
        catEye=0.35, sa=0.12, coma=0.1, astig=0.08, fc=0.1, k1=0.025, latCA=0.6, longCA=0.6, natVig=0.8,
        castAmt=0.2, warmth=0.5, haze=0.03, breathing=0.0)),
    7: ("LOMO Illumina 25 T1.3", dict(focal=25, maxF=1.3, roundness=0.7, catEye=0.4, sa=0.15, coma=0.1,
        astig=0.06, fc=0.06, k1=0.015, longCA=1.0, secCA=0.6, sphCA=0.6, castAmt=0.12, warmth=-0.4,
        haze=0.02)),
    8: ("Blackwing7 20.7 T1.9 X-Tuned", dict(focal=20.7, maxF=1.9, catEye=0.35, sa=0.18, coma=0.08, astig=0.06,
        fc=0.06, k1=0.02, sphCA=0.7, castAmt=0.05, warmth=0.2, haze=0.07, hazeSpread=0.03, breathing=0.0)),
    9: ("Angenieux 10x25 zoom 55 T3.7", dict(focal=55, maxF=3.7, blades=6, roundness=0.6, catEye=0.3,
        sa=0.15, coma=0.12, astig=0.1, fc=0.12, k1=0.01, latCA=1.0, natVig=0.8, castAmt=0.2, warmth=0.5,
        haze=0.12, hazeSpread=0.12, breathing=0.0)),
    10: ("Petzval Pro 55 T1.8", dict(focal=55, maxF=1.8, blades=0, roundness=1.0, rimBias=0.2, catEye=0.8,
        rimRadius=1.0, swirl=0.9, sa=0.1, coma=0.35, astig=1.2, fc=2.0, latCA=0.6, longCA=1.0, natVig=1.0,
        castAmt=0.08, warmth=0.3, haze=0.03, breathing=0.0)),
    11: ("Helios 44-2 58 f2", dict(focal=58, maxF=2.0, blades=8, roundness=0.4, rimBias=0.35, catEye=0.6,
        rimRadius=1.0, swirl=0.45, sa=0.10, coma=0.12, astig=0.4, fc=0.5, latCA=0.8, longCA=1.2, secCA=0.6,
        natVig=0.8, castAmt=0.15, warmth=0.6, breathing=0.0)),
    12: ("Deakinizer #2A 32 T2.1", dict(focal=32, maxF=2.1, blades=0, roundness=1.0, catEye=0.6, rimRadius=1.0,
        swirl=0.4, sa=0.25, coma=0.5, astig=2.5, fc=0.8, k1=0.02, latCA=6.0, longCA=1.5, secCA=1.0,
        sphCA=1.0, natVig=1.0, castAmt=0.1, warmth=0.2, haze=0.05, hazeSpread=0.08, breathing=0.0)),
    13: ("Civil War detuned", dict(focal=35, maxF=2.0, blades=0, roundness=1.0, catEye=0.7, rimRadius=1.0,
        swirl=0.5, sa=0.3, coma=0.7, astig=4.0, fc=1.2, k1=0.02, latCA=25.0, longCA=4.0, secCA=1.5, sphCA=1.5,
        natVig=1.1, castAmt=0.1, warmth=0.1, haze=0.06, hazeSpread=0.1, breathing=0.0)),
    14: ("Pocket Dispo 28 f10", dict(focal=28, maxF=10.0, blades=0, roundness=1.0, catEye=0.2, rimRadius=1.0,
        sa=0.2, coma=0.3, astig=0.35, fc=0.8, k1=0.07, k2=0.01, latCA=1.5, longCA=0.5, secCA=0.3, sphCA=0.3,
        natVig=1.0, castAmt=0.15, warmth=0.4, haze=0.05, hazeSpread=0.1, breathing=0.0)),
    15: ("Lensbaby Obscura 16 f90", dict(focal=16, maxF=90.0, blades=0, roundness=1.0, catEye=0.0, rimRadius=2.0,
        sa=0.3, coma=0.0, astig=0.0, fc=0.1, latCA=0.5, longCA=0.0, secCA=0.0, sphCA=0.0, natVig=1.0,
        castAmt=0.05, warmth=0.2, haze=0.35, hazeSpread=0.12, breathing=0.0)),
    16: ("7Artisans Floral Bloom 37 T2.9", dict(focal=37, maxF=2.9, blades=0, roundness=1.0, rimBias=-0.4,
        sa=3.0, coma=0.6, astig=0.3, fc=0.6, longCA=1.0, sphCA=0.8, natVig=0.8, castAmt=0.08, warmth=0.3,
        haze=0.3, hazeSpread=0.08)),
    17: ("Soap Bubble 100 f2.8 (Trioplan)", dict(focal=100, maxF=2.8, blades=15, roundness=0.9, rimBias=0.8,
        catEye=0.45, rimRadius=1.0, swirl=0.2, sa=-0.25, coma=0.1, astig=0.1, fc=0.15, longCA=1.5,
        secCA=0.8, sphCA=1.2, castAmt=0.05, warmth=0.3, breathing=0.0)),
    18: ("Anamorphic 2x 50 T2", dict(focal=50, maxF=2.0, blades=0, roundness=1.0, rimBias=0.1, catEye=0.4,
        rimRadius=1.05, swirl=0.05, sa=0.12, coma=0.1, astig=0.15, fc=0.2, k1=0.04, k2=0.01, latCA=1.2,
        longCA=1.0, secCA=0.6, natVig=0.8, breathing=0.0, squeeze=2.0)),
    19: ("Pinhole f150", dict(focal=30, maxF=150.0, blades=0, roundness=1.0, catEye=0.0, rimRadius=3.0,
        sa=0.0, coma=0.0, astig=0.0, fc=0.0, latCA=0.0, longCA=0.0, secCA=0.0, sphCA=0.0, natVig=1.0,
        haze=0.02, hazeSpread=0.02, breathing=0.0)),
    21: ("Sigma 15 f2.8 Diagonal Fisheye", dict(focal=15, maxF=2.8, blades=7, roundness=0.7, catEye=0.0,
        sa=0.04, coma=0.08, astig=0.1, fc=0.1, latCA=1.5, longCA=0.4, secCA=0.2, sphCA=0.2, natVig=0.9,
        castAmt=0.03, haze=0.02)),
    22: ("Nikon Nikkor 20 f4", dict(focal=20, maxF=4.0, blades=7, roundness=0.3, catEye=0.35, rimRadius=1.05,
        sa=0.04, coma=0.18, astig=0.15, fc=0.12, k1=0.035, k2=-0.008, latCA=1.8, longCA=0.4, secCA=0.3,
        sphCA=0.3, natVig=1.1, castAmt=0.05, warmth=0.1, haze=0.02)),
    27: ("Vivitar Series 1 135 f2.3", dict(focal=135, maxF=2.3, blades=6, roundness=0.35, rimBias=-0.05,
        catEye=0.3, rimRadius=1.1, sa=0.15, coma=0.05, astig=0.03, fc=0.03, k1=-0.006, latCA=0.3, longCA=1.6,
        secCA=1.1, sphCA=0.7, natVig=0.6, castAmt=0.05, warmth=0.15, haze=0.03)),
    29: ("Leica Telyt-S 800 f6.3", dict(focal=800, maxF=6.3, blades=8, roundness=0.5, catEye=0.1, rimRadius=1.3,
        sa=0.08, coma=0.02, astig=0.01, fc=0.01, k1=-0.01, latCA=0.2, longCA=1.4, secCA=1.6, sphCA=0.6,
        natVig=0.3, castAmt=0.04, warmth=0.1, haze=0.12, hazeSpread=0.1)),
}

# Real lenses that also need style-path values (the fisheyes' projection).
LENS_STYLE = {21: dict(proj=3, noDOF=1)}

# Order of real lenses in the Lens list: by focal length, clean before characterful.
LENS_ORDER = [21, 15, 22, 8, 6, 5, 7, 14, 19, 12, 13, 16, 3,
              1, 18, 4, 9, 10, 11, 17, 27, 29]

STYLE_DEFAULT = dict(
    proj=0, fov=0.0, circle=0.0, pixLines=0.0, pixAspect=1.0, pixSoft=0.0, scan=0.0, mask=0.0,
    curve=0.0, conv=0.0, chromaSmear=0.0, wobble=0.0, weave=0.0, gate=0.0, tint=(1.0, 1.0, 1.0),
    tube=0.0, copies=0.0, prismOffset=0.0, kaleido=0.0, cells=0.0, glass=0, glassAmt=0.0, stereo=0,
    tilt=0.0, port=0, apBoost=1.0, lensAmt=1.0, noDOF=0, extraVig=0.0, extraK1=0.0, extraFC=0.0,
    haze=0.0, hazeSpread=0.0, baseLens=1, zoom=0.0, orthoWidth=0.0, revStrength=0.0, focal=35, fstop=None)
STYLE_INT = {"proj", "glass", "stereo", "port", "noDOF", "baseLens"}

# proj: 0 lens (perspective)  1 fisheye equidistant  2 fisheye stereographic  3 fisheye equisolid
#       4 360 equirect  5 tiny planet  6 mirror ball  7 orthographic  8 Doom y-shear
#       9 reverse perspective (hypercentric)
STYLES = {
    101: ("[Style] PS1", dict(fov=60, pixLines=240, noDOF=1, lensAmt=0.0, focal=31)),
    102: ("[Style] N64", dict(fov=60, pixLines=240, pixSoft=1.0, noDOF=1, lensAmt=0.0, haze=0.04, hazeSpread=0.02, focal=31)),
    103: ("[Style] Doom / Build engine", dict(proj=8, fov=90, pixLines=200, noDOF=1, lensAmt=0.0, focal=18)),
    104: ("[Style] Game Boy Camera", dict(fov=50, pixLines=112, noDOF=1, lensAmt=0.6, baseLens=14, extraVig=0.5, focal=38)),
    105: ("[Style] CRT TV", dict(pixLines=480, pixSoft=0.6, scan=0.55, mask=0.45, curve=0.1, conv=1.0, gate=0.08,
                                 lensAmt=0.3, extraVig=0.6, focal=35)),
    106: ("[Style] VHS camcorder", dict(pixLines=240, pixAspect=1.8, pixSoft=1.0, wobble=1.0, conv=1.5, chromaSmear=1.0,
                                        baseLens=9, lensAmt=0.6, apBoost=0.4, haze=0.05, hazeSpread=0.05, focal=35)),
    108: ("[Style] Toy camera (Holga)", dict(baseLens=14, lensAmt=2.0, extraVig=2.0, extraFC=0.4, haze=0.08,
                                             hazeSpread=0.1, focal=40, fstop=10)),
    109: ("[Style] Super 8", dict(baseLens=9, lensAmt=1.0, gate=0.15, weave=1.0, haze=0.05, focal=30)),
    110: ("[Style] Skate fisheye (VX1000)", dict(proj=3, fov=160, pixLines=480, pixSoft=0.7, conv=0.4, lensAmt=0.5,
                                                extraVig=1.0, noDOF=1, focal=10)),
    111: ("[Style] CCTV security", dict(proj=2, fov=115, pixLines=480, pixSoft=0.9, haze=0.04, hazeSpread=0.05,
                                        extraVig=0.5, noDOF=1, lensAmt=0.4, focal=12)),
    113: ("[Style] Peephole", dict(proj=1, fov=180, circle=0.85, extraVig=1.5, haze=0.05, lensAmt=0.4, noDOF=1, focal=8)),
    114: ("[Style] 2000s webcam", dict(fov=55, pixLines=240, pixSoft=1.0, baseLens=14, lensAmt=0.8, conv=0.6, haze=0.06,
                                       hazeSpread=0.06, extraVig=0.5, noDOF=1, focal=35)),
    115: ("[Style] Night vision", dict(fov=40, tube=0.95, tint=(0.3, 1.4, 0.4), extraFC=0.5, baseLens=7, lensAmt=0.7,
                                       extraVig=1.0, haze=0.08, hazeSpread=0.05, focal=50)),
    116: ("[Style] Anaglyph 3D (red/cyan)", dict(stereo=1, lensAmt=0.3, focal=35)),
    117: ("[Style] Prism filter", dict(copies=5, prismOffset=0.15, haze=0.03, focal=50)),
    118: ("[Style] Kaleidoscope", dict(kaleido=6, focal=35)),
    119: ("[Style] Compound eye", dict(fov=70, cells=9, lensAmt=0.5, noDOF=1, focal=25)),
    120: ("[Style] Frosted glass", dict(glass=1, glassAmt=1.0, focal=50)),
    121: ("[Style] Ribbed glass", dict(glass=2, glassAmt=1.0, focal=50)),
    123: ("[Style] Underwater (flat port)", dict(port=1, tint=(0.55, 0.9, 1.05), haze=0.15, hazeSpread=0.25, focal=24)),
    124: ("[Style] Tilt-shift miniature", dict(tilt=10.0, apBoost=4.0, focal=50)),
    125: ("[Style] Tiny planet", dict(proj=5, noDOF=1, lensAmt=0.0, zoom=0.5, focal=6)),
    126: ("[Style] Mirror ball", dict(proj=6, noDOF=1, lensAmt=0.0, focal=50)),
    127: ("[Style] 360 equirectangular", dict(proj=4, noDOF=1, lensAmt=0.0, focal=12)),
    128: ("[Style] Isometric (orthographic)", dict(proj=7, noDOF=1, lensAmt=0.0, orthoWidth=150.0, focal=50)),
    129: ("[Style] Reverse perspective (hypercentric)", dict(proj=9, noDOF=1, lensAmt=0.0, revStrength=0.5, focal=50)),
}


def lens(i):
    d = dict(LENS_DEFAULT); d.update(LENSES[i][1]); return d


def style(i):
    d = dict(STYLE_DEFAULT); d.update(STYLES[i][1]); return d
