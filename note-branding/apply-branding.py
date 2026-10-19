from pathlib import Path
import re, plistlib
from PIL import Image
ROOT=Path.cwd()
ASSETS=Path(__file__).resolve().parent
im=Image.open(ASSETS/'logo-note.png').convert('RGBA')
logo=im.crop(im.getbbox());logo.thumbnail((1200,300),Image.Resampling.LANCZOS)
for name in ('logo.png','logo_light.png','logo_dark.png'):
 logo.save(ROOT/'flutter/assets'/name)
# Preserve the complete supplied icon and its transparency.
mark=Image.open(ASSETS/'icon-note.png').convert('RGBA')
mark.thumbnail((1024,1024),Image.Resampling.LANCZOS)
icon=Image.new('RGBA',(1024,1024),(0,0,0,0))
icon.alpha_composite(mark,((1024-mark.width)//2,(1024-mark.height)//2))
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
old='constraints: BoxConstraints(maxWidth: 300, maxHeight: 60),'
assert s.count(old)==1,'Logo layout source changed'
s=s.replace(old,'constraints: BoxConstraints(maxWidth: 170, maxHeight: 40),')
p.write_text(s)
p=ROOT/'flutter/macos/Runner/Info.plist'
with p.open('rb') as f:info=plistlib.load(f)
info['CFBundleDisplayName']='NO.TE Teleassistenza'
with p.open('wb') as f:plistlib.dump(info,f,sort_keys=False)
print('Branding NO.TE applicato; identificativi, servizio e autenticazione invariati.')
