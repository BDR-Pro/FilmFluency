from django.contrib import admin

# Register your models here.
from .models import Payment,Invoice,Product

admin.site.register(Payment)
admin.site.register(Invoice)
admin.site.register(Product)

