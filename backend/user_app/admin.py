from django.contrib import admin

# Register your models here.
from .models import TOTP

admin.site.register(TOTP)