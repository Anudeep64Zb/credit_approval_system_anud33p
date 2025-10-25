import pandas as pd
from customers.models import Customer

def import_customers():
    df = pd.read_excel('customer_data.xlsx')
    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['Customer ID'],
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'age': row['Age'],
                'phone_number': row['Phone Number'],
                'monthly_salary': row['Monthly Salary'],
                'approved_limit': row['Approved Limit'],
                'current_debt': 0,  # Or from data if available
            }
        )
    print("Customers imported successfully.")
