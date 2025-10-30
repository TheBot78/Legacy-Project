import os

BASE_DIR = "/host_files"

def safe_path(sel):
    abs_sel = os.path.abspath(sel)
    if not abs_sel.startswith(BASE_DIR):
        abs_sel = BASE_DIR
    return abs_sel

def list_dir(sel):
    abs_sel = safe_path(sel)
    items = []
    try:
        for name in os.listdir(abs_sel):
            path = os.path.join(abs_sel, name)
            items.append({
                "name": name,
                "is_dir": os.path.isdir(path),
                "path": path
            })
    except Exception:
        items = []
    parent = os.path.dirname(abs_sel) if abs_sel != BASE_DIR else None
    return abs_sel, items, parent