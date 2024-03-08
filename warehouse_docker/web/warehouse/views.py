from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
import requests
import json
import re
import cv2
#from .forms import CustomUserCreationForm

from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm
from .forms import UserRegisterForm
from .forms import CustomerProfileForm
from .forms import PhoneVerificationForm
from .forms import RentalSpaceForm
from .forms import UnitForm
from .forms import ItemForm
from .forms import ProfileEditForm
from .models import MembershipOrder
from .models import UserBalance


from .models import Location, MembershipType, MembershipOrder, PurchaseOrder, UserBalance, RentalSpace, SpaceType, UnitType, Unit, Item, CustomerProfile
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.http import JsonResponse
import qrcode
from io import BytesIO
from django.core.files.images import ImageFile
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.signing import Signer
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
import base64
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404
import boto3
import numpy as np
import uuid
from django.conf import settings
from django.http import HttpResponseForbidden



#儲值 消費

def process_deposit_order(deposit_order_id):
    deposit_order = MembershipOrder.objects.get(id=deposit_order_id)
    user_balance = UserBalance.objects.get(user=deposit_order.user)
    user_balance.deposit(deposit_order.amount)
    # 这里可以添加其他处理逻辑，例如更新订单状态等

def process_purchase_order(purchase_order_id):
    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    user_balance = UserBalance.objects.get(user=purchase_order.user)

    if user_balance.withdraw(purchase_order.amount):
        purchase_order.payment_status = 'Paid'
        purchase_order.save()
        # 这里可以添加其他处理逻辑
    else:
        raise ValidationError("Insufficient funds")

#購買會員
@login_required
def buy_membership_backup(request):
    if request.method == 'POST':
        '''user = request.user
        membership_type_id = request.POST.get('membership_type')
        location_id = request.POST.get('location')
        start_date = timezone.now()'''

        user_id = request.user.id
        membership_type_id = request.POST.get('membership_type')
        location_id = request.POST.get('location')
        start_date = timezone.now()

        membership_type = MembershipType.objects.get(id=membership_type_id)
        print(membership_type)
        location = Location.objects.get(id=location_id)
        print(location)
        '''order = MembershipOrder.objects.create(
            user=user,
            location=location,
            membership_type=membership_type,  # 确保设置了 membership_type
            start_date=start_date,
            end_date=start_date, #先設置為同一天 之後再用set_end_date()更新
            amount=membership_type.price,
            payment_status='Pending'
        )

        order.save()
        print("訂單已建立")
        order.set_end_date()  # 根据会员类型设置结束日期
        print(order.end_date)'''

        request.session['pending_order'] = {
            'user_id': user_id,
            'membership_type_id': membership_type_id,
            'location_id': location_id,
            'start_date': start_date.isoformat(),
            'end_date': start_date.isoformat(),  # 初始设置为相同的日期
            'amount': str(membership_type.price),
            'payment_status': 'Pending'
        }

        return redirect('pay_for_membership')

        # ... 重定向到支付页面或其他逻辑 ...
        return redirect('pay_for_membership')

    else:
        membership_types = MembershipType.objects.all()
        locations = Location.objects.all()
        return render(request, 'buy_membership.html', {'membership_types': membership_types, 'locations': locations})

@login_required
def buy_membership(request):
    if request.method == 'POST':
        user_id = request.user.id
        membership_type_id = request.POST.get('membership_type')
        location_id = request.POST.get('location')
        space_type_name = request.POST.get('space_type')
        start_date = now()

        # 获取 MembershipType 实例
        membership_type = MembershipType.objects.get(id=membership_type_id)
        location = Location.objects.get(id=location_id)

        # 计算结束日期
        duration = timedelta(days=membership_type.rental_duration)
        end_date = start_date + duration

        # 将订单信息存储在 session 中
        request.session['pending_order'] = {
            'user_id': user_id,
            'membership_type_id': membership_type_id,
            'location_id': location_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),  # 存储计算后的结束日期
            'amount': str(membership_type.price),
            'payment_status': 'Pending',
            'space_type': space_type_name
        }
        print("存入session")
        return redirect('pay_for_membership')

    else:
        membership_types = MembershipType.objects.all()
        locations = Location.objects.all()
        space_types = SpaceType.objects.all()
        return render(request, 'buy_membership.html', {
            'membership_types': membership_types,
            'locations': locations,
            'space_types': space_types
        })


