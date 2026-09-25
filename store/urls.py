from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Public
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # Auth
    path('register/', views.register, name='register'),

    # Checkout / Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),

    # ===== STAFF / MANAGER (UI-Based) =====
    path('manage/', views.manage_dashboard, name='manage_dashboard'),
    path('manage/products/', views.manage_products, name='manage_products'),
    path('manage/products/add/', views.manage_product_create, name='manage_product_create'),
    path('manage/products/edit/<int:product_id>/', views.manage_product_edit, name='manage_product_edit'),
    path('manage/products/delete/<int:product_id>/', views.manage_product_delete, name='manage_product_delete'),
    path('manage/categories/', views.manage_categories, name='manage_categories'),
    path('manage/categories/add/', views.manage_category_create, name='manage_category_create'),
    path('manage/categories/edit/<int:category_id>/', views.manage_category_edit, name='manage_category_edit'),
    path('manage/categories/delete/<int:category_id>/', views.manage_category_delete, name='manage_category_delete'),
    path('manage/orders/', views.manage_orders, name='manage_orders'),
    path('manage/orders/<int:order_id>/', views.manage_order_detail, name='manage_order_detail'),
    path('manage/users/', views.manage_users, name='manage_users'),
]
