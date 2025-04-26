

# from django.urls import path
# from . import views
# from django.contrib.auth import views as auth_views

# urlpatterns = [
#     path('', views.home, name='home'),                # Home page
#     path('register/', views.register, name='register'),
#     path('login/', views.custom_login, name='login'),
#     path('logout/',                                   # <— add this!
#          auth_views.LogoutView.as_view(next_page='login'),
#          name='logout'),
#     path('cart/', views.cart_view, name='cart'),
#     path('orders/', views.orders_view, name='orders'),
#     path('add_to_cart/<int:product_id>/', 
#          views.add_to_cart, name='add_to_cart'),
#     path('dashboard/', views.dashboard, name='dashboard'),

# ]


from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(next_page='login'),
         name='logout'),
   

    path('cart/', views.cart_view, name='cart'),
path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('orders/', views.orders_view, name='orders'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('dashboard/', views.dashboard, name='dashboard'),
     path('products/', views.products, name='products'),
    #  path('products/', views.product_list, name='product_list'),
      path('place-order/', views.place_order, name='place_order'),
    path('order-history/', views.order_history, name='order_history'),
    
        path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
        # In urls.py
path('product/<int:pk>/', views.product_detail, name='product_detail'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)