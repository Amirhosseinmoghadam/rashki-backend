#!/usr/bin/env python3
"""Run brands test modules one by one, continuing after individual failures."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
settings = os.environ.get('DJANGO_SETTINGS_MODULE', 'core.settings.development')
os.environ['DJANGO_SETTINGS_MODULE'] = settings
modules = ['test_models', 'test_serializers', 'test_views', 'test_permissions', 'test_admin']

print(f'Using Django settings: {settings}', flush=True)
check = subprocess.run([sys.executable, 'manage.py', 'check', f'--settings={settings}'])
if check.returncode:
    sys.exit(check.returncode)

failed = []
for name in modules:
    print(f'\n===== brands.tests.{name} =====', flush=True)
    result = subprocess.run([
        sys.executable, 'manage.py', 'test', f'brands.tests.{name}',
        f'--settings={settings}', '--noinput',
    ])
    if result.returncode:
        failed.append(name)
print('\nFailed modules:', ', '.join(failed) if failed else 'none', flush=True)
sys.exit(1 if failed else 0)
