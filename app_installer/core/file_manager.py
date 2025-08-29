import json
from pathlib import Path
from typing import List, Dict


def load_catalog(path: Path) -> Dict[str, List[Dict[str, str]]]:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def export_selection(path: Path, apps: List[Dict[str, str]]):
    with path.open('w', encoding='utf-8') as f:
        json.dump(apps, f, indent=2)


def import_selection(path: Path) -> List[Dict[str, str]]:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def save_backup(path: Path, apps: List[Dict[str, str]]):
    with path.open('w', encoding='utf-8') as f:
        json.dump(apps, f, indent=2)