# views.py
'''def pay_for_membership(request, order_id):
    order = MembershipOrder.objects.get(id=order_id)
    user_balance, created = UserBalance.objects.get_or_create(user=request.user)

    if not order.end_date:
        order.set_end_date()

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        # 添加支付处理逻辑

        return HttpResponse(f"Chosen payment method: {payment_method}")
    else:
        context = {
            'order': order,
            'user_balance': user_balance  # 将用户余额传递到模板
        }
        return render(request, 'pay_for_membership.html', context)'''
#準備支付頁面寫在session裡面
@login_required
def pay_for_membership(request):
    pending_order = request.session.get('pending_order')
    if not pending_order:
        return HttpResponse("No pending order found.")

    user_balance, created = UserBalance.objects.get_or_create(user=request.user)

    # 从 session 中的信息获取并准备订单数据
    location_name = Location.objects.get(id=pending_order['location_id']).location_name
    start_date = parse_datetime(pending_order['start_date'])
    end_date = parse_datetime(pending_order['end_date'])
    '''order_data = {
        'membership_type_id': pending_order['membership_type_id'],
        'location_id': pending_order['location_id'],
        'start_date': pending_order['start_date'],
        'end_date': pending_order['end_date'],  # 这可能需要进一步处理以显示正确格式
        'amount': pending_order['amount'],
        'payment_status': pending_order['payment_status']
    }'''
    context = {
        'order': {
            'amount': pending_order['amount'],
            'location_name': location_name,
            'start_date': start_date,
            'end_date': end_date
        },
        'user_balance': user_balance.balance
    }



    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        # 这里添加支付处理逻辑

        return HttpResponse(f"Chosen payment method: {payment_method}")
    else:
        return render(request, 'pay_for_membership.html', context)

@login_required
def pay_on_site(request):
    pending_order = request.session.get('pending_order')
    if not pending_order:
        return HttpResponse("No pending order found.")

    # 构建确认支付的 URL 並建立加密的 token
    signer = Signer()
    token = signer.sign(f"{request.user.id}:{request.session.session_key}")

    confirm_url = request.build_absolute_uri(
        reverse('confirm_payment', args=[token])
    )
    print(confirm_url)
    # 生成 QR 码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(confirm_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qrcode_base64 = base64.b64encode(buffer.getvalue()).decode()
    qrcode_data = mark_safe(f"data:image/png;base64,{qrcode_base64}")

    return render(request, 'pay_on_site.html', {'qrcode_data': qrcode_data})




#支付成功

@login_required
def confirm_payment(request):
    pending_order = request.session.get('pending_order')
    if not pending_order:
        return HttpResponse("No pending order to confirm.")

    # 从 session 中的信息创建 MembershipOrder
    user = User.objects.get(id=pending_order['user_id']) #id 是前端頁面輸入框輸入該資料的id
    membership_type = MembershipType.objects.get(id=pending_order['membership_type_id'])
    location = Location.objects.get(id=pending_order['location_id'])
    start_date = parse_datetime(pending_order['start_date'])
    end_date = parse_datetime(pending_order['end_date'])  # 初始为相同的日期
    amount = Decimal(pending_order['amount'])

    order = MembershipOrder(
        user=user,
        membership_type=membership_type,
        location=location,
        start_date=start_date,
        end_date=end_date,
        amount=amount,
        payment_status=pending_order['payment_status']
    )
    order.set_end_date()  # 更新结束日期
    order.save()

    # 清除 session 中的订单信息
    del request.session['pending_order']

    return HttpResponse("Payment confirmed and order created.")

