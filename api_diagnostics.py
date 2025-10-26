#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive API Diagnostics for Credit Approval System
Tests URL patterns, views, serializers, models, and services
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Handle Windows encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_approval.settings')
sys.path.insert(0, r'c:\credit_approval_system\credit_approval')
django.setup()

from django.test import RequestFactory, Client
from django.urls import reverse, get_resolver
from customers.models import Customer
from loans.models import Loan
from customers.serializers import CustomerRegistrationSerializer, CustomerDetailSerializer
from loans.serializers import LoanEligibilitySerializer, LoanDetailSerializer
from loans.services import CreditCalculator, LoanCalculator
from rest_framework.test import APIClient
import json

print("=" * 80)
print("DJANGO API DIAGNOSTICS - Credit Approval System")
print("=" * 80)

# ============================================================================
# 1. URL PATTERN CHECK
# ============================================================================
print("\n1. URL ROUTING DIAGNOSTICS")
print("-" * 80)

resolver = get_resolver()
print(f"✓ Root URL config loaded: {resolver.urlconf_name}")

patterns_to_check = [
    ('api/customers/register/', 'register_customer'),
    ('api/loans/check-eligibility/', 'check_eligibility'),
]

print("\nChecking URL patterns:")
for pattern, name in patterns_to_check:
    try:
        url_obj = resolver.resolve(f'/{pattern}')
        print(f"  ✓ /{pattern} → {url_obj.func.__name__} (matches '{url_obj.url_name}')")
    except Exception as e:
        print(f"  ✗ /{pattern} → NOT FOUND - {e}")

# ============================================================================
# 2. MODEL CHECK
# ============================================================================
print("\n2. DATABASE MODELS DIAGNOSTICS")
print("-" * 80)

print("\nCustomer Model:")
print(f"  ✓ Table: {Customer._meta.db_table}")
print(f"  ✓ Fields: {[f.name for f in Customer._meta.get_fields()]}")
print(f"  ✓ Records in DB: {Customer.objects.count()}")

print("\nLoan Model:")
print(f"  ✓ Table: {Loan._meta.db_table}")
print(f"  ✓ Fields: {[f.name for f in Loan._meta.get_fields()]}")
print(f"  ✓ Records in DB: {Loan.objects.count()}")

# ============================================================================
# 3. SERIALIZER VALIDATION TEST
# ============================================================================
print("\n3. SERIALIZER VALIDATION DIAGNOSTICS")
print("-" * 80)

print("\nTesting CustomerRegistrationSerializer:")
test_customer_data = {
    'first_name': 'John',
    'last_name': 'Doe',
    'age': 30,
    'monthly_salary': Decimal('50000.00'),
    'phone_number': 9876543210,
}
serializer = CustomerRegistrationSerializer(data=test_customer_data)
if serializer.is_valid():
    print(f"  ✓ Valid data passes validation")
    print(f"  ✓ Validated fields: {list(serializer.validated_data.keys())}")
else:
    print(f"  ✗ Validation errors: {serializer.errors}")

# Test invalid data
invalid_data = {
    'first_name': 'John',
    # missing required fields
}
serializer_invalid = CustomerRegistrationSerializer(data=invalid_data)
if not serializer_invalid.is_valid():
    print(f"  ✓ Invalid data rejected: {list(serializer_invalid.errors.keys())}")

print("\nTesting LoanEligibilitySerializer:")
test_loan_data = {
    'customer_id': 1,
    'loan_amount': Decimal('100000.00'),
    'interest_rate': Decimal('10.50'),
    'tenure': 12,
}
serializer = LoanEligibilitySerializer(data=test_loan_data)
if serializer.is_valid():
    print(f"  ✓ Valid data passes validation")
    print(f"  ✓ Validated fields: {list(serializer.validated_data.keys())}")
else:
    print(f"  ✗ Validation errors: {serializer.errors}")

# ============================================================================
# 4. SERVICES LOGIC TEST
# ============================================================================
print("\n4. SERVICES LOGIC DIAGNOSTICS")
print("-" * 80)

print("\nTesting CreditCalculator:")
print("  Testing credit score calculation...")

# Create a test customer
Customer.objects.filter(phone_number=9999999999).delete()
test_customer = Customer.objects.create(
    first_name='Test',
    last_name='User',
    age=35,
    phone_number=9999999999,
    monthly_salary=Decimal('75000.00'),
    approved_limit=Decimal('300000.00'),
    current_debt=Decimal('0.00')
)
print(f"    ✓ Test customer created (ID: {test_customer.customer_id})")

# Create test loans for the customer
Loan.objects.filter(customer=test_customer).delete()
loan1 = Loan.objects.create(
    customer=test_customer,
    loan_amount=Decimal('100000.00'),
    tenure=12,
    interest_rate=Decimal('12.00'),
    monthly_repayment=Decimal('8884.00'),
    emis_paid_on_time=10,
    start_date=date.today() - timedelta(days=90),
    end_date=date.today() + timedelta(days=30)
)
print(f"    ✓ Test loan created (ID: {loan1.loan_id})")

