"""Pre-blur background photos into tiny WebP files, so the browser never runs a live blur.
Usage: python tools/bg.py <out_dir> name=photo.png [name=photo.png ...]"""
import sys, os
from PIL import Image, ImageFilter

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for arg in sys.argv[2:]:
    name, path = arg.split('=', 1)
    im = Image.open(path).convert('RGB')
    # crop to 16:9 so every photo fills the cards the same way
    w, h = im.size
    tw, th = (w, round(w * 9 / 16)) if w / h < 16 / 9 else (round(h * 16 / 9), h)
    im = im.crop(((w - tw) // 2, (h - th) // 2, (w + tw) // 2, (h + th) // 2))
    im = im.resize((640, 360), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.6))
    dst = os.path.join(out, name + '.webp')
    im.save(dst, 'WEBP', quality=62, method=6)
    print(name, os.path.getsize(dst), 'bytes')
