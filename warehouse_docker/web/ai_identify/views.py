from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.files.images import ImageFile
from warehouse.models import Location, RentalSpace, Unit, Item
from warehouse.forms import RentalSpaceForm, UnitForm, ItemForm
import cv2
import numpy as np
from io import BytesIO
from django.utils import timezone

def resize_image(image, size=(1024, 768)):
    """調整圖片至指定解析度"""
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)
def generate_item_id():
    local_now = timezone.localtime(timezone.now()) #將UTC時間轉換成本地時間
    date_str = local_now.strftime('%Y%m%d%H')
    count = Item.objects.filter(item_id__startswith=date_str).count()
    return f"{date_str}-{count + 1}"

# Create your views here.
def detect_and_crop_objects(image_file):
    # 讀取圖片
    image = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    print(image)
    # 調整解析度
    image = resize_image(image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 轉為灰階
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)  # 應用閾值處理

    # 尋找輪廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cropped_images = []
    for contour in contours:
        # 獲取輪廓的邊界框
        x, y, w, h = cv2.boundingRect(contour)
        # 擴大範圍 10%
        x, y, w, h = enlarge_bbox(x, y, w, h, 0.1)
        cropped = image[y:y + h, x:x + w]

        # 將裁剪的圖片轉換為 Django 可以處理的格式
        is_success, buffer = cv2.imencode(".jpg", cropped)
        if is_success:
            io_buffer = BytesIO(buffer)
            cropped_images.append(ImageFile(io_buffer))

    return cropped_images

def enlarge_bbox(x, y, w, h, scale):
    dx = w * scale
    dy = h * scale
    x = max(0, x - dx // 2)
    y = max(0, y - dy // 2)
    w += dx
    h += dy
    return int(x), int(y), int(w), int(h)

@login_required
def ai_identify(request, location_id, rentalspace_id, unit_id):
    location = get_object_or_404(Location, id=location_id)
    rentalspace = get_object_or_404(RentalSpace, id=rentalspace_id)
    unit = get_object_or_404(Unit, id=unit_id)
    current_user = request.user

    if not (rentalspace.order.user == current_user or current_user.is_staff):
        return HttpResponseForbidden("您没有权限访问此页面。")

    if request.method == 'POST':
        image_file = request.FILES.get('image')
        if not image_file:
            # 處理錯誤：沒有提供圖片
            pass

        # 處理上傳的圖片，進行物體識別和裁剪
        cropped_images = detect_and_crop_objects(image_file)
        for i, img in enumerate(cropped_images):
            cv2.imwrite(f'cropped_image_{i}.jpg', img)

        # 遍歷裁剪後的圖片，創建 Item 實例
        for cropped_image in cropped_images:
            item_id = generate_item_id()
            unit = rentalspace.units.first()  # 假設使用第一個單元，這裡可以根據需要調整
            new_item = Item.objects.create(
                unit=unit,
                photo=cropped_image,  # 假設 photo 字段可以直接存儲圖片，可能需要進行調整
                item_id=item_id,
                # ... 其他字段 ...
            )


            return redirect('manage_rentalspace', space_id=rentalspace.space_id)

    context = {
        'location_id': location_id,
        'rentalspace_id': rentalspace_id,
        'unit_id': unit_id,

    }
    return render(request, 'item_number_scan.html', context)