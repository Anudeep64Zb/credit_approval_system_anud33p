from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home_view(request):
    return JsonResponse({
        "message": "Credit Approval System API",
        "endpoints": {
            "admin": "/admin/",
            "customers": "/api/customers/",
            "loans": "/api/loans/"
        }
    })

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/customers/', include('customers.urls')),
    path('api/loans/', include('loans.urls')),
]