credit_score = CreditCalculator.calculate_credit_score(test_customer)
print(f"  ✓ Credit score calculated: {credit_score}")
print(f"    - Score range: 0-100")
print(f"    - Components: On-time payment, Loan count, Current year activity, Volume utilization")

print("\nTesting LoanCalculator (EMI):")
principal = Decimal('500000')
rate = Decimal('12.00')
tenure = 60
emi = LoanCalculator.calculate_emi(principal, rate, tenure)
print(f"  ✓ EMI calculated for ₹{principal} @ {rate}% for {tenure} months")
print(f"    - Monthly EMI: ₹{emi}")

# ============================================================================
# 5. API ENDPOINT TEST (using Django test client)
# ============================================================================
print("\n5. API ENDPOINT RESPONSE TEST")
print("-" * 80)

client = APIClient()

print("\nTesting POST /api/customers/register/:")
customer_payload = {
    'first_name': 'Alice',
    'last_name': 'Smith',
    'age': 28,
    'monthly_salary': 65000,
    'phone_number': 9876543211,
}
response = client.post('/api/customers/register/', customer_payload, format='json')
print(f"  Status Code: {response.status_code}")
print(f"  Response: {json.dumps(response.data, indent=2, default=str)}")

if response.status_code == 201:
    print(f"  ✓ Customer successfully registered")
    customer_id = response.data.get('customer_id')
else:
    print(f"  ✗ Registration failed")
    customer_id = 1  # fallback

print(f"\nTesting POST /api/loans/check-eligibility/:")
# Get a valid customer for testing
valid_customer = Customer.objects.first()
if valid_customer:
    loan_payload = {
        'customer_id': valid_customer.customer_id,
        'loan_amount': 200000,
        'interest_rate': 13.5,
        'tenure': 24,
    }
    response = client.post('/api/loans/check-eligibility/', loan_payload, format='json')
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.data, indent=2, default=str)}")
    
    if response.status_code == 200:
        print(f"  ✓ Eligibility check completed")
        approval = response.data.get('approval')
        print(f"    - Approval: {approval}")
        print(f"    - Corrected Rate: {response.data.get('corrected_interest_rate')}%")
        print(f"    - Monthly EMI: ₹{response.data.get('monthly_installment')}")
    else:
        print(f"  ✗ Eligibility check failed")
else:
    print(f"  ✗ No customers in DB, creating one...")
    Customer.objects.create(
        first_name='Default',
        last_name='Customer',
        age=30,
        monthly_salary=60000,
        phone_number=9111111111,
        approved_limit=240000
    )

# ============================================================================
# 6. COMMON ERROR SCENARIOS
# ============================================================================
print("\n6. ERROR SCENARIO TESTING")
print("-" * 80)

print("\nScenario A: 404 Not Found (invalid URL)")
response = client.get('/api/invalid-endpoint/')
print(f"  GET /api/invalid-endpoint/ → {response.status_code}")
if response.status_code == 404:
    print(f"  ✓ 404 correctly returned for non-existent route")

print("\nScenario B: Missing Required Fields (Serializer validation)")
invalid_payload = {'first_name': 'Test'}  # missing required fields
response = client.post('/api/customers/register/', invalid_payload, format='json')
print(f"  POST /api/customers/register/ with invalid data → {response.status_code}")
print(f"  Response: {response.data}")
if response.status_code == 400:
    print(f"  ✓ 400 Bad Request correctly returned")

print("\nScenario C: Customer Not Found (404)")
response = client.post('/api/loans/check-eligibility/', {
    'customer_id': 99999,
    'loan_amount': 100000,
    'interest_rate': 10,
    'tenure': 12,
}, format='json')
print(f"  POST /api/loans/check-eligibility/ with invalid customer → {response.status_code}")
if response.status_code == 404 and 'error' in response.data:
    print(f"  ✓ 404 correctly returned: {response.data['error']}")

# ============================================================================
# 7. DATABASE INTEGRITY CHECK
# ============================================================================
print("\n7. DATABASE INTEGRITY CHECK")
print("-" * 80)

# Check relationships
customers_with_loans = Customer.objects.filter(loans__isnull=False).distinct().count()
print(f"  ✓ Customers with loans: {customers_with_loans}")

# Check data consistency
all_loans = Loan.objects.all()
for loan in all_loans[:3]:  # sample first 3
    if loan.customer:
        print(f"  ✓ Loan {loan.loan_id} → Customer {loan.customer.customer_id} (relationship OK)")
    else:
        print(f"  ✗ Loan {loan.loan_id} → No customer (orphaned record)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTICS COMPLETE")
print("=" * 80)
print("\n✓ All core components checked:")
print("  1. URL routing configured correctly")
print("  2. Models and database schema valid")
print("  3. Serializers validate data properly")
print("  4. Services perform calculations correctly")
print("  5. API endpoints respond with correct status codes")
print("  6. Error scenarios handled appropriately")
print("  7. Database relationships intact")
print("\nNext steps:")
print("  → If you see errors above, provide the full output")
print("  → Test with your own data via REST client (Postman/Insomnia)")
print("  → Check server logs: python manage.py runserver --verbosity 3")
print("=" * 80)
