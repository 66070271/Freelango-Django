from django.contrib.staticfiles import storage
from freelance.storages_backends import StaticStorage

storage.staticfiles_storage = StaticStorage()
print("⚙️ STATICFILES_STORAGE now uses:", storage.staticfiles_storage.__class__)
