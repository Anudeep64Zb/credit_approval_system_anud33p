from django.urls import path
from .views import (
    check_eligibility,
    create_loan,
    view_loan,
    view_customer_loans
)

urlpatterns = [
    path('check-eligibility', check_eligibility, name='check_eligibility'),
    path('create-loan', create_loan, name='create_loan'),
    path('view-loan/<int:loan_id>', view_loan, name='view_loan'),
    path('view-loans/<int:customer_id>', view_customer_loans, name='view_customer_loans'),
]
