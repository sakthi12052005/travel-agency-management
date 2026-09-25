from django.db import models




class Tour(models.Model):

    tour_name = models.CharField(max_length=200)

    tour_date = models.DateField()

    customer_count = models.PositiveIntegerField(default=0)

    package_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    collection = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    hotel_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    car_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    food_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    other_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_expense(self):
        return (
            self.hotel_expense
            + self.car_expense
            + self.food_expense
            + self.other_expense
        )

    @property
    def profit(self):
        return self.collection - self.total_expense

    @property
    def pending_amount(self):
        return self.package_amount - self.collection

    def __str__(self):
        return self.tour_name
class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class Payment(models.Model):

    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_date = models.DateField()

    payment_method = models.CharField(
        max_length=50,
        default='Cash'
    )

    note = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.tour.tour_name} - ₹{self.amount}"
    # ============================
# PAYMENTS
# ============================

def payments(request):

    payment_list = Payment.objects.select_related('tour').order_by('-payment_date', '-id')

    total_paid = sum(
        payment.amount or 0
        for payment in payment_list
    )

    return render(
        request,
        'finance/payments.html',
        {
            'payments': payment_list,
            'total_paid': total_paid,
        }
    )


def add_payment(request):

    tours = Tour.objects.all().order_by('-date')

    if request.method == 'POST':

        tour_id = request.POST.get('tour')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')
        note = request.POST.get('note')

        tour = get_object_or_404(
            Tour,
            id=tour_id
        )

        Payment.objects.create(
            tour=tour,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            note=note
        )

        return redirect('payments')

    return render(
        request,
        'finance/add_payment.html',
        {
            'tours': tours
        }
    )