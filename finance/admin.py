from django.contrib import admin
from .models import Tour


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):

    list_display = (
        'tour_name',
        'tour_date',
        'customer_count',
        'collection',
        'hotel_expense',
        'car_expense',
        'food_expense',
        'other_expense',
    )

    list_filter = ('tour_date',)

    search_fields = ('tour_name',)