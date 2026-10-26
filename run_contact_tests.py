#!/usr/bin/env python3
"""Execute contact test modules one by one and report failures."""
import os
import subprocess
import sys
from pathlib import Path

MODULES = ("test_models","test_serializers","test_views","test_permissions","test_throttles","test_admin")

def main():
    root=Path(__file__).resolve().parent
    if not (root/"manage.py").is_file():
        print("ERROR: place this script next to manage.py",file=sys.stderr)
        return 2
    settings=os.environ.get("DJANGO_SETTINGS_MODULE","core.settings.development")
    failed=[]
    for module in MODULES:
        print(f"\n===== contact.tests.{module} =====",flush=True)
        cmd=[sys.executable,str(root/"manage.py"),"test",f"contact.tests.{module}",f"--settings={settings}","--noinput"]
        result=subprocess.run(cmd,cwd=root)
        if result.returncode:
            failed.append(module)
    print("\nFailed modules:",failed or "none")
    return 1 if failed else 0

if __name__=="__main__":
    raise SystemExit(main())
