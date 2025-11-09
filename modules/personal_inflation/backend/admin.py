from django.contrib import admin
from .models import (
    ProductCategory, Product, Store, PersonalBasket, 
    BasketItem, PriceRecord, InflationReport, PriceAlert
)

# Register models with admin
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(Store)
admin.site.register(PersonalBasket)
admin.site.register(BasketItem)
admin.site.register(PriceRecord)
admin.site.register(InflationReport)
admin.site.register(PriceAlert)