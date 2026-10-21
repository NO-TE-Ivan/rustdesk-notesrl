from pathlib import Path
import runpy, plistlib
from PIL import Image

root = Path.cwd()
assets = Path(__file__).resolve().parent
runpy.run_path(str(assets / 'apply-branding.py'), run_name='__main__')

p = root / 'flutter/macos/Runner/Info.plist'
with p.open('rb') as f:
    info = plistlib.load(f)
info['CFBundleDisplayName'] = 'NO.TE Teleassistenza'
info['CFBundleName'] = 'NO.TE Teleassistenza'
with p.open('wb') as f:
    plistlib.dump(info, f, sort_keys=False)

# macOS template icons use alpha, not the colour of the square background.
small = Image.open(root / 'flutter/assets/icon.png').convert('RGBA')
mask = small.convert('L').point(lambda x: max(0, min(255, (x - 175) * 255 // 70)))
tray = Image.new('RGBA', small.size, (0, 0, 0, 0))
tray.putalpha(mask)
tray = tray.resize((32, 32), Image.Resampling.LANCZOS)
tray.save(root / 'flutter/assets/note-tray.png')
tray.save(root / 'res/mac-tray-dark-x2.png')
p = root / 'src/tray.rs'
s = p.read_text()
old = '../Frameworks/App.framework/Resources/flutter_assets/assets/icon.png'
assert s.count(old) == 1, 'macOS tray resource path changed'
s = s.replace(old, '../Frameworks/App.framework/Resources/flutter_assets/assets/note-tray.png')
p.write_text(s)
print('macOS: branding V3, nome visualizzato e icona menu applicati.')
