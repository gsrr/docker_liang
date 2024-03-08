from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime
from django.core.validators import FileExtensionValidator
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    real_name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    id_number = models.CharField(max_length=20, default="0")  # 身分證明文件號碼，初始值為"0"
    id_photo = models.ImageField(upload_to='id_photos/', blank=True, null=True)
    united_invoice = models.CharField(max_length=20, default="0")  # 統一發票號碼，初始值為"0"

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "客戶資料"
        verbose_name_plural = "客戶資料"

class Location(models.Model):
    location_id = models.CharField(max_length=50, unique=True,null=True)
    location_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    max_space_number = models.IntegerField(default=0)
    occupied_space_number = models.IntegerField(default=0)
    available_space_number = models.IntegerField(editable=False, default=0)

    def __str__(self):
        return self.location_name

    def clean(self):
        # 确保占用空间不超过最大空间
        if self.occupied_space_number > self.max_space_number:
            raise ValidationError("Occupied space number cannot be greater than max space number.")

    def save(self, *args, **kwargs):
        # 在保存之前运行 clean 方法来验证数据
        self.clean()
        # 更新 available_space_number
        self.available_space_number = self.max_space_number - self.occupied_space_number
        super(Location, self).save(*args, **kwargs)


    class Meta:
        verbose_name = "管理倉庫地點"
        verbose_name_plural = "管理倉庫地點"

class SpaceType(models.Model):
    space_type_id = models.CharField(max_length=50, unique=True,blank=True)
    space_type_name = models.CharField(max_length=255)
    dimensions_L = models.CharField(max_length=100, null=True)
    dimensions_W = models.CharField(max_length=100, null=True)
    dimensions_H = models.CharField(max_length=100, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return self.space_type_name

    class Meta:
        verbose_name = "管理租賃空間類型"
        verbose_name_plural = "管理租賃空間類型"


class MembershipType(models.Model):
    membership_type_id = models.CharField(max_length=50, unique=True, blank=True)
    membership_type_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rental_duration = models.IntegerField()  # 会员类型的有效期或其他相关属性


    def __str__(self):
        return self.membership_type_name

    class Meta:
        verbose_name = "管理會員資格類型"
        verbose_name_plural = "管理會員資格類型"

class MembershipOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name='location', on_delete=models.CASCADE, null=True)
    membership_type = models.ForeignKey(MembershipType, on_delete=models.CASCADE,default=1, null=True)
    start_date = models.DateTimeField(blank=True)
    end_date = models.DateTimeField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    choices = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    )
    payment_status = models.CharField(max_length=100, choices=choices, default='Pending')
    PAYMENT_CHOICES = (
        ('Installment', '分期付款'),
        ('Full', '一次性付清'),
    )

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Full')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def set_end_date(self):
        if self.start_date and self.membership_type:
            duration = datetime.timedelta(days=self.membership_type.rental_duration)
            self.end_date = self.start_date + duration
            print(self.end_date)


    class Meta:
        verbose_name = "購買會員資格訂單"
        verbose_name_plural = "購買會員資格訂單"



class PurchaseOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=100, default='Pending')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Purchase Order {self.id} by {self.user.username}"

    class Meta:
        verbose_name = "夠買商品訂單"
        verbose_name_plural = "購買商品訂單"


#關於支付
#付款計畫期數,其數1代表一次性付款,以上代表分期付款
class PaymentPlan(models.Model):
    order = models.ForeignKey(MembershipOrder, related_name='payment_plans', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_installments = models.IntegerField(default=1)  # 一次性付款是1，分期付款可以是更多
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Payment Plan for Order {self.order.id}"

#紀錄每一次分期付款的詳細資料

class InstallmentPlan(models.Model):
    payment_plan = models.ForeignKey(PaymentPlan, related_name='installments', on_delete=models.CASCADE, null=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)  # 實際支付日期

    def __str__(self):
        return f"Installment {self.id} for Payment Plan {self.payment_plan.id}"

#發票

class Invoice(models.Model):
    installment = models.OneToOneField(InstallmentPlan, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50)
    invoice_date = models.DateField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice {self.invoice_number}"




class UserBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s balance"

    def deposit(self, amount):
        if amount < 0:
            raise ValidationError("Deposit amount must be positive.")
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if amount < 0:
            raise ValidationError("Withdrawal amount must be positive.")
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    class Meta:
        verbose_name = "客戶餘額"
        verbose_name_plural = "客戶餘額"





class RentalSpace(models.Model):
    space_id = models.CharField(max_length=50, unique=True,blank=True)
    order = models.ForeignKey(MembershipOrder, related_name='rental_spaces', on_delete=models.CASCADE,null=True)  # order foreign key
    space_type = models.ForeignKey(SpaceType, related_name='spacetype', on_delete=models.CASCADE, null=True)
    location = models.ForeignKey(Location, related_name='warelocation', on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.space_id + self.location.location_name

    class Meta:
        verbose_name = "已租賃空間"
        verbose_name_plural = "已租賃空間"




class UnitType(models.Model):
    unit_type_id = models.CharField(max_length=50, unique=True,blank=True)
    unit_type_name = models.CharField(max_length=255)
    dimensions_L = models.CharField(max_length=100, null=True)
    dimensions_W = models.CharField(max_length=100, null=True)
    dimensions_H = models.CharField(max_length=100, null=True)
    def __str__(self):
        return self.unit_type_name

    class Meta:
        verbose_name = "管理儲存單位類型"
        verbose_name_plural = "管理儲存單位類型"

class Unit(models.Model):
    unit_id = models.CharField(max_length=50, unique=True, null=True)
    space = models.ForeignKey(RentalSpace, related_name='units', on_delete=models.CASCADE)
    unit_type = models.ForeignKey(UnitType, related_name='unittype', on_delete=models.CASCADE, null=True)
    unit_notes = models.CharField(max_length=100, blank=True, null=True)  # 最大长度设置为100

    def __str__(self):
        return self.unit_id or "未命名单位"

    class Meta:
        verbose_name = "已存入的儲存箱或單位"
        verbose_name_plural = "已存入的儲存箱或單位"

class Item(models.Model):
    unit = models.ForeignKey(Unit, related_name='items', on_delete=models.CASCADE) # unit關聯用 unit.items.all()
    item_id = models.CharField(max_length=50, unique=True)
    photo = models.ImageField(upload_to='item_photos/')
    video_url = models.URLField()
    item_notes = models.CharField(max_length=50, blank=True, null=True)  # 最大长度设置为100
    def __str__(self):
        return self.item_id or "未命名物品"

    class Meta:
        verbose_name = "儲藏品"
        verbose_name_plural = "儲藏品"
