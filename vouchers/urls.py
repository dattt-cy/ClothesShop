from django.urls import path
from . import views

urlpatterns = [
    path('', views.voucher_list, name='voucher_list'),
    path('collect/<int:voucher_id>/', views.collect_voucher, name='collect_voucher'),
    path('apply/', views.apply_voucher, name='apply_voucher'),
    path('remove/', views.remove_voucher, name='remove_voucher'),
]
