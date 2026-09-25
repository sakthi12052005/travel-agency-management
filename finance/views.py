from django.shortcuts import render, redirect, get_object_or_404
from .models import Tour, Payment
from .models import Tour, Customer, Payment
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Customer
from decimal import Decimal
from django.contrib.auth import logout


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(request):

    tours = Tour.objects.all().order_by('-tour_date')

    total_collection = sum(
        tour.collection or 0
        for tour in tours
    )

    total_expense = sum(
        tour.total_expense or 0
        for tour in tours
    )

    total_profit = (
        total_collection - total_expense
    )

    total_tours = tours.count()

    hotel_expense = sum(
        tour.hotel_expense or 0
        for tour in tours
    )

    car_expense = sum(
        tour.car_expense or 0
        for tour in tours
    )

    food_expense = sum(
        tour.food_expense or 0
        for tour in tours
    )

    other_expense = sum(
        tour.other_expense or 0
        for tour in tours
    )

    context = {
        'tours': tours,
        'total_collection': total_collection,
        'total_expense': total_expense,
        'total_profit': total_profit,
        'total_tours': total_tours,

        'hotel_expense': hotel_expense,
        'car_expense': car_expense,
        'food_expense': food_expense,
        'other_expense': other_expense,
    }

    return render(
        request,
        'finance/dashboard.html',
        context
    )


# =========================================================
# ADD TOUR
# =========================================================

def add_tour(request):

    if request.method == 'POST':

        Tour.objects.create(
            tour_name=request.POST.get('tour_name'),
            tour_date=request.POST.get('tour_date'),
            customer_count=request.POST.get('customer_count'),

            package_amount=request.POST.get('package_amount') or 0,
            collection=request.POST.get('collection') or 0,

            hotel_expense=request.POST.get('hotel_expense') or 0,
            car_expense=request.POST.get('car_expense') or 0,
            food_expense=request.POST.get('food_expense') or 0,
            other_expense=request.POST.get('other_expense') or 0,
        )

        return redirect('dashboard')

    return render(
        request,
        'finance/add_tour.html'
    )


# =========================================================
# TOUR LIST
# =========================================================

def tour_list(request):

    tours = Tour.objects.all().order_by('-tour_date')

    return render(
        request,
        'finance/tour_list.html',
        {
            'tours': tours
        }
    )


# =========================================================
# TOUR DETAIL
# =========================================================

def tour_detail(request, tour_id):

    tour = get_object_or_404(
        Tour,
        id=tour_id
    )

    return render(
        request,
        'finance/tour_detail.html',
        {
            'tour': tour
        }
    )


# =========================================================
# EDIT TOUR
# =========================================================

def edit_tour(request, tour_id):

    tour = get_object_or_404(
        Tour,
        id=tour_id
    )

    if request.method == 'POST':

        tour.tour_name = request.POST.get('tour_name')
        tour.tour_date = request.POST.get('tour_date')
        tour.customer_count = request.POST.get('customer_count')

        tour.package_amount = (
            request.POST.get('package_amount') or 0
        )

        tour.collection = (
            request.POST.get('collection') or 0
        )

        tour.hotel_expense = (
            request.POST.get('hotel_expense') or 0
        )

        tour.car_expense = (
            request.POST.get('car_expense') or 0
        )

        tour.food_expense = (
            request.POST.get('food_expense') or 0
        )

        tour.other_expense = (
            request.POST.get('other_expense') or 0
        )

        tour.save()

        return redirect(
            'tour_detail',
            tour_id=tour.id
        )

    return render(
        request,
        'finance/edit_tour.html',
        {
            'tour': tour
        }
    )


# =========================================================
# DELETE TOUR
# =========================================================

def delete_tour(request, tour_id):

    tour = get_object_or_404(
        Tour,
        id=tour_id
    )

    if request.method == 'POST':

        tour.delete()

        return redirect('tour_list')

    return render(
        request,
        'finance/delete_tour.html',
        {
            'tour': tour
        }
    )


# =========================================================
# ADD PAYMENT
# =========================================================

