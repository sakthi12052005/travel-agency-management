from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'add-tour/',
        views.add_tour,
        name='add_tour'
    ),

    path(
        'tours/',
        views.tour_list,
        name='tour_list'
    ),
    path(
    'tours/<int:tour_id>/',
    views.tour_detail,
    name='tour_detail'
    ),

    path(
    'tours/<int:tour_id>/edit/',
    views.edit_tour,
    name='edit_tour'
),

path(
    'tours/<int:tour_id>/delete/',
    views.delete_tour,
    name='delete_tour'
),

path(
    'payments/<int:payment_id>/edit/',
    views.edit_payment,
    name='edit_payment'
),

path(
    'payments/<int:payment_id>/delete/',
    views.delete_payment,
    name='delete_payment'
),
path(
    'reports/',
    views.reports,
    name='reports'
),
path('reports/pdf/', 
     views.report_pdf,
       name='report_pdf'
       ),

path(
    'customers/',
    views.customers,
    name='customers'
),

path(
    'customers/add/',
    views.add_customer,
    name='add_customer'
),

path(
    'customers/<int:customer_id>/edit/',
    views.edit_customer,
    name='edit_customer'
),

path(
    'customers/<int:customer_id>/delete/',
    views.delete_customer,
    name='delete_customer'
),
path(
    'payments/',
    views.payments,
    name='payments'
),

path(
    'payments/add/',
    views.add_payment,
    name='add_payment'
),

path(
    'tours/<int:tour_id>/payment/',
    views.add_payment,
    name='add_payment_for_tour'
),
path(
    'expenses/',
    views.expenses,
    name='expenses'
),
path(
    'settings/',
    views.settings,
    name='settings'
),
path(
    'logout/',
    views.logout_view,
    name='logout'
),

]