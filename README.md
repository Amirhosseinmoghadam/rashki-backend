# Rashki backend

Django / Django REST Framework backend for the motorcycle spare parts store.

## Local setup

Use Python 3.12 and Docker Compose:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `DJANGO_SECRET_KEY`, `JWT_SIGNING_KEY`, and `AUTH_OTP_HMAC_KEY` in `.env`
to three separate randomly generated values. Generate each value with:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(48))'
```

The database credentials in `.env.example` match the local development
database in `compose.yaml`. Use separate credentials in production.

```bash
docker compose up -d --wait db
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Development uses a local-memory cache; production requires Redis.
Configure SMS and payment credentials separately to exercise those integrations.

## Migrations

Migration files are versioned source files. After changing an installed model:

```bash
python manage.py makemigrations
python manage.py migrate
git add <app>/migrations/
```

The initial migrations cover the currently installed apps. `inventory` is
disabled in settings and still references the removed `ProductVariant` model;
it is intentionally excluded until its model relationships are updated.

For a new database, use ordinary `migrate`. If an existing database was built
without versioned migrations, back it up and compare its schema to these
migrations before adopting them. Use `migrate --fake-initial` only when the
existing schema matches; Django's table-existence check does not validate all
columns or constraints. Never delete existing data to adopt migrations.

## Verification with PostgreSQL

```bash
pip check
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
python manage.py test --noinput
```

`DATABASE_URL` must point to PostgreSQL to run the row-lock tests. Those tests
use separate connections and real commits to check lock contention and ensure
concurrent cancellation restores reserved stock once. SQLite skips these two
tests and cannot verify row-level locking.

The GitHub Actions workflow runs the full suite against PostgreSQL 16 and
checks that model changes have committed migrations. It mocks external services
through the existing tests; it does not send real SMS or charge payments.
