from decimal import Decimal
from django.utils import timezone
from customers.models import Customer
from loans.models import Loan
from decimal import Decimal

class CreditCalculator:
    @staticmethod
    def calculate_credit_score(customer):
        loans = Loan.objects.filter(customer=customer)
        
        # Rule 1: If total current loans > approved limit, score = 0
        total_current_loans = sum(loan.loan_amount for loan in loans if loan.end_date > timezone.now().date())
        if total_current_loans > customer.approved_limit:
            return 0
        
        score = Decimal("0")
        
        # Component 1: Past loans paid on time (35 points)
        on_time_score = CreditCalculator._calculate_on_time_score(loans)
        score += on_time_score * 0.35
        
        # Component 2: Number of loans taken (25 points)
        loan_count_score = CreditCalculator._calculate_loan_count_score(loans)
        score += loan_count_score * 0.25
        
        # Component 3: Loan activity in current year (20 points)
        current_year_score = CreditCalculator._calculate_current_year_score(loans)
        score += current_year_score * 0.20
        
        # Component 4: Loan approved volume (20 points)
        volume_score = CreditCalculator._calculate_volume_score(loans, customer)
        score += volume_score * Decimal('0.20')

        
        return min(100, max(0, score))
    
    @staticmethod
    def _calculate_on_time_score(loans):
        if not loans:
            return 50
        total_emis = sum(loan.tenure for loan in loans)
        on_time_emis = sum(loan.emis_paid_on_time for loan in loans)
        return (on_time_emis / total_emis) * 100 if total_emis > 0 else 50
    
    @staticmethod
    def _calculate_loan_count_score(loans):
        loan_count = len(loans)
        if loan_count == 0:
            return 50
        elif loan_count <= 5:
            return 100
        elif loan_count <= 10:
            return 75
        else:
            return 25
    
    @staticmethod
    def _calculate_current_year_score(loans):
        current_year = timezone.now().year
        current_year_loans = [loan for loan in loans if loan.start_date.year == current_year]
        return min(len(current_year_loans) * 25, 100)
    
    @staticmethod
    def _calculate_volume_score(loans, customer):
        if customer.approved_limit == 0:
            return 50
        total_approved = sum(loan.loan_amount for loan in loans)
        utilization = (total_approved / customer.approved_limit) * 100
        return max(0, 100 - utilization)

class LoanCalculator:
    @staticmethod
    def calculate_emi(principal, annual_rate, tenure_months):
        monthly_rate = annual_rate / (12 * 100)
        emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / ((1 + monthly_rate) ** tenure_months - 1)
        return round(emi, 2)
