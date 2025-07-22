import subprocess
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass


@dataclass
class InstallResult:
    name: str
    id: str
    returncode: int
    stdout: str
    stderr: str
    start: datetime
    end: datetime

    @property
    def duration(self) -> float:
        return (self.end - self.start).total_seconds()

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


def install_app(app: Dict[str, str]) -> InstallResult:
    start = datetime.now()
    cmd = [
        'winget',
        'install',
        '--id',
        app['id'],
        '--silent',
        '--accept-package-agreements',
        '--accept-source-agreements',
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    end = datetime.now()

    log(f"Installed {app['id']}: {proc.returncode}")
    if proc.stdout:
        log(proc.stdout)
    if proc.stderr:
        log(proc.stderr)

    return InstallResult(
        name=app.get('name', ''),
        id=app['id'],
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        start=start,
        end=end,
    )


def install_apps(apps: List[Dict[str, str]]) -> List[InstallResult]:
    results: List[InstallResult] = []
    for app in apps:
        result = install_app(app)
        results.append(result)
    return results
