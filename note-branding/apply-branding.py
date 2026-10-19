from pathlib import Path
import re, plistlib
from PIL import Image
ROOT=Path.cwd()
ASSETS=Path(__file__).resolve().parent
im=Image.open(ASSETS/'logo-note.png').convert('RGBA')
logo=im.crop(im.getbbox());logo.thumbnail((1200,300),Image.Resampling.LANCZOS)
for name in ('logo.png','logo_light.png','logo_dark.png'):
 logo.save(ROOT/'flutter/assets'/name)
# Small icon uses the first letter of the supplied mark, without redrawing it.
letter=im.crop((195,263,372,440));letter=letter.crop(letter.getbbox())
letter.thumbnail((660,660),Image.Resampling.LANCZOS)
icon=Image.new('RGBA',(1024,1024),(255,255,255,255))
icon.alpha_composite(letter,((1024-letter.width)//2,(1024-letter.height)//2))
for rel in ('res/icon.png','res/mac-icon.png','flutter/assets/icon.png'):icon.save(ROOT/rel)
for rel in ('res/icon.ico','flutter/windows/runner/resources/app_icon.ico'):
 icon.save(ROOT/rel,format='ICO',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
icon.save(ROOT/'flutter/macos/Runner/AppIcon.icns',format='ICNS')
# Only presentation strings: retain app identifiers, executables and service names.
p=ROOT/'flutter/lib/common.dart';s=p.read_text()
old='String getWindowName({WindowType? overrideType}) {\n  final name = bind.mainGetAppNameSync();'
assert s.count(old)==1,'Window title source changed'
s=s.replace(old,"String getWindowName({WindowType? overrideType}) {\n  const name = 'NO.TE Teleassistenza';")
for key,color in [('accent','454545'),('button','454545'),('idColor','707070')]:
 s,count=re.subn(r'(static const Color '+key+r' = Color\()0x[0-9A-Fa-f]+(\);)',r'\g<1>0xFF'+color+r'\2',s)
 assert count==1,'Color source changed: '+key
p.write_text(s)
p=ROOT/'flutter/lib/desktop/pages/desktop_home_page.dart';s=p.read_text()
old='      buildTip(context),';assert s.count(old)==1
s=s.replace(old,"""      const Padding(
        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        child: Text('NO.TE Teleassistenza',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
      ),
      buildTip(context),""")
p.write_text(s)
p=ROOT/'flutter/macos/Runner/Info.plist'
with p.open('rb') as f:info=plistlib.load(f)
info['CFBundleDisplayName']='NO.TE Teleassistenza'
with p.open('wb') as f:plistlib.dump(info,f,sort_keys=False)
print('Branding NO.TE applicato; identificativi, servizio e autenticazione invariati.')
