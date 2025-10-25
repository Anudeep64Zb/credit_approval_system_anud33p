from django.core.management.base import BaseCommand
from customers.models import Customer
from loans.services import CreditCalculator, LoanCalculator

class Command(BaseCommand):
    help = 'Test credit approval flow'

    def handle(self, *args, **kwargs):
        customer = Customer.objects.filter(loans__isnull=False).first()
        if not customer:
            self.stdout.write("No customer found with loans to test.")
            return

        self.stdout.write(f"Testing Customer: {customer.get_full_name()}")
        credit_score = CreditCalculator.calculate_credit_score(customer)
        self.stdout.write(f"Credit Score: {credit_score:.2f}")

        test_loans = [
            (50000, 12.0, 12),
            (500000, 12.0, 24),
            (2000000, 12.0, 36),
        ]
        for loan_amount, rate, tenure in test_loans:
            emi = LoanCalculator.calculate_emi(loan_amount, rate, tenure)
            self.stdout.write(f"\nLoan: ₹{loan_amount}, Rate: {rate}%, Tenure: {tenure} months")
            self.stdout.write(f"Monthly EMI: ₹{emi}")

            current_emis = sum(loan.monthly_repayment for loan in customer.loans.all()
                               if loan.end_date.year >= 2025)

            if current_emis > 0.5 * customer.monthly_salary:
                self.stdout.write("❌ REJECTED: Current EMIs exceed 50% of monthly salary")
            else:
                if credit_score > 50:
                    approval = True
                    corrected_rate = rate
                elif 30 < credit_score <= 50:
                    approval = rate >= 12
                    corrected_rate = max(rate, 12)
                elif 10 < credit_score <= 30:
                    approval = rate >= 16
                    corrected_rate = max(rate, 16)
                else:
                    approval = False
                    corrected_rate = rate

                self.stdout.write(f"✅ APPROVED: {approval}")
                self.stdout.write(f"Corrected Interest Rate: {corrected_rate}%")