#支付成功後執行的函數 完成鍵是測試用, 實際流程完成付款後執行此功能 接著跳轉到創建租賃空間頁面分配id
@login_required
def confirm_payment_test(request):
    pending_order = request.session.get('pending_order')
    if not pending_order:
        return HttpResponse("No pending order to confirm.")

    # 从 session 中的信息创建 MembershipOrder
    user = User.objects.get(id=pending_order['user_id'])
    membership_type = MembershipType.objects.get(id=pending_order['membership_type_id'])
    location = Location.objects.get(id=pending_order['location_id'])
    start_date = parse_datetime(pending_order['start_date'])
    end_date = parse_datetime(pending_order['end_date'])  # 初始为相同的日期
    amount = Decimal(pending_order['amount'])


    order = MembershipOrder(
        user=user,
        membership_type=membership_type,
        location=location,
        start_date=start_date,
        end_date=end_date,
        amount=amount,
        payment_status='Paid' #與confirm_payment唯一差別
    )
    order.set_end_date()  # 更新结束日期
    order.save()

    # 清除 session 中的订单信息
    #del request.session['pending_order'] #注意被清除掉session 之後的函數讀不到
    order_id = order.id
    #return redirect('create_rentalspace', order_id=order_id) ＃測試手動設置空間類型
    return redirect('create_rentalspace_auto', order_id=order_id) #測試自動設置空間類型

#創建租賃空間從QRcode頁面跳轉過來
def create_rentalspace(request, order_id):
    order = get_object_or_404(MembershipOrder, id=order_id)

    existing_spaces = RentalSpace.objects.filter(location=order.location).values_list('space_id', flat=True)
    form = RentalSpaceForm(request.POST or None)
    error_message = None

    if request.method == 'POST' and form.is_valid():
        space_id = form.cleaned_data['space_id']

        if space_id in existing_spaces:
            error_message = "此空間已出租。"
        else:
            rental_space = form.save(commit=False)
            rental_space.order = order
            rental_space.location = order.location
            rental_space.save()
            return redirect('some_success_page')  # 更改为您的成功页面的 URL 名称

    return render(request, 'create_rentalspace.html', {
        'form': form,
        'order': order,
        'existing_spaces': existing_spaces,
        'error_message': error_message
    })


#完成付款後自動分配空間id
@login_required
def create_rentalspace_auto(request, order_id):
    #order = get_object_or_404(MembershipOrder, id=order_id)
    order = MembershipOrder.objects.filter(payment_status= 'Paid', id=order_id).first()
    pending_order = request.session.get('pending_order')#此處調取session只是為了取得space_type_name,其他資料都從order取得
    if not pending_order:
        # 处理 pending_order 不存在的情况，例如重定向到错误页面或显示错误消息
        print("pending_order 不存在")
    space_type_name = pending_order.get('space_type')


    print(space_type_name)

    # 获取对应的 SpaceType 实例
    space_type = SpaceType.objects.filter(space_type_name=space_type_name).first()
    print(space_type)
    if not space_type:
        # 如果没有找到对应的 SpaceType，处理错误
        return redirect('error_page')

    existing_space_ids = set(RentalSpace.objects.filter(location=order.location).values_list('space_id', flat=True))
    max_space_id = order.location.max_space_number

    available_space_ids = set(str(i) for i in range(1, max_space_id + 1)) - existing_space_ids
    space_id = random.choice(list(available_space_ids)) if available_space_ids else None

    if not space_id:
        print("没有可用的 space_id")
        return redirect('error_page')  # 重定向到错误页面
    else:
        print(f"生成的 space_id: {space_id}")

    RentalSpace.objects.create(
        space_id=space_id,
        order=order,
        space_type=space_type,  # 使用 SpaceType 实例
        location=order.location,
        notes=""  # 留空
    )

    return redirect('my_rental_space')  # 更改为您的成功页面的 URL 名称
#會員管理自身倉儲頁面 已租賃倉儲清單列表


