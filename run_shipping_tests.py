#!/usr/bin/env python3
"""Run shipping test modules independently and report failures."""
import os
import subprocess
import sys
from pathlib import Path

MODULES = [
    "test_service_values",
    "test_provider_registry",
    "test_packaging",
    "test_manual_tariff",
    "test_tipax_payload_helpers",
    "test_contracts",
]


def main():
    root = Path(__file__).resolve().parent
    os.chdir(root)
    settings = os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings.development")
    failures = []
    for filename in MODULES:
        label = f"shipping.tests.{filename}"
        print(f"\n===== {label} =====", flush=True)
        result = subprocess.run([sys.executable, str(root / "manage.py"), "test", label,
                                 f"--settings={settings}", "--noinput"], check=False)
        if result.returncode:
            failures.append(filename)
    print("\nFailed modules:", failures or "none", flush=True)
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
