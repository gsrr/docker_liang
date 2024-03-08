from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerProfile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm
from .models import RentalSpace, SpaceType
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
from captcha.fields import CaptchaField
from django.shortcuts import render, redirect

#處理工作人員創建租賃空間的表格
class RentalSpaceForm(forms.ModelForm):
    class Meta:
        model = RentalSpace
        fields = ['space_id', 'space_type', 'notes']
        widgets = {
            'space_type': forms.Select(),
            'notes': forms.Textarea(),
        }

from django import forms
from .models import Unit, Item

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_type', 'unit_notes']
        labels = {
            'unit_type': '單元類型',
            'unit_notes': '備註'
        }
        widgets = {
            'unit_type': forms.Select(),
            'unit_notes': forms.TextInput(attrs={'placeholder': '備註'})
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['photo', 'item_notes']
        labels = {
            'photo': '上傳照片',
            'item_notes': '備註'
        }
        widgets = {
            'photo': forms.FileInput(attrs={'placeholder': '上傳照片'}),
            'item_notes': forms.TextInput(attrs={'placeholder': '備註 最多50字節'})
        }

    def clean_photo(self): #clean_photo後面的photo是指定的欄位名稱,不能隨便取名
        image = self.cleaned_data.get('photo')
        print("clean_photo 被調用")
        if image and image.size > 300 * 1024:
            img = Image.open(image)
            output = BytesIO()
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            img.save(output, format='JPEG', quality=75)
            output.seek(0)
            content_file = ContentFile(output.read())
            file_name = "{}.jpg".format(uuid.uuid4())  # 使用UUID生成加密文件名
            image = InMemoryUploadedFile(content_file, None, file_name, 'image/jpeg', content_file.tell, None)

        return image

    def save(self, commit=True):
        item = super().save(commit=False)

        photo = self.cleaned_data.get('photo')
        if photo:
            ext = photo.name.split('.')[-1]
            encrypted_file_name = f"{uuid.uuid4()}.{ext}"
            item.photo.save(encrypted_file_name, photo, save=False)

        if commit:
            item.save()
        return item







class CustomPasswordResetForm(PasswordResetForm):
    username = forms.CharField(max_length=150)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("您的帳戶名或信箱不正確")

        return cleaned_data

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['real_name', 'address', 'phone', 'id_number', 'id_photo']

class PhoneVerificationForm(forms.Form):
    phone = forms.CharField(max_length=15, required=True, label="請輸入手機號")
    otc = forms.CharField(max_length=6, required=False, label="請輸入收到的OTP驗證碼")  # OTP 碼通常是6位數字
    captcha = CaptchaField(label="圖形驗證")  # 圖形驗證碼

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # 在這裡添加對手機號碼的格式驗證
        return phone

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['real_name', 'address']  # 包括需要更新的字段
