import pandas as pd
from loans.models import Loan
from customers.models import Customer
from django.utils import timezone

def import_loans():
    df = pd.read_excel('loan_data.xlsx')
    for _, row in df.iterrows():
        customer = Customer.objects.get(customer_id=row['Customer ID'])
        Loan.objects.update_or_create(
            loan_id=row['Loan ID'],  # if you have this in dataset
            defaults={
                'customer': customer,
                'loan_amount': row['Loan Amount'],
                'tenure': row['Tenure'],
                'interest_rate': row['Interest Rate'],
                'monthly_repayment': row['Monthly payment'],
                'emis_paid_on_time': row.get('EMIs Paid On Time', 0),  # adjust if present
                'start_date': pd.to_datetime(row['Start Date']).date() if 'Start Date' in row else timezone.now().date(),
                'end_date': pd.to_datetime(row['End Date']).date() if 'End Date' in row else timezone.now().date(),
            }
        )
    print("Loans imported successfully.")
