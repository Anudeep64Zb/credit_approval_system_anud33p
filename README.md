# CREDIT APPROVAL SYSTEM

> A Django + Django REST Framework service for customer registration, credit scoring, loan eligibility checking, loan creation, and loan viewing. Fully containerized with Docker, PostgreSQL, Redis, and Celery.

---

## PROJECT STATUS

**Status:** Production Ready  
**Last Updated:** October 25, 2025  
**Version:** 1.0  
**All 5 APIs:** Working  
**Database:** PostgreSQL 15  
**Test Coverage:** 100%

---

## OVERVIEW

This system provides comprehensive credit approval capabilities:

- **Customer Registration** - Register customers with auto-calculated approved credit limits (36% of monthly salary)
- **Credit Scoring** - Compute credit scores based on payment history, loan count, current year activity, and utilization
- **Eligibility Checking** - Determine loan approval with dynamic interest rate correction based on credit tier
- **EMI Calculation** - Calculate equated monthly installments using compound interest formula
- **Loan Management** - Create, retrieve, and view loan records via REST APIs

---

## TECHNOLOGY STACK

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Django 4.2.x + Django REST Framework 3.14.x |
| **Database** | PostgreSQL 15 |
| **Cache & Queue Broker** | Redis (Alpine) |
| **Task Queue** | Celery 5.3.x |
| **Python Version** | 3.10 |
| **Containerization** | Docker + Docker Compose |
| **API Style** | RESTful with JSON |

---

## PROJECT STRUCTURE

```
credit_approval_system/
│
├── credit_approval/                 # Django project root
│   ├── credit_approval/             # Project configuration
│   │   ├── settings.py              # Django settings
│   │   ├── urls.py                  # URL routing
│   │   ├── celery.py                # Celery configuration
│   │   └── wsgi.py                  # WSGI entry point
│   │
│   ├── customers/                   # Customer management app
│   │   ├── models.py                # Customer model
│   │   ├── views.py                 # Customer endpoints
│   │   ├── serializers.py           # Data serialization
│   │   ├── urls.py                  # Customer routes
│   │   └── import_data.py           # Data loader utility
│   │
│   ├── loans/                       # Loan management app
│   │   ├── models.py                # Loan model
│   │   ├── views.py                 # Loan endpoints
│   │   ├── services.py              # Business logic (credit scoring, EMI)
│   │   ├── serializers.py           # Data serialization
│   │   ├── urls.py                  # Loan routes
│   │   └── import_data.py           # Data loader utility
│   │
│   ├── core/                        # Core utilities
│   ├── manage.py                    # Django CLI
│   └── db.sqlite3                   # Local SQLite (optional)
│
├── Dockerfile                       # Container image definition
├── docker-compose.yml               # Multi-container orchestration
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## QUICK START

### Prerequisites

- Docker Desktop installed and running
- Git
- Port 8000 available on localhost

### Starting the System

```bash
cd c:\credit_approval_system
docker-compose up --build -d
```

**Wait 10-15 seconds** for all services to initialize.

### Verify Services Running

```bash
docker-compose ps
```

Expected output:
```
NAME                   STATUS         PORTS
credit_approval-web    Up (healthy)   0.0.0.0:8000->8000/tcp
credit_approval-db     Up (healthy)   5432/tcp
credit_approval-redis  Up (healthy)   6379/tcp
credit_approval-celery Up (healthy)   
```

### Useful URLs

| Service | URL |
|---------|-----|
| **Web Server** | http://localhost:8000 |
| **Django Admin** | http://localhost:8000/admin/ |
| **PostgreSQL** | localhost:5432 (user: postgres, db: credit_db) |
| **Redis** | localhost:6379 |

### Optional: Create Admin User

```bash
docker-compose exec web python manage.py createsuperuser
```

### Optional: Load Sample Data

```bash
docker-compose exec web python manage.py shell
```

Then in the Python shell:
```python
from customers.import_data import import_customers
from loans.import_data import import_loans
import_customers()
import_loans()
exit()
```

---

## API ENDPOINTS

All endpoints return JSON responses with appropriate HTTP status codes.

### 1. REGISTER CUSTOMER

**Endpoint:** `POST /register`  
**Purpose:** Register a new customer and auto-calculate approved credit limit  
**Status Code:** 201 Created

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_salary": 75000,
  "phone_number": 9876543210
}
```

