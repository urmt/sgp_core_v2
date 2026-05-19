#!/usr/bin/env python3
import os, json, pickle, hashlib
from pathlib import Path
from datetime import datetime

ROOT = Path("STRICT_STATE")
ROOT.mkdir(exist_ok=True)
REGISTRY_FILE = ROOT / "STATE_REGISTRY.json"

def sha256_bytes(b): return hashlib.sha256(b).hexdigest()

def load_registry():
    if not REGISTRY_FILE.exists(): return {}
    with open(REGISTRY_FILE, "r") as f: return json.load(f)
def save_registry(reg):
    with open(REGISTRY_FILE, "w") as f: json.dump(reg, f, indent=2)

def save_object(name, obj, category="general"):
    registry = load_registry()
    cat_dir = ROOT / category
    cat_dir.mkdir(exist_ok=True)
    path = cat_dir / f"{name}.pkl"
    raw = pickle.dumps(obj)
    with open(path, "wb") as f: f.write(raw)
    h = sha256_bytes(raw)
    registry[name] = {"name":name,"category":category,"path":str(path),"sha256":h,"timestamp":datetime.utcnow().isoformat()+"Z","canonical":True,"duplicate_allowed":False}
    save_registry(registry)
    print(f"[SAVED] {name} @ {path}")
    print(f"         SHA256={h}")
    return path

def load_object(name):
    registry = load_registry()
    if name not in registry: raise KeyError(f"OBJECT NOT FOUND: {name}")
    meta = registry[name]
    path = Path(meta["path"])
    if not path.exists(): raise FileNotFoundError(f"MISSING FILE: {path}")
    with open(path, "rb") as f: raw = f.read()
    actual = sha256_bytes(raw)
    if actual != meta["sha256"]: raise RuntimeError(f"HASH FAILURE: expected {meta['sha256']}, got {actual}")
    print(f"[LOADED] {name} (verified)")
    return pickle.loads(raw)

def list_objects():
    registry = load_registry()
    print("="*60)
    print("STRICT STATE REGISTRY")
    print("="*60)
    if not registry: print("NO OBJECTS")
    for name, meta in sorted(registry.items()):
        print(f"\n{name}")
        print(f"  category: {meta['category']}")
        print(f"  hash: {meta['sha256'][:16]}...")

if __name__ == "__main__":
    print("="*60)
    print("STRICT 1SCRIPT STATE MANAGER")
    print("="*60)
    example = {"phase":"V2_079","lda_auc":0.905,"gate_pass_rate":0.76,"finding":"gate destroys separable info"}
    save_object("phase2_results", example, "research")
    restored = load_object("phase2_results")
    print("\nRESTORED:", restored)
    print()
    list_objects()