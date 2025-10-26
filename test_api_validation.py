#!/usr/bin/env python
"""Quick API validation test"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("CREDIT APPROVAL SYSTEM - API VALIDATION TEST")
print("=" * 80)

# TEST 1: Register Customer
print("\n[TEST 1] Customer Registration")
print("-" * 80)
payload = {
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_salary": 75000,
    "phone_number": 9876543210
}
response = requests.post(f"{BASE_URL}/api/customers/register/", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 201:
    customer_id = response.json().get("customer_id")
    print(f"✓ Customer registered successfully (ID: {customer_id})")
else:
    print(f"✗ Registration failed")
    customer_id = 1

# TEST 2: Check Eligibility
print("\n[TEST 2] Loan Eligibility Check")
print("-" * 80)
payload = {
    "customer_id": customer_id,
    "loan_amount": 500000,
    "interest_rate": 14.5,
    "tenure": 24
}
response = requests.post(f"{BASE_URL}/api/loans/check-eligibility/", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    approval = response.json().get("approval")
    print(f"✓ Eligibility check completed (Approval: {approval})")
else:
    print(f"✗ Eligibility check failed")

# TEST 3: Test with different credit scenarios
print("\n[TEST 3] Credit Scoring Scenarios")
print("-" * 80)

# Register multiple customers to test scenarios
test_customers = [
    {"name": "High Income", "salary": 150000},
    {"name": "Low Income", "salary": 30000},
    {"name": "New Customer", "salary": 60000},
]

for i, cust in enumerate(test_customers, 2):
    payload = {
        "first_name": cust["name"].split()[0],
        "last_name": cust["name"].split()[1] if len(cust["name"].split()) > 1 else "Cust",
        "age": 25 + i,
        "monthly_salary": cust["salary"],
        "phone_number": 9800000000 + i
    }
    response = requests.post(f"{BASE_URL}/api/customers/register/", json=payload)
    if response.status_code == 201:
        cid = response.json().get("customer_id")
        print(f"  ✓ {cust['name']}: Registered (ID: {cid}, Salary: ₹{cust['salary']})")

# TEST 4: Test error scenarios
print("\n[TEST 4] Error Handling - Invalid Customer")
print("-" * 80)
payload = {
    "customer_id": 99999,
    "loan_amount": 100000,
    "interest_rate": 10,
    "tenure": 12
}
response = requests.post(f"{BASE_URL}/api/loans/check-eligibility/", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
if response.status_code == 404:
    print("✓ Error handling correct - 404 for invalid customer")

# TEST 5: Test validation errors
print("\n[TEST 5] Error Handling - Missing Fields")
print("-" * 80)
payload = {"first_name": "Test"}  # Missing required fields
response = requests.post(f"{BASE_URL}/api/customers/register/", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
if response.status_code == 400:
    print("✓ Error handling correct - 400 for invalid data")

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
