from django.urls import path
from . import views


urlpatterns = [
path('', views.home, name='home'),
path('add/<int:product_id>/', views.add_to_cart, name='add'),
path('cart/', views.cart, name='cart'),
path('increase/<int:item_id>/', views.increase_quantity, name='increase'),
path('decrease/<int:item_id>/', views.decrease_quantity, name='decrease'),
path('remove/<int:item_id>/', views.remove_item, name='remove'),
path('checkout/', views.checkout, name='checkout'),
path('success/', views.success, name='success'),
path('my-orders/', views.my_orders, name='my_orders'),
path('stripe-checkout/', views.stripe_checkout, name='stripe_checkout'),




]