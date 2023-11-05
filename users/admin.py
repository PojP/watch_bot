from django.contrib import admin
from .models import Users,SearchHistory,ActiveTime

admin.site.register(Users)
admin.site.register(SearchHistory)
admin.site.register(ActiveTime)
# Register your models here.
