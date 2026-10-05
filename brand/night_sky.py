"""The night sky for the site, without the glare.

  python3 brand/night_sky.py

The sky behind every page is the app's baked night sky. In the app the bright
patch in the upper right is where the sun sits; on the site there is no sun
there, only text, and in the dark theme the patch washed the text out.

This takes the app's image (`brand/sky-night-source.webp`) and removes the
patch, nothing else: the palette, the bands and the thin wave lines stay. The
correction is computed from a blurred copy, so it follows the soft light and
does not touch the lines; inside the patch the light is pulled down to the
brown around it and warmed back to the same hue.

Needs `ffmpeg` and `cwebp` (brew install ffmpeg webp). No Python packages.
"""
import math
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sky-night-source.webp")
OUT = os.path.join(HERE, "..", "img", "sky-night.webp")

# Where the patch is (in pixels of the 1600x1698 image), how far down the light
# is pulled, and how much green and blue are taken out to keep it brown.
P = dict(CX=1150, CY=285, SX=760, SY=330, ANG=-7, GAIN=2.4, T=43, K=0.07, TG=0.70, TB=0.43, OV=70, BLUR=26)
c, s = math.cos(math.radians(P["ANG"])), math.sin(math.radians(P["ANG"]))
L = "(0.30*r(X,Y)+0.59*g(X,Y)+0.11*b(X,Y))"
dx, dy = "(X-%g)" % P["CX"], "(Y-%g)" % P["CY"]
u = "((%s*%g+%s*%g)/%g)" % (dx, c, dy, s, P["SX"])
v = "((-%s*%g+%s*%g)/%g)" % (dx, s, dy, c, P["SY"])
m = "clip(%g*exp(-(%s*%s+%s*%s)),0,1)" % (P["GAIN"], u, u, v, v)
# The map of multipliers is computed from the BLURRED image: the soft light is
# in it, the thin lines are not, so a line is multiplied by the same factor as
# the ground around it and stays a line. st(0)=luminance, st(1)=mask,
# st(2)=excess over the target, st(3)=luminance factor, st(4)=tint weight.
pre = ("st(0,%s);st(1,%s);st(2,max(ld(0)-%g,0));"
       "st(3,1-ld(1)*(1-(%g+ld(2)*%g)/max(ld(0),1))*gt(ld(0),%g));"
       "st(4,ld(1)*clip(ld(2)/%g,0,1));") % (L, m, P["T"], P["T"], P["K"], P["T"], P["OV"])
def ch(t): return "%s255*ld(3)*(1-ld(4)*(1-%g))" % (pre, t)
flt = ("[0]format=gbrp,split[a][b];"
       "[b]gblur=sigma=%g,geq=r='%s':g='%s':b='%s'[m];"
       "[a][m]blend=all_mode=multiply") % (P["BLUR"], ch(1.0), ch(P["TG"]), ch(P["TB"]))
with tempfile.TemporaryDirectory() as tmp:
    png = os.path.join(tmp, "sky.png")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", SRC, "-filter_complex", flt, "-frames:v", "1", png], check=True)
    subprocess.run(["cwebp", "-quiet", "-q", "88", "-m", "6", "-sharp_yuv", png, "-o", OUT], check=True)
print("written", os.path.normpath(OUT), os.path.getsize(OUT), "bytes")
