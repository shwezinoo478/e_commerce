from django.contrib import admin

# Register your models here.
from .models import Product,Customer,Order,Category

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Product)