@login_required
def my_rental_space(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # 获取当前用户的有效订单和个人资料
    valid_orders = MembershipOrder.objects.filter(
        user=request.user,
        end_date__gte=now(),
        payment_status='Paid'
    )
    spaces_by_order = {order: RentalSpace.objects.filter(order=order) for order in valid_orders}
    customer_profile = CustomerProfile.objects.get(user=request.user)  # 获取当前用户的个人资料

    return render(request, 'my_rental_space.html', {
        'spaces_by_order': spaces_by_order,
        'customer_profile': customer_profile  # 传递个人资料到模板
    })

#修改個人資料


@login_required
def profile_edit(request):
    customer_profile = CustomerProfile.objects.get(user=request.user)
    form = ProfileEditForm(instance=customer_profile)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=customer_profile)
        if form.is_valid():
            form.save()
            # 這裡添加處理手機號碼驗證的邏輯
            # ...
            return redirect('my_rental_space')

    return render(request, 'profile_edit.html', {'form': form})







# 预签名URL生成函数
# 预签名URL生成函数
def generate_presigned_url(s3_key):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': s3_key},
        ExpiresIn=3600  # 有效期1小时
    )
    return url

@login_required
def manage_rentalspace(request, space_id):
    current_user = request.user
    is_staff = current_user.is_staff
    rentalspace = get_object_or_404(RentalSpace, space_id=space_id)

    if not (rentalspace.order.user == current_user or is_staff):
        return HttpResponseForbidden("您没有权限访问此页面。")


    units = rentalspace.units.all()
    unit_types = UnitType.objects.all()
    items = Item.objects.filter(unit__in=units)
    # 生成预签名URL
    # 为每个item生成预签名URL
    # 初始化表单放在前面,確保表單在POST之前已經初始化
    unit_form = UnitForm()
    item_form = ItemForm()
    # 初始化 items 列表 用於排序
    items_sorted = []
    for unit in units:
        # 對每個 unit 的 items 進行按 item_id 排序
        sorted_items = unit.items.order_by('item_id')
        items_sorted.extend(sorted_items)

    if request.method == 'POST':
        if 'add_unit' in request.POST:
            unit_form = UnitForm(request.POST)
            unit_form_count = Unit.objects.filter(space=rentalspace).count()
            print(unit_form_count)
            if unit_form_count < 20:
                if unit_form.is_valid():
                    unit = unit_form.save(commit=False)
                    unit.space = rentalspace
                    unit.unit_id = generate_unit_id()
                    unit.save()
                    return redirect('manage_rentalspace', space_id=space_id)
            else:
                messages.error(request, "已達到最大上限（20個單元）。")
                return redirect('manage_rentalspace', space_id=space_id)

        elif 'add_item' in request.POST or 'add_multiple_items' in request.POST:
            unit_id = request.POST.get('unit_id')
            print(unit_id)
            unit = get_object_or_404(Unit, id=unit_id)
            current_items_count = unit.items.count()

            if current_items_count < 10:
                if 'add_item' in request.POST:
                    item_form = ItemForm(request.POST, request.FILES)
                    if item_form.is_valid():
                        item = item_form.save(commit=False)
                        item.unit = unit
                        item.item_id = generate_item_id()
                        item.save()
                        # ... 其他图片处理逻辑 ...
                #注意以下是多張圖片上傳的邏輯, 當時沒有正確調用ItemForm, 所以沒有驗證表單以及調用方法, 這裡只是為了展示多張圖片上傳的邏輯
                elif 'add_multiple_items' in request.POST:
                    files = request.FILES.getlist('item_photos')
                    remaining_slots = 10 - current_items_count
                    files_to_add = files[:remaining_slots]  # 限制文件数量
                    for file in files_to_add:
                        form_data = {'item_notes': ''}  # 如果有其他字段，也可以在這裡填寫
                        file_data = {'photo': file}

                        item_form = ItemForm(form_data, file_data)
                        if item_form.is_valid():
                            item = item_form.save(commit=False)
                            item.unit = unit
                            item.item_id = generate_item_id()
                            item.save()
                            # 如果需要，這裡可以添加其他圖片處理邏輯
                        else:
                            print("表單驗證錯誤:", item_form.errors)


                return redirect('manage_rentalspace', space_id=space_id)
            else:
                messages.error(request, "已达到最大上传数量（10张）。")
                return redirect('manage_rentalspace', space_id=space_id)



    return render(request, 'manage_rentalspace.html', {
        'rentalspace': rentalspace,
        'units': units,
        'item': items,
        'items_sorted': items_sorted,
        'unit_types': unit_types,
        'unit_form': unit_form,
        'item_form': item_form

    })
