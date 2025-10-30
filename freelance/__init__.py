from django.contrib.staticfiles import storage as static_storage
from django.core.files import storage as file_storage
from freelance.storages_backends import StaticStorage, MediaStorage

# --- Force Django to use S3 for static files ---
static_storage.staticfiles_storage = StaticStorage()
print("⚙️ STATICFILES_STORAGE now uses:", static_storage.staticfiles_storage.__class__)

# --- Force Django to use S3 for media uploads ---
file_storage.default_storage = MediaStorage()
print("📦 DEFAULT_FILE_STORAGE now uses:", file_storage.default_storage.__class__)
