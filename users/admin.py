from django.contrib import admin
from .models import Users,SearchHistory,ActiveTime,AutoPost

admin.site.register(Users)
admin.site.register(SearchHistory)
admin.site.register(ActiveTime)
admin.site.register(AutoPost)
# Register your models here.