def add_payment(request, tour_id=None):

    # If payment is opened from a specific tour
    selected_tour = None

    if tour_id:
        selected_tour = get_object_or_404(Tour, id=tour_id)

    # Get all tours
    tours = Tour.objects.all().order_by('-tour_date')

    if request.method == 'POST':

        # If no tour was selected from URL, get it from form
        selected_tour_id = request.POST.get('tour_id')

        if not selected_tour_id:
            return render(
                request,
                'finance/add_payment.html',
                {
                    'tours': tours,
                    'selected_tour': selected_tour,
                    'error': 'Please select a tour.'
                }
            )

        selected_tour = get_object_or_404(
            Tour,
            id=selected_tour_id
        )

        amount = request.POST.get('amount') or 0

        try:
            amount = float(amount)
        except ValueError:
            amount = 0

        # Calculate already paid amount
        total_paid = sum(
            payment.amount
            for payment in selected_tour.payments.all()
        )

        pending = selected_tour.package_amount - total_paid

        # Prevent overpayment
        if amount > pending:

            return render(
                request,
                'finance/add_payment.html',
                {
                    'tours': tours,
                    'selected_tour': selected_tour,
                    'pending': pending,
                    'error': f'Payment cannot exceed pending amount ₹{pending:,.2f}'
                }
            )

        if amount <= 0:

            return render(
                request,
                'finance/add_payment.html',
                {
                    'tours': tours,
                    'selected_tour': selected_tour,
                    'pending': pending,
                    'error': 'Payment amount must be greater than ₹0.'
                }
            )

        # Create payment
        Payment.objects.create(
            tour=selected_tour,
            amount=amount,
            payment_date=request.POST.get('payment_date'),
            payment_method=request.POST.get('payment_method'),
            note=request.POST.get('note', '')
        )

        # Recalculate collection
        total_paid = sum(
            payment.amount
            for payment in selected_tour.payments.all()
        )

        selected_tour.collection = total_paid
        selected_tour.save()

        # Go back to tour detail
        return redirect(
            'tour_detail',
            tour_id=selected_tour.id
        )

    # Calculate pending for selected tour
    pending = None

    if selected_tour:
        total_paid = sum(
            payment.amount
            for payment in selected_tour.payments.all()
        )

        pending = selected_tour.package_amount - total_paid

    return render(
        request,
        'finance/add_payment.html',
        {
            'tours': tours,
            'selected_tour': selected_tour,
            'pending': pending
        }
    )
# =========================================================
# REPORTS
# =========================================================

def reports(request):

    tours = Tour.objects.all().order_by('-tour_date')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date:
        tours = tours.filter(
            tour_date__gte=from_date
        )

    if to_date:
        tours = tours.filter(
            tour_date__lte=to_date
        )

    report_tours = []

    for tour in tours:

        total_expense = (
            (tour.hotel_expense or 0)
            + (tour.car_expense or 0)
            + (tour.food_expense or 0)
            + (tour.other_expense or 0)
        )

        profit = (
            (tour.collection or 0)
            - total_expense
        )

        report_tours.append({
            'id': tour.id,
            'tour_name': tour.tour_name,
            'tour_date': tour.tour_date,
            'customer_count': tour.customer_count,
            'package_amount': tour.package_amount or 0,
            'collection': tour.collection or 0,
            'hotel_expense': tour.hotel_expense or 0,
            'car_expense': tour.car_expense or 0,
            'food_expense': tour.food_expense or 0,
            'other_expense': tour.other_expense or 0,
            'total_expense': total_expense,
            'profit': profit,
        })
    # -----------------------------------------------------
    # TOTALS
    # -----------------------------------------------------

    total_tours = len(report_tours)

    total_collection = sum(
        tour['collection']
        for tour in report_tours
    )

    total_hotel = sum(
        tour['hotel_expense']
        for tour in report_tours
    )

    total_car = sum(
        tour['car_expense']
        for tour in report_tours
    )

    total_food = sum(
        tour['food_expense']
        for tour in report_tours
    )

    total_other = sum(
        tour['other_expense']
        for tour in report_tours
    )

    total_expense = (
        total_hotel
        + total_car
        + total_food
        + total_other
    )

    total_profit = (
        total_collection
        - total_expense
    )

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {
    'tours': report_tours,
    'from_date': from_date,
    'to_date': to_date,

    'total_tours': total_tours,
    'total_collection': total_collection,
    'total_expense': total_expense,
    'total_profit': total_profit,

    'total_hotel': total_hotel,
    'total_car': total_car,
    'total_food': total_food,
    'total_other': total_other,
}
    return render(
        request,
        'finance/reports.html',
        context
    )
