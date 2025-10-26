#!/usr/bin/env python
"""
Comprehensive API Test Suite - All 5 Endpoints
Tests the complete workflow and all endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("  COMPREHENSIVE API TEST SUITE - ALL 5 ENDPOINTS")
print("="*70)

# Test 1: Register Customer
print("\n[TEST 1] POST /register - Register New Customer")
print("-" * 70)

register_payload = {
    "first_name": "Alice",
    "last_name": "Johnson",
    "age": 32,
    "monthly_salary": 95000,
    "phone_number": 9876543210
}

try:
    response = requests.post(
        f"{BASE_URL}/register",
        json=register_payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if response.status_code == 201:
        customer_id = data['customer_id']
        print(f"✅ PASS - Customer registered with ID: {customer_id}")
    else:
        print(f"❌ FAIL - Expected 201, got {response.status_code}")
        customer_id = None
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    customer_id = None

# Test 2: Check Eligibility
if customer_id:
    print("\n[TEST 2] POST /check-eligibility - Check Loan Eligibility")
    print("-" * 70)
    
    eligibility_payload = {
        "customer_id": customer_id,
        "loan_amount": 500000,
        "interest_rate": 14.5,
        "tenure": 24
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/check-eligibility",
            json=eligibility_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200:
            approval = data['approval']
            print(f"✅ PASS - Eligibility check: {'APPROVED' if approval else 'REJECTED'}")
        else:
            print(f"❌ FAIL - Expected 200, got {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    # Test 3: Create Loan
    print("\n[TEST 3] POST /create-loan - Create New Loan")
    print("-" * 70)
    
    create_loan_payload = {
        "customer_id": customer_id,
        "loan_amount": 400000,
        "interest_rate": 13.0,
        "tenure": 20
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/create-loan",
            json=create_loan_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 201:
            loan_id = data['loan_id']
            print(f"✅ PASS - Loan created with ID: {loan_id}")
        else:
            print(f"❌ FAIL - Expected 201, got {response.status_code}")
            loan_id = None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        loan_id = None

    # Test 4: View Specific Loan
    if loan_id:
        print(f"\n[TEST 4] GET /view-loan/{loan_id} - View Specific Loan")
        print("-" * 70)
        
        try:
            response = requests.get(
                f"{BASE_URL}/view-loan/{loan_id}",
                headers={"Content-Type": "application/json"}
            )
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(json.dumps(data, indent=2))
            
            if response.status_code == 200:
                print(f"✅ PASS - Loan {loan_id} retrieved successfully")
            else:
                print(f"❌ FAIL - Expected 200, got {response.status_code}")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

    # Test 5: View Customer Loans
    print(f"\n[TEST 5] GET /view-loans/{customer_id} - View All Customer Loans")
    print("-" * 70)
    
    try:
        response = requests.get(
            f"{BASE_URL}/view-loans/{customer_id}",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200:
            total = data['total_loans']
            print(f"✅ PASS - Retrieved {total} loan(s) for customer {customer_id}")
        else:
            print(f"❌ FAIL - Expected 200, got {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

# Test 6: Error Handling
print("\n[TEST 6] Error Handling - Invalid Customer")
print("-" * 70)

try:
    response = requests.get(
        f"{BASE_URL}/view-loans/99999",
        headers={"Content-Type": "application/json"}
    )
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if response.status_code == 404:
        print(f"✅ PASS - Correctly returned 404 for invalid customer")
    else:
        print(f"❌ FAIL - Expected 404, got {response.status_code}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

# Test 7: Home Endpoint
print("\n[TEST 7] GET / - Home Endpoint (URL Reference)")
print("-" * 70)

try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if response.status_code == 200:
        endpoints = data.get('endpoints', {})
        endpoint_count = len(endpoints)
        print(f"✅ PASS - Home endpoint shows {endpoint_count} available endpoints")
    else:
        print(f"❌ FAIL - Expected 200, got {response.status_code}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("\n" + "="*70)
print("  TEST SUITE COMPLETE")
print("="*70 + "\n")