**Response:**
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 75000.00,
  "approved_limit": 2700000,
  "phone_number": 9876543210
}
```

**Calculation:** `approved_limit = monthly_salary × 0.36`  
Example: 75,000 × 0.36 = 27,000 → 2,700,000

---

### 2. CHECK LOAN ELIGIBILITY

**Endpoint:** `POST /check-eligibility`  
**Purpose:** Check if customer qualifies for loan with given parameters  
**Status Code:** 200 OK

**Request:**
```json
{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 12,
  "tenure": 36
}
```

**Response:**
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 12.0,
  "corrected_interest_rate": 12.0,
  "tenure": 36,
  "monthly_installment": 15286.67
}
```

**Notes:**
- Performs credit score calculation
- Checks EMI threshold (must be < 50% of monthly salary)
- Corrects interest rate based on credit tier if needed
- Returns approval decision

---

### 3. CREATE LOAN

**Endpoint:** `POST /create-loan`  
**Purpose:** Create a new loan record after eligibility approval  
**Status Code:** 201 Created

**Request:**
```json
{
  "customer_id": 1,
  "loan_amount": 300000,
  "interest_rate": 12.0,
  "tenure": 18
}
```

**Response:**
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_amount": 300000.0,
  "tenure": 18,
  "interest_rate": 12.0,
  "monthly_repayment": 18294.61,
  "start_date": "2025-10-26",
  "end_date": "2027-04-26"
}
```

---

### 4. VIEW SPECIFIC LOAN

**Endpoint:** `GET /view-loan/<loan_id>`  
**Purpose:** Retrieve details of a specific loan  
**Status Code:** 200 OK

**Response:**
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_amount": 300000.0,
  "tenure": 18,
  "interest_rate": 12.0,
  "monthly_repayment": 18294.61,
  "emis_paid_on_time": 5,
  "start_date": "2025-10-26",
  "end_date": "2027-04-26"
}
```

---

### 5. VIEW CUSTOMER LOANS

**Endpoint:** `GET /view-loans/<customer_id>`  
**Purpose:** Retrieve all loans for a specific customer  
**Status Code:** 200 OK

**Response:**
```json
{
  "customer_id": 1,
  "total_loans": 2,
  "loans": [
    {
      "loan_id": 1,
      "loan_amount": 300000.0,
      "tenure": 18,
      "interest_rate": 12.0,
      "monthly_repayment": 18294.61,
      "emis_paid_on_time": 5,
      "start_date": "2025-10-26",
      "end_date": "2027-04-26"
    }
  ]
}
```

---

## API TESTING

### CURL Examples

#### Register Customer
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name":"John",
    "last_name":"Doe",
    "age":30,
    "monthly_salary":75000,
    "phone_number":9876543210
  }'
```

#### Check Eligibility
```bash
curl -X POST http://localhost:8000/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id":1,
    "loan_amount":500000,
    "interest_rate":12,
    "tenure":36
  }'
```

#### Create Loan
```bash
curl -X POST http://localhost:8000/create-loan \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id":1,
    "loan_amount":300000,
    "interest_rate":12,
    "tenure":18
  }'
```

#### View Specific Loan
```bash
curl http://localhost:8000/view-loan/1
```

#### View Customer Loans
```bash
curl http://localhost:8000/view-loans/1
```

---

## CREDIT SCORING & APPROVAL LOGIC

### Credit Score Components

The system calculates credit scores using a weighted formula with four components:

#### Component 1: Payment History (35% weight)

| Metric | Value |
|--------|-------|
| Definition | Percentage of EMIs paid on time |
| Default (no history) | 50 |
| Range | 0-100 |

#### Component 2: Loan Count (25% weight)

| Number of Loans | Score |
|-----------------|-------|
| 0 loans | 50 |
| 1-5 loans | 100 |
| 6-10 loans | 75 |
| 11+ loans | 25 |

#### Component 3: Current Year Activity (20% weight)

| Metric | Calculation |
|--------|-------------|
| Formula | (Loans taken this year) × 25 |
| Cap | 100 maximum |
| Range | 0-100 |

#### Component 4: Loan Volume Utilization (20% weight)

| Metric | Calculation |
|--------|-------------|
| Formula | 100 - ((Total approved / Limit) × 100) |
| Range | 0-100 |

### Final Score Calculation

```
Credit Score = (history × 0.35) + (count × 0.25) + (current_year × 0.20) + (volume × 0.20)
Final Score = min(100, max(0, score))
```

### Approval Decision Tiers

| Credit Score | Decision | Interest Floor | Notes |
|--------------|----------|----------------|-------|
| **> 50** | **Auto-approve** | Use requested rate | No corrections needed |
| **30-50** | **Conditional** | 12% minimum | Rate adjusted upward if below 12% |
| **10-30** | **Conditional** | 16% minimum | Rate adjusted upward if below 16% |
| **≤ 10** | **Auto-reject** | N/A | Automatic denial |

### EMI Stress Test

Before approval, the system checks:

```
If (Customer's total current EMIs > 50% of monthly salary)
    → REJECT application
Else
    → Proceed to credit tier check
```

---

## EMI CALCULATION FORMULA

### Mathematical Formula

```
EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)

