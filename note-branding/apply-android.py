import os, re, json, base64
from pathlib import Path
host = os.environ['RENDEZVOUS_SERVER'].strip()
key = os.environ['RS_PUB_KEY'].strip()
assert re.fullmatch(r'[A-Za-z0-9.-]+', host), 'RENDEZVOUS_SERVER mancante o non valido'
assert len(base64.b64decode(key, validate=True)) == 32, 'RS_PUB_KEY non valida'
p = Path('libs/hbb_common/src/config.rs')
s = p.read_text(encoding='utf-8')
s, n = re.subn(r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\[[^;]+;', 'pub const RENDEZVOUS_SERVERS: &[&str] = &[' + json.dumps(host) + '];', s)
assert n == 1, 'Costante server non trovata'
s, n = re.subn(r'pub const RS_PUB_KEY: &str = "[^"]*";', 'pub const RS_PUB_KEY: &str = ' + json.dumps(key) + ';', s)
assert n == 1, 'Costante chiave non trovata'
old = 'pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = Default::default();'
assert s.count(old) == 1, 'DEFAULT_SETTINGS non trovata'
entries = {'custom-rendezvous-server': host, 'key': key}
new = 'pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new({\n    let mut settings = HashMap::new();\n'
for k, v in entries.items():
    new += '    settings.insert(' + json.dumps(k) + '.to_owned(), ' + json.dumps(v) + '.to_owned());\n'
new += '    settings\n});'
s = s.replace(old, new)

old_hard = 'pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = Default::default();'
assert s.count(old_hard) == 1, 'HARD_SETTINGS non trovata'
hard = {'conn-type': 'incoming', 'disable-account': 'Y', 'disable-ab': 'Y'}
new_hard = 'pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new({\n    let mut settings = HashMap::new();\n'
for k, v in hard.items():
    new_hard += '    settings.insert(' + json.dumps(k) + '.to_owned(), ' + json.dumps(v) + '.to_owned());\n'
new_hard += '    settings\n});'
s = s.replace(old_hard, new_hard)
old_override = 'pub static ref OVERWRITE_SETTINGS: RwLock<HashMap<String, String>> = Default::default();'
assert s.count(old_override) == 1, 'OVERWRITE_SETTINGS non trovata'
s = s.replace(old_override, new.replace('DEFAULT_SETTINGS:', 'OVERWRITE_SETTINGS:'))

old_builtin = 'pub static ref BUILTIN_SETTINGS: RwLock<HashMap<String, String>> = Default::default();'
assert s.count(old_builtin) == 1, 'BUILTIN_SETTINGS non trovata'
s = s.replace(old_builtin, 'pub static ref BUILTIN_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new({ let mut settings = HashMap::new(); settings.insert("hide-network-settings".to_owned(), "Y".to_owned()); settings });')

p.write_text(s, encoding='utf-8')
print('DNS e chiave incorporati nei sorgenti:', host)

import sys
if '--config-only' in sys.argv:
    sys.exit(0)
from PIL import Image
assets=Path(__file__).resolve().parent
mark=Image.open(assets/'icon-note.png').convert('RGBA')
mark=mark.crop(mark.getbbox())
logo=Image.open(assets/'logo-note.png').convert('RGBA')
logo=logo.crop(logo.getbbox()); logo.thumbnail((1200,300),Image.Resampling.LANCZOS)
for name in ('logo.png','logo_light.png','logo_dark.png'):
    logo.save(Path('flutter/assets')/name)
res=Path('flutter/android/app/src/main/res')
for folder,scale in [('mdpi',1),('hdpi',1.5),('xhdpi',2),('xxhdpi',3),('xxxhdpi',4)]:
    dest=res/('mipmap-'+folder)
    dest.mkdir(exist_ok=True)
    for name,side,fraction in [('ic_launcher',48,.92),('ic_launcher_round',48,.92),('ic_launcher_foreground',108,.62)]:
        size=int(side*scale)
        canvas=Image.new('RGBA',(size,size),(0,0,0,0))
        im=mark.copy();im.thumbnail((int(size*fraction),int(size*fraction)),Image.Resampling.LANCZOS)
        canvas.alpha_composite(im,((size-im.width)//2,(size-im.height)//2))
        canvas.save(dest/(name+'.png'))
    # Monochrome notification symbol: white central NO/TE letters on transparency.
    original=Image.open(assets/'icon-note.png').convert('RGB').crop((300,315,700,715))
    alpha=original.convert('L').point(lambda x: max(0,min(255,(x-160)*3)))
    tray=Image.new('RGBA',original.size,'white');tray.putalpha(alpha)
    tray.resize((int(24*scale),int(24*scale)),Image.Resampling.LANCZOS).save(dest/'ic_stat_logo.png')
def patch(rel,old,new):
    p=Path(rel);s=p.read_text();assert old in s, rel+': testo atteso assente'
    p.write_text(s.replace(old,new))
patch('flutter/android/app/src/main/AndroidManifest.xml','android:label="RustDesk"','android:label="NO.TE Teleassistenza"')
patch('flutter/android/app/src/main/AndroidManifest.xml','android:label="RustDesk Input"','android:label="NO.TE Teleassistenza - Controllo"')
patch('flutter/android/app/src/main/res/values/strings.xml','RustDesk','NO.TE Teleassistenza')
patch('flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/MainService.kt','"RustDesk"','"NO.TE Teleassistenza"')
patch('flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/MainService.kt','"RustDesk Service"','"NO.TE Teleassistenza"')
patch('flutter/lib/mobile/pages/home_page.dart','return Text(bind.mainGetAppNameSync());',"return const Text('NO.TE Teleassistenza');")
# Open on the incoming screen instead of the empty chat page.
patch('flutter/lib/mobile/pages/home_page.dart','    initPages();\n  }','    initPages();\n    if (isAndroid && bind.isIncomingOnly()) _selectedIndex = 1;\n  }')
p=Path('flutter/lib/common.dart');s=p.read_text()
for key,color in [('accent','454545'),('button','454545'),('idColor','707070')]:
    s,n=re.subn(r'(static const Color '+key+r' = Color\()0x[0-9A-Fa-f]+(\);)',r'\g<1>0xFF'+color+r'\2',s)
    assert n==1,key
p.write_text(s)
# Keep native namespace/JNI identity; use a dedicated application ID per server.
client=os.environ['NOTE_CLIENT'].lower()
assert client in ('teleassistenza1','teleassistenza2')
patch('flutter/android/app/build.gradle','applicationId "com.carriez.flutter_hbb"','applicationId "it.notesolution.'+client+'"')
print('Branding Android NO.TE applicato:',client)

# NO.TE: explicit assistance consent, immediately actionable, without countdown.
p = Path('flutter/lib/mobile/pages/server_page.dart')
s = p.read_text(encoding='utf-8')
start = s.index('class ScamWarningDialogState extends State<ScamWarningDialog> {')
end = s.index('class ServerInfo extends StatelessWidget {', start)
original = s[start:end]
assert 'startCountdown();' in original and 'show-scam-warning' in original
replacement = r'''class ScamWarningDialogState extends State<ScamWarningDialog> {
  bool _dontShowAgain = false;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: Colors.white,
      title: const Text(
        'Avvia teleassistenza NO.TE',
        style: TextStyle(color: Color(0xFF202020), fontWeight: FontWeight.bold),
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Avviando la teleassistenza consenti al tecnico di vedere il tuo '
              'schermo e, se autorizzato, controllare il dispositivo.\n\n'
              'Procedi solo se hai richiesto assistenza a NO.TE Solution. '
              'Se una persona sconosciuta ti ha chiesto di avviare questa app, '
              'annulla e contatta NO.TE tramite i recapiti ufficiali.\n\n'
              'Puoi interrompere la sessione in qualsiasi momento.',
              style: TextStyle(color: Color(0xFF202020), fontSize: 16),
            ),
            const SizedBox(height: 16),
            CheckboxListTile(
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
              activeColor: const Color(0xFF454545),
              checkColor: Colors.white,
              title: const Text('Non visualizzare più',
                  style: TextStyle(color: Color(0xFF202020))),
              value: _dontShowAgain,
              onChanged: (value) {
                setState(() { _dontShowAgain = value ?? false; });
              },
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          style: TextButton.styleFrom(foregroundColor: const Color(0xFF454545)),
          onPressed: () { Navigator.of(context).pop(); },
          child: const Text('Annulla'),
        ),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF454545),
            foregroundColor: Colors.white,
          ),
          onPressed: () {
            if (_dontShowAgain) {
              bind.mainSetLocalOption(key: 'show-scam-warning', value: 'N');
            }
            final serverModel = widget.serverModel;
            Navigator.of(context).pop();
            serverModel.toggleService();
          },
          child: const Text('Avvia assistenza'),
        ),
      ],
    );
  }
}

'''
p.write_text(s[:start] + replacement + s[end:], encoding='utf-8')
print('Conferma NO.TE applicata: avvio immediato senza timer, consenso mantenuto.')

# Reuse the upstream password/authentication menu and dialog.
p = Path('flutter/lib/mobile/pages/server_page.dart')
s = p.read_text(encoding='utf-8')
assert s.count('_DropDownAction') == 3
s = s.replace('_DropDownAction', 'NoteSecurityAction')
p.write_text(s, encoding='utf-8')
p = Path('flutter/lib/mobile/pages/settings_page.dart')
s = p.read_text(encoding='utf-8')
anchor = "import 'scan_page.dart';"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + "\nimport 'server_page.dart' show NoteSecurityAction;")
anchor = '        SettingsSection(title: Text(translate("Settings")), tiles: ['
assert s.count(anchor) == 1
section = '''        if (isAndroid && !outgoingOnly)
          SettingsSection(
            title: const Text('Sicurezza'),
            tiles: [
              SettingsTile(
                title: const Text('Password permanente'),
                leading: const Icon(Icons.lock_outline),
                onPressed: (context) { setPasswordDialog(); },
              ),
              SettingsTile(
                title: const Text('Modalità di autenticazione'),
                description: const Text('Apri il menu a destra per scegliere password, conferma manuale o entrambe.'),
                leading: const Icon(Icons.security),
                trailing: NoteSecurityAction(),
              ),
            ],
          ),
'''
s = s.replace(anchor, section + anchor)
p.write_text(s, encoding='utf-8')
print('Sicurezza Android abilitata; impostazioni di rete nascoste.')
