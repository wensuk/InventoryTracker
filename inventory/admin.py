from django.contrib import admin
from .models import Category, Item, Brand, Product, Record, Bill, Order

# Register your models here.
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Record)
admin.site.register(Bill)
admin.site.register(Order)