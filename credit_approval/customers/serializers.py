from rest_framework import serializers
from .models import Customer

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_salary', 'phone_number']
    
    def create(self, validated_data):
        # Calculate approved limit (rounded to nearest lakh)
        monthly_salary = validated_data['monthly_salary']
        approved_limit = round(36 * monthly_salary / 100000) * 100000
        
        customer = Customer.objects.create(
            **validated_data,
            approved_limit=approved_limit,
            current_debt=0
        )
        return customer

class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'monthly_salary', 'approved_limit', 'phone_number', 'current_debt']
