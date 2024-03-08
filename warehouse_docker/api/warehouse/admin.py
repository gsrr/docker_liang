from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import CustomerProfile
from .models import RentalSpace
from .models import MembershipOrder
from .models import Unit
from .models import Item
from .models import Location
from .models import SpaceType
from .models import UnitType
from .models import MembershipType
from .models import PurchaseOrder
from .models import UserBalance
from django.urls import reverse
from django.utils.html import format_html




# Register your models here.
admin.site.register(CustomerProfile)

admin.site.register(MembershipOrder)
admin.site.register(Unit)
admin.site.register(Item)

admin.site.register(SpaceType)
admin.site.register(UnitType)
admin.site.register(MembershipType)
admin.site.register(PurchaseOrder)
admin.site.register(UserBalance)

admin.site.site_header = '瑞龍倉 倉儲租賃管理系統'  # 替换为您想要的标题



class RentalSpaceAdmin(admin.ModelAdmin):
    search_fields = ['order__user__username', 'order__user__first_name', 'order__user__last_name', 'order__user__email',
                    'order__user__customerprofile__real_name',
                    'order__user__customerprofile__phone',
                    'order__user__customerprofile__address'
                     ]



admin.site.register(RentalSpace, RentalSpaceAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'view_rental_spaces_link')

    def view_rental_spaces_link(self, obj):
        url = (
            reverse("admin:warehouse_rentalspace_changelist")
            + "?"
            + "location__id__exact="
            + str(obj.id)
        )
        return format_html('<a href="{}">查看已出租空間號碼</a>', url)

    view_rental_spaces_link.short_description = "租賃空間"

admin.site.register(Location, LocationAdmin)