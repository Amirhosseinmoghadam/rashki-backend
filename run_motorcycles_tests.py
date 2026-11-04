#!/usr/bin/env python3
"""Run motorcycles test modules in order, stopping only after the summary."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SETTINGS = os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings.development")
MODULES = [
    "test_models", "test_serializers", "test_views", "test_permissions", "test_urls",
]


def main():
    if not (ROOT / "manage.py").exists():
        print("Error: place this script beside manage.py", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = SETTINGS
    print(f"Using Django settings: {SETTINGS}", flush=True)
    check = subprocess.run([sys.executable, "manage.py", "check", f"--settings={SETTINGS}"], cwd=ROOT, env=env)
    if check.returncode:
        print("Django system check failed; no tests were executed.", file=sys.stderr)
        return check.returncode
    failures = []
    for module in MODULES:
        label = f"motorcycles.tests.{module}"
        print(f"\n===== {label} =====", flush=True)
        result = subprocess.run([sys.executable, "manage.py", "test", label, f"--settings={SETTINGS}", "--noinput"], cwd=ROOT, env=env)
        if result.returncode:
            failures.append(module)
    print("\nFailed modules:", failures if failures else "none", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
