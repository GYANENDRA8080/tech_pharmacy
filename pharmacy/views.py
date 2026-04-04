from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.conf import settings
import json
import datetime
import io

from .models import Medicine, Bill, BillItem, Patient, StockTransaction


# ── Dashboard ─────────────────────────────────────────────────────────────────
def dashboard(request):
    today = datetime.date.today()
    this_month = today.replace(day=1)

    total_medicines = Medicine.objects.count()
    total_stock_value = sum(m.stock_value for m in Medicine.objects.all())
    bills_this_month = Bill.objects.filter(date__gte=this_month).count()
    revenue_this_month = Bill.objects.filter(
        date__gte=this_month, status='paid'
    ).aggregate(total=Sum('grand_total'))['total'] or 0

    low_stock = Medicine.objects.filter(stock__gt=0, stock__lte=5).count()
    out_of_stock = Medicine.objects.filter(stock__lte=0).count()
    expired = Medicine.objects.filter(expiry__lt=today).exclude(stock__lte=0).count()
    expiring_soon = Medicine.objects.filter(
        expiry__gte=today,
        expiry__lte=today + datetime.timedelta(days=90)
    ).count()

    recent_bills = Bill.objects.select_related('patient').order_by('-created_at')[:8]
    alert_medicines = Medicine.objects.filter(
        Q(stock__lte=5) | Q(expiry__lt=today + datetime.timedelta(days=90))
    ).order_by('stock')[:10]

    # Category breakdown
    categories = Medicine.objects.values('category').annotate(
        count=Count('id'), total_stock=Sum('stock')
    ).order_by('-count')[:8]

    context = {
        'total_medicines': total_medicines,
        'total_stock_value': total_stock_value,
        'bills_this_month': bills_this_month,
        'revenue_this_month': revenue_this_month,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'expired': expired,
        'expiring_soon': expiring_soon,
        'recent_bills': recent_bills,
        'alert_medicines': alert_medicines,
        'categories': categories,
        'today': today,
    }
    return render(request, 'pharmacy/dashboard.html', context)