def report_pdf(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="ADN_Financial_Report.pdf"'
    )

    pdf = canvas.Canvas(response)
    pdf.setTitle("ADN Financial Report")

    # =========================
    # GET TOURS
    # =========================

    tours = Tour.objects.all().order_by('tour_date')

    if from_date:
        tours = tours.filter(tour_date__gte=from_date)

    if to_date:
        tours = tours.filter(tour_date__lte=to_date)

    # =========================
    # TOTALS
    # =========================

    total_collection = 0
    total_expense = 0

    for tour in tours:
        total_collection += tour.collection or 0
        total_expense += tour.total_expense

    total_profit = total_collection - total_expense

    # =========================
    # HEADER
    # =========================

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(50, 800, "ADN - Financial Report")

    pdf.setFont("Helvetica", 11)

    y = 770

    if from_date:
        pdf.drawString(50, y, f"From Date: {from_date}")
        y -= 20

    if to_date:
        pdf.drawString(50, y, f"To Date: {to_date}")
        y -= 25

    pdf.line(50, y, 550, y)
    y -= 30

    # =========================
    # SUMMARY
    # =========================

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Financial Summary")

    y -= 25

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        50, y,
        f"Total Tours: {tours.count()}"
    )
    y -= 22

    pdf.drawString(
        50, y,
        f"Total Collection: Rs. {total_collection:,.2f}"
    )
    y -= 22

    pdf.drawString(
        50, y,
        f"Total Expenses: Rs. {total_expense:,.2f}"
    )
    y -= 22

    pdf.drawString(
        50, y,
        f"Net Profit: Rs. {total_profit:,.2f}"
    )

    y -= 35

    pdf.line(50, y, 550, y)

    y -= 30

    # =========================
    # TOUR DETAILS
    # =========================

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(50, y, "Tour-wise Financial Details")

    y -= 30

    for tour in tours:

        # New page if required
        if y < 170:
            pdf.showPage()
            y = 800

            pdf.setFont("Helvetica-Bold", 15)
            pdf.drawString(
                50, y,
                "ADN - Tour-wise Financial Details"
            )

            y -= 35

        # -------------------------
        # TOUR HEADER
        # -------------------------

        pdf.setFont("Helvetica-Bold", 13)

        pdf.drawString(
            50,
            y,
            f"Tour: {tour.tour_name}"
        )

        y -= 20

        pdf.setFont("Helvetica", 10)

        tour_date = (
            tour.tour_date.strftime("%d-%m-%Y")
            if tour.tour_date
            else "-"
        )

        pdf.drawString(
            50,
            y,
            f"Tour Date: {tour_date}"
        )

        pdf.drawString(
            250,
            y,
            f"Customers: {tour.customer_count or 0}"
        )

        y -= 20

        pdf.drawString(
            50,
            y,
            f"Package Amount: Rs. {tour.package_amount or 0:,.2f}"
        )

        y -= 25

        # -------------------------
        # FINANCIAL DETAILS
        # -------------------------

        pdf.setFont("Helvetica-Bold", 10)

        pdf.drawString(50, y, "Collection")
        pdf.drawString(180, y, "Hotel")
        pdf.drawString(280, y, "Car")
        pdf.drawString(370, y, "Food")
        pdf.drawString(450, y, "Other")

        y -= 15

        pdf.setFont("Helvetica", 10)

        pdf.drawString(
            50,
            y,
            f"Rs. {(tour.collection or 0):,.2f}"
        )

        pdf.drawString(
            180,
            y,
            f"Rs. {(tour.hotel_expense or 0):,.2f}"
        )

        pdf.drawString(
            280,
            y,
            f"Rs. {(tour.car_expense or 0):,.2f}"
        )

        pdf.drawString(
            370,
            y,
            f"Rs. {(tour.food_expense or 0):,.2f}"
        )

        pdf.drawString(
            450,
            y,
            f"Rs. {(tour.other_expense or 0):,.2f}"
        )

        y -= 22

        # -------------------------
        # EXPENSE + PROFIT
        # -------------------------

        pdf.setFont("Helvetica-Bold", 10)

        pdf.drawString(
            50,
            y,
            f"Total Expense: Rs. {tour.total_expense:,.2f}"
        )

        pdf.drawString(
            300,
            y,
            f"Profit: Rs. {((tour.collection or 0) - tour.total_expense):,.2f}"
        )

        y -= 20

        pdf.line(50, y, 550, y)

        y -= 25

    # =========================
    # FOOTER
    # =========================

    pdf.setFont("Helvetica", 9)

    if y < 60:
        pdf.showPage()
        y = 800

    pdf.drawString(
        50,
        y,
        "Generated by ADN Travel Finance System"
    )

    pdf.save()

    return response
