from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Inventory
    path('inventory/', views.inventory, name='inventory'),
    path('inventory/add/', views.medicine_add, name='medicine_add'),
    path('inventory/<int:pk>/', views.medicine_detail, name='medicine_detail'),
    path('inventory/<int:pk>/edit/', views.medicine_edit, name='medicine_edit'),
    path('inventory/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    path('inventory/<int:pk>/stock/', views.stock_adjust, name='stock_adjust'),
    
    # Billing
    path('billing/', views.billing, name='billing'),
    path('billing/create/', views.create_bill, name='create_bill'),
    path('billing/save/', views.save_bill, name='save_bill'),
    path('billing/<int:pk>/', views.bill_detail, name='bill_detail'),
    path('billing/<int:pk>/pdf/', views.bill_pdf, name='bill_pdf'),
    path('billing/<int:pk>/whatsapp/', views.send_whatsapp_bill, name='send_whatsapp'),
    
    # Alerts
    path('alerts/', views.alerts, name='alerts'),
    
    # API
    path('api/medicines/', views.medicine_search_api, name='medicine_search_api'),
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
]
