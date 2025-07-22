import subprocess
from pathlib import Path
from typing import List, Dict
from datetime import datetime

LOG_PATH = Path(__file__).resolve().parent.parent / 'logs' / 'install.log'


def is_winget_available() -> bool:
    try:
        subprocess.run(['winget', '--version'], capture_output=True, check=True)
        return True
    except Exception:
        return False


def log(message: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")


def install_app(app_id: str) -> subprocess.CompletedProcess:
    cmd = ['winget', 'install', '--id', app_id, '--silent', '--accept-package-agreements', '--accept-source-agreements']
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log(f"Installed {app_id}: {proc.returncode}")
    if proc.stdout:
        log(proc.stdout)
    if proc.stderr:
        log(proc.stderr)
    return proc


def install_apps(apps: List[Dict[str, str]]) -> List[subprocess.CompletedProcess]:
    results = []
    for app in apps:
        result = install_app(app['id'])
        results.append(result)
    return results
