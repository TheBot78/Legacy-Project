import json
from pathlib import Path
from backend.api import GwImportGEDRequest, import_ged

# Read GEDCOM text
ged_path = Path('data/Harry-Potter.ged')
ged_text = ged_path.read_text(encoding='utf-8')

# Call the endpoint function programmatically
req = GwImportGEDRequest(db_name='Harry-Potter', ged_text=ged_text, notes_origin_file=str(ged_path))
resp = import_ged(req)
print('resp ok:', resp.get('ok'))
print('db_dir:', resp.get('db_dir'))
print('gw_path:', resp.get('gw_path'))
print('gwf_path:', resp.get('gwf_path'))

# Verify files under backend/bases
base_dir = Path('backend/bases/Harry-Potter.gwb')
files = [
    'base.json','base.acc.json','strings.inx.json','names.inx.json',
    'nb_persons','particles.txt','snames.dat','fnames.dat','names.inx','names.acc','fnames.inx','strings.inx','base','base.acc'
]
missing = [f for f in files if not (base_dir / f).exists()]
print('missing:', missing)

# Show first lines of textual files
for show in ['particles.txt','snames.dat','fnames.dat']:
    p = base_dir / show
    if p.exists():
        head = '\n'.join(p.read_text(encoding='utf-8').splitlines()[:5])
        print(f'--- {show} head ---\n{head}')

# Check .gw and .gwf presence
gw = Path('backend/bases/Harry-Potter.gw')
gwf = Path('backend/bases/Harry-Potter.gwf')
print('gw exists:', gw.exists())
print('gwf exists:', gwf.exists())
# Print small head of gwf
if gwf.exists():
    print('gwf head:', '\n'.join(gwf.read_text(encoding='utf-8').splitlines()[:3]))

# Check counts from base.json
base_json = base_dir / 'base.json'
if base_json.exists():
    counts = json.loads(base_json.read_text(encoding='utf-8')).get('counts', {})
    print('base.json counts:', counts)