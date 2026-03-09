from django.urls import path
from . import views

urlpatterns = [
    # ---- Web Admin UI ----
    path('', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:id>/', views.delete_product, name='delete_product'),
    
    # ---- Staff Management ----
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/delete/<int:id>/', views.delete_staff, name='delete_staff'),
    
    # ---- APIs for Flutter App ----
    path('api/products/', views.api_products, name='api_products'),
    path('api/products/<int:id>/', views.api_product_detail, name='api_product_detail'),
]
