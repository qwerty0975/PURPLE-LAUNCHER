import os
from datetime import datetime
from config import PATCH_INFO

def parse_preset(path):
    result = {"engine": "", "iwad": "", "mod": "", "map": ""}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    if key in result and not result[key]:
                        result[key] = value
    except Exception:
        pass
    return result

def preview_presets(paths, root):
    previews = []
    for path in paths:
        if not path or not os.path.isfile(path):
            previews.append(f"Missing: {os.path.relpath(path, root)}")
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            header = f"--- {os.path.relpath(path, root)} ---"
            previews.append(header + "\n" + content)
        except Exception as e:
            previews.append(f"Failed to read {os.path.basename(path)}: {e}")
    return "\n\n".join(previews)

def save_preset(path, engine, iwad, mod, mapf):
    header = [
        "# Purple Launcher preset",
        f"# Created: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')}",
        f"# VERSION: {PATCH_INFO['version']}",
        "[PRESET]",
        f"name={os.path.splitext(os.path.basename(path))[0]}",
        f"engine={engine or ''}",
        f"iwad={iwad or ''}",
        f"mod={mod or ''}",
        f"map={mapf or ''}"
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(header) + "\n")