import subprocess
from typing import List, Dict


def list_installed_apps(user_only: bool = True) -> List[Dict[str, str]]:
    cmd = ['winget', 'list']
    if user_only:
        cmd.append('--source=winget')
    proc = subprocess.run(cmd, capture_output=True, text=True)
    apps = []
    for line in proc.stdout.splitlines()[2:]:
        parts = line.split()
        if len(parts) >= 3:
            app_id = parts[-1]
            name = ' '.join(parts[:-2])
            apps.append({'name': name, 'id': app_id})
    return apps
