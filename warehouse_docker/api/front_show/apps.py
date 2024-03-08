from django.apps import AppConfig


class FrontShowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'front_show'
    verbose_name = '管理頁面顯示文字以及圖片'  # 将显示在管理后台中的名称

