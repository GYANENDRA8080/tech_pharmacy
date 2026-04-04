from django.db import models
from django.utils import timezone
import datetime


class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ('INJ', 'Injection'),
        ('TAB', 'Tablet'),
        ('CAP', 'Capsule'),
        ('SYRUP', 'Syrup'),
        ('DROP', 'Drop'),
        ('OINTMENT', 'Ointment'),
        ('POWDER', 'Powder'),
        ('SURGICAL', 'Surgical'),
        ('FLUID', 'Fluid/IV'),
        ('INFUSION', 'Infusion'),
        ('RESPULE', 'Respule'),
        ('EAR DROP', 'Ear Drop'),
        ('NASAL SPRAY', 'Nasal Spray'),
        ('MOUTH WASH', 'Mouth Wash'),
        ('SHAMPOO', 'Shampoo'),
        ('SOAP', 'Soap'),
        ('NRX TAB', 'NRX Tablet'),
        ('BETADINE GARGLE', 'Betadine Gargle'),
        ('PC', 'PC'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='TAB')
    batch_no = models.CharField(max_length=100, blank=True)
    mfd = models.DateField(null=True, blank=True)
    expiry = models.DateField(null=True, blank=True)
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pack = models.CharField(max_length=20, default='1*10')
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def stock_value(self):
        return float(self.stock) * float(self.mrp)

    @property
    def status(self):
        if self.stock <= 0:
            return 'out_of_stock'
        elif self.stock <= 5:
            return 'low_stock'
        elif self.expiry and self.expiry < datetime.date.today():
            return 'expired'
        elif self.expiry and self.expiry <= datetime.date.today() + datetime.timedelta(days=90):
            return 'expiring_soon'
        return 'in_stock'

    @property
    def status_display(self):
        s = self.status
        mapping = {
            'out_of_stock': 'Out of Stock',
            'low_stock': 'Low Stock',
            'expired': 'Expired',
            'expiring_soon': 'Expiring Soon',
            'in_stock': 'In Stock',
        }
        return mapping.get(s, 'In Stock')

    @property
    def status_color(self):
        s = self.status
        mapping = {
            'out_of_stock': 'danger',
            'low_stock': 'warning',
            'expired': 'dark',
            'expiring_soon': 'orange',
            'in_stock': 'success',
        }
        return mapping.get(s, 'success')


class Patient(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    doctor_name = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Bill(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    bill_no = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    patient_name = models.CharField(max_length=200, blank=True)
    doctor_name = models.CharField(max_length=200, blank=True)
    date = models.DateField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')
    whatsapp_sent = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Bill #{self.bill_no}"

    def save(self, *args, **kwargs):
        if not self.bill_no:
            last = Bill.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.bill_no = f"SWS-{str(num).zfill(5)}"
        super().save(*args, **kwargs)


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True)
    medicine_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, blank=True)
    pack = models.CharField(max_length=20, blank=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    amount_before_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.medicine_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.amount_before_discount = float(self.mrp) * float(self.quantity)
        discount_amount = self.amount_before_discount * float(self.discount_percent) / 100
        after_discount = self.amount_before_discount - discount_amount
        self.gst_amount = after_discount * float(self.gst_percent) / 100
        self.final_amount = after_discount + self.gst_amount
        super().save(*args, **kwargs)


class StockTransaction(models.Model):
    TYPE_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out (Sale)'),
        ('adjustment', 'Adjustment'),
    ]
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine.name} - {self.transaction_type} - {self.quantity}"
