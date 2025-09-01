from django.contrib import admin

# Register your models here.
from tracker.models import Asset, PriceHistory, Alert


admin.site.register(Asset)
admin.site.register(PriceHistory)
admin.site.register(Alert)