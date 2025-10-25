from rest_framework import serializers
from .models import Loan

class LoanEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()

class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['customer', 'loan_amount', 'tenure', 'interest_rate', 'monthly_repayment', 'start_date', 'end_date']

class LoanDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'customer_name', 'loan_amount', 'tenure', 'interest_rate', 
                 'monthly_repayment', 'emis_paid_on_time', 'start_date', 'end_date']
