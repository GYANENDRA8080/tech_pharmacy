# ✚ Swastik Pharmacy & Surgical Center — Management System

**Prop: Gayatri Upadhyay | Dr. Vikash Mishra | 📞 9450055621 / 8115409504**

A complete pharmacy management system built with Django. Features include:
- 📊 Live Dashboard with KPIs
- 💊 Full Medicine Inventory Management
- 🧾 Invoice / Billing with PDF Generation
- 📱 WhatsApp Bill Sharing (one-click)
- ⚠️ Expiry & Stock Alerts
- 📱 Mobile + Desktop Responsive UI

---

## 🚀 Quick Setup (First Time)

### Step 1 — Install Python (if not installed)
Download Python 3.11+ from https://www.python.org/downloads/

### Step 2 — Install dependencies
Open terminal/command prompt in this folder and run:
```bash
pip install -r requirements.txt
```

### Step 3 — Initialize the database
```bash
python manage.py migrate
```

### Step 4 — Import your medicines from Excel
Place your `Swastik_Pharmacy.xlsx` file in this folder, then run:
```bash
python manage.py import_medicines Swastik_Pharmacy.xlsx
```

### Step 5 — Create admin user (optional)
```bash
python manage.py createsuperuser
```

### Step 6 — Start the server
```bash
python manage.py runserver
```

### Step 7 — Open in browser
- **Main App:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

## 📱 Mobile Access (Same WiFi)
Run with your local IP:
```bash
python manage.py runserver 0.0.0.0:8000
```
Then open `http://YOUR-PC-IP:8000` on your mobile phone.

Find your PC IP:
- Windows: `ipconfig` → IPv4 Address
- Linux/Mac: `ifconfig` or `ip addr`

---

## 🧾 Features

### Dashboard
- Total medicines, stock value, monthly revenue
- Low stock, out-of-stock, expired, expiring soon counts
- Recent bills and urgent alerts

### Inventory
- Add / Edit / Delete medicines
- Filter by category, status (low stock, expired, etc.)
- Search by name
- Stock adjustment with transaction history

### Billing / Invoice
- Search and add medicines with autocomplete
- Auto-calculate GST, discounts, totals
- Generate professional PDF invoices
- Send bill via WhatsApp (opens WhatsApp with pre-filled message)

### Alerts
- Out of stock medicines
- Low stock (≤5 units)
- Expired medicines
- Expiring in next 90 days

---

## 📱 WhatsApp Integration
The system uses WhatsApp Web links (`wa.me`) to send bills.
When you click "Send WhatsApp":
1. Enter patient's phone number
2. Click "Open WhatsApp"
3. WhatsApp opens with the bill pre-filled — just hit Send!

For automated WhatsApp Business API (without manual confirmation),
configure `WHATSAPP_API_TOKEN` and `WHATSAPP_PHONE_ID` in `settings.py`.

---

## 🔐 Security (Before going live)
Edit `swastik_project/settings.py`:
```python
DEBUG = False
SECRET_KEY = 'your-very-secret-random-key-here'
ALLOWED_HOSTS = ['your-domain.com', 'your-ip-address']
```

---

## 📁 Project Structure
```
swastik_pharmacy/
├── manage.py
├── requirements.txt
├── Swastik_Pharmacy.xlsx     ← Place your Excel here
├── swastik_project/
│   ├── settings.py
│   └── urls.py
└── pharmacy/
    ├── models.py             ← Database models
    ├── views.py              ← Business logic
    ├── urls.py               ← URL routes
    ├── admin.py              ← Admin panel config
    ├── management/commands/
    │   └── import_medicines.py  ← Excel import command
    └── templates/pharmacy/   ← HTML templates
        ├── base.html
        ├── dashboard.html
        ├── inventory.html
        ├── create_bill.html
        ├── bill_detail.html
        ├── billing.html
        ├── alerts.html
        └── ...
```

---

## 💡 Tips
- **PDF Bills** require `reportlab` — included in requirements.txt
- **Import from Excel** — run `import_medicines` command anytime to sync
- **Admin Panel** — full CRUD for all data at `/admin/`
- All amounts are in **Indian Rupees (₹)**
- GST rates: INJ/Surgical = 5%, Tabs/Caps/Syrups = 12%, Shampoo/Soap = 18%
