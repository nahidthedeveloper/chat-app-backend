from django.contrib import admin

from authentication.models import Account


# Register your models here.

class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')


admin.site.register(Account, AccountAdmin)
