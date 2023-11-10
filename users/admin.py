from django.contrib import admin
from .models import Users,SearchHistory,ActiveTime,AutoPost,ButtonLinks

admin.site.register(Users)
admin.site.register(SearchHistory)
admin.site.register(ActiveTime)
admin.site.register(AutoPost)
admin.site.register(ButtonLinks)
# Register your models here.
