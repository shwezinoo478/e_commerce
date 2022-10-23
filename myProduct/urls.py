from django.urls import path
from . import views as view


urlpatterns = [
    path('getCategory/', view.get_category , name="get_category_item" ),
    path('home/', view.product_item.as_view() , name ="home_view"),
    path('getDetails/<int:id>/', view.get_details , name="get_product_details"),
    path("register/", view.register_request, name="register"),
    path("login/", view.login_request, name="login"),
    path("logout/", view.logout_request, name= "logout"),
    path("cache/<int:id>/",view.cache_recipes_view , name = "cacheData"),
    path("cartList/",view.cart_list_view , name = "cartData"),
    path("cartDelete/<str:id>/",view.del_key , name="deleteKey"),
    path("customerInfo/",view.order_item , name="customerInfo"),
    path("customerDetails/",view.customerInsertData , name="customerDetails"),
    path("cachClear/",view.clear_cache, name="cacheClear")
]
