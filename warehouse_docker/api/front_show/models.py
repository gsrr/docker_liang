from django.db import models

class FrontEndContent(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name="Key")
    value1 = models.TextField(verbose_name="Content1")
    value2 = models.TextField(blank=True, null=True, verbose_name="Content2")
    value3 = models.TextField(blank=True, null=True, verbose_name="Content3")
    value4 = models.TextField(blank=True, null=True, verbose_name="Content4")
    value5 = models.TextField(blank=True, null=True, verbose_name="Content5")

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = "管理顯示文字內容"
        verbose_name_plural = "管理顯示文字內容"

class FrontEndImage(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name="Key")
    image = models.ImageField(upload_to='page_images/', verbose_name="Image")

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = "管理顯示圖片"
        verbose_name_plural = "管理顯示圖片"