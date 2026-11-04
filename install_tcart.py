"""Safely install the TCart hooks into the existing rashki-backend.

Run from the project root: python install_tcart.py [--dry-run]
Provider and reconciliation command are distributed separately in the original package.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
MARK = 'TCART_HMAC_GUARD_V2'
PENDING_MARK = 'TCART_PRESERVE_PENDING_V2'
SETTINGS_MARK = 'TCART_CALLBACK_SETTINGS_V2'


class InstallError(RuntimeError):
    pass


def locate_method(source: str, cls: str, meth: str) -> ast.FunctionDef:
    tree = ast.parse(source)
    classes = [x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == cls]
    if len(classes) != 1:
        raise InstallError(f'Expected exactly one class {cls}')
    methods = [x for x in classes[0].body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x.name == meth]
    if len(methods) != 1 or not isinstance(methods[0], ast.FunctionDef):
        raise InstallError(f'Expected exactly one synchronous method {cls}.{meth}')
    return methods[0]


def patch_view(s: str) -> str:
    if MARK in s:
        return s
    m = locate_method(s, 'TCartCallbackAPIView', 'post')
    section = '\n'.join(s.splitlines()[m.lineno - 1:m.end_lineno])
    if 'process_payment_callback' not in section or 'public_id' not in section:
        raise InstallError('TCart callback method has unexpected structure; will not edit')
    if 'verify_callback_signature' in section:
        raise InstallError('Callback has custom signature validation; refusing to duplicate')
    # Insert after method signature (or docstring), before any existing logic.
    first = m.body[0]
    idx = first.end_lineno if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str) else first.lineno - 1
    block = '''        # TCART_HMAC_GUARD_V2: authenticate signed provider webhook before DB mutation.
        from payments.providers.tcart import TCartProvider

        payload = request.data
        if not isinstance(payload, dict):
            return Response({"success": False, "message": "Invalid TCart payload"}, status=400)
        if not TCartProvider.verify_callback_signature(
            payload,
            request.headers.get("X-Resid-Signature", ""),
            getattr(settings, "TCART_CALLBACK_SECRET", ""),
        ):
            return Response({"success": False, "message": "Invalid TCart signature"}, status=403)
        if payload.get("event") != "payment.confirmed" or payload.get("status") != "paid":
            return Response({"success": False, "message": "Unexpected TCart event"}, status=400)
        if not PaymentAttempt.objects.filter(
            public_id=public_id,
            provider=PaymentAttempt.Provider.TCART,
            provider_reference=str(payload.get("invoice_id", "")),
        ).exists():
            return Response({"success": False, "message": "Unknown TCart invoice"}, status=404)

'''
    lines = s.splitlines(keepends=True)
    lines.insert(idx, block)
    return ''.join(lines)


def patch_service(s: str) -> str:
    if PENDING_MARK in s:
        return s
    tree = ast.parse(s)
    funs = [x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'process_payment_callback']
    if len(funs) != 1:
        raise InstallError('process_payment_callback function not found uniquely')
    fn = funs[0]
    lines = s.splitlines(keepends=True)
    # Find the first top-level atomic context after the provider verify call.
    atomic = []
    for stmt in fn.body:
        if isinstance(stmt, ast.With):
            if any(isinstance(item.context_expr, ast.Call) and isinstance(item.context_expr.func, ast.Attribute) and item.context_expr.func.attr == 'atomic' for item in stmt.items):
                atomic.append(stmt)
    if len(atomic) != 1:
        raise InstallError(f'Expected one final transaction.atomic in callback, found {len(atomic)}')
    before_atomic = ''.join(lines[fn.lineno-1:atomic[0].lineno-1])
    if 'provider.verify_payment' not in before_atomic and 'verify_payment' not in before_atomic:
        raise InstallError('Expected provider verification before atomic transaction')
    block = '''    # TCART_PRESERVE_PENDING_V2: a pending bank-transfer invoice is not failed.
    if (
        provider_key == PaymentAttempt.Provider.TCART
        and not result.success
        and result.failure_code == "pending"
    ):
        return attempt

'''
    lines.insert(atomic[0].lineno - 1, block)
    return ''.join(lines)


def patch_settings(s: str) -> str:
    if SETTINGS_MARK in s:
        return s
    if 'TCART_API_TOKEN' not in s:
        raise InstallError('Existing TCart configuration block not found')
    extra = '''\n# TCART_CALLBACK_SETTINGS_V2 - callback_secret differs from the SMS secret.
TCART_CALLBACK_SECRET = os.getenv("TCART_CALLBACK_SECRET", "")
TCART_RETURN_URL = os.getenv("TCART_RETURN_URL", "")
'''
    if 'TCART_CALLBACK_SECRET =' in s or 'TCART_RETURN_URL =' in s:
        # Protect pre-existing custom environment settings from overwrites.
        extra = '\n# TCART_CALLBACK_SETTINGS_V2 - existing settings retained.\n'
        if 'TCART_CALLBACK_SECRET =' not in s:
            extra += 'TCART_CALLBACK_SECRET = os.getenv("TCART_CALLBACK_SECRET", "")\n'
        if 'TCART_RETURN_URL =' not in s:
            extra += 'TCART_RETURN_URL = os.getenv("TCART_RETURN_URL", "")\n'
    return s.rstrip() + '\n' + extra


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Preflight only: do not write any files')
    args = parser.parse_args()
    paths = {
        'payments/api/v1/views.py': patch_view,
        'payments/services.py': patch_service,
        'core/settings/base.py': patch_settings,
    }
    if not (ROOT / 'manage.py').is_file():
        raise InstallError('Place install_tcart.py next to manage.py in the Backend directory')
    changes = {}
    for rel, transform in paths.items():
        p = ROOT / rel
        if not p.is_file():
            raise InstallError(f'Missing file: {rel}')
        old = p.read_text(encoding='utf-8')
        updated = transform(old)
        ast.parse(updated, filename=rel)
        changes[p] = (old, updated)
        print(('Already patched: ' if updated == old else 'Ready to patch: ') + rel)
    if args.dry_run:
        print('Dry run passed; no files changed.')
        return
    # Stage all changes on same filesystem before modifying originals.
    staged = {}
    try:
        for p, (old, new) in changes.items():
            if old == new:
                continue
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=p.parent, delete=False) as f:
                f.write(new)
                staged[p] = Path(f.name)
        # Preserve original snapshot once; do not overwrite older backups.
        for p in staged:
            b = p.with_suffix(p.suffix + '.tcart-backup')
            if not b.exists():
                shutil.copy2(p, b)
        replaced = []
        try:
            for p, tmp in staged.items():
                tmp.replace(p)
                replaced.append(p)
        except Exception:
            # Restore this run's originals, not necessarily a stale backup.
            for p in replaced:
                p.write_text(changes[p][0], encoding='utf-8')
            raise
    finally:
        for tmp in staged.values():
            tmp.unlink(missing_ok=True)
    print('TCart hooks installed. Run python manage.py check --settings=core.settings.development')


if __name__ == '__main__':
    try:
        main()
    except (InstallError, SyntaxError, OSError) as exc:
        print(f'Installation aborted: {exc}', file=sys.stderr)
        sys.exit(1)
