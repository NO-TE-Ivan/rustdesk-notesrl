from pathlib import Path
import re, plistlib, io, struct
from PIL import Image
ROOT=Path.cwd()
ASSETS=Path(__file__).resolve().parent
im=Image.open(ASSETS/'logo-note.png').convert('RGBA')
logo=im.crop(im.getbbox());logo.thumbnail((1200,300),Image.Resampling.LANCZOS)
for name in ('logo.png','logo_light.png','logo_dark.png'):
 logo.save(ROOT/'flutter/assets'/name)
# Large icons: remove empty border, keeping the complete circular mark.
mark=Image.open(ASSETS/'icon-note.png').convert('RGBA')
mark=mark.crop(mark.getbbox())
mark.thumbnail((950,950),Image.Resampling.LANCZOS)
icon=Image.new('RGBA',(1024,1024),(0,0,0,0))
icon.alpha_composite(mark,((1024-mark.width)//2,(1024-mark.height)//2))
# Small icons: only the central NO / TE lettering, without the circular motto.
source=Image.open(ASSETS/'icon-note.png').convert('RGBA')
assert source.size==(1002,1024), 'Unexpected source icon dimensions'
small=source.crop((300,315,700,715)).resize((256,256),Image.Resampling.LANCZOS)
small.save(ROOT/'flutter/assets/icon.png')
for rel in ('res/icon.png','res/mac-icon.png'):icon.save(ROOT/rel)
# ICO directory with a separate optimized image for each small size.
def save_ico(path):
 sizes=[16,20,24,32,48,64,128,256]
 blocks=[]
 for size in sizes:
  buf=io.BytesIO()
  (small if size<=32 else icon).resize((size,size),Image.Resampling.LANCZOS).save(buf,format='PNG')
  blocks.append(buf.getvalue())
 offset=6+16*len(sizes)
 header=struct.pack('<HHH',0,1,len(sizes))
 for size,block in zip(sizes,blocks):
  header+=struct.pack('<BBBBHHII',size%256,size%256,0,0,1,32,len(block),offset)
  offset+=len(block)
 path.write_bytes(header+b''.join(blocks))
for rel in ('res/icon.ico','res/tray-icon.ico','flutter/windows/runner/resources/app_icon.ico','flutter/assets/icon.ico'):
 save_ico(ROOT/rel)
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

# Windows presentation names; retain the service/configuration identity.
def patch_file(rel, replacements):
 p=ROOT/rel
 s=p.read_text(encoding='utf-8')
 for old,new,count in replacements:
  assert s.count(old)==count, f'{rel}: expected {count} occurrences of {old!r}, got {s.count(old)}'
  s=s.replace(old,new)
 p.write_text(s,encoding='utf-8')

patch_file('flutter/lib/desktop/pages/desktop_setting_page.dart', [
 ('const Color _accentColor = MyTheme.accent;', 'Color _settingsAccent(BuildContext context) => Theme.of(context).brightness == Brightness.dark\n    ? const Color(0xFFF2F2F2) : const Color(0xFF303030);', 1),
 ('style: const TextStyle(\n        color: _accentColor,', 'style: TextStyle(\n        color: _accentColor,', 1),
 ('_accentColor', '_settingsAccent(context)', 5),
 ("_Card(title: translate('About RustDesk')", "_Card(title: 'NO.TE Teleassistenza'", 1),
])
patch_file('flutter/windows/runner/Runner.rc', [
 ('"Purslane Tech Pte. Ltd."', '"NO.TE Solution"', 1),
 ('"RustDesk Remote Desktop"', '"NO.TE Teleassistenza"', 1),
 ('"ProductName", "RustDesk"', '"ProductName", "NO.TE Teleassistenza"', 1),
])
for rel in ('build.rs','libs/portable/build.rs'):
 patch_file(rel, [('let mut res = winres::WindowsResource::new();',
  'let mut res = winres::WindowsResource::new();\n        res.set("FileDescription", "NO.TE Teleassistenza")\n            .set("ProductName", "NO.TE Teleassistenza")\n            .set("CompanyName", "NO.TE Solution");',1)])

p=ROOT/'src/platform/windows.rs'
s=p.read_text()
# Public shortcut names, including their uninstall cleanup.
s=s.replace('{app_name}.lnk', 'NO.TE Teleassistenza.lnk')
s=s.replace('Uninstall NO.TE Teleassistenza.lnk', 'Disinstalla NO.TE Teleassistenza.lnk')
s=s.replace('{app_name} Tray.lnk', 'NO.TE Teleassistenza Tray.lnk')
s=s.replace('embedded_tray_shortcut_commands(&app_name,', 'embedded_tray_shortcut_commands("NO.TE Teleassistenza",')
# Two positional arguments supply the Start-menu folder and desktop shortcut.
old='crate::get_app_name()\n    );\n    let exe = format!'
assert s.count(old)==1
s=s.replace(old,'"NO.TE Teleassistenza"\n    );\n    let exe = format!')
old='tmp_path,\n            crate::get_app_name()'
assert s.count(old)==1
s=s.replace(old,'tmp_path,\n            "NO.TE Teleassistenza"')
s=s.replace('/v DisplayName /t REG_SZ /d \\"{app_name}\\"', '/v DisplayName /t REG_SZ /d \\"NO.TE Teleassistenza\\"')
s=s.replace('/v Publisher /t REG_SZ /d \\"{app_name}\\"', '/v Publisher /t REG_SZ /d \\"NO.TE Solution\\"')
s=s.replace('DisplayName= \\"{app_name} Service\\"','DisplayName= \\"NO.TE Teleassistenza Service\\"')
# Remove named format arguments whose visible labels are now constants.
s=s.replace('        uninstall_amyuni_idd=get_uninstall_amyuni_idd(),\n        app_name = crate::get_app_name(),',
            '        uninstall_amyuni_idd=get_uninstall_amyuni_idd(),')
s=s.replace('", app_name = crate::get_app_name())', '")')
assert '/v DisplayName /t REG_SZ /d \\"NO.TE Teleassistenza\\"' in s
p.write_text(s)
# The custom ICO must be used by both the installer and the installed app.
patch_file('src/platform/windows.rs', [
 ('if crate::is_custom_client() {\n        if let Some(p) = PathBuf::from(exe).parent() {',
  '{\n        if let Some(p) = PathBuf::from(exe).parent() {',1),
])
p=ROOT/'src/tray.rs';s=p.read_text()
a=s.index('    let tooltip = |count: usize| {');b=s.index('    let mut _tray_icon',a)
s=s[:a]+s[a:b].replace('crate::get_app_name()', '"NO.TE Teleassistenza"')+s[b:]
p.write_text(s)
print('Branding V3 applicato: icone, nomi visibili Windows, contrasto impostazioni.')
