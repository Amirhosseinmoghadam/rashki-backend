#!/usr/bin/env python3
"""Run article test modules sequentially with the project's actual settings."""
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings.development')
MODULES=['test_models','test_serializers','test_views','test_permissions','test_known_issues']
failed=[]
for module in MODULES:
    label=f'articles.tests.{module}'
    print(f'\n===== {label} =====',flush=True)
    result=subprocess.run([sys.executable,str(ROOT/'manage.py'),'test',label,'--noinput',f'--settings={os.environ["DJANGO_SETTINGS_MODULE"]}'],cwd=ROOT)
    if result.returncode:
        failed.append(module)
print('\nFailed modules:',failed or 'none')
sys.exit(bool(failed))
