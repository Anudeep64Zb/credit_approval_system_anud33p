from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from customers.models import Customer
from .services import CreditCalculator, LoanCalculator
from .serializers import LoanEligibilitySerializer


@csrf_exempt
def temporary_view(request):
    return JsonResponse({
        "message": "Loans API - Under Construction", 
        "status": "active"
    })

@api_view(['POST'])
def check_eligibility(request):
    serializer = LoanEligibilitySerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        customer_id = data['customer_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        credit_score = CreditCalculator.calculate_credit_score(customer)
        
        current_emis = sum(loan.monthly_repayment for loan in customer.loans.all() 
                          if loan.end_date > timezone.now().date())
        
        if current_emis > 0.5 * customer.monthly_salary:
            approval = False
        else:
            if credit_score > 50:
                approval = True
            elif 30 < credit_score <= 50:
                approval = interest_rate >= 12
            elif 10 < credit_score <= 30:
                approval = interest_rate >= 16
            else:
                approval = False
        
        corrected_interest_rate = interest_rate
        if approval:
            if 30 < credit_score <= 50 and interest_rate < 12:
                corrected_interest_rate = 12
            elif 10 < credit_score <= 30 and interest_rate < 16:
                corrected_interest_rate = 16

        monthly_installment = LoanCalculator.calculate_emi(
            loan_amount, corrected_interest_rate, tenure
        )

        response_data = {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': float(interest_rate),
            'corrected_interest_rate': float(corrected_interest_rate),
            'tenure': tenure,
            'monthly_installment': float(monthly_installment)
        }

        return Response(response_data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
def get_loan_details(request, loan_id):
    from .models import Loan
    from .serializers import LoanDetailSerializer

    try:
        loan = Loan.objects.get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = LoanDetailSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)