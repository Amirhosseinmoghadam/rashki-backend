# Rashki Backend | بک‌اند فروشگاه رشکی

راهنمای فارسی و انگلیسی راه‌اندازی، توسعه و مدیریت بک‌اند فروشگاه قطعات موتورسیکلت.
Bilingual setup, development and operations guide for the motorcycle spare-parts store backend.

> مبنای این مستند: کد شاخه `main` در کامیت `7226186`. / Source baseline: `main` at commit `7226186`.

## فهرست | Contents

- [راهنمای فارسی](#راهنمای-فارسی)
- [English guide](#english-guide)
- [اپ‌ها و مدل‌ها / Apps and models](#apps-and-models)
- [متغیرهای محیطی / Environment variables](#environment-variables)
- [فرهنگ کامل فیلدها / Complete model field reference](#model-field-reference)
- [مسیرهای API / API routes](#api-routes)

<a id="راهنمای-فارسی"></a>
## راهنمای فارسی

### ۱. معماری و پیش‌نیازها

پروژه از Python 3.12، Django 5.2، Django REST Framework، JWT، PostgreSQL 16 و Redis استفاده می‌کند. `manage.py` به‌صورت پیش‌فرض تنظیمات `core.settings.development` را بارگذاری می‌کند؛ فایل‌های WSGI و ASGI پیش‌فرض production دارند. کش توسعه **Redis** است؛ SQLite فقط در نبود `DATABASE_URL` جایگزین می‌شود و برای تأیید قفل‌های ردیفی کافی نیست.

ساختار هر اپ معمولاً شامل `models.py`، `admin.py`، `api/v1/serializers.py`، `views.py` و `urls.py` است. منطق کسب‌وکار در اپ‌های مرتبط داخل `services.py` و خواندن داده در `selectors.py` قرار دارد. `core` تنظیمات و مسیرهای اصلی، و `utils` ابزارهای مشترک را نگه می‌دارد. `inventory` نصب نشده و هنوز به `ProductVariant` حذف‌شده وابسته است؛ آن را بدون اصلاح مدل‌ها فعال نکنید.

### ۲. دریافت کد و نصب وابستگی‌ها

تمام دستورهای `manage.py` از ریشه ریپازیتوری، یعنی پوشه‌ای که `manage.py` و `requirements.txt` دارد، اجرا می‌شوند. در clone جدید نام این پوشه `rashki-backend` است؛ در سیستم فعلی شما ممکن است `Backend` باشد.

```bash
git clone https://github.com/Amirhosseinmoghadam/rashki-backend.git
cd rashki-backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
cp .env.example .env
```

در Windows PowerShell فعال‌سازی محیط با `.venv\Scripts\Activate.ps1` است. اگر `.env` از قبل دارید، دستور `cp` را اجرا نکنید تا تنظیماتتان جایگزین نشود. dependencyهای پروژه را از همان `requirements.txt` نصب کنید؛ نصب پراکنده نسخه‌های دیگر قابلیت بازتولید را کم می‌کند.

### ۳. تنظیم فایل `.env`

سه کلید مستقل بسازید؛ دستور زیر را سه بار اجرا و هر خروجی را برای یک کلید استفاده کنید:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(48))'
```

```dotenv
DJANGO_SECRET_KEY=replace_with_random_value_1
JWT_SIGNING_KEY=replace_with_random_value_2
AUTH_OTP_HMAC_KEY=replace_with_random_value_3
DATABASE_URL=postgresql://rashki:rashki_dev@127.0.0.1:5432/rashki
REDIS_URL=redis://127.0.0.1:6379/1
ALLOWED_HOSTS=localhost,127.0.0.1
```

رمز PostgreSQL در URL باید همان رمز کاربر دیتابیس باشد؛ رمز مدیر Django مستقل است. اگر رمز شامل کاراکتر ویژه است، بخش رمز URL باید percent-encoded شود. `.env` را commit نکنید. مقدار `DEBUG` در فایل env تنظیمات development را تغییر نمی‌دهد؛ این فایل Python صریحاً `DEBUG=True` دارد.

### ۴. اجرای PostgreSQL و Redis؛ یکی از دو مسیر را انتخاب کنید

#### مسیر A: مک بدون Docker، با Homebrew

```bash
brew install postgresql@16 redis
brew services start postgresql@16
brew services start redis
"$(brew --prefix postgresql@16)/bin/createuser" --createdb --pwprompt rashki
"$(brew --prefix postgresql@16)/bin/createdb" --owner=rashki rashki
redis-cli ping
```

کاربر و دیتابیس را فقط بار اول بسازید. هنگام درخواست رمز، رمز انتخابی را وارد و `DATABASE_URL` را مطابق آن تنظیم کنید. خروجی Redis باید `PONG` باشد. اختیار `--createdb` برای ساخت دیتابیس تست لازم است. روی سیستم شما که سرویس‌ها و دیتابیس قبلاً ساخته شده‌اند، فقط شروع سرویس‌ها کافی است.

#### مسیر B: Docker

فایل `compose.yaml` فعلی **فقط** سرویس `db` دارد؛ دستور `docker compose up redis` در این نسخه معتبر نیست. Redis را جدا اجرا کنید:

```bash
docker compose up -d --wait db
docker run -d --name rashki-redis -p 127.0.0.1:6379:6379 redis:7
docker exec rashki-redis redis-cli ping
```

در دفعات بعد برای کانتینر Redis موجود از `docker start rashki-redis` استفاده کنید. PostgreSQL Compose دارای volume پایدار است. `docker compose down` کانتینرها را متوقف می‌کند؛ افزودن `-v` volume دیتابیس را حذف می‌کند. سرویس Homebrew و Docker را هم‌زمان روی پورت یکسان اجرا نکنید.

### ۵. بررسی اتصال، migration، مدیر و تست‌ها؛ به همین ترتیب

```bash
python manage.py check
python manage.py shell -c 'from django.conf import settings; from django.db import connection; from django.core.cache import cache; print(connection.vendor); print(settings.CACHES["default"]["BACKEND"]); cache.set("rashki:redis:test", "ok", 30); print(cache.get("rashki:redis:test")); cache.delete("rashki:redis:test")'
python manage.py migrate --noinput
python manage.py createsuperuser
python manage.py makemigrations --check --dry-run
python manage.py test --noinput
python manage.py runserver
```

بررسی اتصال باید `postgresql`، `django_redis.cache.RedisCache` و `ok` را چاپ کند. برای مدیر شماره موبایل و رمز مناسب وارد کنید. `runserver` ترمینال را اشغال می‌کند؛ برای فرمان‌های دیگر ترمینال دوم با محیط فعال باز کنید یا با `Ctrl+C` سرور را متوقف کنید.

- مدیریت: http://127.0.0.1:8000/admin/
- Swagger: http://127.0.0.1:8000/swagger/
- ReDoc: http://127.0.0.1:8000/redoc/
- Schema: http://127.0.0.1:8000/schema/

دیتابیس PostgreSQL جدید داده SQLite قبلی را خودکار ندارد. migration ساختار دیتابیس را می‌سازد؛ محصول و تنظیمات فروشگاه را ایجاد نمی‌کند.

### ۶. ترتیب ایجاد داده‌های فروشگاه

۱. استان و شهر را از admin ایجاد کنید یا با اتصال معتبر تیپاکس همگام کنید.
۲. دسته‌بندی کالا و برند قطعه را بسازید؛ برند موتورسیکلت و مدل آن برای سازگاری کالا جدا هستند.
۳. تنظیمات قیمت‌گذاری و در صورت استفاده از قیمت دلاری، یک نرخ فعال USD تعریف کنید.
۴. محصول با دسته‌بندی، حالت قیمت، قیمت پایه، وضعیت فعال، موجودی، وزن و ابعاد بسته‌بندی ایجاد کنید. تصاویر، ویژگی‌ها و سازگاری موتورسیکلت را اضافه کنید. `current_price_toman` قیمت محاسبه‌شده است؛ از فرم و actionهای قیمت‌گذاری admin استفاده کنید.
۵. `ShippingOrigin` فعال و پیش‌فرض بسازید؛ تنظیمات ارسال و روش ارسال را تعیین کنید. برای روش دستی تعرفه `ShippingRateRule` معتبر بسازید. برای تیپاکس تنظیمات فرستنده، شناسه‌های بسته‌بندی و نگاشت شهر/استان/مبدا را تکمیل کنید.
۶. کاربر مشتری، پروفایل و آدرس گیرنده معتبر ایجاد کنید؛ سپس سبد، استعلام ارسال، سفارش و پرداخت را از API آزمایش کنید.

مبلغ‌ها در منطق فروشگاه تومان، وزن‌های دارای پسوند `_grams` گرم و ابعاد محصول دارای پسوند `_cm` سانتی‌متر هستند. داده خام Provider الزاماً همین واحدها را ندارد. قیمت‌ها و اطلاعات گیرنده/ارسال در سفارش snapshot می‌شوند؛ فیلدهای محاسبه‌شده و snapshot را در درخواست خرید به‌دلخواه ارسال نکنید.

### ۷. دستورهای اختصاصی پروژه و ترتیب اجرا

این دستورها پس از نصب وابستگی‌ها، تنظیم env، اجرای سرویس‌ها و migration اجرا می‌شوند. فرمان‌های تیپاکس با API بیرونی تماس می‌گیرند و نیازمند اعتبارنامه و دسترسی شبکه‌اند؛ برای روشن‌کردن سرور اجباری نیستند. با این حال مسیر بسته‌بندی سبد و checkout به کارتن مناسب در `ShippingProviderPackingOption` نیاز دارد؛ حتی تعرفه دستی نیز این نیاز را حذف نمی‌کند. می‌توان رکوردهای معتبر را از admin ایجاد کرد یا با sync دریافت کرد.

```bash
# ابتدا مشاهده داده مرجع Provider
python manage.py tipax_reference_data
# سپس ایجاد/به‌روزرسانی استان‌ها، شهرها و نگاشت‌ها
python manage.py sync_tipax_locations
# بعد دریافت گزینه‌های بسته‌بندی و اعتبارسنجی مرجع بسته
python manage.py sync_tipax_packing
```

پس از این مراحل نتیجه sync و نگاشت‌ها را در admin بررسی و مبدا پیش‌فرض، نگاشت مبدا Provider و تنظیمات تیپاکس را کامل کنید. شناسه Provider را حدس نزنید.

| دستور | کاربرد و نکته |
|---|---|
| `tipax_reference_data` | نمایش داده‌های مرجع بسته‌بندی، محتوا، نوع مرسوله، نوع پرداخت و شهرها؛ ابزار تشخیص، نه seed کامل فروشگاه |
| `sync_tipax_locations` | همگام‌سازی استان/شهر داخلی و catalog/نگاشت Provider |
| `sync_tipax_packing` | همگام‌سازی گزینه‌های بسته‌بندی و اعتبارسنجی reference data |
| `tipax_sync_catalog` | مسیر جایگزین دریافت catalog شهر/استان/بسته‌بندی و نگاشت خودکار امن؛ اجرای آن جای بررسی نگاشت‌های مبهم را نمی‌گیرد |
| `tipax_sync_catalog --skip-auto-map` | دریافت catalog بدون نگاشت خودکار شهر/استان |
| `tipax_sync_catalog --deactivate-missing` | غیرفعال‌سازی رکوردهای catalog غایب از پاسخ؛ فقط پس از اطمینان از کامل‌بودن پاسخ API |
| `sync_addresses_from_tipax --inspect --sample-size 5` | مسیر دیگر برای مشاهده نمونه استان/شهر بدون تغییر دیتابیس |
| `sync_addresses_from_tipax --dry-run` | اجرای sync آدرس و rollback تراکنش در پایان؛ تماس API همچنان انجام می‌شود |
| `sync_addresses_from_tipax` | sync مستقیم استان/شهر داخلی؛ برای راه‌اندازی معمول مسیر `sync_tipax_locations` را استفاده کنید |
| `populate_locations` | deprecated؛ فقط هشدار و راهنمای استفاده از `sync_tipax_locations` چاپ می‌کند |
| `expire_unpaid_orders` | انقضای سفارش‌های واجد شرایط و آزادسازی موجودی رزروشده |

برای مشاهده optionهای دقیق هر فرمان:

```bash
python manage.py help
python manage.py help tipax_sync_catalog
python manage.py help sync_addresses_from_tipax
```

انقضای سفارش را پس از شروع فعالیت فروشگاه دوره‌ای اجرا کنید؛ زمان پرداخت در کد فعلی ۲۰ دقیقه است:

```bash
python manage.py expire_unpaid_orders
```

فرمان فقط سفارش `pending_payment` با مهلت گذشته و پرداخت `unpaid` یا `failed` را پردازش می‌کند؛ پرداخت `pending` را عمداً کنار می‌گذارد. reconciliation پرداخت pending در این فرمان پیاده نشده است. نمونه cron هر دقیقه، با جایگزینی مسیر واقعی پروژه و Python محیط مجازی:

```cron
* * * * * cd /absolute/path/rashki-backend && /absolute/path/rashki-backend/.venv/bin/python manage.py expire_unpaid_orders >> /absolute/path/rashki-backend/order-expiry.log 2>&1
```

### ۸. احراز هویت، پرداخت و ارسال

ورود مشتری با شماره ایرانی `09xxxxxxxxx` و OTP است؛ درخواست‌های محافظت‌شده هدر `Authorization: Bearer <access_token>` دارند. مدیر Django با رمز وارد admin می‌شود. access پیش‌فرض ۱۸۰ دقیقه و refresh ۳۰ روز است؛ refresh چرخش و blacklist دارد.

وجود `MELIPAYAMAK_API_TOKEN` به‌تنهایی OTP را وصل نمی‌کند: `accounts/sms.py` یک callable از setting به نام `AUTH_OTP_SENDER` می‌خواهد که `phone_number` و `code` بپذیرد. در تنظیمات فعلی این setting از env بارگذاری نشده؛ اتصال sender نیازمند تغییر تنظیمات Python است. بدون sender، development پیامک واقعی نمی‌فرستد و production خطا می‌دهد. `AUTH_OTP_DEBUG_RETURN_CODE` نیز setting Python است و به‌طور پیش‌فرض فعال نیست؛ برای توسعه محلی می‌توان آن را صریحاً تنظیم کرد.

زرین‌پال Provider پیاده‌شده است و merchant، callback قابل دسترس و تنظیمات واحد پول لازم دارد. `ZARINPAL_SANDBOX` در development برابر True و production برابر False است؛ در sandbox، Provider URLهای پرداخت را با URLهای sandbox جایگزین می‌کند. **TCart هنوز عملیاتی نیست**: start و verify خطای configuration می‌دهند؛ گذاشتن token در env این بخش را تکمیل نمی‌کند. API پست پیشتاز نیز هنوز پیاده نشده و خطای unavailable می‌دهد؛ برای پست از تعرفه دستی استفاده کنید. مسیرهای refund وجود دارند، اما پشتیبانی عملی Provider و نتیجه اجرای سرویس باید بررسی شود؛ وجود مدل/endpoint تضمین بازپرداخت بانکی نیست.

جریان اصلی: ورود ← آدرس ← افزودن کالا به سبد ← استعلام ارسال ← ایجاد سفارش ← شروع پرداخت ← callback/verify ← پیگیری سفارش/مرسوله. checkout قیمت و موجودی را در تراکنش بررسی و موجودی را رزرو می‌کند؛ لغو/انقضا از سرویس‌های پروژه انجام شود تا موجودی صحیح برگردد.

### ۹. توسعه، تست و Git

```bash
# پس از تغییر مدل
python manage.py makemigrations
python manage.py migrate --noinput
# پیش از ثبت تغییر
python -m pip check
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --noinput
# تست‌های هدفمند
python manage.py test accounts.tests addresses.tests orders.tests --noinput
python manage.py test orders.tests.test_postgres_locking --noinput
# بررسی وضعیت migration
python manage.py showmigrations
python manage.py migrate --plan
# تغییر رمز مدیر موجود
python manage.py changepassword YOUR_PHONE_NUMBER
```

migrationها فایل منبع هستند و باید commit شوند؛ `.env`، `.venv`، فایل دیتابیس، media و patch دانلودشده را اضافه نکنید. برای دیتابیس تازه `migrate` معمولی کافی است. `--fake-initial` فقط بعد از backup و تطبیق schema دیتابیس قدیمی استفاده شود؛ وجود جدول به‌تنهایی سازگاری ستون و constraint را اثبات نمی‌کند.

CI در `.github/workflows/backend-tests.yml` روی Python 3.12، PostgreSQL 16 و Redis 7 اجرا می‌شود و dependency، system check، migration drift، migration و تست را بررسی می‌کند. تست قفل نیازمند PostgreSQL و کاربری با اجازه ساخت test DB است؛ SQLite آن را skip می‌کند. نتیجه قبلی ۲۱ تست بوده، ولی تعداد تست معیار ثابت پروژه نیست. تست‌ها تضمین ارسال واقعی پیامک، پرداخت واقعی یا صحت همه حالت‌های هم‌زمانی نیستند.

برای جایگزینی README با فایل این مستند در ریشه پروژه:

```bash
git diff -- README.md
git add README.md
git commit -m "Document bilingual setup, apps, fields and management commands"
git push origin main
```

### ۱۰. production و رفع خطا

production باید `DJANGO_SETTINGS_MODULE=core.settings.production`، کلیدهای مستقل، host واقعی، PostgreSQL، Redis، تنظیمات SMS/OTP و سرویس‌های مورد استفاده داشته باشد. Gunicorn/Uvicorn در requirements فعلی نیستند؛ سرور deployment را جدا انتخاب، نصب و نسخه آن را ثبت کنید. `runserver` برای استقرار نیست. تنظیمات HTTPS، reverse proxy قابل اعتماد، static و media، backup و اجرای دوره‌ای انقضا را فراهم کنید.

```bash
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py check --deploy
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py migrate --noinput
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py collectstatic --noinput
```

| مشکل | بررسی |
|---|---|
| `command not found: docker` | مسیر Homebrew را انتخاب کنید یا Docker نصب کنید |
| PostgreSQL connection refused | سرویس، پورت و `DATABASE_URL` را بررسی کنید |
| authentication failed | رمز کاربر PostgreSQL و URL یکسان نیست |
| permission denied to create database | کاربر تست باید `CREATEDB` داشته باشد؛ برای نقش موجود administrator می‌تواند `ALTER ROLE rashki CREATEDB;` اجرا کند |
| Redis connection refused | سرویس Redis و `REDIS_URL` را بررسی کنید |
| چاپ `ok` ولی شک به cache | backend را همراه نتیجه set/get چاپ کنید؛ LocMemCache هم `ok` می‌دهد |
| خطای env/key | سه کلید اجباری را در `.env` ریشه پروژه تنظیم کنید |
| `No changes detected` | تغییر مدل نیازمند migration جدید پیدا نشده؛ اجرای migrationهای موجود را ثابت نمی‌کند |
| صفحه `(END)` در Git | با `q` از pager خارج شوید |
| قیمت/ارسال نامعتبر | نرخ فعال، قیمت محاسبه‌شده، وزن، ابعاد، origin، تعرفه و mapping را بررسی کنید |

<a id="english-guide"></a>
## English guide

### Overview and installation

Rashki is a Django 5.2 / DRF backend for motorcycle spare parts. Use Python 3.12, PostgreSQL 16 and Redis. `manage.py` defaults to development settings; WSGI/ASGI default to production. Development uses Redis. SQLite is only a fallback when `DATABASE_URL` is absent and cannot validate row locking. `inventory` is disabled and references a removed `ProductVariant`; it needs repairs before activation.

Run commands from the repository root containing `manage.py`:

```bash
git clone https://github.com/Amirhosseinmoghadam/rashki-backend.git
cd rashki-backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
cp .env.example .env
```

On Windows PowerShell activate with `.venv\Scripts\Activate.ps1`. Do not overwrite an existing `.env`. Generate three independent secrets with `python -c 'import secrets; print(secrets.token_urlsafe(48))'`, then set `DJANGO_SECRET_KEY`, `JWT_SIGNING_KEY`, and `AUTH_OTP_HMAC_KEY`. Configure `DATABASE_URL` and `REDIS_URL` as shown in the Persian setup. Database credentials are independent from the Django administrator password. Never commit `.env`. Development hardcodes `DEBUG=True` regardless of the env value.

### Start services: choose one route

macOS with Homebrew, without Docker:

```bash
brew install postgresql@16 redis
brew services start postgresql@16
brew services start redis
"$(brew --prefix postgresql@16)/bin/createuser" --createdb --pwprompt rashki
"$(brew --prefix postgresql@16)/bin/createdb" --owner=rashki rashki
redis-cli ping
```

Create the role/database only once. Set the database URL password to the password you enter. The development role needs database creation privileges for tests.

Docker: current Compose contains only PostgreSQL, so run Redis separately:

```bash
docker compose up -d --wait db
docker run -d --name rashki-redis -p 127.0.0.1:6379:6379 redis:7
docker exec rashki-redis redis-cli ping
```

For an existing Redis container use `docker start rashki-redis`. Do not run competing services on the same port. PostgreSQL data lives in a named volume; `docker compose down -v` deletes it.

### Ordered first run

```bash
python manage.py check
python manage.py shell -c 'from django.conf import settings; from django.db import connection; from django.core.cache import cache; print(connection.vendor); print(settings.CACHES["default"]["BACKEND"]); cache.set("rashki:redis:test", "ok", 30); print(cache.get("rashki:redis:test")); cache.delete("rashki:redis:test")'
python manage.py migrate --noinput
python manage.py createsuperuser
python manage.py makemigrations --check --dry-run
python manage.py test --noinput
python manage.py runserver
```

Expect `postgresql`, `django_redis.cache.RedisCache`, and `ok`. Visit `/admin/`, `/swagger/`, `/redoc/`, and `/schema/` at `http://127.0.0.1:8000`. Keep the server terminal open; use another activated terminal for commands. A new PostgreSQL database does not automatically import old SQLite records.

### Initial business data and integrations

Create locations, product categories and parts brands; optionally motorcycle brands/models for compatibility. Configure pricing and an active USD exchange rate for USD-priced products. Add an active product with base price, stock, weight, packing dimensions, images and attributes. Use admin pricing forms/actions to calculate `current_price_toman`. Configure an active default shipping origin and shipping settings/methods. Manual methods need applicable rate rules. Tipax methods also need sender information, provider reference data and city/province/origin mappings. Finally create a customer profile/address and exercise checkout through the API.

Store prices use toman; `_grams` fields use grams and product `_cm` fields use centimetres. Raw provider data can use different units. Orders store address, item-price and shipping snapshots. Use the business services for cancellation/expiry rather than directly editing statuses or stock.

Customer login uses an Iranian phone number and OTP. Protected requests use `Authorization: Bearer <access_token>`. Access defaults to 180 minutes; refresh defaults to 30 days with rotation and blacklisting. Admin login uses a password.

OTP delivery needs a Python setting `AUTH_OTP_SENDER` pointing to a callable accepting `phone_number` and `code`. This setting is not currently read from env; Melipayamak credentials alone do not wire OTP delivery. Without a sender, DEBUG does not send real SMS and production raises an error. `AUTH_OTP_DEBUG_RETURN_CODE` is also a Python setting and disabled by default.

ZarinPal is implemented and requires merchant/callback configuration. Development sets `ZARINPAL_SANDBOX=True` and the provider substitutes sandbox payment URLs; production sets it to False. TCart is a scaffold: both start and verify raise configuration errors, even if tokens are set. The Post Pishtaz API provider also raises an unavailable error; use manual postal tariffs until it is implemented. Refund models/routes do not imply every provider supports actual refunds. Inspect provider support before use.

### Project management commands

After setup/migrations and valid Tipax credentials, the recommended initial order is:

```bash
python manage.py tipax_reference_data
python manage.py sync_tipax_locations
python manage.py sync_tipax_packing
```

Inspect synced data and unresolved mappings in admin; complete the origin mapping and sender settings. These commands call external APIs. Starting the server does not require them, but checkout packaging needs suitable packing records even when shipping tariffs are manual.

| Command | Purpose |
|---|---|
| `tipax_reference_data` | Display provider reference data; diagnostic, not a complete store seed |
| `sync_tipax_locations` | Sync internal provinces/cities and provider catalog/mappings |
| `sync_tipax_packing` | Sync packing options and validate packing references |
| `tipax_sync_catalog` | Alternative catalog sync with safe automatic location mapping |
| `tipax_sync_catalog --skip-auto-map` | Sync catalog without automatic mapping |
| `tipax_sync_catalog --deactivate-missing` | Deactivate missing provider entries; requires a complete API response |
| `sync_addresses_from_tipax --inspect --sample-size 5` | Inspect sample states/cities without changing the database |
| `sync_addresses_from_tipax --dry-run` | Perform address sync then roll back the transaction; still calls the API |
| `sync_addresses_from_tipax` | Alternative direct internal location sync |
| `populate_locations` | Deprecated warning-only command; use `sync_tipax_locations` |
| `expire_unpaid_orders` | Expire eligible overdue orders and release reserved stock |

Use `python manage.py help COMMAND_NAME` to inspect flags. Run `expire_unpaid_orders` periodically through your scheduler; the cron example in the Persian guide runs every minute. The payment deadline is hardcoded to 20 minutes in base settings. Only overdue `pending_payment` orders with payment status `unpaid` or `failed` are eligible. Payment status `pending` is intentionally excluded; this command does not reconcile pending payments.

### Development, CI and deployment

After model edits, run `makemigrations` then `migrate`. Before committing, run `pip check`, `manage.py check`, `makemigrations --check --dry-run`, and `test --noinput`. PostgreSQL locking tests can be targeted with `python manage.py test orders.tests.test_postgres_locking --noinput`. Commit migration source files, not local databases/secrets/uploads. Use ordinary migrations for fresh databases; use `--fake-initial` only after backing up and matching an existing schema.

The GitHub Actions workflow starts PostgreSQL 16 and Redis 7 on Python 3.12, checks dependencies/model drift and runs migrations/tests. Tests do not prove live SMS/payment delivery or every concurrency scenario. SQLite skips PostgreSQL-specific lock tests.

Production requires `DJANGO_SETTINGS_MODULE=core.settings.production`, real allowed hosts, independent secrets, PostgreSQL, Redis and configured integrations. Install and version a production WSGI/ASGI server separately: Gunicorn/Uvicorn are not in the current requirements. Configure HTTPS, trusted proxy handling, static/media hosting, backups and order expiry scheduling. Run `check --deploy`, `migrate --noinput`, and `collectstatic --noinput` with production settings. Do not deploy `runserver`.

Connection-refused errors usually mean the relevant service/port/URL is wrong. PostgreSQL password errors require matching role credentials. Test-database permission errors require `CREATEDB`. Redis set/get alone does not identify the backend: print its class as well. Missing keys must be set in the root `.env`. `No changes detected` means no new model migrations are required, not that existing migrations were applied.


<a id="apps-and-models"></a>
## اپ‌ها و مدل‌ها | Apps and models

| App | کاربرد | Responsibility | Models |
|---|---|---|---|
| `accounts` | کاربران، OTP و JWT | Users, OTP and JWT | `User`, `OTPCode` |
| `addresses` | استان، شهر و آدرس گیرنده | Provinces, cities and recipient addresses | `Province`, `City`, `Address` |
| `articles` | مقالات، دسته مقاله و SEO | Articles, article categories and SEO | `ArticleCategory`, `Article` |
| `brands` | برند سازنده قطعه | Parts manufacturers | `Brand` |
| `carts` | سبد کاربر، اقلام و تخفیف | User cart, items and applied discount | `Cart`, `CartItem` |
| `categories` | دسته‌بندی سلسله‌مراتبی کالا | Hierarchical product categories | `Category` |
| `contact` | درخواست تماس و استعلام | Contact and inquiry requests | `ContactRequest` |
| `discounts` | کد تخفیف، دامنه و سابقه مصرف | Discount scopes, limits and usage history | `DiscountCode`, `DiscountUsage` |
| `motorcycles` | برند و مدل موتورسیکلت | Motorcycle brands and models | `MotorcycleBrand`, `MotorcycleModel` |
| `orders` | سفارش، snapshot اقلام و رزرو موجودی | Orders, item snapshots and stock reservation | `Order`, `OrderItem` |
| `payments` | تلاش پرداخت و بازپرداخت | Payment attempts and refunds | `PaymentAttempt`, `PaymentRefund` |
| `pricing` | نرخ ارز و قواعد محاسبه قیمت | Exchange rates and price calculation | `ExchangeRate`, `PricingSettings` |
| `products` | کالا، تصویر، ویژگی و سازگاری | Products, images, attributes and compatibility | `Product`, `ProductImage`, `ProductAttribute`, `ProductAttributeOption`, `CategoryAttribute`, `ProductAttributeValue`, `ProductCompatibility`, `ProductRelation` |
| `shipping` | روش، تعرفه، مبدا، catalog و مرسوله | Methods, rates, origins, catalog and shipments | `TipaxSettings`, `ShippingSettings`, `ShippingMethod`, `ShippingRateRule`, `ShippingProviderCityMap`, `TipaxPackageProfile`, `Shipment`, `ShippingOrigin`, `ShippingProviderProvince`, `ShippingProviderCity`, `ShippingProviderPackingOption`, `ShippingProviderProvinceMap`, `ShippingProviderOriginMap` |
| `wishlists` | علاقه‌مندی کاربر | User wishlist | `WishlistItem` |

### قواعد مهم | Important business rules

- `brands.Brand` برند قطعه است؛ `motorcycles.MotorcycleBrand` برند موتور. / Parts brands and motorcycle brands are separate entities.
- `Cart` برای هر کاربر یکی است؛ افزودن به سبد جای رزرو checkout نیست. / One cart per user; stock reservation happens at checkout.
- قیمت دلاری به نرخ فعال نیاز دارد؛ قیمت ثابت از پایه تومان محاسبه می‌شود. / USD pricing needs an active rate; fixed pricing uses a toman base.
- ویژگی کالا از نوع text/number/boolean/choice در مدل تعریف می‌شود؛ مقدار باید با نوع سازگار باشد. / Attribute values must match their declared type.
- `is_active`، `status` و محدودیت‌های زمانی بر قابل‌استفاده‌بودن داده اثر دارند. / Active flags, statuses and validity windows affect availability.
- مبلغ‌های سفارش و پرداخت و snapshotها خروجی سرویس‌ها هستند. / Order/payment amounts and snapshots are service-managed data.

<a id="environment-variables"></a>
## متغیرهای محیطی | Environment variables

`.env.example` همه تنظیمات قابل بارگذاری را ندارد. جدول زیر از settings استخراج شده؛ مقادیر نمونه credentials مناسب production نیستند.
`.env.example` is not exhaustive. This reference comes from settings; sample credentials are not production credentials.

| Variable | Default / پیش‌فرض | Source / منبع |
|---|---|---|
| `ALLOWED_HOSTS` | `['localhost', '127.0.0.1']`; `[]` | development.py, production.py |
| `AUTH_OTP_EXPIRE_SECONDS` | `120` | base.py |
| `AUTH_OTP_HMAC_KEY` | `required / اجباری` | base.py |
| `AUTH_OTP_IP_WINDOW_SECONDS` | `10 * 60` | base.py |
| `AUTH_OTP_LENGTH` | `6` | base.py |
| `AUTH_OTP_MAX_ATTEMPTS` | `5` | base.py |
| `AUTH_OTP_MAX_SENDS_PER_HOUR` | `5` | base.py |
| `AUTH_OTP_MAX_SENDS_PER_IP_WINDOW` | `30` | base.py |
| `AUTH_OTP_MAX_VERIFY_PER_IP_WINDOW` | `60` | base.py |
| `AUTH_OTP_MAX_VERIFY_PER_WINDOW` | `20` | base.py |
| `AUTH_OTP_RESEND_SECONDS` | `60` | base.py |
| `AUTH_OTP_VERIFY_IP_WINDOW_SECONDS` | `10 * 60` | base.py |
| `AUTH_OTP_VERIFY_WINDOW_SECONDS` | `10 * 60` | base.py |
| `CONTACT_THROTTLE_RATE` | `'5/hour'` | base.py |
| `CORS_ALLOWED_ORIGINS` | `['http://localhost:5173', 'http://127.0.0.1:5173']`; `[]` | development.py, production.py |
| `CSRF_TRUSTED_ORIGINS` | `['http://localhost:5173', 'http://127.0.0.1:5173']`; `[]` | development.py, production.py |
| `DATABASE_URL` | `f"sqlite:///{BASE_DIR / 'db.sqlite3'}"`; `''`; `required / اجباری` | development.py, production.py, production.py |
| `DB_CONN_MAX_AGE` | `60` | production.py |
| `DJANGO_SECRET_KEY` | `required / اجباری` | base.py |
| `JWT_ACCESS_MINUTES` | `180` | base.py |
| `JWT_REFRESH_DAYS` | `30` | base.py |
| `JWT_SIGNING_KEY` | `required / اجباری` | base.py |
| `MAX_IMAGE_PIXEL_COUNT` | `40000000` | base.py |
| `MAX_IMAGE_UPLOAD_SIZE` | `10 * 1024 * 1024` | base.py |
| `MELIPAYAMAK_API_TOKEN` | `''`; `required / اجباری` | base.py, production.py |
| `MELIPAYAMAK_DEFAULT_FROM` | `''`; `required / اجباری` | base.py, production.py |
| `PAYMENT_FAILED_REDIRECT_URL` | `'http://localhost:5173/payment/failed'` | base.py |
| `PAYMENT_HTTP_TIMEOUT_SECONDS` | `'15'` | base.py |
| `PAYMENT_SUCCESS_REDIRECT_URL` | `'http://localhost:5173/payment/success'` | base.py |
| `REDIS_URL` | `'redis://127.0.0.1:6379/1'`; `''` | development.py, production.py |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `False` | production.py |
| `SECURE_HSTS_PRELOAD` | `False` | production.py |
| `SECURE_HSTS_SECONDS` | `3600` | production.py |
| `SECURE_SSL_REDIRECT` | `True` | production.py |
| `TCART_API_TOKEN` | `''` | base.py |
| `TCART_CREATE_INVOICE_URL` | `''` | base.py |
| `TCART_INVOICE_STATUS_URL` | `''` | base.py |
| `TCART_WEBHOOK_SECRET` | `''` | base.py |
| `TIPAX_ACCESS_TOKEN` | `''` | base.py |
| `TIPAX_AMOUNT_DIVISOR_TO_TOMAN` | `'1'` | base.py |
| `TIPAX_API_KEY` | `''` | base.py |
| `TIPAX_BASE_URL` | `'https://omtestapi.tipax.ir'` | base.py |
| `TIPAX_HTTP_TIMEOUT_SECONDS` | `'20'` | base.py |
| `TIPAX_PASSWORD` | `''` | base.py |
| `TIPAX_REFRESH_TOKEN` | `''` | base.py |
| `TIPAX_USERNAME` | `''` | base.py |
| `TRUST_X_FORWARDED_PROTO` | `False` | production.py |
| `ZARINPAL_GATEWAY_URL` | `'https://www.zarinpal.com/pg/StartPay/'` | base.py |
| `ZARINPAL_MERCHANT_ID` | `''` | base.py |
| `ZARINPAL_PROVIDER_CURRENCY` | `'IRT'` | base.py |
| `ZARINPAL_REQUEST_URL` | `'https://api.zarinpal.com/pg/v4/payment/request.json'` | base.py |
| `ZARINPAL_VERIFY_URL` | `'https://api.zarinpal.com/pg/v4/payment/verify.json'` | base.py |

`AUTH_OTP_SENDER`، `AUTH_OTP_DEBUG_RETURN_CODE`، `ORDER_PAYMENT_TIMEOUT_MINUTES` و `ZARINPAL_SANDBOX` تنظیمات Python هستند؛ افزودن نام آنها به `.env` بدون wiring در settings کافی نیست. پیش‌فرض divisor تیپاکس در کد 1، ولی در `.env.example` مقدار 10 است؛ بر اساس واحد واقعی API آن را انتخاب کنید.
These are Python settings rather than automatically loaded env switches. Tipax amount divisor defaults to 1 in code but 10 in the example env: choose it based on the actual API currency unit.

<a id="model-field-reference"></a>
## فرهنگ کامل فیلدهای مدل | Complete model field reference

این بخش فیلدهای صریح مدل‌های نصب‌شده را پوشش می‌دهد؛ فیلد مدل با payload قابل‌نوشتن API یکسان نیست. serializerها و Swagger منبع قرارداد درخواست/پاسخ‌اند. `id` ضمنی از نوع BigAutoField است؛ `User` علاوه بر این جدول فیلدهای ارثی password، last_login، is_superuser، groups و user_permissions دارد. default یک callable نمایش نام تابع است، نه مقدار ثابت. blank مربوط به validation و null مربوط به ذخیره دیتابیس است. تاریخ‌های خودکار و `editable=False` را عموماً سرویس مدیریت می‌کند.
This lists explicitly declared installed-model fields, not writable API payloads. Serializers/Swagger define request contracts. Implicit IDs are BigAutoField; User also inherits password, last_login, is_superuser, groups and user_permissions. Callable defaults are function names. Blank is validation-level; null is database-level. Automatic timestamps and non-editable fields are generally service-managed.

### `accounts`

#### `User`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `phone_number` | `CharField` | Phone Number / phone number | unique=True; max_length=11; validators=[validate_iran_mobile] |
| `first_name` | `CharField` | First Name / first name | blank=True; max_length=100 |
| `last_name` | `CharField` | Last Name / last name | blank=True; max_length=100 |
| `is_phone_verified` | `BooleanField` | Phone Verified / is phone verified | default=False |
| `is_active` | `BooleanField` | Active / is active | default=True |
| `is_staff` | `BooleanField` | Staff Status / is staff | default=False; _('Designates whether the user can log into the admin site.') |
| `date_joined` | `DateTimeField` | Date Joined / date joined | default=timezone.now |
| `created_at` | `DateTimeField` | Created At / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | Updated At / updated at | auto_now=True |

#### `OTPCode`

**OTPPurpose:** `AUTH` = `('auth', _('Authentication'))`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `phone_number` | `CharField` | Phone Number / phone number | max_length=11; validators=[validate_iran_mobile] |
| `code_hash` | `CharField` | Code Hash / code hash | max_length=128 |
| `purpose` | `CharField` | Purpose / purpose | default=OTPPurpose.AUTH; max_length=20; choices=OTPPurpose.choices |
| `attempts` | `PositiveSmallIntegerField` | Attempts / attempts | default=0 |
| `max_attempts` | `PositiveSmallIntegerField` | Max Attempts / max attempts | default=5 |
| `is_used` | `BooleanField` | Used / is used | default=False |
| `expires_at` | `DateTimeField` | Expires At / expires at | — |
| `created_at` | `DateTimeField` | Created At / created at | auto_now_add=True |

### `addresses`

#### `Province`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `name` | `CharField` | Name / name | unique=True; max_length=100; _('The official name of the province.') |

#### `City`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `province` | `ForeignKey` | Province / province | → Province; on_delete=models.CASCADE; _('The province this city belongs to.') |
| `name` | `CharField` | Name / name | max_length=150; _('The official name of the city.') |

#### `Address`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `user` | `ForeignKey` | User / user | → User; on_delete=models.CASCADE |
| `first_name` | `CharField` | نام / first name | null=True; blank=True; max_length=100 |
| `last_name` | `CharField` | نام خانوادگی / last name | null=True; blank=True; max_length=100 |
| `mobile_number` | `CharField` | شماره موبایل / mobile number | null=True; blank=True; max_length=11; validators=[RegexValidator(regex='^09[0-9]{9}$', message='شماره موبایل نامعتبر است.')] |
| `phone_number` | `CharField` | شماره تلفن ثابت / phone number | null=True; blank=True; max_length=11; validators=[RegexValidator(regex='^[0-9]{11}$', message='شماره تلفن باید 11 رقم باشد.')] |
| `province` | `ForeignKey` | استان / province | → Province; on_delete=models.PROTECT |
| `city` | `ForeignKey` | شهر / city | → City; on_delete=models.PROTECT |
| `postal_code` | `CharField` | کد پستی / postal code | null=True; blank=True; max_length=10; validators=[RegexValidator(regex='^[0-9]{10}$', message='کد پستی باید 10 رقم باشد.')] |
| `postal_address` | `TextField` | آدرس پستی / postal address | null=True; blank=True |
| `is_default` | `BooleanField` | آدرس پیش‌فرض / is default | default=False |
| `created_at` | `DateTimeField` | Created At / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | Updated At / updated at | auto_now=True |

### `articles`

#### `ArticleCategory`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `name` | `CharField` | نام / name | unique=True; max_length=150 |
| `slug` | `SlugField` | slug / slug | unique=True; max_length=180 |
| `description` | `TextField` | description / description | blank=True |
| `is_active` | `BooleanField` | is active / is active | default=True |

#### `Article`

**Status:** `DRAFT` = `('draft', 'پیش‌نویس')`; `PUBLISHED` = `('published', 'منتشر شده')`; `ARCHIVED` = `('archived', 'بایگانی')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `title` | `CharField` | عنوان / title | max_length=255 |
| `slug` | `SlugField` | اسلاگ / slug | unique=True; max_length=280 |
| `excerpt` | `TextField` | خلاصه / excerpt | blank=True |
| `content` | `TextField` | محتوا / content | — |
| `cover_image` | `ImageField` | تصویر اصلی / cover image | null=True; blank=True |
| `category` | `ForeignKey` | دسته‌بندی / category | → ArticleCategory; on_delete=models.PROTECT |
| `author` | `ForeignKey` | نویسنده / author | → settings.AUTH_USER_MODEL; on_delete=models.PROTECT |
| `products` | `ManyToManyField` | محصولات مرتبط / products | → products.Product; blank=True |
| `motorcycles` | `ManyToManyField` | موتورسیکلت‌های مرتبط / motorcycles | → motorcycles.MotorcycleModel; blank=True |
| `status` | `CharField` | وضعیت / status | default=Status.DRAFT; max_length=20; choices=Status.choices |
| `is_featured` | `BooleanField` | مقاله ویژه / is featured | default=False |
| `reading_time` | `PositiveIntegerField` | زمان مطالعه / reading time | default=1; بر حسب دقیقه |
| `view_count` | `PositiveIntegerField` | تعداد بازدید / view count | default=0 |
| `seo_title` | `CharField` | SEO Title / seo title | blank=True; max_length=255 |
| `meta_description` | `CharField` | Meta Description / meta description | blank=True; max_length=320 |
| `published_at` | `DateTimeField` | تاریخ انتشار / published at | null=True; blank=True |
| `created_at` | `DateTimeField` | created at / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at / updated at | auto_now=True |

### `brands`

#### `Brand`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `name` | `CharField` | نام برند / name | unique=True; max_length=150 |
| `slug` | `SlugField` | اسلاگ / slug | blank=True; unique=True; max_length=180 |
| `logo` | `ImageField` | لوگو / logo | null=True; blank=True; validators=[validate_image] |
| `description` | `TextField` | توضیحات / description | blank=True |
| `website` | `URLField` | وب‌سایت / website | blank=True |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

### `carts`

#### `Cart`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `user` | `OneToOneField` | کاربر / user | → settings.AUTH_USER_MODEL; on_delete=models.CASCADE |
| `applied_discount` | `ForeignKey` | کد تخفیف اعمال‌شده / applied discount | → discounts.DiscountCode; null=True; blank=True; on_delete=models.SET_NULL |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `CartItem`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `cart` | `ForeignKey` | سبد خرید / cart | → Cart; on_delete=models.CASCADE |
| `product` | `ForeignKey` | محصول / product | → products.Product; on_delete=models.CASCADE |
| `quantity` | `PositiveIntegerField` | تعداد / quantity | default=1; validators=[MinValueValidator(1)] |
| `created_at` | `DateTimeField` | تاریخ افزودن / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

### `categories`

#### `Category`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `name` | `CharField` | نام دسته‌بندی / name | max_length=150 |
| `slug` | `SlugField` | اسلاگ / slug | blank=True; unique=True; max_length=180 |
| `parent` | `ForeignKey` | دسته والد / parent | → self; null=True; blank=True; on_delete=models.PROTECT |
| `image` | `ImageField` | تصویر / image | null=True; blank=True; validators=[validate_image] |
| `description` | `TextField` | توضیحات / description | blank=True |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `created_at` | `DateTimeField` | created at / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at / updated at | auto_now=True |

### `contact`

#### `ContactRequest`

**Subject:** `WHOLESALE_COOPERATION` = `('wholesale_cooperation', 'درخواست همکاری عمده')`; `PRICE_INQUIRY` = `('price_inquiry', 'استعلام قیمت')`; `AVAILABILITY_INQUIRY` = `('availability_inquiry', 'استعلام موجودی')`; `PRODUCT_QUESTION` = `('product_question', 'پرسش درباره محصول')`; `OTHER` = `('other', 'سایر')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `first_name` | `CharField` | نام / first name | max_length=100 |
| `last_name` | `CharField` | نام خانوادگی / last name | max_length=100 |
| `phone_number` | `CharField` | شماره تماس / phone number | max_length=11; validators=[phone_validator] |
| `subject` | `CharField` | موضوع درخواست / subject | max_length=50; choices=Subject.choices |
| `description` | `TextField` | توضیحات / description | max_length=3000 |
| `is_read` | `BooleanField` | خوانده شده / is read | default=False |
| `created_at` | `DateTimeField` | تاریخ ثبت / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

### `discounts`

#### `DiscountCode`

**DiscountType:** `PERCENTAGE` = `('percentage', 'درصدی')`; `FIXED_AMOUNT` = `('fixed_amount', 'مبلغ ثابت')`

**Scope:** `ALL` = `('all', 'تمام محصولات')`; `PRODUCTS` = `('products', 'محصولات مشخص')`; `CATEGORIES` = `('categories', 'دسته‌بندی‌های مشخص')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `code` | `CharField` | کد تخفیف / code | unique=True; max_length=50 |
| `description` | `CharField` | توضیحات / description | blank=True; max_length=500 |
| `discount_type` | `CharField` | نوع تخفیف / discount type | max_length=20; choices=DiscountType.choices |
| `percentage` | `DecimalField` | درصد تخفیف / percentage | null=True; blank=True; max_digits=5; decimal_places=2; validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100'))] |
| `fixed_amount_toman` | `PositiveBigIntegerField` | مبلغ ثابت تخفیف به تومان / fixed amount toman | null=True; blank=True; validators=[MinValueValidator(1)] |
| `minimum_order_toman` | `PositiveBigIntegerField` | حداقل مبلغ سفارش به تومان / minimum order toman | default=0 |
| `maximum_discount_toman` | `PositiveBigIntegerField` | حداکثر مبلغ تخفیف به تومان / maximum discount toman | null=True; blank=True; validators=[MinValueValidator(1)] |
| `scope` | `CharField` | دامنه تخفیف / scope | default=Scope.ALL; max_length=20; choices=Scope.choices |
| `products` | `ManyToManyField` | محصولات مشمول تخفیف / products | → products.Product; blank=True |
| `categories` | `ManyToManyField` | دسته‌بندی‌های مشمول تخفیف / categories | → categories.Category; blank=True |
| `start_at` | `DateTimeField` | زمان شروع / start at | default=timezone.now |
| `end_at` | `DateTimeField` | زمان پایان / end at | null=True; blank=True |
| `usage_limit` | `PositiveIntegerField` | حداکثر تعداد استفاده / usage limit | null=True; blank=True; validators=[MinValueValidator(1)] |
| `usage_limit_per_user` | `PositiveIntegerField` | حداکثر استفاده هر کاربر / usage limit per user | null=True; blank=True; validators=[MinValueValidator(1)] |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `DiscountUsage`

**Status:** `USED` = `('used', 'استفاده شده')`; `REVOKED` = `('revoked', 'برگشت داده شده')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `discount` | `ForeignKey` | کد تخفیف / discount | → DiscountCode; on_delete=models.PROTECT |
| `user` | `ForeignKey` | کاربر / user | → settings.AUTH_USER_MODEL; null=True; blank=True; on_delete=models.SET_NULL |
| `reference` | `CharField` | مرجع استفاده / reference | unique=True; max_length=150 |
| `code_snapshot` | `CharField` | نسخه کد تخفیف / code snapshot | max_length=50 |
| `subtotal_toman` | `PositiveBigIntegerField` | مبلغ سبد قبل از تخفیف / subtotal toman | — |
| `eligible_subtotal_toman` | `PositiveBigIntegerField` | مبلغ مشمول تخفیف / eligible subtotal toman | — |
| `discount_amount_toman` | `PositiveBigIntegerField` | مبلغ تخفیف / discount amount toman | — |
| `status` | `CharField` | وضعیت / status | default=Status.USED; max_length=20; choices=Status.choices |
| `used_at` | `DateTimeField` | زمان استفاده / used at | auto_now_add=True |
| `revoked_at` | `DateTimeField` | زمان برگشت / revoked at | null=True; blank=True |

### `motorcycles`

#### `MotorcycleBrand`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `name` | `CharField` | نام برند / name | unique=True; max_length=150 |
| `slug` | `SlugField` | اسلاگ / slug | blank=True; unique=True; max_length=180 |
| `logo` | `ImageField` | لوگو / logo | null=True; blank=True; validators=[validate_image] |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `MotorcycleModel`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `brand` | `ForeignKey` | برند موتورسیکلت / brand | → MotorcycleBrand; on_delete=models.PROTECT |
| `name` | `CharField` | مدل / name | max_length=150 |
| `slug` | `SlugField` | اسلاگ / slug | blank=True; unique=True; max_length=180 |
| `production_start_year` | `PositiveIntegerField` | سال شروع تولید / production start year | null=True; blank=True |
| `production_end_year` | `PositiveIntegerField` | سال پایان تولید / production end year | null=True; blank=True |
| `engine_volume` | `PositiveIntegerField` | حجم موتور / engine volume | null=True; blank=True; validators=[MinValueValidator(1)]; حجم موتور بر حسب CC |
| `description` | `TextField` | توضیحات / description | blank=True |
| `image` | `ImageField` | تصویر / image | null=True; blank=True; validators=[validate_image] |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

### `orders`

#### `Order`

**Status:** `PENDING_PAYMENT` = `('pending_payment', 'در انتظار پرداخت')`; `PROCESSING` = `('processing', 'در حال پردازش')`; `PACKING` = `('packing', 'در حال بسته‌بندی')`; `SHIPPED` = `('shipped', 'ارسال شده')`; `DELIVERED` = `('delivered', 'تحویل شده')`; `CANCELLED` = `('cancelled', 'لغو شده')`; `EXPIRED` = `('expired', 'منقضی شده')`

**PaymentStatus:** `UNPAID` = `('unpaid', 'پرداخت نشده')`; `PENDING` = `('pending', 'در انتظار نتیجه پرداخت')`; `PAID` = `('paid', 'پرداخت شده')`; `FAILED` = `('failed', 'پرداخت ناموفق')`; `REFUNDED` = `('refunded', 'بازپرداخت کامل')`; `PARTIALLY_REFUNDED` = `('partially_refunded', 'بازپرداخت جزئی')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `order_number` | `CharField` | شماره سفارش / order number | unique=True; max_length=50; editable=False |
| `user` | `ForeignKey` | کاربر / user | → settings.AUTH_USER_MODEL; on_delete=models.PROTECT |
| `status` | `CharField` | وضعیت سفارش / status | default=Status.PENDING_PAYMENT; max_length=30; choices=Status.choices |
| `payment_status` | `CharField` | وضعیت پرداخت / payment status | default=PaymentStatus.UNPAID; max_length=30; choices=PaymentStatus.choices |
| `address` | `ForeignKey` | آدرس اصلی / address | → addresses.Address; null=True; blank=True; on_delete=models.SET_NULL |
| `shipping_first_name` | `CharField` | نام گیرنده / shipping first name | max_length=150 |
| `shipping_last_name` | `CharField` | نام خانوادگی گیرنده / shipping last name | max_length=150 |
| `shipping_mobile_number` | `CharField` | موبایل گیرنده / shipping mobile number | max_length=20 |
| `shipping_phone_number` | `CharField` | تلفن گیرنده / shipping phone number | blank=True; max_length=20 |
| `shipping_province_name` | `CharField` | استان / shipping province name | max_length=150 |
| `shipping_city_name` | `CharField` | شهر / shipping city name | max_length=150 |
| `shipping_postal_code` | `CharField` | کد پستی / shipping postal code | max_length=20 |
| `shipping_postal_address` | `TextField` | آدرس پستی / shipping postal address | — |
| `shipping_method` | `ForeignKey` | روش ارسال / shipping method | → shipping.ShippingMethod; null=True; blank=True; on_delete=models.SET_NULL |
| `shipping_method_code` | `CharField` | کد روش ارسال / shipping method code | max_length=100 |
| `shipping_method_name` | `CharField` | نام روش ارسال / shipping method name | max_length=150 |
| `shipping_provider` | `CharField` | شرکت حمل‌ونقل / shipping provider | max_length=50 |
| `shipping_service_code` | `CharField` | کد سرویس ارسال / shipping service code | max_length=100 |
| `shipping_weight_grams` | `PositiveIntegerField` | وزن مرسوله به گرم / shipping weight grams | — |
| `shipping_provider_data` | `JSONField` | اطلاعات محاسبه ارسال / shipping provider data | blank=True; default=dict |
| `discount` | `ForeignKey` | کد تخفیف / discount | → discounts.DiscountCode; null=True; blank=True; on_delete=models.SET_NULL |
| `discount_code` | `CharField` | کد تخفیف Snapshot / discount code | blank=True; max_length=50 |
| `discount_type` | `CharField` | نوع تخفیف / discount type | blank=True; max_length=30 |
| `discount_scope` | `CharField` | دامنه تخفیف / discount scope | blank=True; max_length=30 |
| `subtotal_toman` | `PositiveBigIntegerField` | جمع کالاها به تومان / subtotal toman | — |
| `eligible_discount_subtotal_toman` | `PositiveBigIntegerField` | جمع مبلغ مشمول تخفیف / eligible discount subtotal toman | default=0 |
| `discount_amount_toman` | `PositiveBigIntegerField` | مبلغ تخفیف به تومان / discount amount toman | default=0 |
| `shipping_amount_toman` | `PositiveBigIntegerField` | هزینه ارسال به تومان / shipping amount toman | — |
| `total_toman` | `PositiveBigIntegerField` | مبلغ نهایی به تومان / total toman | — |
| `customer_note` | `CharField` | توضیحات مشتری / customer note | blank=True; max_length=1000 |
| `terms_accepted_at` | `DateTimeField` | زمان پذیرش قوانین / terms accepted at | — |
| `stock_reserved_at` | `DateTimeField` | زمان رزرو موجودی / stock reserved at | null=True; blank=True |
| `stock_released_at` | `DateTimeField` | زمان آزادسازی موجودی / stock released at | null=True; blank=True |
| `expires_at` | `DateTimeField` | مهلت پرداخت / expires at | — |
| `paid_at` | `DateTimeField` | زمان پرداخت / paid at | null=True; blank=True |
| `cancelled_at` | `DateTimeField` | زمان لغو / cancelled at | null=True; blank=True |
| `shipped_at` | `DateTimeField` | زمان ارسال / shipped at | null=True; blank=True |
| `delivered_at` | `DateTimeField` | زمان تحویل / delivered at | null=True; blank=True |
| `created_at` | `DateTimeField` | تاریخ ثبت / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `OrderItem`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `order` | `ForeignKey` | سفارش / order | → Order; on_delete=models.CASCADE |
| `product` | `ForeignKey` | محصول / product | → products.Product; on_delete=models.PROTECT |
| `product_id_snapshot` | `PositiveBigIntegerField` | شناسه محصول Snapshot / product id snapshot | — |
| `product_name` | `CharField` | نام محصول / product name | max_length=250 |
| `product_slug` | `CharField` | Slug محصول / product slug | blank=True; max_length=280 |
| `product_sku` | `CharField` | SKU / product sku | blank=True; max_length=100 |
| `product_brand_name` | `CharField` | برند محصول / product brand name | blank=True; max_length=150 |
| `product_unit` | `CharField` | واحد محصول / product unit | max_length=30 |
| `unit_price_toman` | `PositiveBigIntegerField` | قیمت واحد به تومان / unit price toman | — |
| `quantity` | `PositiveIntegerField` | تعداد / quantity | — |
| `total_price_toman` | `PositiveBigIntegerField` | قیمت کل به تومان / total price toman | — |

### `payments`

#### `PaymentAttempt`

**Provider:** `ZARINPAL` = `('zarinpal', 'زرین‌پال')`; `TCART` = `('tcart', 'TCart')`

**Status:** `CREATED` = `('created', 'ایجاد شده')`; `PENDING` = `('pending', 'در انتظار پرداخت')`; `SUCCEEDED` = `('succeeded', 'موفق')`; `FAILED` = `('failed', 'ناموفق')`; `CANCELLED` = `('cancelled', 'لغوشده')`; `EXPIRED` = `('expired', 'منقضی')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `public_id` | `UUIDField` | شناسه عمومی / public id | unique=True; default=uuid.uuid4; editable=False |
| `order` | `ForeignKey` | سفارش / order | → orders.Order; on_delete=models.PROTECT |
| `provider` | `CharField` | روش پرداخت / provider | max_length=30; choices=Provider.choices |
| `status` | `CharField` | وضعیت پرداخت / status | default=Status.CREATED; max_length=30; choices=Status.choices |
| `amount_toman` | `PositiveBigIntegerField` | مبلغ سفارش به تومان / amount toman | — |
| `provider_amount` | `PositiveBigIntegerField` | مبلغ Provider / provider amount | — |
| `provider_currency` | `CharField` | واحد پول Provider / provider currency | max_length=10 |
| `provider_adjustment_toman` | `IntegerField` | تعدیل مبلغ Provider به تومان / provider adjustment toman | default=0 |
| `provider_reference` | `CharField` | شناسه Provider / provider reference | blank=True; max_length=255 |
| `provider_transaction_id` | `CharField` | شماره تراکنش Provider / provider transaction id | blank=True; max_length=255 |
| `provider_session_id` | `CharField` | شناسه Session Provider / provider session id | blank=True; max_length=255 |
| `gateway_url` | `URLField` | آدرس پرداخت / gateway url | blank=True; max_length=1000 |
| `idempotency_key` | `CharField` | کلید Idempotency / idempotency key | unique=True; max_length=100 |
| `request_payload` | `JSONField` | اطلاعات درخواست / request payload | blank=True; default=dict |
| `response_payload` | `JSONField` | پاسخ Provider / response payload | blank=True; default=dict |
| `callback_payload` | `JSONField` | اطلاعات Callback / callback payload | blank=True; default=dict |
| `failure_code` | `CharField` | کد خطا / failure code | blank=True; max_length=100 |
| `failure_message` | `CharField` | پیام خطا / failure message | blank=True; max_length=1000 |
| `started_at` | `DateTimeField` | زمان شروع پرداخت / started at | null=True; blank=True |
| `expires_at` | `DateTimeField` | مهلت پرداخت / expires at | — |
| `verified_at` | `DateTimeField` | زمان تایید پرداخت / verified at | null=True; blank=True |
| `failed_at` | `DateTimeField` | زمان شکست پرداخت / failed at | null=True; blank=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `PaymentRefund`

**Status:** `CREATED` = `('created', 'ایجاد شده')`; `PENDING` = `('pending', 'در انتظار نتیجه')`; `SUCCEEDED` = `('succeeded', 'موفق')`; `FAILED` = `('failed', 'ناموفق')`; `REQUIRES_REVIEW` = `('requires_review', 'نیازمند بررسی')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `public_id` | `UUIDField` | شناسه عمومی بازپرداخت / public id | unique=True; default=uuid.uuid4; editable=False |
| `order` | `ForeignKey` | سفارش / order | → orders.Order; on_delete=models.PROTECT |
| `payment_attempt` | `ForeignKey` | پرداخت اصلی / payment attempt | → PaymentAttempt; on_delete=models.PROTECT |
| `provider` | `CharField` | Provider پرداخت / provider | max_length=30; choices=PaymentAttempt.Provider.choices |
| `status` | `CharField` | وضعیت بازپرداخت / status | default=Status.CREATED; max_length=30; choices=Status.choices |
| `amount_toman` | `PositiveBigIntegerField` | مبلغ بازپرداخت به تومان / amount toman | — |
| `provider_amount` | `PositiveBigIntegerField` | مبلغ Provider / provider amount | null=True; blank=True |
| `provider_currency` | `CharField` | واحد پول Provider / provider currency | blank=True; max_length=10 |
| `provider_session_id` | `CharField` | شناسه Session Provider / provider session id | blank=True; max_length=255 |
| `provider_refund_id` | `CharField` | شناسه بازپرداخت Provider / provider refund id | blank=True; max_length=255 |
| `idempotency_key` | `CharField` | کلید Idempotency / idempotency key | unique=True; max_length=100 |
| `reason` | `CharField` | دلیل بازپرداخت / reason | blank=True; max_length=100 |
| `description` | `CharField` | توضیحات بازپرداخت / description | blank=True; max_length=500 |
| `request_payload` | `JSONField` | درخواست بازپرداخت / request payload | blank=True; default=dict |
| `response_payload` | `JSONField` | پاسخ بازپرداخت / response payload | blank=True; default=dict |
| `failure_code` | `CharField` | کد خطا / failure code | blank=True; max_length=100 |
| `failure_message` | `CharField` | پیام خطا / failure message | blank=True; max_length=1000 |
| `requested_at` | `DateTimeField` | زمان ارسال درخواست بازپرداخت / requested at | null=True; blank=True |
| `completed_at` | `DateTimeField` | زمان تکمیل بازپرداخت / completed at | null=True; blank=True |
| `failed_at` | `DateTimeField` | زمان شکست بازپرداخت / failed at | null=True; blank=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

### `pricing`

#### `ExchangeRate`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `currency` | `CharField` | ارز / currency | default=USD; max_length=3 |
| `rate_toman` | `PositiveBigIntegerField` | نرخ به تومان / rate toman | validators=[MinValueValidator(1)] |
| `is_active` | `BooleanField` | نرخ فعال / is active | default=False |
| `effective_at` | `DateTimeField` | زمان اعمال نرخ / effective at | default=timezone.now |
| `note` | `CharField` | یادداشت / note | blank=True; max_length=500 |
| `created_by` | `ForeignKey` | ثبت‌کننده / created by | → settings.AUTH_USER_MODEL; null=True; blank=True; editable=False; on_delete=models.SET_NULL |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `PricingSettings`

**RoundingMode:** `NEAREST` = `('nearest', 'نزدیک‌ترین مقدار')`; `UP` = `('up', 'رو به بالا')`; `DOWN` = `('down', 'رو به پایین')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `rounding_step_toman` | `PositiveIntegerField` | گام گردکردن قیمت به تومان / rounding step toman | default=1000; validators=[MinValueValidator(1)] |
| `rounding_mode` | `CharField` | روش گردکردن قیمت / rounding mode | default=RoundingMode.NEAREST; max_length=20; choices=RoundingMode.choices |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

### `products`

#### `Product`

**Status:** `DRAFT` = `('draft', 'پیش‌نویس')`; `ACTIVE` = `('active', 'فعال')`; `ARCHIVED` = `('archived', 'آرشیو شده')`

**PricingMode:** `USD_BASED` = `('usd_based', 'بر اساس دلار')`; `FIXED` = `('fixed', 'قیمت ثابت')`

**Unit:** `PIECE` = `('piece', 'عدد')`; `PAIR` = `('pair', 'جفت')`; `SET` = `('set', 'ست')`; `PACKAGE` = `('package', 'بسته')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `name` | `CharField` | نام محصول / name | max_length=250 |
| `slug` | `SlugField` | اسلاگ / slug | blank=True; unique=True; max_length=280 |
| `category` | `ForeignKey` | دسته‌بندی / category | → categories.Category; on_delete=models.PROTECT |
| `brand` | `ForeignKey` | برند محصول / brand | → brands.Brand; null=True; blank=True; on_delete=models.PROTECT |
| `unit` | `CharField` | واحد فروش / unit | default=Unit.PIECE; max_length=20; choices=Unit.choices |
| `sku` | `CharField` | SKU / sku | null=True; blank=True; unique=True; max_length=100 |
| `manufacturer_part_number` | `CharField` | شماره فنی سازنده / manufacturer part number | blank=True; max_length=150 |
| `oem_code` | `CharField` | کد OEM / oem code | blank=True; max_length=150 |
| `barcode` | `CharField` | بارکد / barcode | null=True; blank=True; unique=True; max_length=100 |
| `short_description` | `CharField` | توضیح کوتاه / short description | blank=True; max_length=500 |
| `description` | `TextField` | توضیحات کامل / description | blank=True |
| `search_keywords` | `TextField` | کلمات کلیدی جستجو / search keywords | blank=True; عبارت‌های مترادف و جایگزین برای بهبود جستجوی محصول |
| `pricing_mode` | `CharField` | روش قیمت‌گذاری / pricing mode | default=PricingMode.FIXED; max_length=20; choices=PricingMode.choices |
| `base_price_usd` | `DecimalField` | قیمت پایه دلاری / base price usd | null=True; blank=True; max_digits=14; decimal_places=4; validators=[MinValueValidator(Decimal('0.0001'))] |
| `base_price_toman` | `PositiveBigIntegerField` | قیمت پایه به تومان / base price toman | null=True; blank=True; validators=[MinValueValidator(1)] |
| `markup_percent` | `DecimalField` | درصد افزایش قیمت / markup percent | default=Decimal('0'); max_digits=7; decimal_places=3; validators=[MinValueValidator(Decimal('0'))] |
| `fixed_cost_toman` | `PositiveBigIntegerField` | هزینه ثابت اضافی به تومان / fixed cost toman | default=0 |
| `current_price_toman` | `PositiveBigIntegerField` | قیمت نهایی فعلی به تومان / current price toman | null=True; blank=True; editable=False |
| `last_exchange_rate_toman` | `PositiveBigIntegerField` | آخرین نرخ دلار استفاده‌شده / last exchange rate toman | null=True; blank=True; editable=False |
| `price_updated_at` | `DateTimeField` | آخرین بروزرسانی قیمت / price updated at | null=True; blank=True; editable=False |
| `is_price_locked` | `BooleanField` | قفل قیمت / is price locked | default=False |
| `stock_quantity` | `PositiveIntegerField` | موجودی / stock quantity | default=0 |
| `low_stock_threshold` | `PositiveIntegerField` | حد هشدار موجودی / low stock threshold | default=3 |
| `weight_grams` | `PositiveIntegerField` | وزن به گرم / weight grams | null=True; blank=True |
| `length_cm` | `DecimalField` | طول به سانتی‌متر / length cm | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `width_cm` | `DecimalField` | عرض به سانتی‌متر / width cm | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `height_cm` | `DecimalField` | ارتفاع به سانتی‌متر / height cm | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `shipping_length_cm` | `DecimalField` | طول بسته برای ارسال (cm) / shipping length cm | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))]; طول واقعی محصول پس از آماده‌سازی برای ارسال. برای انتخاب خودکار بسته تیپاکس استفاده می‌شود. |
| `shipping_width_cm` | `DecimalField` | عرض بسته برای ارسال (cm) / shipping width cm | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `shipping_height_cm` | `DecimalField` | ارتفاع بسته برای ارسال (cm) / shipping height cm | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `compatible_motorcycles` | `ManyToManyField` | موتورسیکلت‌های سازگار / compatible motorcycles | → motorcycles.MotorcycleModel; blank=True |
| `related_products` | `ManyToManyField` | محصولات مرتبط / related products | → self; blank=True |
| `meta_title` | `CharField` | عنوان SEO / meta title | blank=True; max_length=250 |
| `meta_description` | `CharField` | توضیحات SEO / meta description | blank=True; max_length=320 |
| `status` | `CharField` | وضعیت / status | default=Status.DRAFT; max_length=20; choices=Status.choices |
| `is_featured` | `BooleanField` | محصول ویژه / is featured | default=False |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `ProductImage`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `product` | `ForeignKey` | محصول / product | → Product; on_delete=models.CASCADE |
| `image` | `ImageField` | تصویر / image | validators=[validate_image] |
| `alt_text` | `CharField` | متن جایگزین تصویر / alt text | blank=True; max_length=250 |
| `is_primary` | `BooleanField` | تصویر اصلی / is primary | default=False |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش / sort order | default=0 |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |

#### `ProductAttribute`

**DataType:** `TEXT` = `('text', 'متن')`; `NUMBER` = `('number', 'عدد')`; `BOOLEAN` = `('boolean', 'بله / خیر')`; `CHOICE` = `('choice', 'انتخابی')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `name` | `CharField` | نام ویژگی / name | unique=True; max_length=150 |
| `slug` | `SlugField` | اسلاگ / slug | blank=True; unique=True; max_length=180 |
| `data_type` | `CharField` | نوع داده / data type | max_length=20; choices=DataType.choices |
| `unit` | `CharField` | واحد / unit | blank=True; max_length=50 |
| `is_filterable` | `BooleanField` | قابل فیلتر / is filterable | default=False |
| `is_searchable` | `BooleanField` | قابل جستجو / is searchable | default=False |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش / sort order | default=0 |
| `categories` | `ManyToManyField` | دسته‌بندی‌ها / categories | → categories.Category; blank=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `ProductAttributeOption`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `attribute` | `ForeignKey` | ویژگی / attribute | → ProductAttribute; on_delete=models.CASCADE |
| `value` | `CharField` | مقدار / value | max_length=150 |
| `slug` | `SlugField` | اسلاگ / slug | blank=True; max_length=180 |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش / sort order | default=0 |
| `is_active` | `BooleanField` | فعال / is active | default=True |

#### `CategoryAttribute`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `category` | `ForeignKey` | دسته‌بندی / category | → categories.Category; on_delete=models.CASCADE |
| `attribute` | `ForeignKey` | ویژگی / attribute | → ProductAttribute; on_delete=models.CASCADE |
| `is_required` | `BooleanField` | الزامی / is required | default=False |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش / sort order | default=0 |

#### `ProductAttributeValue`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `product` | `ForeignKey` | محصول / product | → Product; on_delete=models.CASCADE |
| `attribute` | `ForeignKey` | ویژگی / attribute | → ProductAttribute; on_delete=models.PROTECT |
| `value_text` | `TextField` | مقدار متنی / value text | blank=True |
| `value_number` | `DecimalField` | مقدار عددی / value number | null=True; blank=True; max_digits=18; decimal_places=4 |
| `value_boolean` | `BooleanField` | مقدار بله / خیر / value boolean | null=True; blank=True |
| `option` | `ForeignKey` | گزینه انتخاب‌شده / option | → ProductAttributeOption; null=True; blank=True; on_delete=models.PROTECT |

#### `ProductCompatibility`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `product` | `ForeignKey` | محصول / product | → Product; on_delete=models.CASCADE |
| `motorcycle` | `ForeignKey` | مدل موتورسیکلت / motorcycle | → motorcycles.MotorcycleModel; on_delete=models.PROTECT |
| `compatible_start_year` | `PositiveIntegerField` | سال شروع سازگاری / compatible start year | null=True; blank=True |
| `compatible_end_year` | `PositiveIntegerField` | سال پایان سازگاری / compatible end year | null=True; blank=True |
| `note` | `CharField` | توضیح سازگاری / note | blank=True; max_length=500 |

#### `ProductRelation`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `product` | `ForeignKey` | محصول / product | → Product; on_delete=models.CASCADE |
| `related_product` | `ForeignKey` | محصول مرتبط / related product | → Product; on_delete=models.CASCADE |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش / sort order | default=0 |

### `shipping`

#### `TipaxSettings`

**PaymentType:** `SENDER_CREDIT` = `(10, 'سمت فرستنده - اعتباری')`; `RECEIVER_POSTPAID` = `(20, 'سمت گیرنده - پس‌کرایه')`; `RECEIVER_COD` = `(30, 'سمت گیرنده - پرداخت در محل')`; `SENDER_COD_WITH_CREDIT` = `(40, 'سمت فرستنده - پرداخت در محل از اعتبار')`; `SENDER_WALLET` = `(50, 'سمت فرستنده - پرداخت از کیف پول')`; `SENDER_CASH` = `(80, 'سمت فرستنده - نقدی')`; `SENDER_BRANCH_CREDIT` = `(90, 'سمت فرستنده - اعتبار نمایندگی')`; `CASH_AND_PAY_IN_PLACE` = `(100, 'نقدی - پس‌کرایه')`

**PickupType:** `CUSTOMER_LOCATION` = `(10, 'جمع‌آوری در محل مشتری')`; `BRANCH` = `(20, 'تحویل در نمایندگی')`

**DistributionType:** `CUSTOMER_LOCATION` = `(10, 'تحویل در محل گیرنده')`; `BRANCH` = `(20, 'تحویل در نمایندگی')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `payment_type` | `PositiveSmallIntegerField` | نوع پرداخت هزینه تیپاکس / payment type | default=PaymentType.SENDER_CREDIT; choices=PaymentType.choices |
| `pickup_type` | `PositiveSmallIntegerField` | نوع جمع‌آوری / pickup type | default=PickupType.CUSTOMER_LOCATION; choices=PickupType.choices |
| `distribution_type` | `PositiveSmallIntegerField` | نوع تحویل / distribution type | default=DistributionType.CUSTOMER_LOCATION; choices=DistributionType.choices |
| `default_service_id` | `PositiveSmallIntegerField` | سرویس پیش‌فرض تیپاکس / default service id | default=2 |
| `enable_label_privacy` | `BooleanField` | مخفی کردن اطلاعات روی لیبل / enable label privacy | default=False |
| `customer_substation_code` | `CharField` | کد شعبه مشتری / customer substation code | blank=True; max_length=100 |
| `customer_id` | `PositiveBigIntegerField` | Customer ID در تیپاکس / customer id | null=True; blank=True |
| `sender_full_name` | `CharField` | نام کامل فرستنده / sender full name | blank=True; max_length=250 |
| `sender_mobile` | `CharField` | موبایل فرستنده / sender mobile | blank=True; max_length=20 |
| `sender_phone` | `CharField` | تلفن فرستنده / sender phone | blank=True; max_length=20 |
| `origin_full_address` | `TextField` | آدرس کامل مبدا / origin full address | blank=True |
| `origin_postal_code` | `CharField` | کد پستی مبدا / origin postal code | blank=True; max_length=20 |
| `origin_floor` | `CharField` | طبقه مبدا / origin floor | blank=True; max_length=20 |
| `origin_unit` | `CharField` | واحد مبدا / origin unit | blank=True; max_length=20 |
| `origin_no` | `CharField` | پلاک مبدا / origin no | blank=True; max_length=30 |
| `origin_latitude` | `CharField` | Latitude مبدا / origin latitude | blank=True; max_length=50 |
| `origin_longitude` | `CharField` | Longitude مبدا / origin longitude | blank=True; max_length=50 |
| `origin_description` | `CharField` | توضیحات مبدا / origin description | blank=True; max_length=500 |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `ShippingSettings`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `origin_city` | `ForeignKey` | شهر مبدا ارسال / origin city | → addresses.City; null=True; blank=True; on_delete=models.PROTECT |
| `package_extra_weight_grams` | `PositiveIntegerField` | وزن اضافه بسته‌بندی به گرم / package extra weight grams | default=150 |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `ShippingMethod`

**Provider:** `POST` = `('post', 'شرکت ملی پست')`; `TIPAX` = `('tipax', 'تیپاکس')`; `CUSTOM` = `('custom', 'سفارشی')`

**CalculationMode:** `MANUAL` = `('manual', 'تعرفه دستی')`; `API` = `('api', 'API')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `code` | `SlugField` | کد روش ارسال / code | unique=True; max_length=100 |
| `name` | `CharField` | نام روش ارسال / name | max_length=150 |
| `provider` | `CharField` | شرکت حمل‌ونقل / provider | max_length=20; choices=Provider.choices |
| `service_code` | `CharField` | کد سرویس / service code | max_length=100 |
| `calculation_mode` | `CharField` | روش محاسبه هزینه / calculation mode | default=CalculationMode.MANUAL; max_length=20; choices=CalculationMode.choices |
| `description` | `CharField` | توضیحات / description | blank=True; max_length=500 |
| `estimated_min_days` | `PositiveSmallIntegerField` | حداقل زمان تحویل به روز / estimated min days | null=True; blank=True |
| `estimated_max_days` | `PositiveSmallIntegerField` | حداکثر زمان تحویل به روز / estimated max days | null=True; blank=True |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش / sort order | default=0 |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `ShippingRateRule`

**DestinationScope:** `NATIONWIDE` = `('nationwide', 'کل کشور')`; `PROVINCE` = `('province', 'استان')`; `CITY` = `('city', 'شهر')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `method` | `ForeignKey` | روش ارسال / method | → ShippingMethod; on_delete=models.CASCADE |
| `destination_scope` | `CharField` | محدوده مقصد / destination scope | default=DestinationScope.NATIONWIDE; max_length=20; choices=DestinationScope.choices |
| `province` | `ForeignKey` | استان مقصد / province | → addresses.Province; null=True; blank=True; on_delete=models.CASCADE |
| `city` | `ForeignKey` | شهر مقصد / city | → addresses.City; null=True; blank=True; on_delete=models.CASCADE |
| `min_weight_grams` | `PositiveIntegerField` | حداقل وزن به گرم / min weight grams | default=0 |
| `max_weight_grams` | `PositiveIntegerField` | حداکثر وزن به گرم / max weight grams | null=True; blank=True |
| `base_price_toman` | `PositiveBigIntegerField` | هزینه پایه به تومان / base price toman | validators=[MinValueValidator(0)] |
| `included_weight_grams` | `PositiveIntegerField` | وزن شامل هزینه پایه به گرم / included weight grams | default=1000 |
| `additional_per_kg_toman` | `PositiveBigIntegerField` | هزینه هر کیلو اضافه به تومان / additional per kg toman | default=0 |
| `priority` | `IntegerField` | اولویت / priority | default=0 |
| `effective_from` | `DateTimeField` | شروع اعتبار تعرفه / effective from | default=timezone.now |
| `effective_to` | `DateTimeField` | پایان اعتبار تعرفه / effective to | null=True; blank=True |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `note` | `CharField` | یادداشت / note | blank=True; max_length=500 |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `ShippingProviderCityMap`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `provider` | `CharField` | شرکت حمل‌ونقل / provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `city` | `ForeignKey` | شهر / city | → addresses.City; on_delete=models.CASCADE |
| `provider_city_id` | `PositiveBigIntegerField` | شناسه شهر در Provider / provider city id | — |
| `provider_city_name` | `CharField` | نام شهر در Provider / provider city name | blank=True; max_length=150 |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی / updated at | auto_now=True |

#### `TipaxPackageProfile`

**PackType:** `ENVELOPE` = `(10, 'پاکت')`; `PACKAGE` = `(20, 'بسته')`; `MINI_PACK` = `(50, 'مینی پک')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `title` | `CharField` | عنوان / title | max_length=150 |
| `min_weight_grams` | `PositiveIntegerField` | حداقل وزن به گرم / min weight grams | default=0 |
| `max_weight_grams` | `PositiveIntegerField` | حداکثر وزن به گرم / max weight grams | null=True; blank=True |
| `length` | `DecimalField` | طول بسته / length | max_digits=8; decimal_places=2 |
| `width` | `DecimalField` | عرض بسته / width | max_digits=8; decimal_places=2 |
| `height` | `DecimalField` | ارتفاع بسته / height | max_digits=8; decimal_places=2 |
| `packing_id` | `PositiveIntegerField` | Packing ID / packing id | default=0 |
| `package_content_id` | `PositiveIntegerField` | Package Content ID / package content id | — |
| `pack_type` | `PositiveSmallIntegerField` | نوع بسته Tipax / pack type | default=20; شناسه نوع بسته در Tipax. برای بسته معمولی فروشگاه مقدار 20 استفاده می‌شود. |
| `parcel_type_id` | `PositiveIntegerField` | Parcel Type ID / parcel type id | default=0 |
| `is_unusual` | `BooleanField` | بسته نامتعارف / is unusual | default=False |
| `priority` | `IntegerField` | اولویت / priority | default=0 |
| `is_active` | `BooleanField` | فعال / is active | default=True |

#### `Shipment`

**Status:** `CREATED` = `('created', 'ایجاد شده')`; `REGISTERED` = `('registered', 'ثبت اولیه')`; `PROCESSING` = `('processing', 'در حال پردازش')`; `WAITING_PICKUP` = `('waiting_pickup', 'در انتظار جمع‌آوری')`; `COLLECTED` = `('collected', 'جمع‌آوری شده')`; `SHIPPED` = `('shipped', 'در حال ارسال')`; `DELIVERED` = `('delivered', 'تحویل شده')`; `RETURNED` = `('returned', 'عودت شده')`; `CANCELLED` = `('cancelled', 'ابطال شده')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `order` | `ForeignKey` | سفارش / order | → orders.Order; on_delete=models.PROTECT |
| `shipping_method` | `ForeignKey` | روش ارسال / shipping method | → ShippingMethod; null=True; blank=True; on_delete=models.SET_NULL |
| `provider` | `CharField` | Provider / provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `status` | `CharField` | وضعیت / status | default=Status.CREATED; max_length=30; choices=Status.choices |
| `external_order_id` | `CharField` | Order ID Provider / external order id | blank=True; max_length=150 |
| `tracking_codes` | `JSONField` | کدهای رهگیری / tracking codes | blank=True; default=list |
| `primary_tracking_code` | `CharField` | کد رهگیری اصلی / primary tracking code | blank=True; max_length=150 |
| `provider_status_id` | `CharField` | کد وضعیت Provider / provider status id | blank=True; max_length=50 |
| `provider_status_name` | `CharField` | وضعیت Provider / provider status name | blank=True; max_length=250 |
| `quoted_amount_toman` | `PositiveBigIntegerField` | هزینه برآوردشده / quoted amount toman | null=True; blank=True |
| `final_amount_toman` | `PositiveBigIntegerField` | هزینه نهایی / final amount toman | null=True; blank=True |
| `request_payload` | `JSONField` | درخواست Provider / request payload | blank=True; default=dict |
| `response_payload` | `JSONField` | پاسخ Provider / response payload | blank=True; default=dict |
| `tracking_payload` | `JSONField` | آخرین پاسخ رهگیری / tracking payload | blank=True; default=dict |
| `cancelled_at` | `DateTimeField` | زمان ابطال / cancelled at | null=True; blank=True |
| `created_at` | `DateTimeField` | created at / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at / updated at | auto_now=True |

#### `ShippingOrigin`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `title` | `CharField` | عنوان مبدا / title | max_length=120 |
| `province` | `ForeignKey` | استان / province | → Province; on_delete=models.PROTECT |
| `city` | `ForeignKey` | شهر / city | → City; on_delete=models.PROTECT |
| `postal_address` | `TextField` | آدرس / postal address | blank=True; default= |
| `postal_code` | `CharField` | کد پستی / postal code | blank=True; default=; max_length=10 |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `is_default` | `BooleanField` | مبدا پیش‌فرض / is default | default=False |
| `created_at` | `DateTimeField` | created at / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at / updated at | auto_now=True |

#### `ShippingProviderProvince`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `provider` | `CharField` | provider / provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `provider_province_id` | `CharField` | provider province id / provider province id | max_length=64 |
| `name` | `CharField` | name / name | blank=True; default=; max_length=150 |
| `is_active` | `BooleanField` | is active / is active | default=True |
| `raw_data` | `JSONField` | raw data / raw data | blank=True; default=dict |
| `created_at` | `DateTimeField` | created at / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at / updated at | auto_now=True |

#### `ShippingProviderCity`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `provider` | `CharField` | provider / provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `provider_city_id` | `CharField` | provider city id / provider city id | max_length=64 |
| `provider_province_id` | `CharField` | provider province id / provider province id | blank=True; default=; max_length=64 |
| `name` | `CharField` | name / name | max_length=150 |
| `provider_uuid` | `CharField` | provider uuid / provider uuid | blank=True; default=; max_length=100 |
| `latitude` | `DecimalField` | latitude / latitude | null=True; blank=True; max_digits=12; decimal_places=8 |
| `longitude` | `DecimalField` | longitude / longitude | null=True; blank=True; max_digits=12; decimal_places=8 |
| `is_active` | `BooleanField` | is active / is active | default=True |
| `raw_data` | `JSONField` | raw data / raw data | blank=True; default=dict |
| `created_at` | `DateTimeField` | created at / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at / updated at | auto_now=True |

#### `ShippingProviderPackingOption`

**Kind:** `CARTON` = `('carton', 'کارتن')`; `BUBBLE` = `('bubble', 'نایلون حبابدار')`; `ENVELOPE` = `('envelope', 'پاکت')`; `SACK` = `('sack', 'گونی')`; `FLYER` = `('flyer', 'فلایر')`; `NO_PACKING` = `('no_packing', 'بدون بسته‌بندی')`; `OTHER` = `('other', 'سایر')`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `provider` | `CharField` | provider / provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `provider_packing_id` | `PositiveBigIntegerField` | provider packing id / provider packing id | — |
| `title` | `CharField` | title / title | max_length=200 |
| `kind` | `CharField` | kind / kind | default=Kind.OTHER; max_length=30; choices=Kind.choices |
| `box_number` | `PositiveSmallIntegerField` | box number / box number | null=True; blank=True |
| `pack_type` | `PositiveIntegerField` | pack type / pack type | null=True; blank=True |
| `length` | `DecimalField` | length / length | null=True; blank=True; max_digits=8; decimal_places=2 |
| `width` | `DecimalField` | width / width | null=True; blank=True; max_digits=8; decimal_places=2 |
| `height` | `DecimalField` | height / height | null=True; blank=True; max_digits=8; decimal_places=2 |
| `min_weight` | `DecimalField` | min weight / min weight | null=True; blank=True; max_digits=8; decimal_places=2 |
| `max_weight` | `DecimalField` | max weight / max weight | null=True; blank=True; max_digits=8; decimal_places=2 |
| `min_length` | `DecimalField` | min length / min length | null=True; blank=True; max_digits=8; decimal_places=2 |
| `max_length` | `DecimalField` | max length / max length | null=True; blank=True; max_digits=8; decimal_places=2 |
| `min_width` | `DecimalField` | min width / min width | null=True; blank=True; max_digits=8; decimal_places=2 |
| `max_width` | `DecimalField` | max width / max width | null=True; blank=True; max_digits=8; decimal_places=2 |
| `min_height` | `DecimalField` | min height / min height | null=True; blank=True; max_digits=8; decimal_places=2 |
| `max_height` | `DecimalField` | max height / max height | null=True; blank=True; max_digits=8; decimal_places=2 |
| `provider_price` | `DecimalField` | provider price / provider price | null=True; blank=True; max_digits=18; decimal_places=3 |
| `is_active` | `BooleanField` | is active / is active | default=True |
| `raw_data` | `JSONField` | raw data / raw data | blank=True; default=dict |
| `created_at` | `DateTimeField` | created at / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at / updated at | auto_now=True |

#### `ShippingProviderProvinceMap`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `provider` | `CharField` | provider / provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `province` | `ForeignKey` | province / province | → addresses.Province; on_delete=models.CASCADE |
| `provider_province_id` | `CharField` | provider province id / provider province id | max_length=64 |
| `provider_province_name` | `CharField` | provider province name / provider province name | blank=True; default=; max_length=150 |
| `is_active` | `BooleanField` | is active / is active | default=True |
| `created_at` | `DateTimeField` | created at / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at / updated at | auto_now=True |

#### `ShippingProviderOriginMap`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `provider` | `CharField` | Provider / provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `origin` | `ForeignKey` | مبدا ارسال / origin | → ShippingOrigin; on_delete=models.CASCADE |
| `provider_address_id` | `PositiveBigIntegerField` | شناسه آدرس در Provider / provider address id | — |
| `provider_address_title` | `CharField` | عنوان آدرس در Provider / provider address title | blank=True; max_length=250 |
| `is_active` | `BooleanField` | فعال / is active | default=True |
| `raw_data` | `JSONField` | اطلاعات خام Provider / raw data | blank=True; default=dict |
| `created_at` | `DateTimeField` | created at / created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at / updated at | auto_now=True |

### `wishlists`

#### `WishlistItem`

| Field | نوع / Type | توضیح / Meaning | قواعد / Rules |
|---|---|---|---|
| `user` | `ForeignKey` | کاربر / user | → settings.AUTH_USER_MODEL; on_delete=models.CASCADE |
| `product` | `ForeignKey` | محصول / product | → products.Product; on_delete=models.CASCADE |
| `created_at` | `DateTimeField` | تاریخ افزودن / created at | auto_now_add=True |


<a id="api-routes"></a>
## مسیرهای API | API routes

مسیرهای زیر از URLconf استخراج شده‌اند. routerها برای resource ثبت‌شده مسیر collection/detail تولید می‌کنند؛ method، permission، pagination، query parameters و فیلدهای read-only را از serializer، view و Swagger بررسی کنید. `pricing` در تنظیمات نصب است ولی URLconf اصلی آن را include نمی‌کند. `inventory` نیز route فعال در core ندارد.
Routes below follow URLconf. Routers generate collection/detail routes; consult views/serializers/Swagger for methods, permissions, pagination and writable fields. Pricing is installed but its API URLconf is not included by core. Inventory is not exposed by core.

| App | Prefix | Paths / router resources |
|---|---|---|
| `accounts` | `/api/v1/accounts/` | `send-otp/`, `verify-otp/`, `complete-profile/`, `me/`, `token/refresh/`, `logout/` |
| `addresses` | `/api/v1/locations/` | `provinces/`, `provinces/<int:province_id>/cities/`, `addresses/`, `addresses/<int:pk>/`, `addresses/<int:pk>/set-default/` |
| `articles` | `/api/v1/articles/` | `categories/`, `categories/<int:pk>/`, `articles/`, `articles/featured/`, `articles/<str:identifier>/` |
| `brands` | `/api/v1/brands/` | `brands` (router) |
| `carts` | `/api/v1/` | `cart/`, `cart/items/`, `cart/items/<int:product_id>/`, `cart/clear/`, `cart/discount/` |
| `categories` | `/api/v1/` | `categories` (router) |
| `contact` | `/api/v1/contact/` | ``, `admin/`, `admin/<int:pk>/` |
| `discounts` | `/api/v1/` | `discount-codes` (router), `discounts/validate/` |
| `motorcycles` | `/api/v1/motorcycles/` | `motorcycle-brands` (router), `motorcycles` (router) |
| `orders` | `/api/v1/` | `orders/`, `orders/<str:order_number>/cancel/`, `orders/<str:order_number>/` |
| `payments` | `/api/v1/` | `payments/start/`, `payments/<uuid:public_id>/`, `payments/zarinpal/callback/<uuid:public_id>/`, `payments/tcart/callback/<uuid:public_id>/`, `payments/refunds/`, `payments/refunds/<uuid:public_id>/`, `payments/refunds/<uuid:public_id>/execute/` |
| `products` | `/api/v1/` | `products` (router), `product-images` (router), `product-attributes` (router) |
| `shipping` | `/api/v1/` | `shipping-methods` (router), `shipping-rate-rules` (router), `shipping/quotes/` |
| `wishlists` | `/api/v1/` | `wishlist/`, `wishlist/product-ids/`, `wishlist/<int:product_id>/` |

### نمونه فراخوانی | Request examples

```bash
curl -X POST http://127.0.0.1:8000/api/v1/accounts/send-otp/ \
  -H 'Content-Type: application/json' \
  -d '{"phone_number":"09123456789"}'

curl http://127.0.0.1:8000/api/v1/accounts/me/ \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

در توسعه بدون OTP sender، نمونه اول الزاماً کد واقعی ارسال نمی‌کند. برای verify و checkout فیلدهای دقیق request را از Swagger بررسی کنید. نوشتن مستقیم در دیتابیس برای شبیه‌سازی پرداخت یا دورزدن validation جای تست جریان API نیست.
Without a configured OTP sender, the first example does not deliver an SMS. Use Swagger for verify/checkout request fields and test through the actual service/API flow.