def generate_unit_id():
    today = timezone.now().date()
    count = Unit.objects.filter(unit_id__startswith=today.strftime('%Y%m%d')).count()
    return f"{today.strftime('%Y%m%d')}-{count + 1}"

def generate_item_id():
    local_now = timezone.localtime(timezone.now()) #將UTC時間轉換成本地時間
    date_str = local_now.strftime('%Y%m%d%H')
    count = Item.objects.filter(item_id__startswith=date_str).count()
    return f"{date_str}-{count + 1}"

def delete_unit(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    rentalspace_id = unit.space.space_id
    unit.delete()
    return redirect('manage_rentalspace', space_id=rentalspace_id)

def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    space_id = item.unit.space.space_id
    # 如果 item 有图片，则从 S3 删除
    if item.photo:
        full_key = f"static/{item.photo.name}"  # 添加 'static/' 前缀
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=full_key)
        print(f"已从 S3 删除 {full_key}")
    item.delete()
    return redirect('manage_rentalspace', space_id=space_id)


#編輯unit_notes
@require_POST
def update_unit_notes(request, unit_id):
    data = json.loads(request.body)
    new_notes = data.get('new_notes')

    unit = get_object_or_404(Unit, id=unit_id)
    unit.unit_notes = new_notes
    unit.save()

    return JsonResponse({'success': True})




#編輯item_notes
@require_POST
def update_item_notes(request, item_id):

    data = json.loads(request.body)
    item_notes = data.get('new_notes')

    item = get_object_or_404(Item, id=item_id)
    item.item_notes = item_notes
    item.save()
    print("更新成功")

    return JsonResponse({'success': True})


#以下開始QRcode相關功能
@login_required
def item_number_scan(request, location_id, rentalspace_id, unit_id):
    # 處理POST請求


    # 處理GET請求
    scanned_barcodes = request.session.get('scanned_barcodes', [])

    #以下處理非常重要 用於確保用戶以及工作人員能訪問與其關聯的Unit
    # 获取当前登录的用户
    current_user = request.user
    is_staff = current_user.is_staff



    # 获取指定的Unit
    unit = get_object_or_404(Unit, id=unit_id, space_id=rentalspace_id)

    # 检查Unit是否与当前用户关联或用户是工作人员
    if not (unit.space.order.user == current_user or is_staff):
        return HttpResponseForbidden("您没有权限访问此页面。")

    context = {
        'location_id': location_id,
        'rentalspace_id': rentalspace_id,
        'unit_id': unit_id,
        'scanned_barcodes': scanned_barcodes
    }
    return render(request, 'item_number_scan.html', context)

@csrf_exempt
def handle_scanned_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            barcode_data = data.get('scanned_data')
            if not barcode_data:
                return JsonResponse({'status': 'error', 'message': '无效的数据'}, status=400)

            # 正则表达式匹配年份和货号
            match = re.search(r'/(\d{4})/([a-zA-Z]{1,3}\d{6})$', barcode_data)
            if match:
                year = match.group(1)[-2:]  # 提取年份的最后两位
                item_number = match.group(2)  # 提取货号
                formatted_barcode = f"{item_number}-{year}"  # 格式化输出

                return JsonResponse({'status': 'success', 'message': 'get item_number', 'barcode': formatted_barcode})
            else:
                return JsonResponse({'status': 'error', 'message': '无效的货号格式'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '解析JSON错误'}, status=400)


