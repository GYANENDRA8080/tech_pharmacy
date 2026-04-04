"""
Management command to import medicines from Swastik_Pharmacy.xlsx
Usage: python manage.py import_medicines path/to/Swastik_Pharmacy.xlsx
"""
from django.core.management.base import BaseCommand
import pandas as pd
import datetime
import os


class Command(BaseCommand):
    help = 'Import medicines from Swastik Pharmacy Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', nargs='?',
                            default='Swastik_Pharmacy.xlsx',
                            help='Path to Excel file')

    def handle(self, *args, **options):
        from pharmacy.models import Medicine

        filepath = options['excel_file']
        if not os.path.exists(filepath):
            self.stderr.write(f'File not found: {filepath}')
            return

        self.stdout.write(f'📂 Reading {filepath}...')

        try:
            df = pd.read_excel(filepath, sheet_name='MedList', header=1)
            df.columns = ['name', 'category', 'pack', 'mrp', 'gst', 'stock']
            df = df.dropna(subset=['name'])
            df = df[df['name'].astype(str).str.strip() != '']
        except Exception as e:
            self.stderr.write(f'Error reading Excel: {e}')
            return

        # Also read inventory for batch/mfd/expiry
        try:
            df_inv = pd.read_excel(filepath, sheet_name='Inventory', header=3, skiprows=[0,1,2])
            df_inv.columns = ['num', 'name', 'category', 'batch_no', 'mfd', 'expiry', 'stock', 'pack', 'mrp', 'stock_value', 'status']
            df_inv = df_inv.dropna(subset=['name'])
            inv_dict = {}
            for _, row in df_inv.iterrows():
                inv_dict[str(row['name']).strip()] = row
        except Exception:
            inv_dict = {}

        created = 0
        updated = 0
        errors = 0

        for _, row in df.iterrows():
            try:
                name = str(row['name']).strip().upper()
                if not name:
                    continue

                category = str(row.get('category', 'TAB')).strip()
                pack = str(row.get('pack', '1*10')).strip()
                mrp = float(row.get('mrp', 0)) if pd.notna(row.get('mrp', 0)) else 0
                gst_raw = float(row.get('gst', 0.12)) if pd.notna(row.get('gst', 0.12)) else 0.12
                gst_percent = gst_raw * 100 if gst_raw <= 1 else gst_raw
                stock = float(row.get('stock', 0)) if pd.notna(row.get('stock', 0)) else 0

                inv_row = inv_dict.get(name, {})
                batch_no = ''
                mfd = None
                expiry = None

                if inv_row is not None and len(inv_row) > 0:
                    batch_no = str(inv_row.get('batch_no', '')).strip() if pd.notna(inv_row.get('batch_no', '')) else ''
                    mfd_raw = inv_row.get('mfd')
                    expiry_raw = inv_row.get('expiry')
                    if pd.notna(mfd_raw):
                        mfd = pd.to_datetime(mfd_raw).date() if not isinstance(mfd_raw, datetime.date) else mfd_raw
                    if pd.notna(expiry_raw):
                        expiry = pd.to_datetime(expiry_raw).date() if not isinstance(expiry_raw, datetime.date) else expiry_raw

                med, was_created = Medicine.objects.update_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'pack': pack,
                        'mrp': mrp,
                        'gst_percent': gst_percent,
                        'stock': stock,
                        'batch_no': batch_no,
                        'mfd': mfd,
                        'expiry': expiry,
                    }
                )
                if was_created:
                    created += 1
                    self.stdout.write(f'  ✅ Created: {name}')
                else:
                    updated += 1

            except Exception as e:
                errors += 1
                self.stderr.write(f'  ❌ Error for {row.get("name", "?")}: {e}')

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Import complete!\n'
            f'   ✅ Created: {created}\n'
            f'   🔄 Updated: {updated}\n'
            f'   ❌ Errors: {errors}\n'
        ))
