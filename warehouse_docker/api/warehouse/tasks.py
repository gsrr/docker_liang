from celery import shared_task
from datetime import datetime, timedelta
from .models import MembershipOrder
from warehouse.views import send_sms

@shared_task
def check_membership_expiry():
    print("Checking membership expiry...")
    today = datetime.now().date()
    expiry_start = today + timedelta(days=1)
    expiry_end = today + timedelta(days=3)

    expiring_orders = MembershipOrder.objects.filter(
        end_date__date__range=[expiry_start, expiry_end],
        payment_status='Paid'
    )

    for order in expiring_orders:
        phone_number = order.user.customerprofile.phone
        send_sms(phone_number, "瑞龍倉客戶通知:您的倉儲空間即將到期,請續費或於到期日前清空倉儲,感謝您的支持.")