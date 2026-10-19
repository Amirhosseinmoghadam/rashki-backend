# بک‌اند رشکی — راهنمای فارسی

[English documentation](README.md)

مستند مستقل راه‌اندازی و مدیریت پروژه بر پایه کامیت `7226186` شاخه `main`.

## مسیر مطالعه

۱. بخش سیستم‌عامل خود را انتخاب کنید. ۲. محیط مجازی و `.env` را بسازید. ۳. PostgreSQL و Redis را روشن کنید. ۴. اتصال، migration و تست را اجرا کنید. ۵. مدیر و داده فروشگاه بسازید. ۶. سرور و فرمان‌های نگهداری را اجرا کنید.

- [راهنمای مشترک پروژه](#project-guide)
- [اپ‌ها و مدل‌ها](#apps-and-models)
- [متغیرهای محیطی](#environment-variables)
- [فرهنگ کامل فیلدها](#model-field-reference)
- [مسیرهای API](#api-routes)

## راه‌اندازی بر اساس سیستم‌عامل

از یکی از مسیرها استفاده کنید؛ سرویس بومی و Docker را روی پورت یکسان هم‌زمان اجرا نکنید. به‌جز نصب ابزار و سرویس‌ها، دستورات پروژه با کاربر عادی اجرا می‌شوند.

### شروع از صفر روی macOS

Terminal را باز کنید. ابزارهای Apple را نصب کنید و نصب پنجره بازشده را تمام کنید:

```bash
xcode-select --install
```

اگر Homebrew ندارید، دستور نصب رسمی [brew.sh](https://brew.sh/) را اجرا کنید و دستورهای `shellenv` چاپ‌شده در پایان نصب را انجام دهید؛ مسیر Homebrew در Apple Silicon و Intel متفاوت است. سپس:

```bash
brew install git python@3.12 postgresql@16 redis
python3.12 --version
git --version
```

از بخش «دریافت کد» این فایل شروع کنید و مسیر A سرویس‌ها را اجرا کنید. اگر Docker می‌خواهید، [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/) را برای معماری دستگاه نصب و برنامه را باز کنید؛ سپس مسیر B را انجام دهید. بعد از نصب Python یا Git ممکن است لازم باشد Terminal را دوباره باز کنید.

### شروع از صفر روی Windows 10/11 — PowerShell

۱. [Python 3.12](https://www.python.org/downloads/windows/) را برای معماری سیستم نصب کنید؛ گزینه افزودن Python به PATH و Python launcher را فعال کنید. [Git for Windows](https://git-scm.com/downloads/win) را نصب کنید.
۲. [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) را نصب کنید، الزامات virtualization و WSL 2 صفحه رسمی را انجام دهید و Docker Desktop را باز کنید. برای این مسیر Redis و PostgreSQL هر دو داخل Docker هستند؛ نیازی به نصب Redis بومی Windows نیست.
۳. PowerShell جدید باز کنید و بررسی کنید:

```powershell
py -3.12 --version
git --version
docker version
docker compose version
```

از اینجا دستورهای Windows را در PowerShell اجرا کنید، نه cmd یا Git Bash:

```powershell
git clone https://github.com/Amirhosseinmoghadam/rashki-backend.git
cd rashki-backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
Copy-Item .env.example .env
notepad .env
```

اگر اجرای Activate.ps1 با ExecutionPolicy رد شد، فقط برای همین session اجرا کنید و دوباره فعال‌سازی را انجام دهید:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

سه کلید مستقل با دستور تولید secret در بخش تنظیمات بسازید. `Copy-Item` فقط برای بار اول است؛ فایل موجود را جایگزین نکنید. در `.env` آدرس‌های زیر با Compose پروژه سازگارند:

```dotenv
DATABASE_URL=postgresql://rashki:rashki_dev@127.0.0.1:5432/rashki
REDIS_URL=redis://127.0.0.1:6379/1
```

```powershell
docker compose up -d --wait db
docker run -d --name rashki-redis -p 127.0.0.1:6379:6379 redis:7
docker exec rashki-redis redis-cli ping
```

سپس بخش «بررسی اتصال، migration، مدیر و تست‌ها» را به ترتیب اجرا کنید؛ دستورهای `python manage.py` در PowerShell نیز معتبرند. در دفعات بعد:

```powershell
cd PATH_TO_PROJECT
.\.venv\Scripts\Activate.ps1
docker compose up -d --wait db
docker start rashki-redis
python manage.py runserver
```

**مسیر جایگزین PostgreSQL بومی:** installer رسمی [PostgreSQL Windows](https://www.postgresql.org/download/windows/) نسخه 16 را نصب کنید. از SQL Shell (psql) با کاربر postgres متصل شوید، سپس دستورهای ساخت role/database بخش Linux را اجرا کنید و URL را با رمز انتخابی یکسان کنید. Redis همچنان با Docker اجرا شود. PostgreSQL بومی و Compose را روی پورت 5432 هم‌زمان اجرا نکنید.

**مسیر WSL:** پس از نصب WSL/Ubuntu می‌توانید کل پروژه و سرویس‌ها را داخل Ubuntu طبق راهنمای Linux اجرا کنید. پوشه پروژه و `.venv` را داخل همان محیط بسازید؛ محیط مجازی Windows را داخل WSL استفاده نکنید. برای این مسیر دستورها در ترمینال Ubuntu هستند، نه PowerShell.

### شروع از صفر روی Linux — Ubuntu 24.04 LTS

دستورهای apt زیر مشخصاً برای Ubuntu 24.04 هستند. در Debian، Fedora و سایر توزیع‌ها نام بسته‌ها و نسخه Python متفاوت است؛ راهنمای عمومی Docker پایین، مسیر قابل استفاده روی توزیع‌های پشتیبانی‌شده است.

```bash
sudo apt update
sudo apt install -y git python3.12 python3.12-venv python3-pip postgresql-16 postgresql-client-16 redis-server
sudo systemctl enable --now postgresql
sudo systemctl enable --now redis-server
python3.12 --version
git --version
redis-cli ping
sudo -u postgres psql
```

```sql
CREATE ROLE rashki LOGIN CREATEDB;
\password rashki
CREATE DATABASE rashki OWNER rashki;
\q
```

داخل psql، دستور `\password` رمز را تعاملی می‌گیرد؛ آن را در `DATABASE_URL` استفاده کنید. ساخت role/database فقط بار اول است. اگر role قبلاً وجود دارد، آن را دوباره نسازید؛ با مدیر دیتابیس اختیار `CREATEDB` و رمز آن را بررسی کنید. اکنون بخش دریافت کد را اجرا کنید:

```bash
git clone https://github.com/Amirhosseinmoghadam/rashki-backend.git
cd rashki-backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
cp .env.example .env
nano .env
```

سه کلید مستقل را تنظیم کنید و سپس بخش migration و تست را انجام دهید. Ubuntu ممکن است نسخه Redis متفاوت از Redis 7 در CI نصب کند؛ برای برابری نسخه سرویس با CI از کانتینر `redis:7` استفاده کنید.

**Linux با Docker:** [Docker Engine](https://docs.docker.com/engine/install/) و افزونه Compose را طبق توزیع نصب کنید. Python 3.12، venv و Git نیز روی host لازم‌اند چون Compose فقط دیتابیس را اجرا می‌کند. اگر کاربر اجازه Docker ندارد، دستورهای Docker را با `sudo` اجرا کنید؛ عضویت در گروه docker دسترسی مدیریتی به host می‌دهد. سپس مسیر B سرویس‌ها و دستورهای نصب/راه‌اندازی پروژه را اجرا کنید. برای Docker Desktop نیز صفحه رسمی توزیع مربوط را دنبال کنید.

**بدون systemd / در WSL:** اگر `systemctl` پشتیبانی نمی‌شود، در محیطی که سرویس‌های Ubuntu نصب‌اند از `sudo service postgresql start` و `sudo service redis-server start` استفاده کنید، یا systemd را طبق راهنمای محیط فعال کنید.

<a id="project-guide"></a>
## راهنمای مشترک پروژه


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

### اجرای مستقیم Redis روی مک و نقش آن در OTP

در روش فعلی شما PostgreSQL و Redis **هم‌زمان** روشن می‌مانند. PostgreSQL کاربران و رکوردهای `OTPCode` را نگه می‌دارد؛ در رکورد OTP فقط HMAC کد، زمان انقضا، تعداد تلاش‌ها و وضعیت مصرف ذخیره می‌شود. Redis از طریق Django cache، شمارنده‌های موقت ارسال/تأیید و فاصله ارسال مجدد را بر اساس شماره و IP نگه می‌دارد تا ارسال پیامک و تلاش حدس کد محدود شود.

روی مک Apple Silicon که Homebrew در `/opt/homebrew` نصب است، Redis را در یک ترمینال مستقل اجرا کنید:

```bash
/opt/homebrew/bin/redis-server
```

این اجرا foreground است؛ ترمینال را باز نگه دارید. در ترمینال دوم اتصال را بررسی کنید و PostgreSQL را روشن کنید:

```bash
/opt/homebrew/bin/redis-cli ping
brew services start postgresql@16
```

پاسخ Redis باید `PONG` باشد. سپس در ترمینال پروژه محیط مجازی را فعال و Django را اجرا کنید:

```bash
source .venv/bin/activate
python manage.py runserver
```

در `.env` مقدار `REDIS_URL=redis://127.0.0.1:6379/1` و URL PostgreSQL صحیح باقی بمانند. اجرای مستقیم جایگزین `brew services start redis` است؛ هر دو را هم‌زمان اجرا نکنید. اگر Redis قبلاً به‌صورت service فعال است و می‌خواهید به روش مستقیم بروید، ابتدا `brew services stop redis` بزنید. با `Ctrl+C` Redis مستقیم متوقف می‌شود. مسیر `/opt/homebrew` مخصوص نصب معمول Apple Silicon است؛ برای یافتن مسیر در نصب دیگر از `"$(brew --prefix redis)/bin/redis-server"` استفاده کنید.

| محدودیت OTP | پیش‌فرض کد |
|---|---|
| فاصله ارسال مجدد برای هر شماره | ۶۰ ثانیه |
| تعداد ارسال برای هر شماره | ۵ در یک پنجره یک‌ساعته |
| تعداد ارسال برای هر IP | ۳۰ در پنجره ۱۰ دقیقه‌ای |
| درخواست تأیید برای هر شماره | ۲۰ در پنجره ۱۰ دقیقه‌ای |
| درخواست تأیید برای هر IP | ۶۰ در پنجره ۱۰ دقیقه‌ای |
| طول و اعتبار کد | ۶ رقم، ۱۲۰ ثانیه |
| سقف تلاش هر رکورد OTP | ۵ تلاش |

این پیش‌فرض‌ها با متغیرهای `AUTH_OTP_*` جدول تنظیمات تغییر می‌کنند. محدودیت هر رکورد و انقضا در PostgreSQL، و محدودیت درخواست‌ها در Redis اعمال می‌شوند. این سازوکار ارسال را محدود می‌کند؛ تضمین جلوگیری از تمام حملات توزیع‌شده یا عبور نکردن از سقف در درخواست‌های هم‌زمان نیست، چون بررسی و افزایش چند شمارنده در کد فعلی یک عملیات واحد اتمیک نیست. `AUTH_TRUST_X_FORWARDED_FOR` یک setting Python با پیش‌فرض False است؛ فقط با proxy قابل اعتماد و پاک‌سازی هدر ورودی آن را تنظیم کنید تا IP قابل جعل نباشد. پاک‌کردن Redis یا ازدست‌رفتن داده آن شمارنده‌ها را بازنشانی می‌کند، اما رکورد OTP در PostgreSQL باقی می‌ماند.

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
git diff -- README.md README.fa.md
git add README.md README.fa.md
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


### نگهداری روزانه و زمان‌بندی در Windows

در هر ترمینال جدید ابتدا وارد ریشه پروژه شوید، محیط مجازی را فعال و سرویس‌ها را روشن کنید. `.env` و مدیر را هر بار از نو نسازید. برای اجرای دوره‌ای انقضا در Task Scheduler یک task با کاربر خود بسازید؛ trigger را هر یک دقیقه تکرار کنید. Program را `C:\path\rashki-backend\.venv\Scripts\python.exe`، Arguments را `manage.py expire_unpaid_orders` و Start in را `C:\path\rashki-backend` قرار دهید. مسیرها را با مسیر واقعی جایگزین کنید. PostgreSQL و Redis باید در زمان اجرای task فعال باشند.

### فرمان‌های production در PowerShell

```powershell
$env:DJANGO_SETTINGS_MODULE = "core.settings.production"
python manage.py check --deploy
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

این بخش چک‌لیست تنظیمات است، نه دستور استقرار کامل روی هر میزبان. Gunicorn برای Unix است؛ برای Windows یک WSGI/ASGI server سازگار یا کانتینر Linux انتخاب کنید. مدیریت process، TLS، reverse proxy و backup به میزبان انتخابی وابسته است. برای برگشت به development از `Remove-Item Env:DJANGO_SETTINGS_MODULE` در PowerShell یا `unset DJANGO_SETTINGS_MODULE` در Bash استفاده کنید.

<a id="apps-and-models"></a>
## اپ‌ها و مدل‌ها

| اپ | کاربرد | مدل‌ها |
|---|---|---|
| `accounts` | کاربران، OTP و JWT | `User`, `OTPCode` |
| `addresses` | استان، شهر و آدرس گیرنده | `Province`, `City`, `Address` |
| `articles` | مقالات، دسته مقاله و SEO | `ArticleCategory`, `Article` |
| `brands` | برند سازنده قطعه | `Brand` |
| `carts` | سبد کاربر، اقلام و تخفیف | `Cart`, `CartItem` |
| `categories` | دسته‌بندی سلسله‌مراتبی کالا | `Category` |
| `contact` | درخواست تماس و استعلام | `ContactRequest` |
| `discounts` | کد تخفیف، دامنه و سابقه مصرف | `DiscountCode`, `DiscountUsage` |
| `motorcycles` | برند و مدل موتورسیکلت | `MotorcycleBrand`, `MotorcycleModel` |
| `orders` | سفارش، snapshot اقلام و رزرو موجودی | `Order`, `OrderItem` |
| `payments` | تلاش پرداخت و بازپرداخت | `PaymentAttempt`, `PaymentRefund` |
| `pricing` | نرخ ارز و قواعد محاسبه قیمت | `ExchangeRate`, `PricingSettings` |
| `products` | کالا، تصویر، ویژگی و سازگاری | `Product`, `ProductImage`, `ProductAttribute`, `ProductAttributeOption`, `CategoryAttribute`, `ProductAttributeValue`, `ProductCompatibility`, `ProductRelation` |
| `shipping` | روش، تعرفه، مبدا، catalog و مرسوله | `TipaxSettings`, `ShippingSettings`, `ShippingMethod`, `ShippingRateRule`, `ShippingProviderCityMap`, `TipaxPackageProfile`, `Shipment`, `ShippingOrigin`, `ShippingProviderProvince`, `ShippingProviderCity`, `ShippingProviderPackingOption`, `ShippingProviderProvinceMap`, `ShippingProviderOriginMap` |
| `wishlists` | علاقه‌مندی کاربر | `WishlistItem` |


<a id="environment-variables"></a>
## متغیرهای محیطی

جدول از settings استخراج شده است؛ پیش‌فرض‌ها بر اساس نام فایل تنظیمات نمایش داده شده‌اند. `.env.example` همه متغیرها را ندارد.

| Variable | پیش‌فرض با منبع |
|---|---|
| `ALLOWED_HOSTS` | `production.py`: `[]`; `development.py`: `['localhost', '127.0.0.1']` |
| `AUTH_OTP_EXPIRE_SECONDS` | `base.py`: `120` |
| `AUTH_OTP_HMAC_KEY` | `base.py`: `اجباری` |
| `AUTH_OTP_IP_WINDOW_SECONDS` | `base.py`: `10 * 60` |
| `AUTH_OTP_LENGTH` | `base.py`: `6` |
| `AUTH_OTP_MAX_ATTEMPTS` | `base.py`: `5` |
| `AUTH_OTP_MAX_SENDS_PER_HOUR` | `base.py`: `5` |
| `AUTH_OTP_MAX_SENDS_PER_IP_WINDOW` | `base.py`: `30` |
| `AUTH_OTP_MAX_VERIFY_PER_IP_WINDOW` | `base.py`: `60` |
| `AUTH_OTP_MAX_VERIFY_PER_WINDOW` | `base.py`: `20` |
| `AUTH_OTP_RESEND_SECONDS` | `base.py`: `60` |
| `AUTH_OTP_VERIFY_IP_WINDOW_SECONDS` | `base.py`: `10 * 60` |
| `AUTH_OTP_VERIFY_WINDOW_SECONDS` | `base.py`: `10 * 60` |
| `CONTACT_THROTTLE_RATE` | `base.py`: `'5/hour'` |
| `CORS_ALLOWED_ORIGINS` | `production.py`: `[]`; `development.py`: `['http://localhost:5173', 'http://127.0.0.1:5173']` |
| `CSRF_TRUSTED_ORIGINS` | `production.py`: `[]`; `development.py`: `['http://localhost:5173', 'http://127.0.0.1:5173']` |
| `DATABASE_URL` | `production.py`: `''`; `production.py`: `اجباری`; `development.py`: `f"sqlite:///{BASE_DIR / 'db.sqlite3'}"` |
| `DB_CONN_MAX_AGE` | `production.py`: `60` |
| `DJANGO_SECRET_KEY` | `base.py`: `اجباری` |
| `JWT_ACCESS_MINUTES` | `base.py`: `180` |
| `JWT_REFRESH_DAYS` | `base.py`: `30` |
| `JWT_SIGNING_KEY` | `base.py`: `اجباری` |
| `MAX_IMAGE_PIXEL_COUNT` | `base.py`: `40000000` |
| `MAX_IMAGE_UPLOAD_SIZE` | `base.py`: `10 * 1024 * 1024` |
| `MELIPAYAMAK_API_TOKEN` | `production.py`: `اجباری`; `base.py`: `''` |
| `MELIPAYAMAK_DEFAULT_FROM` | `production.py`: `اجباری`; `base.py`: `''` |
| `PAYMENT_FAILED_REDIRECT_URL` | `base.py`: `'http://localhost:5173/payment/failed'` |
| `PAYMENT_HTTP_TIMEOUT_SECONDS` | `base.py`: `'15'` |
| `PAYMENT_SUCCESS_REDIRECT_URL` | `base.py`: `'http://localhost:5173/payment/success'` |
| `REDIS_URL` | `production.py`: `''`; `development.py`: `'redis://127.0.0.1:6379/1'` |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `production.py`: `False` |
| `SECURE_HSTS_PRELOAD` | `production.py`: `False` |
| `SECURE_HSTS_SECONDS` | `production.py`: `3600` |
| `SECURE_SSL_REDIRECT` | `production.py`: `True` |
| `TCART_API_TOKEN` | `base.py`: `''` |
| `TCART_CREATE_INVOICE_URL` | `base.py`: `''` |
| `TCART_INVOICE_STATUS_URL` | `base.py`: `''` |
| `TCART_WEBHOOK_SECRET` | `base.py`: `''` |
| `TIPAX_ACCESS_TOKEN` | `base.py`: `''` |
| `TIPAX_AMOUNT_DIVISOR_TO_TOMAN` | `base.py`: `'1'` |
| `TIPAX_API_KEY` | `base.py`: `''` |
| `TIPAX_BASE_URL` | `base.py`: `'https://omtestapi.tipax.ir'` |
| `TIPAX_HTTP_TIMEOUT_SECONDS` | `base.py`: `'20'` |
| `TIPAX_PASSWORD` | `base.py`: `''` |
| `TIPAX_REFRESH_TOKEN` | `base.py`: `''` |
| `TIPAX_USERNAME` | `base.py`: `''` |
| `TRUST_X_FORWARDED_PROTO` | `production.py`: `False` |
| `ZARINPAL_GATEWAY_URL` | `base.py`: `'https://www.zarinpal.com/pg/StartPay/'` |
| `ZARINPAL_MERCHANT_ID` | `base.py`: `''` |
| `ZARINPAL_PROVIDER_CURRENCY` | `base.py`: `'IRT'` |
| `ZARINPAL_REQUEST_URL` | `base.py`: `'https://api.zarinpal.com/pg/v4/payment/request.json'` |
| `ZARINPAL_VERIFY_URL` | `base.py`: `'https://api.zarinpal.com/pg/v4/payment/verify.json'` |

`AUTH_OTP_SENDER`، `AUTH_OTP_DEBUG_RETURN_CODE`، `ORDER_PAYMENT_TIMEOUT_MINUTES` و `ZARINPAL_SANDBOX` تنظیمات Python هستند و صرفاً با افزودن به env فعال نمی‌شوند. divisor تیپاکس در کد 1 و در env نمونه 10 است؛ واحد واقعی Provider را بررسی کنید.

<a id="model-field-reference"></a>
## فرهنگ کامل فیلدهای مدل

این بخش فیلدهای صریح مدل‌های نصب‌شده را پوشش می‌دهد؛ فیلد مدل با payload قابل‌نوشتن API یکسان نیست. serializerها و Swagger منبع قرارداد درخواست/پاسخ‌اند. `id` ضمنی از نوع BigAutoField است؛ `User` علاوه بر این جدول فیلدهای ارثی password، last_login، is_superuser، groups و user_permissions دارد. default یک callable نمایش نام تابع است، نه مقدار ثابت. blank مربوط به validation و null مربوط به ذخیره دیتابیس است. تاریخ‌های خودکار و `editable=False` را عموماً سرویس مدیریت می‌کند.

### `accounts`

#### `User`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `phone_number` | `CharField` | Phone Number | unique=True; max_length=11; validators=[validate_iran_mobile] |
| `first_name` | `CharField` | First Name | blank=True; max_length=100 |
| `last_name` | `CharField` | Last Name | blank=True; max_length=100 |
| `is_phone_verified` | `BooleanField` | Phone Verified | default=False |
| `is_active` | `BooleanField` | Active | default=True |
| `is_staff` | `BooleanField` | Staff Status | default=False |
| `date_joined` | `DateTimeField` | Date Joined | default=timezone.now |
| `created_at` | `DateTimeField` | Created At | auto_now_add=True |
| `updated_at` | `DateTimeField` | Updated At | auto_now=True |

#### `OTPCode`

**OTPPurpose:** `AUTH` = `auth`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `phone_number` | `CharField` | Phone Number | max_length=11; validators=[validate_iran_mobile] |
| `code_hash` | `CharField` | Code Hash | max_length=128 |
| `purpose` | `CharField` | Purpose | default=OTPPurpose.AUTH; max_length=20; choices=OTPPurpose.choices |
| `attempts` | `PositiveSmallIntegerField` | Attempts | default=0 |
| `max_attempts` | `PositiveSmallIntegerField` | Max Attempts | default=5 |
| `is_used` | `BooleanField` | Used | default=False |
| `expires_at` | `DateTimeField` | Expires At | — |
| `created_at` | `DateTimeField` | Created At | auto_now_add=True |

### `addresses`

#### `Province`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `name` | `CharField` | Name | unique=True; max_length=100 |

#### `City`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `province` | `ForeignKey` | Province | → Province; on_delete=models.CASCADE |
| `name` | `CharField` | Name | max_length=150 |

#### `Address`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `user` | `ForeignKey` | User | → User; on_delete=models.CASCADE |
| `first_name` | `CharField` | نام | null=True; blank=True; max_length=100 |
| `last_name` | `CharField` | نام خانوادگی | null=True; blank=True; max_length=100 |
| `mobile_number` | `CharField` | شماره موبایل | null=True; blank=True; max_length=11; validators=[RegexValidator(regex='^09[0-9]{9}$', message='شماره موبایل نامعتبر است.')] |
| `phone_number` | `CharField` | شماره تلفن ثابت | null=True; blank=True; max_length=11; validators=[RegexValidator(regex='^[0-9]{11}$', message='شماره تلفن باید 11 رقم باشد.')] |
| `province` | `ForeignKey` | استان | → Province; on_delete=models.PROTECT |
| `city` | `ForeignKey` | شهر | → City; on_delete=models.PROTECT |
| `postal_code` | `CharField` | کد پستی | null=True; blank=True; max_length=10; validators=[RegexValidator(regex='^[0-9]{10}$', message='کد پستی باید 10 رقم باشد.')] |
| `postal_address` | `TextField` | آدرس پستی | null=True; blank=True |
| `is_default` | `BooleanField` | آدرس پیش‌فرض | default=False |
| `created_at` | `DateTimeField` | Created At | auto_now_add=True |
| `updated_at` | `DateTimeField` | Updated At | auto_now=True |

### `articles`

#### `ArticleCategory`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `name` | `CharField` | نام | unique=True; max_length=150 |
| `slug` | `SlugField` | slug | unique=True; max_length=180 |
| `description` | `TextField` | description | blank=True |
| `is_active` | `BooleanField` | is active | default=True |

#### `Article`

**Status:** `DRAFT` = `draft`; `PUBLISHED` = `published`; `ARCHIVED` = `archived`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `title` | `CharField` | عنوان | max_length=255 |
| `slug` | `SlugField` | اسلاگ | unique=True; max_length=280 |
| `excerpt` | `TextField` | خلاصه | blank=True |
| `content` | `TextField` | محتوا | — |
| `cover_image` | `ImageField` | تصویر اصلی | null=True; blank=True |
| `category` | `ForeignKey` | دسته‌بندی | → ArticleCategory; on_delete=models.PROTECT |
| `author` | `ForeignKey` | نویسنده | → settings.AUTH_USER_MODEL; on_delete=models.PROTECT |
| `products` | `ManyToManyField` | محصولات مرتبط | → products.Product; blank=True |
| `motorcycles` | `ManyToManyField` | موتورسیکلت‌های مرتبط | → motorcycles.MotorcycleModel; blank=True |
| `status` | `CharField` | وضعیت | default=Status.DRAFT; max_length=20; choices=Status.choices |
| `is_featured` | `BooleanField` | مقاله ویژه | default=False |
| `reading_time` | `PositiveIntegerField` | زمان مطالعه | default=1 |
| `view_count` | `PositiveIntegerField` | تعداد بازدید | default=0 |
| `seo_title` | `CharField` | SEO Title | blank=True; max_length=255 |
| `meta_description` | `CharField` | Meta Description | blank=True; max_length=320 |
| `published_at` | `DateTimeField` | تاریخ انتشار | null=True; blank=True |
| `created_at` | `DateTimeField` | created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at | auto_now=True |

### `brands`

#### `Brand`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `name` | `CharField` | نام برند | unique=True; max_length=150 |
| `slug` | `SlugField` | اسلاگ | blank=True; unique=True; max_length=180 |
| `logo` | `ImageField` | لوگو | null=True; blank=True; validators=[validate_image] |
| `description` | `TextField` | توضیحات | blank=True |
| `website` | `URLField` | وب‌سایت | blank=True |
| `is_active` | `BooleanField` | فعال | default=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

### `carts`

#### `Cart`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `user` | `OneToOneField` | کاربر | → settings.AUTH_USER_MODEL; on_delete=models.CASCADE |
| `applied_discount` | `ForeignKey` | کد تخفیف اعمال‌شده | → discounts.DiscountCode; null=True; blank=True; on_delete=models.SET_NULL |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `CartItem`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `cart` | `ForeignKey` | سبد خرید | → Cart; on_delete=models.CASCADE |
| `product` | `ForeignKey` | محصول | → products.Product; on_delete=models.CASCADE |
| `quantity` | `PositiveIntegerField` | تعداد | default=1; validators=[MinValueValidator(1)] |
| `created_at` | `DateTimeField` | تاریخ افزودن | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

### `categories`

#### `Category`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `name` | `CharField` | نام دسته‌بندی | max_length=150 |
| `slug` | `SlugField` | اسلاگ | blank=True; unique=True; max_length=180 |
| `parent` | `ForeignKey` | دسته والد | → self; null=True; blank=True; on_delete=models.PROTECT |
| `image` | `ImageField` | تصویر | null=True; blank=True; validators=[validate_image] |
| `description` | `TextField` | توضیحات | blank=True |
| `is_active` | `BooleanField` | فعال | default=True |
| `created_at` | `DateTimeField` | created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at | auto_now=True |

### `contact`

#### `ContactRequest`

**Subject:** `WHOLESALE_COOPERATION` = `wholesale_cooperation`; `PRICE_INQUIRY` = `price_inquiry`; `AVAILABILITY_INQUIRY` = `availability_inquiry`; `PRODUCT_QUESTION` = `product_question`; `OTHER` = `other`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `first_name` | `CharField` | نام | max_length=100 |
| `last_name` | `CharField` | نام خانوادگی | max_length=100 |
| `phone_number` | `CharField` | شماره تماس | max_length=11; validators=[phone_validator] |
| `subject` | `CharField` | موضوع درخواست | max_length=50; choices=Subject.choices |
| `description` | `TextField` | توضیحات | max_length=3000 |
| `is_read` | `BooleanField` | خوانده شده | default=False |
| `created_at` | `DateTimeField` | تاریخ ثبت | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

### `discounts`

#### `DiscountCode`

**DiscountType:** `PERCENTAGE` = `percentage`; `FIXED_AMOUNT` = `fixed_amount`

**Scope:** `ALL` = `all`; `PRODUCTS` = `products`; `CATEGORIES` = `categories`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `code` | `CharField` | کد تخفیف | unique=True; max_length=50 |
| `description` | `CharField` | توضیحات | blank=True; max_length=500 |
| `discount_type` | `CharField` | نوع تخفیف | max_length=20; choices=DiscountType.choices |
| `percentage` | `DecimalField` | درصد تخفیف | null=True; blank=True; max_digits=5; decimal_places=2; validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100'))] |
| `fixed_amount_toman` | `PositiveBigIntegerField` | مبلغ ثابت تخفیف به تومان | null=True; blank=True; validators=[MinValueValidator(1)] |
| `minimum_order_toman` | `PositiveBigIntegerField` | حداقل مبلغ سفارش به تومان | default=0 |
| `maximum_discount_toman` | `PositiveBigIntegerField` | حداکثر مبلغ تخفیف به تومان | null=True; blank=True; validators=[MinValueValidator(1)] |
| `scope` | `CharField` | دامنه تخفیف | default=Scope.ALL; max_length=20; choices=Scope.choices |
| `products` | `ManyToManyField` | محصولات مشمول تخفیف | → products.Product; blank=True |
| `categories` | `ManyToManyField` | دسته‌بندی‌های مشمول تخفیف | → categories.Category; blank=True |
| `start_at` | `DateTimeField` | زمان شروع | default=timezone.now |
| `end_at` | `DateTimeField` | زمان پایان | null=True; blank=True |
| `usage_limit` | `PositiveIntegerField` | حداکثر تعداد استفاده | null=True; blank=True; validators=[MinValueValidator(1)] |
| `usage_limit_per_user` | `PositiveIntegerField` | حداکثر استفاده هر کاربر | null=True; blank=True; validators=[MinValueValidator(1)] |
| `is_active` | `BooleanField` | فعال | default=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `DiscountUsage`

**Status:** `USED` = `used`; `REVOKED` = `revoked`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `discount` | `ForeignKey` | کد تخفیف | → DiscountCode; on_delete=models.PROTECT |
| `user` | `ForeignKey` | کاربر | → settings.AUTH_USER_MODEL; null=True; blank=True; on_delete=models.SET_NULL |
| `reference` | `CharField` | مرجع استفاده | unique=True; max_length=150 |
| `code_snapshot` | `CharField` | نسخه کد تخفیف | max_length=50 |
| `subtotal_toman` | `PositiveBigIntegerField` | مبلغ سبد قبل از تخفیف | — |
| `eligible_subtotal_toman` | `PositiveBigIntegerField` | مبلغ مشمول تخفیف | — |
| `discount_amount_toman` | `PositiveBigIntegerField` | مبلغ تخفیف | — |
| `status` | `CharField` | وضعیت | default=Status.USED; max_length=20; choices=Status.choices |
| `used_at` | `DateTimeField` | زمان استفاده | auto_now_add=True |
| `revoked_at` | `DateTimeField` | زمان برگشت | null=True; blank=True |

### `motorcycles`

#### `MotorcycleBrand`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `name` | `CharField` | نام برند | unique=True; max_length=150 |
| `slug` | `SlugField` | اسلاگ | blank=True; unique=True; max_length=180 |
| `logo` | `ImageField` | لوگو | null=True; blank=True; validators=[validate_image] |
| `is_active` | `BooleanField` | فعال | default=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `MotorcycleModel`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `brand` | `ForeignKey` | برند موتورسیکلت | → MotorcycleBrand; on_delete=models.PROTECT |
| `name` | `CharField` | مدل | max_length=150 |
| `slug` | `SlugField` | اسلاگ | blank=True; unique=True; max_length=180 |
| `production_start_year` | `PositiveIntegerField` | سال شروع تولید | null=True; blank=True |
| `production_end_year` | `PositiveIntegerField` | سال پایان تولید | null=True; blank=True |
| `engine_volume` | `PositiveIntegerField` | حجم موتور | null=True; blank=True; validators=[MinValueValidator(1)] |
| `description` | `TextField` | توضیحات | blank=True |
| `image` | `ImageField` | تصویر | null=True; blank=True; validators=[validate_image] |
| `is_active` | `BooleanField` | فعال | default=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

### `orders`

#### `Order`

**Status:** `PENDING_PAYMENT` = `pending_payment`; `PROCESSING` = `processing`; `PACKING` = `packing`; `SHIPPED` = `shipped`; `DELIVERED` = `delivered`; `CANCELLED` = `cancelled`; `EXPIRED` = `expired`

**PaymentStatus:** `UNPAID` = `unpaid`; `PENDING` = `pending`; `PAID` = `paid`; `FAILED` = `failed`; `REFUNDED` = `refunded`; `PARTIALLY_REFUNDED` = `partially_refunded`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `order_number` | `CharField` | شماره سفارش | unique=True; max_length=50; editable=False |
| `user` | `ForeignKey` | کاربر | → settings.AUTH_USER_MODEL; on_delete=models.PROTECT |
| `status` | `CharField` | وضعیت سفارش | default=Status.PENDING_PAYMENT; max_length=30; choices=Status.choices |
| `payment_status` | `CharField` | وضعیت پرداخت | default=PaymentStatus.UNPAID; max_length=30; choices=PaymentStatus.choices |
| `address` | `ForeignKey` | آدرس اصلی | → addresses.Address; null=True; blank=True; on_delete=models.SET_NULL |
| `shipping_first_name` | `CharField` | نام گیرنده | max_length=150 |
| `shipping_last_name` | `CharField` | نام خانوادگی گیرنده | max_length=150 |
| `shipping_mobile_number` | `CharField` | موبایل گیرنده | max_length=20 |
| `shipping_phone_number` | `CharField` | تلفن گیرنده | blank=True; max_length=20 |
| `shipping_province_name` | `CharField` | استان | max_length=150 |
| `shipping_city_name` | `CharField` | شهر | max_length=150 |
| `shipping_postal_code` | `CharField` | کد پستی | max_length=20 |
| `shipping_postal_address` | `TextField` | آدرس پستی | — |
| `shipping_method` | `ForeignKey` | روش ارسال | → shipping.ShippingMethod; null=True; blank=True; on_delete=models.SET_NULL |
| `shipping_method_code` | `CharField` | کد روش ارسال | max_length=100 |
| `shipping_method_name` | `CharField` | نام روش ارسال | max_length=150 |
| `shipping_provider` | `CharField` | شرکت حمل‌ونقل | max_length=50 |
| `shipping_service_code` | `CharField` | کد سرویس ارسال | max_length=100 |
| `shipping_weight_grams` | `PositiveIntegerField` | وزن مرسوله به گرم | — |
| `shipping_provider_data` | `JSONField` | اطلاعات محاسبه ارسال | blank=True; default=dict |
| `discount` | `ForeignKey` | کد تخفیف | → discounts.DiscountCode; null=True; blank=True; on_delete=models.SET_NULL |
| `discount_code` | `CharField` | کد تخفیف Snapshot | blank=True; max_length=50 |
| `discount_type` | `CharField` | نوع تخفیف | blank=True; max_length=30 |
| `discount_scope` | `CharField` | دامنه تخفیف | blank=True; max_length=30 |
| `subtotal_toman` | `PositiveBigIntegerField` | جمع کالاها به تومان | — |
| `eligible_discount_subtotal_toman` | `PositiveBigIntegerField` | جمع مبلغ مشمول تخفیف | default=0 |
| `discount_amount_toman` | `PositiveBigIntegerField` | مبلغ تخفیف به تومان | default=0 |
| `shipping_amount_toman` | `PositiveBigIntegerField` | هزینه ارسال به تومان | — |
| `total_toman` | `PositiveBigIntegerField` | مبلغ نهایی به تومان | — |
| `customer_note` | `CharField` | توضیحات مشتری | blank=True; max_length=1000 |
| `terms_accepted_at` | `DateTimeField` | زمان پذیرش قوانین | — |
| `stock_reserved_at` | `DateTimeField` | زمان رزرو موجودی | null=True; blank=True |
| `stock_released_at` | `DateTimeField` | زمان آزادسازی موجودی | null=True; blank=True |
| `expires_at` | `DateTimeField` | مهلت پرداخت | — |
| `paid_at` | `DateTimeField` | زمان پرداخت | null=True; blank=True |
| `cancelled_at` | `DateTimeField` | زمان لغو | null=True; blank=True |
| `shipped_at` | `DateTimeField` | زمان ارسال | null=True; blank=True |
| `delivered_at` | `DateTimeField` | زمان تحویل | null=True; blank=True |
| `created_at` | `DateTimeField` | تاریخ ثبت | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `OrderItem`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `order` | `ForeignKey` | سفارش | → Order; on_delete=models.CASCADE |
| `product` | `ForeignKey` | محصول | → products.Product; on_delete=models.PROTECT |
| `product_id_snapshot` | `PositiveBigIntegerField` | شناسه محصول Snapshot | — |
| `product_name` | `CharField` | نام محصول | max_length=250 |
| `product_slug` | `CharField` | Slug محصول | blank=True; max_length=280 |
| `product_sku` | `CharField` | SKU | blank=True; max_length=100 |
| `product_brand_name` | `CharField` | برند محصول | blank=True; max_length=150 |
| `product_unit` | `CharField` | واحد محصول | max_length=30 |
| `unit_price_toman` | `PositiveBigIntegerField` | قیمت واحد به تومان | — |
| `quantity` | `PositiveIntegerField` | تعداد | — |
| `total_price_toman` | `PositiveBigIntegerField` | قیمت کل به تومان | — |

### `payments`

#### `PaymentAttempt`

**Provider:** `ZARINPAL` = `zarinpal`; `TCART` = `tcart`

**Status:** `CREATED` = `created`; `PENDING` = `pending`; `SUCCEEDED` = `succeeded`; `FAILED` = `failed`; `CANCELLED` = `cancelled`; `EXPIRED` = `expired`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `public_id` | `UUIDField` | شناسه عمومی | unique=True; default=uuid.uuid4; editable=False |
| `order` | `ForeignKey` | سفارش | → orders.Order; on_delete=models.PROTECT |
| `provider` | `CharField` | روش پرداخت | max_length=30; choices=Provider.choices |
| `status` | `CharField` | وضعیت پرداخت | default=Status.CREATED; max_length=30; choices=Status.choices |
| `amount_toman` | `PositiveBigIntegerField` | مبلغ سفارش به تومان | — |
| `provider_amount` | `PositiveBigIntegerField` | مبلغ Provider | — |
| `provider_currency` | `CharField` | واحد پول Provider | max_length=10 |
| `provider_adjustment_toman` | `IntegerField` | تعدیل مبلغ Provider به تومان | default=0 |
| `provider_reference` | `CharField` | شناسه Provider | blank=True; max_length=255 |
| `provider_transaction_id` | `CharField` | شماره تراکنش Provider | blank=True; max_length=255 |
| `provider_session_id` | `CharField` | شناسه Session Provider | blank=True; max_length=255 |
| `gateway_url` | `URLField` | آدرس پرداخت | blank=True; max_length=1000 |
| `idempotency_key` | `CharField` | کلید Idempotency | unique=True; max_length=100 |
| `request_payload` | `JSONField` | اطلاعات درخواست | blank=True; default=dict |
| `response_payload` | `JSONField` | پاسخ Provider | blank=True; default=dict |
| `callback_payload` | `JSONField` | اطلاعات Callback | blank=True; default=dict |
| `failure_code` | `CharField` | کد خطا | blank=True; max_length=100 |
| `failure_message` | `CharField` | پیام خطا | blank=True; max_length=1000 |
| `started_at` | `DateTimeField` | زمان شروع پرداخت | null=True; blank=True |
| `expires_at` | `DateTimeField` | مهلت پرداخت | — |
| `verified_at` | `DateTimeField` | زمان تایید پرداخت | null=True; blank=True |
| `failed_at` | `DateTimeField` | زمان شکست پرداخت | null=True; blank=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `PaymentRefund`

**Status:** `CREATED` = `created`; `PENDING` = `pending`; `SUCCEEDED` = `succeeded`; `FAILED` = `failed`; `REQUIRES_REVIEW` = `requires_review`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `public_id` | `UUIDField` | شناسه عمومی بازپرداخت | unique=True; default=uuid.uuid4; editable=False |
| `order` | `ForeignKey` | سفارش | → orders.Order; on_delete=models.PROTECT |
| `payment_attempt` | `ForeignKey` | پرداخت اصلی | → PaymentAttempt; on_delete=models.PROTECT |
| `provider` | `CharField` | Provider پرداخت | max_length=30; choices=PaymentAttempt.Provider.choices |
| `status` | `CharField` | وضعیت بازپرداخت | default=Status.CREATED; max_length=30; choices=Status.choices |
| `amount_toman` | `PositiveBigIntegerField` | مبلغ بازپرداخت به تومان | — |
| `provider_amount` | `PositiveBigIntegerField` | مبلغ Provider | null=True; blank=True |
| `provider_currency` | `CharField` | واحد پول Provider | blank=True; max_length=10 |
| `provider_session_id` | `CharField` | شناسه Session Provider | blank=True; max_length=255 |
| `provider_refund_id` | `CharField` | شناسه بازپرداخت Provider | blank=True; max_length=255 |
| `idempotency_key` | `CharField` | کلید Idempotency | unique=True; max_length=100 |
| `reason` | `CharField` | دلیل بازپرداخت | blank=True; max_length=100 |
| `description` | `CharField` | توضیحات بازپرداخت | blank=True; max_length=500 |
| `request_payload` | `JSONField` | درخواست بازپرداخت | blank=True; default=dict |
| `response_payload` | `JSONField` | پاسخ بازپرداخت | blank=True; default=dict |
| `failure_code` | `CharField` | کد خطا | blank=True; max_length=100 |
| `failure_message` | `CharField` | پیام خطا | blank=True; max_length=1000 |
| `requested_at` | `DateTimeField` | زمان ارسال درخواست بازپرداخت | null=True; blank=True |
| `completed_at` | `DateTimeField` | زمان تکمیل بازپرداخت | null=True; blank=True |
| `failed_at` | `DateTimeField` | زمان شکست بازپرداخت | null=True; blank=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

### `pricing`

#### `ExchangeRate`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `currency` | `CharField` | ارز | default=USD; max_length=3 |
| `rate_toman` | `PositiveBigIntegerField` | نرخ به تومان | validators=[MinValueValidator(1)] |
| `is_active` | `BooleanField` | نرخ فعال | default=False |
| `effective_at` | `DateTimeField` | زمان اعمال نرخ | default=timezone.now |
| `note` | `CharField` | یادداشت | blank=True; max_length=500 |
| `created_by` | `ForeignKey` | ثبت‌کننده | → settings.AUTH_USER_MODEL; null=True; blank=True; editable=False; on_delete=models.SET_NULL |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `PricingSettings`

**RoundingMode:** `NEAREST` = `nearest`; `UP` = `up`; `DOWN` = `down`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `rounding_step_toman` | `PositiveIntegerField` | گام گردکردن قیمت به تومان | default=1000; validators=[MinValueValidator(1)] |
| `rounding_mode` | `CharField` | روش گردکردن قیمت | default=RoundingMode.NEAREST; max_length=20; choices=RoundingMode.choices |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

### `products`

#### `Product`

**Status:** `DRAFT` = `draft`; `ACTIVE` = `active`; `ARCHIVED` = `archived`

**PricingMode:** `USD_BASED` = `usd_based`; `FIXED` = `fixed`

**Unit:** `PIECE` = `piece`; `PAIR` = `pair`; `SET` = `set`; `PACKAGE` = `package`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `name` | `CharField` | نام محصول | max_length=250 |
| `slug` | `SlugField` | اسلاگ | blank=True; unique=True; max_length=280 |
| `category` | `ForeignKey` | دسته‌بندی | → categories.Category; on_delete=models.PROTECT |
| `brand` | `ForeignKey` | برند محصول | → brands.Brand; null=True; blank=True; on_delete=models.PROTECT |
| `unit` | `CharField` | واحد فروش | default=Unit.PIECE; max_length=20; choices=Unit.choices |
| `sku` | `CharField` | SKU | null=True; blank=True; unique=True; max_length=100 |
| `manufacturer_part_number` | `CharField` | شماره فنی سازنده | blank=True; max_length=150 |
| `oem_code` | `CharField` | کد OEM | blank=True; max_length=150 |
| `barcode` | `CharField` | بارکد | null=True; blank=True; unique=True; max_length=100 |
| `short_description` | `CharField` | توضیح کوتاه | blank=True; max_length=500 |
| `description` | `TextField` | توضیحات کامل | blank=True |
| `search_keywords` | `TextField` | کلمات کلیدی جستجو | blank=True |
| `pricing_mode` | `CharField` | روش قیمت‌گذاری | default=PricingMode.FIXED; max_length=20; choices=PricingMode.choices |
| `base_price_usd` | `DecimalField` | قیمت پایه دلاری | null=True; blank=True; max_digits=14; decimal_places=4; validators=[MinValueValidator(Decimal('0.0001'))] |
| `base_price_toman` | `PositiveBigIntegerField` | قیمت پایه به تومان | null=True; blank=True; validators=[MinValueValidator(1)] |
| `markup_percent` | `DecimalField` | درصد افزایش قیمت | default=Decimal('0'); max_digits=7; decimal_places=3; validators=[MinValueValidator(Decimal('0'))] |
| `fixed_cost_toman` | `PositiveBigIntegerField` | هزینه ثابت اضافی به تومان | default=0 |
| `current_price_toman` | `PositiveBigIntegerField` | قیمت نهایی فعلی به تومان | null=True; blank=True; editable=False |
| `last_exchange_rate_toman` | `PositiveBigIntegerField` | آخرین نرخ دلار استفاده‌شده | null=True; blank=True; editable=False |
| `price_updated_at` | `DateTimeField` | آخرین بروزرسانی قیمت | null=True; blank=True; editable=False |
| `is_price_locked` | `BooleanField` | قفل قیمت | default=False |
| `stock_quantity` | `PositiveIntegerField` | موجودی | default=0 |
| `low_stock_threshold` | `PositiveIntegerField` | حد هشدار موجودی | default=3 |
| `weight_grams` | `PositiveIntegerField` | وزن به گرم | null=True; blank=True |
| `length_cm` | `DecimalField` | طول به سانتی‌متر | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `width_cm` | `DecimalField` | عرض به سانتی‌متر | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `height_cm` | `DecimalField` | ارتفاع به سانتی‌متر | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `shipping_length_cm` | `DecimalField` | طول بسته برای ارسال (cm) | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `shipping_width_cm` | `DecimalField` | عرض بسته برای ارسال (cm) | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `shipping_height_cm` | `DecimalField` | ارتفاع بسته برای ارسال (cm) | null=True; blank=True; max_digits=8; decimal_places=2; validators=[MinValueValidator(Decimal('0.01'))] |
| `compatible_motorcycles` | `ManyToManyField` | موتورسیکلت‌های سازگار | → motorcycles.MotorcycleModel; blank=True |
| `related_products` | `ManyToManyField` | محصولات مرتبط | → self; blank=True |
| `meta_title` | `CharField` | عنوان SEO | blank=True; max_length=250 |
| `meta_description` | `CharField` | توضیحات SEO | blank=True; max_length=320 |
| `status` | `CharField` | وضعیت | default=Status.DRAFT; max_length=20; choices=Status.choices |
| `is_featured` | `BooleanField` | محصول ویژه | default=False |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `ProductImage`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `product` | `ForeignKey` | محصول | → Product; on_delete=models.CASCADE |
| `image` | `ImageField` | تصویر | validators=[validate_image] |
| `alt_text` | `CharField` | متن جایگزین تصویر | blank=True; max_length=250 |
| `is_primary` | `BooleanField` | تصویر اصلی | default=False |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش | default=0 |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |

#### `ProductAttribute`

**DataType:** `TEXT` = `text`; `NUMBER` = `number`; `BOOLEAN` = `boolean`; `CHOICE` = `choice`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `name` | `CharField` | نام ویژگی | unique=True; max_length=150 |
| `slug` | `SlugField` | اسلاگ | blank=True; unique=True; max_length=180 |
| `data_type` | `CharField` | نوع داده | max_length=20; choices=DataType.choices |
| `unit` | `CharField` | واحد | blank=True; max_length=50 |
| `is_filterable` | `BooleanField` | قابل فیلتر | default=False |
| `is_searchable` | `BooleanField` | قابل جستجو | default=False |
| `is_active` | `BooleanField` | فعال | default=True |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش | default=0 |
| `categories` | `ManyToManyField` | دسته‌بندی‌ها | → categories.Category; blank=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `ProductAttributeOption`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `attribute` | `ForeignKey` | ویژگی | → ProductAttribute; on_delete=models.CASCADE |
| `value` | `CharField` | مقدار | max_length=150 |
| `slug` | `SlugField` | اسلاگ | blank=True; max_length=180 |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش | default=0 |
| `is_active` | `BooleanField` | فعال | default=True |

#### `CategoryAttribute`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `category` | `ForeignKey` | دسته‌بندی | → categories.Category; on_delete=models.CASCADE |
| `attribute` | `ForeignKey` | ویژگی | → ProductAttribute; on_delete=models.CASCADE |
| `is_required` | `BooleanField` | الزامی | default=False |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش | default=0 |

#### `ProductAttributeValue`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `product` | `ForeignKey` | محصول | → Product; on_delete=models.CASCADE |
| `attribute` | `ForeignKey` | ویژگی | → ProductAttribute; on_delete=models.PROTECT |
| `value_text` | `TextField` | مقدار متنی | blank=True |
| `value_number` | `DecimalField` | مقدار عددی | null=True; blank=True; max_digits=18; decimal_places=4 |
| `value_boolean` | `BooleanField` | مقدار بله / خیر | null=True; blank=True |
| `option` | `ForeignKey` | گزینه انتخاب‌شده | → ProductAttributeOption; null=True; blank=True; on_delete=models.PROTECT |

#### `ProductCompatibility`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `product` | `ForeignKey` | محصول | → Product; on_delete=models.CASCADE |
| `motorcycle` | `ForeignKey` | مدل موتورسیکلت | → motorcycles.MotorcycleModel; on_delete=models.PROTECT |
| `compatible_start_year` | `PositiveIntegerField` | سال شروع سازگاری | null=True; blank=True |
| `compatible_end_year` | `PositiveIntegerField` | سال پایان سازگاری | null=True; blank=True |
| `note` | `CharField` | توضیح سازگاری | blank=True; max_length=500 |

#### `ProductRelation`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `product` | `ForeignKey` | محصول | → Product; on_delete=models.CASCADE |
| `related_product` | `ForeignKey` | محصول مرتبط | → Product; on_delete=models.CASCADE |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش | default=0 |

### `shipping`

#### `TipaxSettings`

**PaymentType:** `SENDER_CREDIT` = `10`; `RECEIVER_POSTPAID` = `20`; `RECEIVER_COD` = `30`; `SENDER_COD_WITH_CREDIT` = `40`; `SENDER_WALLET` = `50`; `SENDER_CASH` = `80`; `SENDER_BRANCH_CREDIT` = `90`; `CASH_AND_PAY_IN_PLACE` = `100`

**PickupType:** `CUSTOMER_LOCATION` = `10`; `BRANCH` = `20`

**DistributionType:** `CUSTOMER_LOCATION` = `10`; `BRANCH` = `20`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `payment_type` | `PositiveSmallIntegerField` | نوع پرداخت هزینه تیپاکس | default=PaymentType.SENDER_CREDIT; choices=PaymentType.choices |
| `pickup_type` | `PositiveSmallIntegerField` | نوع جمع‌آوری | default=PickupType.CUSTOMER_LOCATION; choices=PickupType.choices |
| `distribution_type` | `PositiveSmallIntegerField` | نوع تحویل | default=DistributionType.CUSTOMER_LOCATION; choices=DistributionType.choices |
| `default_service_id` | `PositiveSmallIntegerField` | سرویس پیش‌فرض تیپاکس | default=2 |
| `enable_label_privacy` | `BooleanField` | مخفی کردن اطلاعات روی لیبل | default=False |
| `customer_substation_code` | `CharField` | کد شعبه مشتری | blank=True; max_length=100 |
| `customer_id` | `PositiveBigIntegerField` | Customer ID در تیپاکس | null=True; blank=True |
| `sender_full_name` | `CharField` | نام کامل فرستنده | blank=True; max_length=250 |
| `sender_mobile` | `CharField` | موبایل فرستنده | blank=True; max_length=20 |
| `sender_phone` | `CharField` | تلفن فرستنده | blank=True; max_length=20 |
| `origin_full_address` | `TextField` | آدرس کامل مبدا | blank=True |
| `origin_postal_code` | `CharField` | کد پستی مبدا | blank=True; max_length=20 |
| `origin_floor` | `CharField` | طبقه مبدا | blank=True; max_length=20 |
| `origin_unit` | `CharField` | واحد مبدا | blank=True; max_length=20 |
| `origin_no` | `CharField` | پلاک مبدا | blank=True; max_length=30 |
| `origin_latitude` | `CharField` | Latitude مبدا | blank=True; max_length=50 |
| `origin_longitude` | `CharField` | Longitude مبدا | blank=True; max_length=50 |
| `origin_description` | `CharField` | توضیحات مبدا | blank=True; max_length=500 |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `ShippingSettings`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `origin_city` | `ForeignKey` | شهر مبدا ارسال | → addresses.City; null=True; blank=True; on_delete=models.PROTECT |
| `package_extra_weight_grams` | `PositiveIntegerField` | وزن اضافه بسته‌بندی به گرم | default=150 |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `ShippingMethod`

**Provider:** `POST` = `post`; `TIPAX` = `tipax`; `CUSTOM` = `custom`

**CalculationMode:** `MANUAL` = `manual`; `API` = `api`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `code` | `SlugField` | کد روش ارسال | unique=True; max_length=100 |
| `name` | `CharField` | نام روش ارسال | max_length=150 |
| `provider` | `CharField` | شرکت حمل‌ونقل | max_length=20; choices=Provider.choices |
| `service_code` | `CharField` | کد سرویس | max_length=100 |
| `calculation_mode` | `CharField` | روش محاسبه هزینه | default=CalculationMode.MANUAL; max_length=20; choices=CalculationMode.choices |
| `description` | `CharField` | توضیحات | blank=True; max_length=500 |
| `estimated_min_days` | `PositiveSmallIntegerField` | حداقل زمان تحویل به روز | null=True; blank=True |
| `estimated_max_days` | `PositiveSmallIntegerField` | حداکثر زمان تحویل به روز | null=True; blank=True |
| `is_active` | `BooleanField` | فعال | default=True |
| `sort_order` | `PositiveSmallIntegerField` | ترتیب نمایش | default=0 |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `ShippingRateRule`

**DestinationScope:** `NATIONWIDE` = `nationwide`; `PROVINCE` = `province`; `CITY` = `city`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `method` | `ForeignKey` | روش ارسال | → ShippingMethod; on_delete=models.CASCADE |
| `destination_scope` | `CharField` | محدوده مقصد | default=DestinationScope.NATIONWIDE; max_length=20; choices=DestinationScope.choices |
| `province` | `ForeignKey` | استان مقصد | → addresses.Province; null=True; blank=True; on_delete=models.CASCADE |
| `city` | `ForeignKey` | شهر مقصد | → addresses.City; null=True; blank=True; on_delete=models.CASCADE |
| `min_weight_grams` | `PositiveIntegerField` | حداقل وزن به گرم | default=0 |
| `max_weight_grams` | `PositiveIntegerField` | حداکثر وزن به گرم | null=True; blank=True |
| `base_price_toman` | `PositiveBigIntegerField` | هزینه پایه به تومان | validators=[MinValueValidator(0)] |
| `included_weight_grams` | `PositiveIntegerField` | وزن شامل هزینه پایه به گرم | default=1000 |
| `additional_per_kg_toman` | `PositiveBigIntegerField` | هزینه هر کیلو اضافه به تومان | default=0 |
| `priority` | `IntegerField` | اولویت | default=0 |
| `effective_from` | `DateTimeField` | شروع اعتبار تعرفه | default=timezone.now |
| `effective_to` | `DateTimeField` | پایان اعتبار تعرفه | null=True; blank=True |
| `is_active` | `BooleanField` | فعال | default=True |
| `note` | `CharField` | یادداشت | blank=True; max_length=500 |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `ShippingProviderCityMap`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `provider` | `CharField` | شرکت حمل‌ونقل | max_length=30; choices=ShippingMethod.Provider.choices |
| `city` | `ForeignKey` | شهر | → addresses.City; on_delete=models.CASCADE |
| `provider_city_id` | `PositiveBigIntegerField` | شناسه شهر در Provider | — |
| `provider_city_name` | `CharField` | نام شهر در Provider | blank=True; max_length=150 |
| `is_active` | `BooleanField` | فعال | default=True |
| `created_at` | `DateTimeField` | تاریخ ایجاد | auto_now_add=True |
| `updated_at` | `DateTimeField` | آخرین بروزرسانی | auto_now=True |

#### `TipaxPackageProfile`

**PackType:** `ENVELOPE` = `10`; `PACKAGE` = `20`; `MINI_PACK` = `50`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `title` | `CharField` | عنوان | max_length=150 |
| `min_weight_grams` | `PositiveIntegerField` | حداقل وزن به گرم | default=0 |
| `max_weight_grams` | `PositiveIntegerField` | حداکثر وزن به گرم | null=True; blank=True |
| `length` | `DecimalField` | طول بسته | max_digits=8; decimal_places=2 |
| `width` | `DecimalField` | عرض بسته | max_digits=8; decimal_places=2 |
| `height` | `DecimalField` | ارتفاع بسته | max_digits=8; decimal_places=2 |
| `packing_id` | `PositiveIntegerField` | Packing ID | default=0 |
| `package_content_id` | `PositiveIntegerField` | Package Content ID | — |
| `pack_type` | `PositiveSmallIntegerField` | نوع بسته Tipax | default=20 |
| `parcel_type_id` | `PositiveIntegerField` | Parcel Type ID | default=0 |
| `is_unusual` | `BooleanField` | بسته نامتعارف | default=False |
| `priority` | `IntegerField` | اولویت | default=0 |
| `is_active` | `BooleanField` | فعال | default=True |

#### `Shipment`

**Status:** `CREATED` = `created`; `REGISTERED` = `registered`; `PROCESSING` = `processing`; `WAITING_PICKUP` = `waiting_pickup`; `COLLECTED` = `collected`; `SHIPPED` = `shipped`; `DELIVERED` = `delivered`; `RETURNED` = `returned`; `CANCELLED` = `cancelled`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `order` | `ForeignKey` | سفارش | → orders.Order; on_delete=models.PROTECT |
| `shipping_method` | `ForeignKey` | روش ارسال | → ShippingMethod; null=True; blank=True; on_delete=models.SET_NULL |
| `provider` | `CharField` | Provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `status` | `CharField` | وضعیت | default=Status.CREATED; max_length=30; choices=Status.choices |
| `external_order_id` | `CharField` | Order ID Provider | blank=True; max_length=150 |
| `tracking_codes` | `JSONField` | کدهای رهگیری | blank=True; default=list |
| `primary_tracking_code` | `CharField` | کد رهگیری اصلی | blank=True; max_length=150 |
| `provider_status_id` | `CharField` | کد وضعیت Provider | blank=True; max_length=50 |
| `provider_status_name` | `CharField` | وضعیت Provider | blank=True; max_length=250 |
| `quoted_amount_toman` | `PositiveBigIntegerField` | هزینه برآوردشده | null=True; blank=True |
| `final_amount_toman` | `PositiveBigIntegerField` | هزینه نهایی | null=True; blank=True |
| `request_payload` | `JSONField` | درخواست Provider | blank=True; default=dict |
| `response_payload` | `JSONField` | پاسخ Provider | blank=True; default=dict |
| `tracking_payload` | `JSONField` | آخرین پاسخ رهگیری | blank=True; default=dict |
| `cancelled_at` | `DateTimeField` | زمان ابطال | null=True; blank=True |
| `created_at` | `DateTimeField` | created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at | auto_now=True |

#### `ShippingOrigin`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `title` | `CharField` | عنوان مبدا | max_length=120 |
| `province` | `ForeignKey` | استان | → Province; on_delete=models.PROTECT |
| `city` | `ForeignKey` | شهر | → City; on_delete=models.PROTECT |
| `postal_address` | `TextField` | آدرس | blank=True; default= |
| `postal_code` | `CharField` | کد پستی | blank=True; default=; max_length=10 |
| `is_active` | `BooleanField` | فعال | default=True |
| `is_default` | `BooleanField` | مبدا پیش‌فرض | default=False |
| `created_at` | `DateTimeField` | created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at | auto_now=True |

#### `ShippingProviderProvince`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `provider` | `CharField` | provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `provider_province_id` | `CharField` | provider province id | max_length=64 |
| `name` | `CharField` | name | blank=True; default=; max_length=150 |
| `is_active` | `BooleanField` | is active | default=True |
| `raw_data` | `JSONField` | raw data | blank=True; default=dict |
| `created_at` | `DateTimeField` | created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at | auto_now=True |

#### `ShippingProviderCity`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `provider` | `CharField` | provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `provider_city_id` | `CharField` | provider city id | max_length=64 |
| `provider_province_id` | `CharField` | provider province id | blank=True; default=; max_length=64 |
| `name` | `CharField` | name | max_length=150 |
| `provider_uuid` | `CharField` | provider uuid | blank=True; default=; max_length=100 |
| `latitude` | `DecimalField` | latitude | null=True; blank=True; max_digits=12; decimal_places=8 |
| `longitude` | `DecimalField` | longitude | null=True; blank=True; max_digits=12; decimal_places=8 |
| `is_active` | `BooleanField` | is active | default=True |
| `raw_data` | `JSONField` | raw data | blank=True; default=dict |
| `created_at` | `DateTimeField` | created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at | auto_now=True |

#### `ShippingProviderPackingOption`

**Kind:** `CARTON` = `carton`; `BUBBLE` = `bubble`; `ENVELOPE` = `envelope`; `SACK` = `sack`; `FLYER` = `flyer`; `NO_PACKING` = `no_packing`; `OTHER` = `other`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `provider` | `CharField` | provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `provider_packing_id` | `PositiveBigIntegerField` | provider packing id | — |
| `title` | `CharField` | title | max_length=200 |
| `kind` | `CharField` | kind | default=Kind.OTHER; max_length=30; choices=Kind.choices |
| `box_number` | `PositiveSmallIntegerField` | box number | null=True; blank=True |
| `pack_type` | `PositiveIntegerField` | pack type | null=True; blank=True |
| `length` | `DecimalField` | length | null=True; blank=True; max_digits=8; decimal_places=2 |
| `width` | `DecimalField` | width | null=True; blank=True; max_digits=8; decimal_places=2 |
| `height` | `DecimalField` | height | null=True; blank=True; max_digits=8; decimal_places=2 |
| `min_weight` | `DecimalField` | min weight | null=True; blank=True; max_digits=8; decimal_places=2 |
| `max_weight` | `DecimalField` | max weight | null=True; blank=True; max_digits=8; decimal_places=2 |
| `min_length` | `DecimalField` | min length | null=True; blank=True; max_digits=8; decimal_places=2 |
| `max_length` | `DecimalField` | max length | null=True; blank=True; max_digits=8; decimal_places=2 |
| `min_width` | `DecimalField` | min width | null=True; blank=True; max_digits=8; decimal_places=2 |
| `max_width` | `DecimalField` | max width | null=True; blank=True; max_digits=8; decimal_places=2 |
| `min_height` | `DecimalField` | min height | null=True; blank=True; max_digits=8; decimal_places=2 |
| `max_height` | `DecimalField` | max height | null=True; blank=True; max_digits=8; decimal_places=2 |
| `provider_price` | `DecimalField` | provider price | null=True; blank=True; max_digits=18; decimal_places=3 |
| `is_active` | `BooleanField` | is active | default=True |
| `raw_data` | `JSONField` | raw data | blank=True; default=dict |
| `created_at` | `DateTimeField` | created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at | auto_now=True |

#### `ShippingProviderProvinceMap`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `provider` | `CharField` | provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `province` | `ForeignKey` | province | → addresses.Province; on_delete=models.CASCADE |
| `provider_province_id` | `CharField` | provider province id | max_length=64 |
| `provider_province_name` | `CharField` | provider province name | blank=True; default=; max_length=150 |
| `is_active` | `BooleanField` | is active | default=True |
| `created_at` | `DateTimeField` | created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at | auto_now=True |

#### `ShippingProviderOriginMap`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `provider` | `CharField` | Provider | max_length=30; choices=ShippingMethod.Provider.choices |
| `origin` | `ForeignKey` | مبدا ارسال | → ShippingOrigin; on_delete=models.CASCADE |
| `provider_address_id` | `PositiveBigIntegerField` | شناسه آدرس در Provider | — |
| `provider_address_title` | `CharField` | عنوان آدرس در Provider | blank=True; max_length=250 |
| `is_active` | `BooleanField` | فعال | default=True |
| `raw_data` | `JSONField` | اطلاعات خام Provider | blank=True; default=dict |
| `created_at` | `DateTimeField` | created at | auto_now_add=True |
| `updated_at` | `DateTimeField` | updated at | auto_now=True |

### `wishlists`

#### `WishlistItem`

| فیلد | نوع | توضیح | قواعد |
|---|---|---|---|
| `user` | `ForeignKey` | کاربر | → settings.AUTH_USER_MODEL; on_delete=models.CASCADE |
| `product` | `ForeignKey` | محصول | → products.Product; on_delete=models.CASCADE |
| `created_at` | `DateTimeField` | تاریخ افزودن | auto_now_add=True |


<a id="api-routes"></a>
## مسیرهای API

مسیرهای زیر از URLconf استخراج شده‌اند. routerها برای resource ثبت‌شده مسیر collection/detail تولید می‌کنند؛ method، permission، pagination، query parameters و فیلدهای read-only را از serializer، view و Swagger بررسی کنید. `pricing` در تنظیمات نصب است ولی URLconf اصلی آن را include نمی‌کند. `inventory` نیز route فعال در core ندارد.

| App | Prefix | مسیرها / منابع router |
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

### نمونه درخواست

```bash
curl -X POST http://127.0.0.1:8000/api/v1/accounts/send-otp/ \
  -H 'Content-Type: application/json' \
  -d '{"phone_number":"09123456789"}'

curl http://127.0.0.1:8000/api/v1/accounts/me/ \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

بدون sender تنظیم‌شده، نمونه ارسال OTP پیامک واقعی نمی‌فرستد. قرارداد verify و checkout را از Swagger بخوانید.

## منابع نصب رسمی

- [Python downloads](https://www.python.org/downloads/)
- [Git installation](https://git-scm.com/downloads)
- [Homebrew](https://brew.sh/)
- [Docker Desktop](https://docs.docker.com/desktop/)
- [Docker Engine on Linux](https://docs.docker.com/engine/install/)
- [PostgreSQL downloads](https://www.postgresql.org/download/)
- [Redis installation](https://redis.io/docs/latest/install/)
- [WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install)
