import subprocess
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass

# Intentar importar rich.progress si está disponible
try:
    from rich.progress import Progress
    _RICH_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    _RICH_AVAILABLE = False


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


def install_app(app: Dict[str, str], interactive: bool = False) -> InstallResult:
    """
    Instala una aplicación usando winget.

    Si `interactive` es True, permite interacción en terminal y no captura salida.
    De lo contrario, se usa instalación silenciosa y se capturan stdout/stderr.
    """
    start = datetime.now()
    cmd = [
        'winget',
        'install',
        '--id',
        app['id'],
    ]

    if not interactive:
        cmd.append('--silent')
    cmd.extend([
        '--accept-package-agreements',
        '--accept-source-agreements',
    ])

    if interactive:
        proc = subprocess.run(cmd, text=True)
        stdout = proc.stdout or ''
        stderr = proc.stderr or ''
    else:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        stdout = proc.stdout
        stderr = proc.stderr

    end = datetime.now()

    log(f"Installed {app['id']}: {proc.returncode}")
    if stdout:
        log(stdout)
    if stderr:
        log(stderr)

    return InstallResult(
        name=app.get('name', ''),
        id=app['id'],
        returncode=proc.returncode,
        stdout=stdout,
        stderr=stderr,
        start=start,
        end=end,
    )


def install_apps(
    apps: List[Dict[str, str]],
    show_progress: bool = False,
    interactive: bool = False,
) -> List[InstallResult]:
    """
    Instala múltiples aplicaciones. Si show_progress es True y rich está disponible,
    se muestra una barra de progreso.
    """
    results: List[InstallResult] = []

    if show_progress and _RICH_AVAILABLE:
        with Progress() as progress:
            task = progress.add_task("Instalando", total=len(apps))
            for app in apps:
                progress.update(task, description=f"Instalando {app.get('name', app['id'])}")
                result = install_app(app, interactive=interactive)
                results.append(result)
                progress.advance(task)
    else:
        for idx, app in enumerate(apps, start=1):
            if show_progress:
                print(f"[{idx}/{len(apps)}] Instalando {app.get('name', app['id'])}")
            result = install_app(app, interactive=interactive)
            results.append(result)

    return results
