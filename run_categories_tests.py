"""Run category test modules individually, then summarize any failures."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SETTINGS = os.environ.get('DJANGO_SETTINGS_MODULE', 'core.settings.development')
MODULES = ['test_models', 'test_serializers', 'test_views', 'test_permissions', 'test_commands']


def main():
    if not (ROOT / 'manage.py').is_file():
        print('ERROR: Place run_categories_tests.py beside manage.py', file=sys.stderr)
        return 2
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = SETTINGS
    print(f'Using Django settings: {SETTINGS}', flush=True)
    check = subprocess.run([sys.executable, 'manage.py', 'check', f'--settings={SETTINGS}'], cwd=ROOT, env=env)
    if check.returncode:
        return check.returncode
    failures = []
    for name in MODULES:
        print(f'\n===== categories.tests.{name} =====', flush=True)
        result = subprocess.run([sys.executable, 'manage.py', 'test', f'categories.tests.{name}',
                                 f'--settings={SETTINGS}', '--noinput'], cwd=ROOT, env=env)
        if result.returncode:
            failures.append(name)
    print(f'\nFailed modules: {failures or "none"}', flush=True)
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
