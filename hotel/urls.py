from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^cart/$', views.cart, name='cart'),
    url(r'^menu/$', views.menu, name='menu'),
    url(r'^myorders/$', views.my_orders, name='my_orders'),

    url(r'^dashboard/admin/users/$', views.users_admin, name='users_admin'),
    url(r'^dashboard/admin/orders/$', views.orders_admin, name='orders_admin'),
    url(r'^dashboard/admin/orders/create_order/$',
        views.create_orders_admin, name='create_orders_admin'),
    url(r'^dashboard/admin/foods/$', views.foods_admin, name='foods_admin'),
    url(r'^dashboard/admin/$', views.dashboard_admin, name='dashboard_admin'),
    url(r'^dashboard/admin/sales/$', views.sales_admin, name='sales_admin'),

    url(r'^dashboard/admin/users/add_user/$', views.add_user, name='add_user'),
    url(r'^dashboard/admin/foods/add_food/$', views.add_food, name='add_food'),
    url(r'^dashboard/admin/sales/add_sales/$',
        views.add_sales, name='add_sales'),
    url(r'^dashboard/admin/foods/editFood/(?P<foodID>\d+)/$',
        views.edit_food, name='edit_food'),
    url(r'^dashboard/admin/foods/foodDetails/(?P<foodID>\d+)/$',
        views.food_details, name='food_details'),
    url(r'^dashboard/admin/sales/editSale/(?P<saleID>\d+)/$',
        views.edit_sales, name='edit_sales'),

    url(r'^dashboard/admin/orders/confirm_order/(?P<orderID>\d+)/$',
        views.confirm_order, name='confirm_order'),
    url(r'^dashboard/admin/orders/view/(?P<orderID>\d+)/$',
        views.order_view_admin, name='view_order'),
    url(r'^dashboard/admin/orders/edit/(?P<orderID>\d+)/$',
        views.order_view_edit, name='view_order_edit'),
    url(r'^dashboard/admin/orders/confirm_delivery/(?P<orderID>\d+)/$',
        views.confirm_delivery, name='confirm_delivery'),

    url(r'^delete_item/(?P<ID>\d+)/$', views.delete_item, name='delete_item'),
    url(r'^add_deliveryBoy/(?P<orderID>\d+)/$',
        views.add_deliveryBoy, name='add_deliveryBoy'),
    url(r'^placeOrder/$', views.placeOrder, name='placeOrder'),
    url(r'^addTocart/(?P<foodID>\d+)/(?P<userID>\d+)/$',
        views.addTocart, name='addTocart'),

    url(r'^dashboard/delivery_boy/$', views.delivery_boy, name='delivery_boy'),
    url(r'^foods/$', views.get_foods, name='foods'),
    url(r'^foods/(?P<food_id>\d+)/$', views.get_food_data, name='food_data'),
    url(r'^dashboard/admin/stock-items/$',
        views.stock_items_admin, name='stock_items_admin'),
    url(r'^dashboard/admin/stock-credit/$',
        views.stock_items_credit_admin, name='stock_items_credit_admin'),
    url(r'^dashboard/admin/stock/item-details/(?P<orderID>\d+)/$',
        views.stock_item_details_admin, name='stock_item_details_admin'),
    url(r'^dashboard/admin/stock-out/$',
        views.stock_item_out_admin, name='stock_item_out_admin'),


]
