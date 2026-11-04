#!/usr/bin/env python3
"""Run pricing test modules independently without overriding Django settings."""
import os
import subprocess
import sys
from pathlib import Path

MODULES = ("test_rounding", "test_calculation", "test_models", "test_services", "test_activation", "test_batch", "test_admin")


def main():
    root = Path(__file__).resolve().parent
    os.chdir(root)
    settings = os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings.development")
    failures = []
    for module in MODULES:
        label = f"pricing.tests.{module}"
        print(f"\n===== {label} =====", flush=True)
        result = subprocess.run([sys.executable, "manage.py", "test", label, f"--settings={settings}", "--noinput"], check=False)
        if result.returncode:
            failures.append(module)
    print("\nFailed modules:", failures or "none")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
