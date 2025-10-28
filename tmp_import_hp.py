from pathlib import Path
from backend.ged_parser import parse_ged_text
from backend.storage import write_gwb, write_gw, write_gwf

db_name = "Harry-Potter"
root = Path("bases")
root.mkdir(exist_ok=True)

with open("data/Harry-Potter.ged", encoding="utf-8") as f:
    ged_text = f.read()

parsed = parse_ged_text(ged_text)
persons = parsed["persons"]
families = parsed["families"]

notes_origin = "data/Harry-Potter.ged"

db_dir = write_gwb(root, db_name, persons, families, notes_origin)
gw_path = write_gw(root, db_name, persons, families)
gwf_path = write_gwf(root, db_name)

print(f"db_dir={db_dir}")
print(f"gw_path={gw_path}")
print(f"gwf_path={gwf_path}")
