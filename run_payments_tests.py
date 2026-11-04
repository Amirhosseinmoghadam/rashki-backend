#!/usr/bin/env python3
"""Run payments test modules independently, preserving failures and summaries."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

MODULES = [
    'test_payment_models_contract',
    'test_payment_serializers_contract',
    'test_payment_registry',
    'test_payment_urls',
    'test_payment_permissions',
    'test_payment_service_units',
    'test_payment_tcart_security',
]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--settings',default=os.environ.get('DJANGO_SETTINGS_MODULE','core.settings.development'))
    parser.add_argument('--include-existing',action='store_true',help='Also discover and run all other payments tests')
    args=parser.parse_args()
    os.chdir(Path(__file__).resolve().parent)
    failures=[]
    for name in MODULES:
        label='payments.tests.'+name
        print('\n===== '+label+' =====',flush=True)
        rc=subprocess.call([sys.executable,'manage.py','test',label,'--settings='+args.settings,'--noinput'])
        if rc: failures.append(label)
    if args.include_existing:
        print('\n===== FULL payments.tests DISCOVERY =====',flush=True)
        rc=subprocess.call([sys.executable,'manage.py','test','payments.tests','--settings='+args.settings,'--noinput'])
        if rc: failures.append('payments.tests')
    print('\nFailed modules:',failures or 'none',flush=True)
    return 1 if failures else 0

if __name__=='__main__':
    raise SystemExit(main())
