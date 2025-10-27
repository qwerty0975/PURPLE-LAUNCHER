import os

def classify_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".exe":
        return "engine"
    elif ext == ".pk3":
        return "mod"
    elif ext == ".wad":
        return "wad"
    elif ext == ".zip":
        return "map"
    return None