"""django_warehouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from warehouse.views import register
from warehouse.views import login_request
from warehouse.views import logout_request
from warehouse.views import PasswordReset, PasswordResetDone, PasswordResetConfirm, PasswordResetComplete
from warehouse.views import homepageshow
from warehouse.views import phone_verification
from warehouse.views import buy_membership
from warehouse.views import pay_for_membership
from warehouse.views import pay_on_site
from warehouse.views import confirm_payment
from warehouse.views import confirm_payment_test
from warehouse.views import create_rentalspace
from warehouse.views import my_rental_space
from warehouse.views import create_rentalspace_auto
from warehouse.views import manage_rentalspace
from warehouse.views import delete_unit
from warehouse.views import delete_item
from warehouse.views import update_unit_notes
from warehouse.views import update_item_notes
from django.urls import include, path
from warehouse.views import all_orders_view
from warehouse.views import new_orders_view
from warehouse.views import upcoming_expiry_orders_view
from warehouse.views import expired_orders_view
from warehouse.views import profile_edit
from warehouse.views import change_phone_verification
from warehouse.views import item_number_scan
from warehouse.views import handle_scanned_data
from warehouse.views import update_item_notes
from warehouse.views import update_item_notes_from_scan
from warehouse.views import staff_manage_rentalspace

from front_show.views import rental_method_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("index/", homepageshow, name="homepageshow"),
    path('register/', register, name='register'),
    path("login/", login_request, name="login"),
    path("logout/", logout_request, name="logout"),
    path('phone_verification/', phone_verification, name='phone_verification'),
    path('change_phone/', change_phone_verification, name='change_phone'),

    #以下忘記找回密碼功能
    path('password_reset/', PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDone.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetComplete.as_view(), name='password_reset_complete'),
    #圖形驗證碼
    path('captcha/', include('captcha.urls')),

    #購買會員
    path('buy_membership/', buy_membership, name='buy_membership'),
    path('pay_for_membership/', pay_for_membership, name='pay_for_membership'),
    #現場付款
    path('pay-on-site/', pay_on_site, name='pay_on_site'),
    # 現場支付確認頁面
    path('confirm-payment/<str:token>/', confirm_payment, name='confirm_payment'),
    path('confirm_payment/', confirm_payment_test, name='confirm_payment_test'),
    path('create-rentalspace/<int:order_id>/', create_rentalspace, name='create_rentalspace'),
    path('create-rentalspace_auto/<int:order_id>', create_rentalspace_auto, name='create_rentalspace_auto'),

    #客戶端url
    #修改會員資料
    path('profile_edit/', profile_edit, name='profile_edit'),
    #我的倉儲空間列表
    path('my-rental-space/', my_rental_space, name='my_rental_space'),
    path('manage-rentalspace/<str:space_id>/', manage_rentalspace, name='manage_rentalspace'),
    path('delete_unit/<int:unit_id>/', delete_unit, name='delete_unit'),
    path('delete_item/<int:item_id>/', delete_item, name='delete_item'),
    #編輯notes

    path('unit/<int:unit_id>/update_notes/', update_unit_notes, name='update_unit_notes'),
    path('item/<int:item_id>/update_notes/', update_item_notes, name='update_item_notes'),



    #QRcode 相關
    path('item_number_scan/location/<str:location_id>/rentalspace/<int:rentalspace_id>/unit/<int:unit_id>/', item_number_scan, name='item_number_scan'),
    path('handle_scanned_data/', handle_scanned_data, name='handle_scanned_data'),
    path('update_item_notes/', update_item_notes_from_scan, name='update_item_notes'),#注意這個更新要與手動更新url區分

    #管理相關頁面列表
    path('order/all_list/', all_orders_view, name='all_orders_view'),
    path('orders/new/', new_orders_view, name='new_orders_view'),
    path('orders/upcoming_expiry/', upcoming_expiry_orders_view, name='upcoming_expiry_orders_view'),
    path('orders/expired/', expired_orders_view, name='expired_orders_view'),
    #工作人員管理每個租賃空間
    path('staff-manage-rentalspace/', staff_manage_rentalspace, name='staff_manage_rentalspace'),

    #前端頁面顯示相關
    path('rental_method/', rental_method_view, name='rental_method_view')



]



from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
