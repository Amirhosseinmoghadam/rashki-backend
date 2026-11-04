#!/usr/bin/env python3
"""Run each discounts test module separately and report failures."""
import os
import subprocess
import sys
from pathlib import Path

MODULES = ["test_models", "test_serializers", "test_services", "test_usage", "test_views", "test_permissions"]
ROOT = Path(__file__).resolve().parent
SETTINGS = os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings.development")


def main():
    if not (ROOT / "manage.py").exists():
        print("ERROR: Put run_discounts_tests.py beside manage.py", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = SETTINGS
    print(f"Using Django settings: {SETTINGS}", flush=True)
    check = subprocess.run([sys.executable, str(ROOT / "manage.py"), "check", f"--settings={SETTINGS}"],
                           cwd=ROOT, env=env)
    if check.returncode:
        print("Django system check failed; tests were not started.", file=sys.stderr)
        return check.returncode
    failures = []
    for module in MODULES:
        label = f"discounts.tests.{module}"
        print(f"\n===== {label} =====", flush=True)
        result = subprocess.run([sys.executable, str(ROOT / "manage.py"), "test", label,
                                 f"--settings={SETTINGS}", "--noinput"], cwd=ROOT, env=env)
        if result.returncode:
            failures.append(module)
    print("\nFailed modules:", failures if failures else "none")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
