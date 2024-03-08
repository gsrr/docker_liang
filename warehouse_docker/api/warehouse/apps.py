from django.apps import AppConfig
class WarehouseConfig(AppConfig):
    name = 'warehouse'
    verbose_name = '倉庫租賃以及購買訂單'  # 将显示在管理后台中的名称

#此處為了更改後台管理介面的app名稱