from django.contrib import admin

# Register your models here.
from .models import TOTP,User

admin.site.register(TOTP)
admin.site.register(User)