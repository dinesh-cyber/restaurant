from django.contrib import admin
from .models import Customer, RawItem, Staff, Order, Food, Comment, stock, Data, OrderContent, Cart, DeliveryBoy, FoodCategories

admin.site.register(Customer)
admin.site.register(Staff)
admin.site.register(Order)
admin.site.register(Food)
admin.site.register(Comment)
admin.site.register(Data)
admin.site.register(DeliveryBoy)
admin.site.register(OrderContent)
admin.site.register(Cart)
admin.site.register(RawItem)
admin.site.register(stock)
admin.site.register(FoodCategories)