# =========================================================
# EDIT PAYMENT
# =========================================================

def edit_payment(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    tour = payment.tour

    # Other payments total
    other_paid = sum(
        p.amount
        for p in tour.payments.all()
        if p.id != payment.id
    )

    max_allowed = (
        tour.package_amount - other_paid
    )

    if request.method == 'POST':

        amount = float(
            request.POST.get('amount') or 0
        )

        # Amount cannot be zero
        if amount <= 0:

            return render(
                request,
                'finance/edit_payment.html',
                {
                    'payment': payment,
                    'tour': tour,
                    'max_allowed': max_allowed,
                    'error': (
                        'Payment amount must be greater than ₹0.'
                    )
                }
            )

        # Prevent overpayment
        if amount > max_allowed:

            return render(
                request,
                'finance/edit_payment.html',
                {
                    'payment': payment,
                    'tour': tour,
                    'max_allowed': max_allowed,
                    'error': (
                        f'Payment cannot exceed '
                        f'₹{max_allowed:,.2f}'
                    )
                }
            )

        payment.amount = amount

        payment.payment_date = (
            request.POST.get('payment_date')
        )

        payment.payment_method = (
            request.POST.get('payment_method')
        )

        payment.note = (
            request.POST.get('note', '')
        )

        payment.save()

        # Recalculate collection
        tour.collection = sum(
            p.amount
            for p in tour.payments.all()
        )

        tour.save()

        return redirect(
            'tour_detail',
            tour_id=tour.id
        )

    return render(
        request,
        'finance/edit_payment.html',
        {
            'payment': payment,
            'tour': tour,
            'max_allowed': max_allowed
        }
    )


# =========================================================
# DELETE PAYMENT
# =========================================================

def delete_payment(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    tour = payment.tour

    if request.method == 'POST':

        payment.delete()

        # Recalculate collection
        tour.collection = sum(
            p.amount
            for p in tour.payments.all()
        )

        tour.save()

        return redirect(
            'tour_detail',
            tour_id=tour.id
        )

    return redirect(
        'tour_detail',
        tour_id=tour.id
    )
# ============================
# CUSTOMERS
# ============================

def customers(request):
    customers = Customer.objects.all().order_by('-created_at')

    return render(
        request,
        'finance/customers.html',
        {
            'customers': customers
        }
    )


def add_customer(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')

        Customer.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address
        )

        return redirect('customers')

    return render(
        request,
        'finance/add_customer.html'
    )


def edit_customer(request, customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    if request.method == 'POST':

        customer.name = request.POST.get('name')
        customer.phone = request.POST.get('phone')
        customer.email = request.POST.get('email')
        customer.address = request.POST.get('address')

        customer.save()

        return redirect('customers')

    return render(
        request,
        'finance/edit_customer.html',
        {
            'customer': customer
        }
    )


def delete_customer(request, customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    if request.method == 'POST':
        customer.delete()

    return redirect('customers')
def payments(request):

    payments = Payment.objects.select_related(
        'tour'
    ).order_by('-payment_date')

    total_paid = sum(
        payment.amount
        for payment in payments
    )

    return render(
        request,
        'finance/payments.html',
        {
            'payments': payments,
            'total_paid': total_paid
        }
    )
def expenses(request):
    tours = Tour.objects.all().order_by('-tour_date')

    total_expense = sum(
        tour.total_expense
        for tour in tours
    )

    return render(
        request,
        'finance/expenses.html',
        {
            'tours': tours,
            'total_expense': total_expense,
        }
    )
def settings(request):
    return render(
        request,
        'finance/settings.html'
    )
def logout_view(request):
    logout(request)
    return redirect('dashboard')