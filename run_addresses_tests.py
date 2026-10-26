#!/usr/bin/env python3
"""Run each addresses test module using this project's Django settings."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

MODULES = (
    'test_models', 'test_serializers', 'test_selectors', 'test_services',
    'test_views', 'test_permissions', 'test_commands',
)
DEFAULT_SETTINGS = 'core.settings.development'


def main():
    parser = argparse.ArgumentParser(description='Run the addresses test suite module-by-module.')
    parser.add_argument('--settings', default=None, help='Django settings module (default: core.settings.development)')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manage = root / 'manage.py'
    if not manage.is_file():
        parser.error('Put this script next to manage.py in the Backend directory.')

    env = os.environ.copy()
    settings_name = args.settings or env.get('DJANGO_SETTINGS_MODULE') or DEFAULT_SETTINGS
    env['DJANGO_SETTINGS_MODULE'] = settings_name
    print(f'Using Django settings: {settings_name}', flush=True)

    preflight = subprocess.run([sys.executable, str(manage), 'check'], cwd=root, env=env)
    if preflight.returncode:
        print('Django preflight failed; tests were not run.', file=sys.stderr)
        print('Check settings dependencies and DATABASES, or pass --settings MODULE.', file=sys.stderr)
        return preflight.returncode

    failures = []
    for module in MODULES:
        print(f'\n===== addresses.tests.{module} =====', flush=True)
        result = subprocess.run([
            sys.executable, str(manage), 'test', f'addresses.tests.{module}', '--noinput',
        ], cwd=root, env=env)
        if result.returncode:
            failures.append(module)

    print('\nFailed modules:', ', '.join(failures) if failures else 'none')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