''''@csrf_exempt
def handle_scanned_data(request):

    if request.method == 'POST':

        try:
            data = json.loads(request.body.decode('utf-8'))
            barcode_data = data.get('scanned_data')
            if not barcode_data:
                return JsonResponse({'status': 'error', 'message': '无效的数据'}, status=400)

            match = re.search(r'[a-zA-Z]{1,3}\d{6}$', barcode_data)
            if match:
                matched_barcode = match[0]  # 提取匹配到的货号部分

                return JsonResponse({'status': 'success', 'message': 'get item_number', 'barcode': matched_barcode})
            else:
                return JsonResponse({'status': 'error', 'message': '無效的貨號格式'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '解析JSON錯誤'}, status=400)'''

#前端掃描到的貨號傳存入item_notes
@require_POST
def update_item_notes_from_scan(request):
    data = json.loads(request.body)
    unit_id = data.get('unit_id')
    print(unit_id)
    scanned_barcodes = data.get('scanned_barcodes').split('\n')

    try:
        unit = Unit.objects.get(id=unit_id)
        items = unit.items.all()
        if len(items) != len(scanned_barcodes):
            return JsonResponse({'status': 'error', 'message': '儲藏品件數與掃描貨號件數不同'}, status=400)

        for item, barcode in zip(items, scanned_barcodes):

            item.item_notes = item.item_id + f" {barcode}"  # 添加货号到 item_notes
            item.save()

        space_id = unit.space.space_id

        return JsonResponse({'status': 'success', 'message': '物品备注更新成功', 'space_id': space_id})


    except Unit.DoesNotExist:
        print("unit error")
        return JsonResponse({'status': 'error', 'message': '指定的单元不存在'}, status=404)
    except Exception as e:
        print("error")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)








#首頁顯示

def homepageshow(request):
    return render(request=request, template_name="index.html")

#以下工作人員顯示各狀態訂單

def all_orders_view(request):

    orders = MembershipOrder.objects.filter(payment_status='Paid').select_related('user', 'location','membership_type').prefetch_related('rental_spaces')
    for order in orders:
        customer_profile = CustomerProfile.objects.filter(user=order.user).first()
        order.customer_name = customer_profile.real_name if customer_profile else "未知"
        order.customer_phone = customer_profile.phone if customer_profile else "未知"
        order.spaces = ', '.join([space.space_id for space in order.rental_spaces.all()])

    return render(request, 'order_management.html', {'membershiporders': orders, 'title': '所有訂單'})
def new_orders_view(request):
    orders = MembershipOrder.objects.filter(payment_status='Paid').select_related('user', 'location', 'membership_type').prefetch_related('rental_spaces')
    for order in orders:
        customer_profile = CustomerProfile.objects.filter(user=order.user).first()
        order.customer_name = customer_profile.real_name if customer_profile else "未知"
        order.customer_phone = customer_profile.phone if customer_profile else "未知"
        order.spaces = ', '.join([space.space_id for space in order.rental_spaces.all()])

    return render(request, 'order_management.html', {'membershiporders': orders, 'title': '新成立訂單'})


from datetime import datetime, timedelta

def upcoming_expiry_orders_view(request):
    today = datetime.now().date()
    three_days_later = today + timedelta(days=3)

    # 選擇在今天和三天後之間到期的訂單
    orders = MembershipOrder.objects.filter(end_date__range=[today, three_days_later],payment_status='Paid').select_related('user', 'location', 'membership_type').prefetch_related('rental_spaces')
    for order in orders:
        customer_profile = CustomerProfile.objects.filter(user=order.user).first()
        order.customer_name = customer_profile.real_name if customer_profile else "未知"
        order.customer_phone = customer_profile.phone if customer_profile else "未知"
        order.spaces = ', '.join([space.space_id for space in order.rental_spaces.all()])
    return render(request, 'order_management.html', {
        'membershiporders': orders,
        'title': '即將到期訂單'
    })


