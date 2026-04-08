from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.shortcuts import redirect
from django.contrib import messages
from .models import Medicine, Bill, BillItem, Patient, StockTransaction


class DeveloperOnlyAdminSite(AdminSite):
    """Custom admin site that only allows superusers (developers) to access"""

    site_header = "Swastik Pharmacy - Developer Admin Panel"
    site_title = "Developer Admin"
    index_title = "Developer Dashboard"

    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        # Only allow superusers (developers) to access admin
        return request.user.is_active and request.user.is_superuser

    def login(self, request, extra_context=None):
        """
        Redirect non-superusers to dashboard with error message
        """
        if request.method == "POST":
            if not self.has_permission(request):
                messages.error(
                    request,
                    "❌ Access Denied: Admin panel is restricted to developers only!",
                )
                return redirect("dashboard")

        return super().login(request, extra_context)


# Create the custom admin site
developer_admin = DeveloperOnlyAdminSite(name="developer_admin")


# Define admin classes
class MedicineAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "stock", "mrp", "expiry", "status_display"]
    list_filter = ["category"]
    search_fields = ["name", "batch_no"]
    ordering = ["name"]


class BillAdmin(admin.ModelAdmin):
    list_display = ["bill_no", "patient_name", "date", "grand_total", "status"]
    list_filter = ["status", "date"]
    search_fields = ["bill_no", "patient_name"]


class BillItemAdmin(admin.ModelAdmin):
    list_display = ["bill", "medicine_name", "quantity", "mrp", "final_amount"]


class PatientAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "doctor_name", "created_at"]
    search_fields = ["name", "phone"]


class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ["medicine", "transaction_type", "quantity", "created_at"]
    list_filter = ["transaction_type"]


# Register models with the custom admin site
developer_admin.register(Medicine, MedicineAdmin)
developer_admin.register(Bill, BillAdmin)
developer_admin.register(BillItem, BillItemAdmin)
developer_admin.register(Patient, PatientAdmin)
developer_admin.register(StockTransaction, StockTransactionAdmin)
