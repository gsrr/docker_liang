from django.shortcuts import render
from django.db import models
from .models import FrontEndContent, FrontEndImage
from django.shortcuts import get_object_or_404
from warehouse.models import Location
from warehouse.models import MembershipType
# Create your views here.

def rental_method_view(request):
    # 使用中文 key
    keys_needed = ['租賃方式說明','內湖費率說明','青田費率說明','瑞龍倉功能說明']  # 这里的中文需要和数据库中的 key 完全匹配
    content1 = {}
    content2 = {}
    content3 = {}
    content4 = {}
    content5 = {}
    locations = Location.objects.all()

    for key in keys_needed:
        try:
            content_item = FrontEndContent.objects.get(key=key)
            content1[key] = content_item.value1
            content2[key] = content_item.value2
            content3[key] = content_item.value3
            content4[key] = content_item.value4
            content5[key] = content_item.value5


        except FrontEndContent.DoesNotExist:
            content1[key] = 'none'
            content2[key] = 'none'
            content3[key] = 'none'
            content4[key] = 'none'
            content5[key] = 'none'

    context = {'content1': content1,
                'content2': content2,
                'content3': content3,
                'content4': content4,
                'content5': content5,
               'locations': locations,

               }
    return render(request, 'rental_method.html', context)