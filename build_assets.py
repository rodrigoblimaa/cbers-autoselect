"""Build helper: preview icon and export translation catalog to Qt Linguist TS."""
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageDraw
from cbers_autoselect.i18n import STRINGS

BASE = Path(__file__).resolve().parent

# Draw entirely with original graphics; no external copyrighted icon dependencies.
scale = 18
s = lambda v: int(round(v*scale))
im = Image.new("RGBA", (s(64), s(64)), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
ink = (43, 52, 61, 255)
green = (15, 158, 56, 255)
white = (255, 255, 255, 255)

# Back scene, front scene: large and readable at 16-24 px.
d.rounded_rectangle((s(3.5),s(4),s(42),s(42)), radius=s(5), outline=ink, width=s(4.6))
d.ellipse((s(10),s(11),s(18),s(19)), fill=ink)
d.line([(s(6),s(35)),(s(16),s(24)),(s(24),s(32)),(s(31),s(26)),(s(39),s(33))], fill=ink, width=s(4), joint='curve')

# Front image needs a small light backing where the two borders intersect.
d.rounded_rectangle((s(17),s(18),s(61.5),s(61.5)), radius=s(5), fill=white)
d.rounded_rectangle((s(17),s(18),s(61.5),s(61.5)), radius=s(5), outline=ink, width=s(4.8))
d.ellipse((s(24),s(25),s(32),s(33)), fill=ink)
d.line([(s(20),s(52)),(s(31),s(41)),(s(38),s(47)),(s(45),s(40)),(s(58),s(52))], fill=ink, width=s(4), joint='curve')

# Green check, sufficiently bold with a narrow white halo.
check = [(s(36.5),s(34.5)),(s(43.5),s(40.5)),(s(56.5),s(26.5))]
d.line(check, fill=white, width=s(10), joint='curve')
d.line(check, fill=green, width=s(6.5), joint='curve')
for x,y in check:
    d.ellipse((x-s(3.2),y-s(3.2),x+s(3.2),y+s(3.2)),fill=green)

icon_dir = BASE / 'cbers_autoselect'
im.resize((64,64), Image.Resampling.LANCZOS).save(icon_dir / 'icon.png')

# User preview compares actual raster sizes against a QGIS-style toolbar.
preview = Image.new('RGB',(510,190),(246,247,248))
pr = ImageDraw.Draw(preview)
pr.rectangle((12,13,498,92),fill=(236,239,241),outline=(202,208,212),width=2)
for x,size in [(40,16),(152,24),(276,32),(395,48)]:
    scaled = im.resize((size,size), Image.Resampling.LANCZOS)
    preview.paste(scaled,(x,30+(48-size)//2),scaled)
    pr.text((x,101),f'{size} px',fill=(53,60,67))
preview.save(BASE / 'icon_toolbar_preview.png')

# TS export: Qt Linguist-editable translation sources (not required at runtime).
root = ET.Element('TS', {'version':'2.1','language':'pt_BR','sourcelanguage':'en_US'})
context = ET.SubElement(root,'context')
ET.SubElement(context,'name').text = 'CBERSAutoSelect'
for key,english in STRINGS['en'].items():
    message=ET.SubElement(context,'message',{'id':key})
    ET.SubElement(message,'source').text=english
    ET.SubElement(message,'translation').text=STRINGS['pt_BR'][key]
ET.indent(root,space='  ')
ET.ElementTree(root).write(
    icon_dir / 'i18n' / 'cbers_autoselect_pt_BR.ts',
    encoding='utf-8',xml_declaration=True,
)
print('Built icons and Qt Linguist TS source.')
