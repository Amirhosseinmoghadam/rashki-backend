#!/usr/bin/env python3
"""Run each products test module and report all failures."""
import os
import subprocess
import sys
from pathlib import Path

MODULES = ['test_models', 'test_helpers', 'test_serializers', 'test_visibility', 'test_permissions', 'test_urls', 'test_images']
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
settings = os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings.development")
failures = []
for name in MODULES:
    print(f"\n===== products.tests.{name} =====", flush=True)
    command = [sys.executable, "manage.py", "test", f"products.tests.{name}",
               f"--settings={settings}", "--noinput"]
    result = subprocess.run(command, check=False)
    if result.returncode:
        failures.append(name)
print("\nFailed modules:", failures if failures else "none")
sys.exit(1 if failures else 0)