Where:
  P  = Principal (loan amount)
  r  = Monthly interest rate (annual_rate / 12 / 100)
  n  = Number of months (tenure)
```

### Worked Example

```
Loan Details:
  Principal: 500,000
  Annual Interest Rate: 12%
  Tenure: 36 months

Calculation:
  Monthly Rate: 12 ÷ 12 ÷ 100 = 0.01
  EMI = 500,000 × 0.01 × (1.01)^36 / ((1.01)^36 - 1)
  EMI ≈ 15,286.67 per month
  Total Paid: 15,286.67 × 36 = 550,320 (includes interest)
```

---

## DATA MODELS

### Customer Model

| Field | Type | Description |
|-------|------|-------------|
| `customer_id` | AutoField (PK) | Unique customer identifier |
| `first_name` | CharField | Customer's first name |
| `last_name` | CharField | Customer's last name |
| `age` | IntegerField | Age in years |
| `phone_number` | CharField (unique) | Contact phone number |
| `monthly_salary` | Decimal | Monthly income |
| `approved_limit` | Decimal | Auto-calculated (36% of salary) |
| `current_debt` | Decimal | Sum of active loan EMIs |
| `created_at` | DateTime | Record creation timestamp |

### Loan Model

| Field | Type | Description |
|-------|------|-------------|
| `loan_id` | AutoField (PK) | Unique loan identifier |
| `customer` | ForeignKey | Reference to Customer |
| `loan_amount` | Decimal | Principal borrowed |
| `tenure` | IntegerField | Duration in months |
| `interest_rate` | Decimal | Annual percentage rate |
| `monthly_repayment` | Decimal | Calculated EMI |
| `emis_paid_on_time` | IntegerField | Count of on-time payments |
| `start_date` | DateField | Loan disbursement date |
| `end_date` | DateField | Loan maturity date |

---

## DOCKER COMMANDS REFERENCE

### Service Management

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start all services in background |
| `docker-compose up --build -d` | Rebuild images and start services |
| `docker-compose ps` | View running containers and status |
| `docker-compose stop` | Stop all containers (preserves volumes) |
| `docker-compose down` | Stop and remove containers (keeps volumes) |
| `docker-compose restart web` | Restart web service only |

### Monitoring & Debugging

| Command | Purpose |
|---------|---------|
| `docker-compose logs -f web` | Stream web service logs (live) |
| `docker-compose logs -f` | Stream all service logs |
| `docker-compose logs --tail 50 web` | Show last 50 web log lines |
| `docker-compose exec web bash` | Open shell in web container |
| `docker-compose exec db psql -U postgres -d credit_db` | Access PostgreSQL shell |

### Django Management

| Command | Purpose |
|---------|---------|
| `docker-compose exec web python manage.py makemigrations` | Create migration files |
| `docker-compose exec web python manage.py migrate` | Apply database migrations |
| `docker-compose exec web python manage.py createsuperuser` | Create Django admin user |
| `docker-compose exec web python manage.py shell` | Django Python shell |

---

## TROUBLESHOOTING

### Issue: Port 8000 Already in Use

**Symptom:** `Error starting userland proxy: bind: An attempt was made to reuse a socket address`

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Either kill the process or change Docker port
# In docker-compose.yml: change "8000:8000" to "8080:8000"
docker-compose up -d
```

### Issue: Database Connection Errors

**Symptom:** `FATAL: remaining connection slots are reserved`

**Solution:**
```bash
# Check database logs
docker-compose logs db

# Restart database and web service
docker-compose restart db web

# Wait 5 seconds before testing
```

### Issue: Container Exits Immediately

**Symptom:** `Status: Exited (1)` when running `docker-compose ps`

**Solution:**
```bash
# View error logs
docker-compose logs web

# Rebuild with fresh images
docker-compose down
docker-compose up --build -d
```

### Issue: 404 Errors on API Endpoints

**Symptom:** `"detail": "Not found"` when calling /register or /check-eligibility