def expired_orders_view(request):
    today = datetime.now().date()
    orders = MembershipOrder.objects.filter(end_date__lte=today, payment_status='Paid').select_related('user', 'location', 'membership_type').prefetch_related('rental_spaces')
    for order in orders:
        customer_profile = CustomerProfile.objects.filter(user=order.user).first()
        order.customer_name = customer_profile.real_name if customer_profile else "未知"
        order.customer_phone = customer_profile.phone if customer_profile else "未知"
        order.spaces = ', '.join([space.space_id for space in order.rental_spaces.all()])
    return render(request, 'order_management.html', {'membershiporders': orders, 'title': '已到期訂單'})


#工作人員管理租賃空間頁面
@staff_member_required
def staff_manage_rentalspace(request):
    locations = Location.objects.prefetch_related('warelocation').all()
    print("display staff_manage_rentalspace")
    context = {'locations': locations}
    return render(request, 'staff_manage_rentalspace.html', context)






#註冊
def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = CustomerProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.phone = request.session.get('verified_phone', '')
            profile.save()
            print("註冊成功")
            return redirect('homepageshow')  # 確保此處的 URL 名稱有效

        else:
            print("註冊失敗，表單驗證未通過")

    else:
        user_form = UserRegisterForm()
        profile_form = CustomerProfileForm()

    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})






#登入 登出

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"已登入用戶 {username}.")
                return redirect("homepageshow")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            print(form.errors)
            messages.error(request,"Other Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form":form})


def logout_request(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have successfully logged out.")
    return redirect("homepageshow")

class PasswordReset(PasswordResetView):
    email_template_name = 'password_reset_email.html'
    template_name = 'password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = CustomPasswordResetForm

class PasswordResetDone(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class PasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
from django.shortcuts import render

# Create your views here.
#註冊驗證碼
def send_sms(phone_number, message):
    url = "https://smsapi.mitake.com.tw/api/mtk/SmSend?CharsetURL=UTF-8"
    data = {
        "username": "42614331SMS",
        "password": "jglee0318",
        "dstaddr": phone_number,
        "smbody": message
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    print(response.text)
    print(phone_number)
    return response.status_code, response.text

import random

def generate_otc_code():
    return ''.join(random.choice('0123456789') for _ in range(4))

#註冊時驗證號碼
def phone_verification(request):
    form = PhoneVerificationForm(request.POST or None)

    if request.method == 'POST':
        if 'send_otc' in request.POST:
            if form.is_valid():
                otc_code = generate_otc_code()
                request.session['otc_code'] = otc_code
                phone_number = form.cleaned_data.get('phone')
                request.session['verified_phone'] = phone_number
                send_sms(phone_number, f"您的驗證碼是: {otc_code}")
                return render(request, 'phone_verification.html', {'form': form, 'otc_sent': True})

        elif 'verify_otc' in request.POST:
            entered_otc = request.POST.get('otc')
            if entered_otc == request.session.get('otc_code'):
                return redirect('register')
            else:
                form.add_error('otc', 'OTC驗證碼不正確')

    return render(request, 'phone_verification.html', {'form': form})

#重新驗證號碼
def change_phone_verification(request):
    form = PhoneVerificationForm(request.POST or None)

    if request.method == 'POST':
        if 'send_otc' in request.POST:
            if form.is_valid():
                otc_code = generate_otc_code()
                request.session['otc_code'] = otc_code
                phone_number = form.cleaned_data.get('phone')
                request.session['verified_phone'] = phone_number
                send_sms(phone_number, f"您的驗證碼是: {otc_code}")
                return render(request, 'phone_verification.html', {'form': form, 'otc_sent': True})

        elif 'verify_otc' in request.POST:
            entered_otc = request.POST.get('otc')
            if entered_otc == request.session.get('otc_code'):
                return redirect('my_rental_space')
            else:
                form.add_error('otc', 'OTC驗證碼不正確')

    return render(request, 'phone_verification.html', {'form': form})

