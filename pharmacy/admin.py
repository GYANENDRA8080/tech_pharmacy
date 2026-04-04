from django.contrib import admin
from .models import Medicine, Bill, BillItem, Patient, StockTransaction


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'stock', 'mrp', 'expiry', 'status_display']
    list_filter = ['category']
    search_fields = ['name', 'batch_no']
    ordering = ['name']


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_no', 'patient_name', 'date', 'grand_total', 'status']
    list_filter = ['status', 'date']
    search_fields = ['bill_no', 'patient_name']


@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ['bill', 'medicine_name', 'quantity', 'mrp', 'final_amount']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'doctor_name', 'created_at']
    search_fields = ['name', 'phone']


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'transaction_type', 'quantity', 'created_at']
    list_filter = ['transaction_type']
