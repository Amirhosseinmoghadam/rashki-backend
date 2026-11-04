#!/usr/bin/env python3
"""Run order test modules one by one; retain existing regression tests."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

MODULES = [
    'test_serializers',
    'test_order_number',
    'test_checkout_validation',
    'test_selectors',
    'test_commands',
    'test_api_contract',
    'test_urls',
    'test_cancellation_api',
    'test_postgres_locking',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--settings', default=os.environ.get('DJANGO_SETTINGS_MODULE', 'core.settings.development'))
    parser.add_argument('--include', nargs='*', help='Run only selected test modules (without test_ prefix permitted)')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if not (root / 'manage.py').exists():
        parser.error('Put this script beside manage.py in the project root.')
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = args.settings
    modules = MODULES if args.include is None else [x if x.startswith('test_') else 'test_' + x for x in args.include]
    failed = []
    for module in modules:
        path = root / 'orders' / 'tests' / (module + '.py')
        if not path.exists():
            print(f'\nMISSING: {path}', flush=True)
            failed.append(module)
            continue
        label = f'orders.tests.{module}'
        print(f'\n===== {label} =====', flush=True)
        result = subprocess.run([sys.executable, str(root / 'manage.py'), 'test', label, f'--settings={args.settings}', '--noinput'], cwd=root, env=env)
        if result.returncode:
            failed.append(module)
    print('\nFailed modules:', failed if failed else 'none')
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(main())
