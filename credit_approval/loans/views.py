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
        
        # Use Decimal for proper type consistency
        from decimal import Decimal
        if current_emis > Decimal('0.5') * customer.monthly_salary:
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
@api_view(['POST'])
def create_loan(request):
    """Create a new loan after eligibility check."""
    from .models import Loan
    from decimal import Decimal
    
    required_fields = ['customer_id', 'loan_amount', 'interest_rate', 'tenure']
    for field in required_fields:
        if field not in request.data:
            return Response(
                {field: ['This field is required.']}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        customer_id = request.data['customer_id']
        loan_amount = request.data['loan_amount']
        interest_rate = request.data['interest_rate']
        tenure = request.data['tenure']
        
        # Verify customer exists
        customer = Customer.objects.get(customer_id=customer_id)
        
        # Check eligibility first
        credit_score = CreditCalculator.calculate_credit_score(customer)
        
        current_emis = sum(
            loan.monthly_repayment for loan in customer.loans.all() 
            if loan.end_date > timezone.now().date()
        )
        
        if current_emis > Decimal('0.5') * customer.monthly_salary:
            return Response(
                {'error': 'Loan rejected: EMI exceeds 50% of monthly salary'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if credit_score <= 10:
            return Response(
                {'error': 'Loan rejected: Credit score too low'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate EMI and create loan
        monthly_repayment = LoanCalculator.calculate_emi(
            loan_amount, interest_rate, tenure
        )
        
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=tenure * 30)
        
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=Decimal(str(loan_amount)),
            tenure=tenure,
            interest_rate=Decimal(str(interest_rate)),
            monthly_repayment=Decimal(str(monthly_repayment)),
            emis_paid_on_time=0,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response({
            'loan_id': loan.loan_id,
            'customer_id': customer_id,
            'loan_amount': float(loan_amount),
            'tenure': tenure,
            'interest_rate': float(interest_rate),
            'monthly_repayment': float(monthly_repayment),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }, status=status.HTTP_201_CREATED)
    
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except (ValueError, TypeError) as e:
        return Response(
            {'error': f'Invalid data: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def view_loan(request, loan_id):
    """Get details of a specific loan."""
    from .models import Loan
    
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        return Response({
            'loan_id': loan.loan_id,
            'customer_id': loan.customer.customer_id,
            'loan_amount': float(loan.loan_amount),
            'tenure': loan.tenure,
            'interest_rate': float(loan.interest_rate),
            'monthly_repayment': float(loan.monthly_repayment),
            'emis_paid_on_time': loan.emis_paid_on_time,
            'start_date': loan.start_date.isoformat(),
            'end_date': loan.end_date.isoformat()
        }, status=status.HTTP_200_OK)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Loan not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """Get all loans for a specific customer."""
    from .models import Loan
    
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer).order_by('-start_date')
        
        loans_data = [
            {
                'loan_id': loan.loan_id,
                'loan_amount': float(loan.loan_amount),
                'tenure': loan.tenure,
                'interest_rate': float(loan.interest_rate),
                'monthly_repayment': float(loan.monthly_repayment),
                'emis_paid_on_time': loan.emis_paid_on_time,
                'start_date': loan.start_date.isoformat(),
                'end_date': loan.end_date.isoformat()
            }
            for loan in loans
        ]
        
        return Response({
            'customer_id': customer_id,
            'total_loans': len(loans_data),
            'loans': loans_data
        }, status=status.HTTP_200_OK)
    
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def get_loan_details(request, loan_id):
    """Legacy endpoint - redirects to view_loan."""
    return view_loan(request, loan_id)