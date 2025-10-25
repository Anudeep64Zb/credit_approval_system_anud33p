import pandas as pd
from celery import shared_task
from customers.models import Customer
from loans.models import Loan

@shared_task
def ingest_customer_data():
    try:
        df = pd.read_excel('customer_data.xlsx')
        
        for _, row in df.iterrows():
            Customer.objects.update_or_create(
                customer_id=row['Customer ID'],  # ← Changed from 'customer_id'
                defaults={
                    'first_name': row['First Name'],  # ← Changed
                    'last_name': row['Last Name'],    # ← Changed
                    'age': row['Age'],                # ← Changed
                    'phone_number': row['Phone Number'],  # ← Changed
                    'monthly_salary': row['Monthly Salary'],  # ← Changed
                    'approved_limit': row['Approved Limit'],  # ← Changed
                    'current_debt': 0  # ← Default value since not in Excel
                }
            )
        return f"Successfully ingested {len(df)} customers"
    except Exception as e:
        return f"Error ingesting customer data: {str(e)}"

@shared_task
def ingest_loan_data():
    try:
        df = pd.read_excel('loan_data.xlsx')
        
        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['Customer ID'])  # ← Updated
                Loan.objects.update_or_create(
                    loan_id=row['Loan ID'],  # ← Updated column name
                    defaults={
                        'customer': customer,
                        'loan_amount': row['Loan Amount'],  # ← Updated
                        'tenure': row['Tenure'],
                        'interest_rate': row['Interest Rate'],  # ← Updated
                        'monthly_repayment': row['Monthly payment'],  # ← Check exact column name
                        'emis_paid_on_time': row['EMIs paid on Time'],  # ← Updated
                        'start_date': row['Date of Approval'],  # ← Updated
                        'end_date': row['End Date']  # ← Updated
                    }
                )
            except Customer.DoesNotExist:
                continue
        return f"Successfully ingested {len(df)} loans"
    except Exception as e:
        return f"Error ingesting loan data: {str(e)}"
