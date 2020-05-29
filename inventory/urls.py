from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("login", views.login_view, name='login'),
    path("register", views.register, name='register'),
    path("logout", views.logout_view, name='logout'),
    path("dashboard", views.dashboard, name='dashboard'),
    path("product", views.product, name='product'),
    path("addProduct", views.addProduct, name='addProduct'),
    path("searchProduct", views.searchProduct, name='searchProduct'),
    path("bill", views.bill, name='bill'),
    path("bill_detail/<slug:bill_num>", views.bill_detail, name='bill_detail'),
    path("bill_update/<slug:bill_num>", views.bill_update, name='bill_update'),
    path("bill_delete/<slug:bill_num>", views.bill_delete, name='bill_delete'),
    path("addBill", views.addBill, name='addBill'),
    path("searchBill", views.searchBill, name='searchBill'),
    path("order", views.order, name='order'),
    path("addOrder", views.addOrder, name='addOrder'),
    path("searchOrder", views.searchOrder, name='searchOrder'),
    path("order_detail/<slug:order_num>", views.order_detail, name='order_detail'),
    path("order_update/<slug:order_num>", views.order_update, name='order_update'),
    path("order_delete/<slug:order_num>", views.order_delete, name='order_delete'),


]