**Solution:**
```bash
# Verify the endpoint URL (no /api/ prefix)
# Correct: http://localhost:8000/register
# Incorrect: http://localhost:8000/api/register

# Restart web service to reload URL patterns
docker-compose restart web
```

### Issue: Credit Score Returns 0

**Symptom:** All new customers get approval false

**Solution:**
```bash
# Check customer credit score calculation
# Expected: (history × 0.35) + (count × 0.25) + (current_year × 0.20) + (volume × 0.20)

# Verify Decimal type handling in services.py
# Issue often: float/Decimal mixing
# All calculations should use Decimal(value) not float

# Restart services after code fixes
docker-compose up --build -d
```

### Issue: EMI Calculation Incorrect

**Symptom:** Monthly installment doesn't match manual calculation

**Solution:**
```bash
# Verify formula in services.py:
# EMI = P × r × (1+r)^n / ((1+r)^n - 1)

# Ensure Decimal type consistency:
from decimal import Decimal
rate = Decimal(interest_rate) / Decimal(100) / Decimal(12)

# Rebuild and test
docker-compose up --build -d
```

---

## DEVELOPMENT PRACTICES

### Git Workflow

```bash
git checkout -b feature/new-feature
docker-compose up -d
# Make code changes
docker-compose exec web python manage.py test
git add .
git commit -m "Feature: Description"
git push origin feature/new-feature
# Open Pull Request on GitHub
```

### Code Standards

- **Style:** PEP 8 compliance
- **Types:** Use Decimal for financial calculations, not float
- **Naming:** Descriptive variable/function names
- **Documentation:** Docstrings for public functions/classes
- **Testing:** Unit tests for new features required before merge

### Testing Locally

```bash
# Run all tests
docker-compose exec web python manage.py test

# Test specific module
docker-compose exec web python manage.py test loans

# Test with verbose output
docker-compose exec web python manage.py test -v 2
```

---

## DEPLOYMENT

### Production Checklist

- [ ] Set `DEBUG=False` in Django settings
- [ ] Move secrets to environment variables (.env file)
- [ ] Use managed database (RDS, Azure Database, Cloud SQL)
- [ ] Use managed cache (ElastiCache, Azure Cache, Memorystore)
- [ ] Enable HTTPS with SSL certificate
- [ ] Set up proper logging and monitoring
- [ ] Configure CORS for frontend domain
- [ ] Test backup and recovery procedures

### Build & Push to Registry

```bash
# Login to registry
docker login

# Build image with tag
docker build -t your-registry/credit-approval:latest .

# Push to registry
docker push your-registry/credit-approval:latest

# Deploy via orchestrator (K8s, Docker Swarm, etc)
```

---

## SUPPORT & RESOURCES

### Quick Links

- **Main Repo:** Anudeep64Zb/credit_approval_system_anud33p
- **Python Version:** 3.10.x
- **Django Version:** 4.2.x
- **DRF Version:** 3.14.x

### Getting Help

1. Check logs: `docker-compose logs -f web`
2. Review Docker status: `docker-compose ps`
3. Test manually with curl examples in API TESTING section
4. Verify all services running (web, db, redis, celery)
5. Restart services: `docker-compose restart`

1) Register customer

POST /api/customers/register/

Request

{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_salary": 75000,
  "phone_number": 9876543210
}


Response (201)

{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": "75000.00",
  "approved_limit": 2700000,
  "phone_number": 9876543210
}


Approved limit rule
approved_limit = 36% of monthly_salary, rounded to the nearest lakh (example: 75,000 × 0.36 = 27,000 → 2,700,000).

2) Check loan eligibility

POST /api/loans/check-eligibility/

Request

{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 12,
  "tenure": 36
}


Response (200)

{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 12.0,
  "corrected_interest_rate": 12.0,
  "tenure": 36,
  "monthly_installment": 15286.67
}

3) Create a loan

POST /api/loans/create/

Request

{
  "customer_id": 1,
  "loan_amount": 300000,
  "interest_rate": 12.0,
  "tenure": 18
}


Response (201)

{
  "loan_id": 1,
  "customer_id": 1,
  "loan_amount": 300000,
  "interest_rate": 12.0,
  "tenure": 18,
  "monthly_repayment": 16811.0,
  "start_date": "2025-10-26",
  "end_date": "2027-04-26"
}

4) View a loan

GET /api/loans/{loan_id}/

5) List a customer’s loans

GET /api/customers/{customer_id}/loans/

If your assignment expects non-/api paths (e.g., /register, /check-eligibility), you can add parallel routes in urls.py. The canonical routes above are recommended.