# ── Inventory ─────────────────────────────────────────────────────────────────
def inventory(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    medicines = Medicine.objects.all()
    if q:
        medicines = medicines.filter(name__icontains=q)
    if category:
        medicines = medicines.filter(category=category)

    today = datetime.date.today()
    if status_filter == 'out_of_stock':
        medicines = medicines.filter(stock__lte=0)
    elif status_filter == 'low_stock':
        medicines = medicines.filter(stock__gt=0, stock__lte=5)
    elif status_filter == 'expired':
        medicines = medicines.filter(expiry__lt=today)
    elif status_filter == 'expiring_soon':
        medicines = medicines.filter(expiry__gte=today, expiry__lte=today + datetime.timedelta(days=90))
    elif status_filter == 'in_stock':
        medicines = medicines.filter(stock__gt=5)

    categories = Medicine.objects.values_list('category', flat=True).distinct().order_by('category')

    context = {
        'medicines': medicines,
        'categories': categories,
        'q': q,
        'selected_category': category,
        'status_filter': status_filter,
        'total_count': medicines.count(),
    }
    return render(request, 'pharmacy/inventory.html', context)


def medicine_add(request):
    if request.method == 'POST':
        try:
            med = Medicine(
                name=request.POST['name'].upper().strip(),
                category=request.POST['category'],
                batch_no=request.POST.get('batch_no', ''),
                pack=request.POST.get('pack', '1*10'),
                mrp=float(request.POST.get('mrp', 0)),
                gst_percent=float(request.POST.get('gst_percent', 12)),
                stock=float(request.POST.get('stock', 0)),
            )
            mfd_str = request.POST.get('mfd', '')
            expiry_str = request.POST.get('expiry', '')
            if mfd_str:
                med.mfd = datetime.datetime.strptime(mfd_str, '%Y-%m-%d').date()
            if expiry_str:
                med.expiry = datetime.datetime.strptime(expiry_str, '%Y-%m-%d').date()
            med.save()
            messages.success(request, f'Medicine "{med.name}" added successfully!')
            return redirect('inventory')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    categories = Medicine.CATEGORY_CHOICES
    return render(request, 'pharmacy/medicine_form.html', {'categories': categories, 'action': 'Add'})


def medicine_edit(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        try:
            med.name = request.POST['name'].upper().strip()
            med.category = request.POST['category']
            med.batch_no = request.POST.get('batch_no', '')
            med.pack = request.POST.get('pack', '1*10')
            med.mrp = float(request.POST.get('mrp', 0))
            med.gst_percent = float(request.POST.get('gst_percent', 12))
            med.stock = float(request.POST.get('stock', 0))
            mfd_str = request.POST.get('mfd', '')
            expiry_str = request.POST.get('expiry', '')
            if mfd_str:
                med.mfd = datetime.datetime.strptime(mfd_str, '%Y-%m-%d').date()
            if expiry_str:
                med.expiry = datetime.datetime.strptime(expiry_str, '%Y-%m-%d').date()
            med.save()
            messages.success(request, f'Medicine "{med.name}" updated!')
            return redirect('inventory')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    categories = Medicine.CATEGORY_CHOICES
    return render(request, 'pharmacy/medicine_form.html', {
        'medicine': med, 'categories': categories, 'action': 'Edit'
    })


def medicine_delete(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        name = med.name
        med.delete()
        messages.success(request, f'Medicine "{name}" deleted.')
        return redirect('inventory')
    return render(request, 'pharmacy/confirm_delete.html', {'object': med, 'type': 'Medicine'})


def medicine_detail(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    transactions = StockTransaction.objects.filter(medicine=med).order_by('-created_at')[:20]
    return render(request, 'pharmacy/medicine_detail.html', {'medicine': med, 'transactions': transactions})


def stock_adjust(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        qty = float(request.POST.get('quantity', 0))
        tx_type = request.POST.get('type', 'in')
        note = request.POST.get('note', '')
        if tx_type == 'in':
            med.stock += qty
        elif tx_type == 'out':
            med.stock = max(0, float(med.stock) - qty)
        else:
            med.stock = qty
        med.save()
        StockTransaction.objects.create(medicine=med, transaction_type=tx_type, quantity=qty, note=note)
        messages.success(request, f'Stock updated for {med.name}')
        return redirect('medicine_detail', pk=pk)
    return render(request, 'pharmacy/stock_adjust.html', {'medicine': med})


# ── Billing ───────────────────────────────────────────────────────────────────
def billing(request):
    bills = Bill.objects.prefetch_related('items').order_by('-created_at')
    q = request.GET.get('q', '')
    if q:
        bills = bills.filter(
            Q(bill_no__icontains=q) | Q(patient_name__icontains=q) | Q(doctor_name__icontains=q)
        )
    context = {'bills': bills, 'q': q}
    return render(request, 'pharmacy/billing.html', context)


def create_bill(request):
    medicines = Medicine.objects.filter(stock__gt=0).values(
        'id', 'name', 'category', 'pack', 'mrp', 'gst_percent', 'stock'
    )
    context = {'medicines_json': json.dumps(list(medicines), default=str)}
    return render(request, 'pharmacy/create_bill.html', context)


@require_POST
def save_bill(request):
    try:
        data = json.loads(request.body)
        patient_name = data.get('patient_name', '')
        doctor_name = data.get('doctor_name', '')
        items_data = data.get('items', [])

        if not items_data:
            return JsonResponse({'error': 'No items in bill'}, status=400)

        # Create or get patient
        patient = None
        if patient_name:
            patient, _ = Patient.objects.get_or_create(
                name=patient_name,
                defaults={'doctor_name': doctor_name}
            )

        bill = Bill(
            patient=patient,
            patient_name=patient_name,
            doctor_name=doctor_name,
            date=datetime.date.today(),
        )
        bill.save()

        subtotal = 0
        total_discount = 0
        total_gst = 0
        grand_total = 0

        for item_data in items_data:
            med = Medicine.objects.get(id=item_data['medicine_id'])
            qty = float(item_data['quantity'])
            discount = float(item_data.get('discount', 0))
            gst_pct = float(item_data.get('gst_percent', med.gst_percent))
            mrp = float(item_data.get('mrp', med.mrp))

            item = BillItem(
                bill=bill,
                medicine=med,
                medicine_name=med.name,
                category=med.category,
                pack=med.pack,
                mrp=mrp,
                quantity=qty,
                discount_percent=discount,
                gst_percent=gst_pct,
            )
            item.save()

            # Deduct stock
            med.stock = max(0, float(med.stock) - qty)
            med.save()
            StockTransaction.objects.create(
                medicine=med, transaction_type='out', quantity=qty,
                note=f'Bill #{bill.bill_no}'
            )

            subtotal += item.amount_before_discount
            total_discount += item.amount_before_discount * discount / 100
            total_gst += float(item.gst_amount)
            grand_total += float(item.final_amount)

        bill.subtotal = subtotal
        bill.total_discount = total_discount
        bill.total_gst = total_gst
        bill.grand_total = grand_total
        bill.save()

        return JsonResponse({'success': True, 'bill_id': bill.id, 'bill_no': bill.bill_no})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    return render(request, 'pharmacy/bill_detail.html', {'bill': bill})


def bill_pdf(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm, cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=15*mm, leftMargin=15*mm,
                                topMargin=15*mm, bottomMargin=15*mm)

        styles = getSampleStyleSheet()
        story = []

        # Header style
        header_style = ParagraphStyle('Header', parent=styles['Normal'],
                                      fontSize=18, fontName='Helvetica-Bold',
                                      textColor=colors.HexColor('#1a5276'),
                                      alignment=TA_CENTER, spaceAfter=2)
        sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
                                   fontSize=9, alignment=TA_CENTER,
                                   textColor=colors.HexColor('#555'))
        label_style = ParagraphStyle('Label', parent=styles['Normal'],
                                     fontSize=9, fontName='Helvetica-Bold')
        value_style = ParagraphStyle('Value', parent=styles['Normal'], fontSize=9)

        # Title
        story.append(Paragraph(f"✚ {settings.PHARMACY_NAME}", header_style))
        story.append(Paragraph(
            f"Prop: {settings.PHARMACY_OWNER} | {settings.PHARMACY_DOCTOR} | "
            f"📞 {settings.PHARMACY_PHONE1} / {settings.PHARMACY_PHONE2}", sub_style))
        story.append(Paragraph(settings.PHARMACY_ADDRESS, sub_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a5276')))
        story.append(Spacer(1, 5*mm))

        # Bill info
        info_data = [
            [Paragraph('<b>Bill No:</b>', label_style), Paragraph(bill.bill_no, value_style),
             Paragraph('<b>Date:</b>', label_style), Paragraph(str(bill.date), value_style)],
            [Paragraph('<b>Patient:</b>', label_style), Paragraph(bill.patient_name or '-', value_style),
             Paragraph('<b>Doctor:</b>', label_style), Paragraph(bill.doctor_name or '-', value_style)],
        ]
        info_table = Table(info_data, colWidths=[30*mm, 65*mm, 25*mm, 60*mm])
        info_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 5*mm))

        # Items table
        headers = ['#', 'Medicine', 'Cat', 'Pack', 'MRP(₹)', 'Qty', 'Disc%', 'GST%', 'Amount(₹)']
        table_data = [headers]
        for i, item in enumerate(bill.items.all(), 1):
            table_data.append([
                str(i),
                item.medicine_name,
                item.category,
                item.pack,
                f"{float(item.mrp):.2f}",
                f"{float(item.quantity):.2f}",
                f"{float(item.discount_percent):.1f}%",
                f"{float(item.gst_percent):.0f}%",
                f"{float(item.final_amount):.2f}",
            ])

        col_widths = [10*mm, 45*mm, 18*mm, 14*mm, 20*mm, 14*mm, 16*mm, 14*mm, 22*mm]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eaf4fb')]),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#ccc')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 5*mm))

        # Totals
        totals_data = [
            ['', '', '', '', '', '', '', 'Subtotal:', f"₹{float(bill.subtotal):.2f}"],
            ['', '', '', '', '', '', '', 'Discount:', f"-₹{float(bill.total_discount):.2f}"],
            ['', '', '', '', '', '', '', 'GST:', f"₹{float(bill.total_gst):.2f}"],
            ['', '', '', '', '', '', '', 'GRAND TOTAL:', f"₹{float(bill.grand_total):.2f}"],
        ]
        totals_table = Table(totals_data, colWidths=col_widths)
        totals_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (7, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (7, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (7, 3), (-1, 3), 11),
            ('TEXTCOLOR', (7, 3), (-1, 3), colors.HexColor('#1a5276')),
            ('LINEABOVE', (7, 3), (-1, 3), 1, colors.HexColor('#1a5276')),
        ]))
        story.append(totals_table)

        story.append(Spacer(1, 8*mm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ccc')))
        story.append(Spacer(1, 3*mm))
        thank_style = ParagraphStyle('Thank', parent=styles['Normal'],
                                     fontSize=9, alignment=TA_CENTER,
                                     textColor=colors.HexColor('#777'))
        story.append(Paragraph("Thank you for choosing Swastik Pharmacy & Surgical Center", thank_style))
        story.append(Paragraph("Get well soon! 🙏", thank_style))

        doc.build(story)
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="Bill_{bill.bill_no}.pdf"'
        return response

    except ImportError:
        return HttpResponse(
            "ReportLab not installed. Run: pip install reportlab",
            content_type='text/plain', status=500
        )


# ── Alerts ────────────────────────────────────────────────────────────────────
def alerts(request):
    today = datetime.date.today()
    out_of_stock = Medicine.objects.filter(stock__lte=0)
    low_stock = Medicine.objects.filter(stock__gt=0, stock__lte=5)
    expired = Medicine.objects.filter(expiry__lt=today)
    expiring_soon = Medicine.objects.filter(
        expiry__gte=today,
        expiry__lte=today + datetime.timedelta(days=90)
    )
    context = {
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'expired': expired,
        'expiring_soon': expiring_soon,
    }
    return render(request, 'pharmacy/alerts.html', context)


# ── WhatsApp ──────────────────────────────────────────────────────────────────
def send_whatsapp_bill(request, pk):
    """Send bill via WhatsApp Business API"""
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        if not phone:
            messages.error(request, 'Phone number required')
            return redirect('bill_detail', pk=pk)

        # WhatsApp message content
        items_text = '\n'.join([
            f"• {item.medicine_name} x{float(item.quantity):.0f} = ₹{float(item.final_amount):.2f}"
            for item in bill.items.all()
        ])

        message = (
            f"🏥 *{settings.PHARMACY_NAME}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📄 *Bill No:* {bill.bill_no}\n"
            f"📅 *Date:* {bill.date}\n"
            f"👤 *Patient:* {bill.patient_name}\n"
            f"👨‍⚕️ *Doctor:* {bill.doctor_name}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💊 *Medicines:*\n{items_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Subtotal:* ₹{float(bill.subtotal):.2f}\n"
            f"🏷️ *Discount:* -₹{float(bill.total_discount):.2f}\n"
            f"📊 *GST:* ₹{float(bill.total_gst):.2f}\n"
            f"✅ *TOTAL: ₹{float(bill.grand_total):.2f}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📞 {settings.PHARMACY_PHONE1}\n"
            f"Get well soon! 🙏"
        )

        import urllib.parse
        wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"

        # Mark as sent
        bill.whatsapp_sent = True
        bill.save()

        return JsonResponse({'success': True, 'wa_url': wa_url, 'message': message})

    return JsonResponse({'error': 'POST required'}, status=400)


# ── API Endpoints ─────────────────────────────────────────────────────────────
def medicine_search_api(request):
    q = request.GET.get('q', '')
    medicines = Medicine.objects.filter(name__icontains=q, stock__gt=0)[:15]
    data = [{
        'id': m.id, 'name': m.name, 'category': m.category,
        'pack': m.pack, 'mrp': float(m.mrp),
        'gst_percent': float(m.gst_percent), 'stock': float(m.stock)
    } for m in medicines]
    return JsonResponse({'results': data})


def dashboard_stats_api(request):
    today = datetime.date.today()
    this_month = today.replace(day=1)
    bills_today = Bill.objects.filter(date=today)
    return JsonResponse({
        'revenue_today': float(bills_today.aggregate(t=Sum('grand_total'))['t'] or 0),
        'bills_today': bills_today.count(),
        'total_medicines': Medicine.objects.count(),
        'low_stock_count': Medicine.objects.filter(stock__gt=0, stock__lte=5).count(),
    })
