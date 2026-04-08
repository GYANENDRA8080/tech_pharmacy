from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create admin user for pharmacy management system"

    def handle(self, *args, **kwargs):
        # Delete old demo users
        User.objects.filter(username__in=["admin", "pharmacist"]).delete()
        self.stdout.write(self.style.WARNING("Removed old users"))

        # Create new admin user with secure credentials
        admin_user = User.objects.create_user(
            username="Gyan123@",
            email="gyan@swastikpharmacy.com",
            password="Gyan321@",
            first_name="Gyan",
            last_name="Admin",
            is_staff=True,
            is_superuser=True,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Admin user created successfully!\n"
                f"  Username: Gyan123@\n"
                f"  Password: Gyan321@\n"
                f"  Email: gyan@swastikpharmacy.com\n"
                f"  Status: KEEP THIS SECRET - Share only with authorized users!"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Admin user is ready!\n"
                f"⚠️  WARNING: Do not share these credentials with unauthorized people!"
            )
        )