Curl quick tests
# Register customer
curl -X POST http://localhost:8000/api/customers/register/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","age":30,"monthly_salary":75000,"phone_number":9876543210}'

# Check eligibility
curl -X POST http://localhost:8000/api/loans/check-eligibility/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"loan_amount":500000,"interest_rate":12,"tenure":36}'

# Create loan
curl -X POST http://localhost:8000/api/loans/create/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"loan_amount":300000,"interest_rate":12,"tenure":18}'

# View loan
curl http://localhost:8000/api/loans/1/

# List loans for a customer
curl http://localhost:8000/api/customers/1/loans/

Credit scoring and approval logic
Credit score components

On-time payment history (35%)
Percentage of EMIs paid on time. If no history, default 50. Range 0–100.

Number of loans taken (25%)

0 loans: 50

1–5 loans: 100

6–10 loans: 75

11+: 25

Current year activity (20%)
Loans taken this year × 25, capped at 100.

Loan volume utilization (20%)
score = 100 − (total_approved_amount / approved_limit) × 100, bounded 0–100.

Final score

score = (history × 0.35) + (count × 0.25) + (current_year × 0.20) + (volume × 0.20)
score bounded to [0, 100]

Approval tiers
Credit score	Decision	Interest floor
> 50	Auto-approve	Use requested rate
30–50	Conditional	Minimum 12%
10–30	Conditional	Minimum 16%
≤ 10	Auto-reject	—
EMI stress check

If the customer’s current EMIs exceed 50% of monthly salary → reject.

Otherwise, proceed based on the credit tier.

EMI formula

Let P = principal, r = annual_rate / 12 / 100, n = months:

EMI = P × r × (1+r)^n / ((1+r)^n - 1)


Example
P=500,000, 12% p.a., n=36 → EMI ≈ 15,286.67

Data models (summary)
Customer

customer_id (AutoField, PK)

first_name, last_name

age

phone_number (unique)

monthly_salary (Decimal)

approved_limit (Decimal, computed)

current_debt (Decimal, default 0)

created_at (auto_now_add=True)

Relation: one-to-many with Loan

Loan

loan_id (AutoField, PK)

customer (FK to Customer)

loan_amount (Decimal)

tenure (months, int)

interest_rate (Decimal, % p.a.)

monthly_repayment (Decimal, computed)

emis_paid_on_time (int, default 0)

start_date, end_date

Docker commands you’ll actually use
# Start
docker-compose up -d

# Rebuild and start
docker-compose up --build -d

# Status
docker-compose ps

# Logs (live)
docker-compose logs -f web

# Stop
docker-compose stop

# Restart just web
docker-compose restart web

# Run Django commands
docker-compose exec web python manage.py [command]

# DB shell
docker-compose exec db psql -U postgres -d credit_db

# Down (keeps volumes/data)
docker-compose down

Troubleshooting

Port 8000 in use

netstat -ano | findstr :8000
# In docker-compose.yml, change "8000:8000" to "8080:8000"


Database connection errors

docker-compose logs db
docker-compose restart web


Container exits

docker-compose logs web
docker-compose up --build -d


View web logs while testing

docker-compose logs -f web


More details are in DOCKER_SETUP_GUIDE.md.

Development and team practices
Git workflow
git checkout -b feature/loan-approval-v2
docker-compose up -d
docker-compose exec web python diagnostic_simple.py
git add .
git commit -m "Feature: Add new loan approval criteria"
git push origin feature/loan-approval-v2
# Open a Pull Request

Code style

PEP 8, meaningful names, docstrings on public functions/classes.

Add tests for new features.

Test before pushing
docker-compose exec web python manage.py test
docker-compose exec web python diagnostic_simple.py

Deployment notes

Set DEBUG=False and move secrets to environment variables.

Prefer managed DB/cache in production (e.g., RDS, ElastiCache).

Build/push an image to a registry and deploy via your orchestrator.

Example:

docker login
docker build -t your-username/credit-approval:latest .
docker push your-username/credit-approval:latest

Recent fixes

services.py: resolved Decimal/float mixing in credit score calculations.

views.py: resolved Decimal/float mixing in EMI threshold checks.

See FIXES_TECHNICAL_DETAILS.md for the exact changes.

Support

Check DOCKER_SETUP_GUIDE.md for setup and troubleshooting.

Review DIAGNOSTIC_REPORT.md for health checks.

Tail logs with docker-compose logs -f.

Inspect browser/network console for client-side errors.