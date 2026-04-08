from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from pharmacy.models import Medicine, Bill, Patient, StockTransaction


class Command(BaseCommand):
    help = "Create admin and staff users with appropriate permissions"

    def handle(self, *args, **kwargs):
        # Delete existing demo users if they exist
        User.objects.filter(username__in=["admin_user", "staff_user"]).delete()
        self.stdout.write(self.style.WARNING("Cleaned up old users"))

        # ========== ADMIN USER ==========
        admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@swastikpharmacy.com",
            password="Admin@123",
            first_name="Admin",
            last_name="Full Access",
            is_staff=True,
            is_superuser=True,  # Full permissions
        )

        self.stdout.write(
            self.style.SUCCESS(
                "✅ ADMIN USER CREATED:\n"
                f"  📧 Username: admin_user\n"
                f"  🔐 Password: Admin@123\n"
                f"  🎯 Access Level: FULL (All Features)\n"
                f"  ✨ Can access: Admin Panel, All Features, Settings\n"
            )
        )

        # ========== STAFF USER ==========
        staff_user = User.objects.create_user(
            username="staff_user",
            email="staff@swastikpharmacy.com",
            password="Staff@123",
            first_name="Staff",
            last_name="Limited Access",
            is_staff=True,
            is_superuser=False,  # No admin access
        )

        # Create/Get Staff group
        staff_group, created = Group.objects.get_or_create(name="Staff")

        # Add only necessary permissions for staff
        content_types = {
            "medicine": ContentType.objects.get_for_model(Medicine),
            "bill": ContentType.objects.get_for_model(Bill),
            "patient": ContentType.objects.get_for_model(Patient),
            "stock": ContentType.objects.get_for_model(StockTransaction),
        }

        # Define staff permissions
        staff_permissions = [
            # Medicine permissions
            "view_medicine",
            "add_medicine",
            "change_medicine",
            # Bill permissions
            "view_bill",
            "add_bill",
            "change_bill",
            # Patient permissions
            "view_patient",
            "add_patient",
            "change_patient",
            # Stock permissions
            "view_stocktransaction",
            "add_stocktransaction",
        ]

        for perm_codename in staff_permissions:
            try:
                permission = Permission.objects.get(codename=perm_codename)
                staff_group.permissions.add(permission)
            except Permission.DoesNotExist:
                pass

        staff_user.groups.add(staff_group)

        self.stdout.write(
            self.style.SUCCESS(
                "✅ STAFF USER CREATED:\n"
                f"  📧 Username: staff_user\n"
                f"  🔐 Password: Staff@123\n"
                f"  🎯 Access Level: LIMITED (Work Only)\n"
                f"  ✨ Can access: Pharmacy UI, Inventory, Billing\n"
                f"  ❌ Cannot access: Admin Panel, Settings\n"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                "\n"
                + "=" * 60
                + "\n📋 USER CREDENTIALS SUMMARY:\n"
                + "=" * 60
                + "\n\n🔓 ADMIN LOGIN:\n"
                + "  Username: admin_user\n"
                + "  Password: Admin@123\n"
                + "  Permissions: FULL ACCESS\n"
                + "\n👤 STAFF LOGIN:\n"
                + "  Username: staff_user\n"
                + "  Password: Staff@123\n"
                + "  Permissions: LIMITED (Workspace Only)\n"
                + "\n"
                + "=" * 60
            )
        )
