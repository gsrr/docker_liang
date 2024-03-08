from django.contrib import admin
from front_show.models import FrontEndContent, FrontEndImage

# Register your models here.
admin.site.register(FrontEndContent)
admin.site.register(FrontEndImage)

admin.site.site_header = '瑞龍倉 倉儲租賃管理系統'