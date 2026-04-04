#!/bin/bash

echo ""
echo "============================================"
echo " ✚ SWASTIK PHARMACY & SURGICAL CENTER"
echo "   Management System"
echo "============================================"
echo ""

# Install deps
echo "[1/4] Installing dependencies..."
pip install -r requirements.txt -q

# Migrate
echo "[2/4] Setting up database..."
python manage.py migrate --run-syncdb -v 0 2>/dev/null

# Import
echo "[3/4] Importing medicines..."
if [ -f "Swastik_Pharmacy.xlsx" ]; then
    python manage.py import_medicines Swastik_Pharmacy.xlsx
else
    echo "     [INFO] Place Swastik_Pharmacy.xlsx here to import medicines"
fi

# Start
echo "[4/4] Starting server..."
echo ""
echo "============================================"
echo " Open browser: http://127.0.0.1:8000"
echo " Mobile: http://$(hostname -I | awk '{print $1}'):8000"
echo " Press Ctrl+C to stop"
echo "============================================"
echo ""

python manage.py runserver 0.0.0.0:8000
