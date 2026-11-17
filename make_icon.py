"""生成 WorkTime 应用图标（与启动页徽标一致）
- 1024 母版：深空金属渐变 + 青色发光指针
- 输出 icon-1024.png / icon-512.png / icon-192.png
- 同时输出一张对比预览图，便于确认
"""
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import os

S = 1024
OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- 1. 斜向金属渐变背景 ----------
grad = Image.linear_gradient("L").resize((int(S * 1.45), int(S * 1.45)), Image.LANCZOS)
grad = grad.rotate(45, resample=Image.BICUBIC, expand=False)
grad = ImageOps.invert(grad)
off = (grad.width - S) // 2
grad = grad.crop((off, off, off + S, off + S))

base = ImageOps.colorize(grad, black="#0f1a26", mid="#22334a", white="#5f809c").convert("RGB")

# ---------- 2. 左上柔光（径向） ----------
BIG = int(S * 2.4)
rad = Image.radial_gradient("L").resize((BIG, BIG), Image.LANCZOS)
rad = ImageOps.invert(rad)                                      # 中心亮、边缘暗
rad = rad.filter(ImageFilter.GaussianBlur(BIG * 0.06))
shift = Image.new("L", (BIG, BIG), 0)
shift.paste(rad, (0, 0))
shift = shift.crop((int(BIG * 0.30), int(BIG * 0.34), int(BIG * 0.30) + S, int(BIG * 0.34) + S))
sheen_mask = shift.point(lambda v: int(v * 0.44))
base = Image.composite(Image.new("RGB", (S, S), "#a8cade"), base, sheen_mask)

# ---------- 3. 指针（青蓝渐变 + 发光） ----------
p0 = (int(S * 0.452), int(S * 0.548))   # 起（中心偏左下）
p1 = (int(S * 0.582), int(S * 0.432))   # 止（右上）

needle = Image.new("RGBA", (S, S), (0, 0, 0, 0))
nd = ImageDraw.Draw(needle)
w = int(S * 0.036)
nd.line([p0, p1], fill=(90, 226, 246, 255), width=w)
for p in (p0, p1):
    nd.ellipse([p[0] - w // 2, p[1] - w // 2, p[0] + w // 2, p[1] + w // 2], fill=(90, 226, 246, 255))

# 渐变：上端更亮
tip = Image.new("RGBA", (S, S), (0, 0, 0, 0))
td = ImageDraw.Draw(tip)
td.line([((p0[0] + p1[0]) // 2, (p0[1] + p1[1]) // 2), p1], fill=(180, 248, 255, 255), width=w)
for p in [p1]:
    td.ellipse([p[0] - w // 2, p[1] - w // 2, p[0] + w // 2, p[1] + w // 2], fill=(180, 248, 255, 255))
needle = Image.alpha_composite(needle, tip)

# 外发光
glow = needle.filter(ImageFilter.GaussianBlur(S * 0.035))
glow = glow.point(lambda v: int(v * 0.9))
base = base.convert("RGBA")
base = Image.alpha_composite(base, glow)
base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(S * 0.08)))
base = Image.alpha_composite(base, needle)

# ---------- 3.5 底部内阴影 + 顶部高光边 ----------
sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rectangle([0, int(S * 0.62), S, S], fill=110)
sh = sh.filter(ImageFilter.GaussianBlur(S * 0.12)).point(lambda v: int(v * 0.42))
base = Image.alpha_composite(base, Image.merge("RGBA", (Image.new("L", (S, S), 0),) * 3 + (sh,)))

# ---------- 4. 内侧描边 + 微暗角 ----------
edge = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ed = ImageDraw.Draw(edge)
ed.rounded_rectangle([1, 1, S - 2, S - 2], radius=int(S * 0.22), outline=(255, 255, 255, 34), width=max(2, S // 340))
base = Image.alpha_composite(base, edge)

vign = Image.new("L", (S, S), 0)
vd = ImageDraw.Draw(vign)
vd.ellipse([-int(S * 0.10), -int(S * 0.10), int(S * 1.10), int(S * 1.10)], fill=255)
vign = ImageOps.invert(vign).filter(ImageFilter.GaussianBlur(S * 0.10)).point(lambda v: int(v * 0.28))
base = Image.alpha_composite(base, Image.merge("RGBA", (Image.new("L", (S, S), 0),) * 3 + (vign,)))

icon = base.convert("RGB")

# ---------- 5. 输出 ----------
icon.save(os.path.join(OUT, "icon-1024.png"))
icon.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "icon-512.png"))
icon.resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, "icon-192.png"))

# ---------- 6. 预览图 ----------
prev = Image.new("RGB", (S + 520, 700), "#101418")
prev.paste(icon.resize((280, 280), Image.LANCZOS), (40, 60))
prev.paste(icon.resize((120, 120), Image.LANCZOS), (360, 60))
prev.paste(icon.resize((64, 64), Image.LANCZOS), (360, 200))
prev.paste(icon.resize((40, 40), Image.LANCZOS), (460, 200))
# 圆形遮罩预览
circ = Image.new("L", (280, 280), 0)
ImageDraw.Draw(circ).ellipse([0, 0, 279, 279], fill=255)
round_icon = icon.resize((280, 280), Image.LANCZOS)
prev.paste(round_icon, (40, 380), circ)
prev.paste(icon.resize((120, 120), Image.LANCZOS), (360, 380))
prev.save(os.path.join(OUT, "icon-preview.png"))

print("done:", os.path.join(OUT, "icon-1024.png"))
