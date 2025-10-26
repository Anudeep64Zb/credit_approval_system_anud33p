from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home_view(request):
    return JsonResponse({
        "message": "Credit Approval System API",
        "endpoints": {
            "admin": "/admin/",
            "register": "/register/",
            "check_eligibility": "/check-eligibility/",
            "create_loan": "/create-loan/",
            "view_loan": "/view-loan/<loan_id>/",
            "view_loans": "/view-loans/<customer_id>/"
        }
    })

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('', include('customers.urls')),
    path('', include('loans.urls')),
]