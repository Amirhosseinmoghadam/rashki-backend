#!/usr/bin/env python3
"""Run wishlist test modules independently, preserving per-module results."""
import os
import subprocess
import sys
from pathlib import Path

MODULES = ["test_models", "test_selectors", "test_serializers", "test_views", "test_permissions", "test_urls"]
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
settings = os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings.development")
failed = []
for module in MODULES:
    print(f"\n===== wishlists.tests.{module} =====", flush=True)
    cmd = [sys.executable, "manage.py", "test", f"wishlists.tests.{module}",
           f"--settings={settings}", "--noinput"]
    code = subprocess.run(cmd, check=False).returncode
    if code: failed.append(module)
print("\nFailed modules:", failed if failed else "none")
sys.exit(1 if failed else 0)
