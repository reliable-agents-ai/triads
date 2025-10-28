# Code Quality Standards

**Authority Level**: DOMAIN-CONDITIONAL (applies to software-development domain)
**Enforcement**: Agents, skills, pre-commit hooks, code review
**Prerequisite**: Constitutional principles + TDD methodology

---

## Quality Statement

**MANDATE**: All code must meet quality standards before commit.

**Code quality is non-negotiable. Clean code is constitutional law.**

---

## The Three Pillars of Code Quality

1. **Readability**: Code is read 10x more than written
2. **Maintainability**: Future developers (including you) must understand it
3. **Correctness**: Code does what it claims to do

---

## Clean Code Principles

### Principle 1: DRY (Don't Repeat Yourself)

**Rule**: Every piece of knowledge must have a single, unambiguous representation.

**Violation Example**:
```python
# ❌ BAD - Duplication
def calculate_order_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
    tax = total * 0.08
    return total + tax

def calculate_cart_total(cart_items):
    total = 0
    for item in cart_items:
        total += item.price * item.quantity  # ❌ Duplicated
    tax = total * 0.08  # ❌ Duplicated
    return total + tax
```

**Fixed**:
```python
# ✅ GOOD - DRY
TAX_RATE = 0.08

def calculate_subtotal(items):
    """Calculate subtotal from items."""
    return sum(item.price * item.quantity for item in items)

def calculate_total_with_tax(subtotal):
    """Add tax to subtotal."""
    return subtotal * (1 + TAX_RATE)

def calculate_order_total(items):
    subtotal = calculate_subtotal(items)
    return calculate_total_with_tax(subtotal)

def calculate_cart_total(cart_items):
    subtotal = calculate_subtotal(cart_items)
    return calculate_total_with_tax(subtotal)
```

**Benefits**:
- Single source of truth for tax calculation
- Change tax rate in one place
- Testable components

---

### Principle 2: SOLID Principles

#### S - Single Responsibility Principle

**Rule**: A class/function should have one, and only one, reason to change.

**Violation Example**:
```python
# ❌ BAD - Multiple responsibilities
class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def save_to_database(self):
        """Save user to database."""  # ❌ Persistence responsibility
        db.execute("INSERT INTO users ...")

    def send_welcome_email(self):
        """Send welcome email."""  # ❌ Email responsibility
        smtp.send(...)

    def hash_password(self):
        """Hash password."""  # ❌ Security responsibility
        return bcrypt.hashpw(...)
```

**Fixed**:
```python
# ✅ GOOD - Single Responsibility
class User:
    """User domain model - only user data."""
    def __init__(self, email, password_hash):
        self.email = email
        self.password_hash = password_hash

class UserRepository:
    """Handles user persistence."""
    def save(self, user):
        db.execute("INSERT INTO users ...")

class PasswordHasher:
    """Handles password hashing."""
    @staticmethod
    def hash(password):
        return bcrypt.hashpw(...)

class WelcomeEmailService:
    """Handles welcome emails."""
    def send(self, user):
        smtp.send(...)
```

#### O - Open/Closed Principle

**Rule**: Open for extension, closed for modification.

**Violation Example**:
```python
# ❌ BAD - Must modify for new payment types
class PaymentProcessor:
    def process(self, payment_type, amount):
        if payment_type == "credit_card":
            return self._process_credit_card(amount)
        elif payment_type == "paypal":
            return self._process_paypal(amount)
        elif payment_type == "crypto":  # ❌ Modifying existing code
            return self._process_crypto(amount)
```

**Fixed**:
```python
# ✅ GOOD - Extend without modifying
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount):
        pass

class CreditCardPayment(PaymentMethod):
    def process(self, amount):
        # Credit card logic
        pass

class PayPalPayment(PaymentMethod):
    def process(self, amount):
        # PayPal logic
        pass

class CryptoPayment(PaymentMethod):  # ✅ New class, no modification
    def process(self, amount):
        # Crypto logic
        pass

class PaymentProcessor:
    def process(self, payment_method: PaymentMethod, amount):
        return payment_method.process(amount)
```

#### L - Liskov Substitution Principle

**Rule**: Subtypes must be substitutable for their base types.

**Violation Example**:
```python
# ❌ BAD - Square violates Rectangle contract
class Rectangle:
    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

class Square(Rectangle):  # ❌ Violates LSP
    def set_width(self, width):
        self.width = width
        self.height = width  # ❌ Unexpected side effect

    def set_height(self, height):
        self.width = height  # ❌ Unexpected side effect
        self.height = height
```

**Fixed**:
```python
# ✅ GOOD - Composition over inheritance
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side
```

#### I - Interface Segregation Principle

**Rule**: Many client-specific interfaces are better than one general-purpose interface.

**Violation Example**:
```python
# ❌ BAD - Fat interface
class Worker(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass

class Robot(Worker):  # ❌ Robots don't eat
    def work(self):
        return "Working"

    def eat(self):
        raise NotImplementedError("Robots don't eat")  # ❌ Forced to implement
```

**Fixed**:
```python
# ✅ GOOD - Segregated interfaces
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Human(Workable, Eatable):
    def work(self):
        return "Working"

    def eat(self):
        return "Eating"

class Robot(Workable):  # ✅ Only implements what it needs
    def work(self):
        return "Working"
```

#### D - Dependency Inversion Principle

**Rule**: Depend on abstractions, not concretions.

**Violation Example**:
```python
# ❌ BAD - Depends on concrete implementation
class EmailService:
    def send(self, to, message):
        # SMTP implementation
        pass

class UserNotifier:
    def __init__(self):
        self.email_service = EmailService()  # ❌ Tight coupling

    def notify(self, user, message):
        self.email_service.send(user.email, message)
```

**Fixed**:
```python
# ✅ GOOD - Depends on abstraction
class NotificationService(ABC):
    @abstractmethod
    def send(self, to, message):
        pass

class EmailService(NotificationService):
    def send(self, to, message):
        # SMTP implementation
        pass

class SMSService(NotificationService):
    def send(self, to, message):
        # SMS implementation
        pass

class UserNotifier:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service  # ✅ Abstraction

    def notify(self, user, message):
        self.notification_service.send(user.contact, message)
```

---

## Code Smells and Fixes

### Smell 1: Long Methods (>20 lines)

**Problem**: Hard to understand, test, and maintain.

**Fix**: Extract methods.

**Before**:
```python
# ❌ BAD - 35 lines
def process_order(order):
    # Validate order
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Negative total")

    # Calculate totals
    subtotal = 0
    for item in order.items:
        subtotal += item.price * item.quantity
    tax = subtotal * 0.08
    shipping = 10 if subtotal < 50 else 0
    total = subtotal + tax + shipping

    # Process payment
    if order.payment_method == "credit_card":
        charge_credit_card(order.card, total)
    elif order.payment_method == "paypal":
        charge_paypal(order.paypal_email, total)

    # Update inventory
    for item in order.items:
        inventory.decrement(item.id, item.quantity)

    # Send confirmation
    send_email(order.customer.email, f"Order confirmed: ${total}")

    return total
```

**After**:
```python
# ✅ GOOD - Small, focused functions
def process_order(order):
    _validate_order(order)
    total = _calculate_total(order)
    _process_payment(order, total)
    _update_inventory(order)
    _send_confirmation(order, total)
    return total

def _validate_order(order):
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Negative total")

def _calculate_total(order):
    subtotal = sum(item.price * item.quantity for item in order.items)
    tax = subtotal * TAX_RATE
    shipping = 0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST
    return subtotal + tax + shipping

def _process_payment(order, total):
    payment_methods = {
        "credit_card": lambda: charge_credit_card(order.card, total),
        "paypal": lambda: charge_paypal(order.paypal_email, total)
    }
    payment_methods[order.payment_method]()

def _update_inventory(order):
    for item in order.items:
        inventory.decrement(item.id, item.quantity)

def _send_confirmation(order, total):
    send_email(order.customer.email, f"Order confirmed: ${total}")
```

### Smell 2: Magic Numbers/Strings

**Problem**: Unclear meaning, hard to change.

**Fix**: Named constants.

**Before**:
```python
# ❌ BAD
def calculate_shipping(weight):
    if weight < 5:
        return 10
    elif weight < 20:
        return 15
    else:
        return 25
```

**After**:
```python
# ✅ GOOD
LIGHT_PACKAGE_THRESHOLD = 5  # pounds
MEDIUM_PACKAGE_THRESHOLD = 20  # pounds
LIGHT_PACKAGE_SHIPPING = 10  # dollars
MEDIUM_PACKAGE_SHIPPING = 15  # dollars
HEAVY_PACKAGE_SHIPPING = 25  # dollars

def calculate_shipping(weight):
    if weight < LIGHT_PACKAGE_THRESHOLD:
        return LIGHT_PACKAGE_SHIPPING
    elif weight < MEDIUM_PACKAGE_THRESHOLD:
        return MEDIUM_PACKAGE_SHIPPING
    else:
        return HEAVY_PACKAGE_SHIPPING
```

### Smell 3: Unclear Variable Names

**Problem**: Intent not obvious.

**Fix**: Descriptive names.

**Before**:
```python
# ❌ BAD
def calc(x, y):
    z = x * y
    if z > 100:
        z = z * 0.9
    return z
```

**After**:
```python
# ✅ GOOD
BULK_DISCOUNT_THRESHOLD = 100
BULK_DISCOUNT_RATE = 0.9

def calculate_order_total(unit_price, quantity):
    subtotal = unit_price * quantity
    if subtotal > BULK_DISCOUNT_THRESHOLD:
        subtotal = subtotal * BULK_DISCOUNT_RATE
    return subtotal
```

### Smell 4: Deep Nesting (>3 levels)

**Problem**: Hard to follow logic.

**Fix**: Guard clauses, early returns.

**Before**:
```python
# ❌ BAD - 4 levels of nesting
def process_user(user):
    if user:
        if user.is_active:
            if user.email_verified:
                if user.has_subscription:
                    return send_premium_content(user)
                else:
                    return send_free_content(user)
            else:
                return send_verification_email(user)
        else:
            return "User inactive"
    else:
        return "User not found"
```

**After**:
```python
# ✅ GOOD - Guard clauses
def process_user(user):
    if not user:
        return "User not found"

    if not user.is_active:
        return "User inactive"

    if not user.email_verified:
        return send_verification_email(user)

    if user.has_subscription:
        return send_premium_content(user)

    return send_free_content(user)
```

### Smell 5: God Classes

**Problem**: Class does too much.

**Fix**: Split responsibilities.

**Before**:
```python
# ❌ BAD - 500 line god class
class UserManager:
    def create_user(self): ...
    def update_user(self): ...
    def delete_user(self): ...
    def send_email(self): ...
    def send_sms(self): ...
    def process_payment(self): ...
    def generate_report(self): ...
    def export_csv(self): ...
    def import_csv(self): ...
    def validate_data(self): ...
    # ... 50 more methods
```

**After**:
```python
# ✅ GOOD - Single Responsibility
class UserRepository:
    def create(self, user): ...
    def update(self, user): ...
    def delete(self, user_id): ...

class NotificationService:
    def send_email(self, to, message): ...
    def send_sms(self, to, message): ...

class PaymentProcessor:
    def process(self, payment): ...

class ReportGenerator:
    def generate(self, data): ...

class CSVHandler:
    def export(self, data): ...
    def import_file(self, file): ...

class DataValidator:
    def validate(self, data): ...
```

---

## Naming Conventions

### Variables and Functions

**Rules**:
- Use `snake_case` for variables and functions (Python)
- Use `camelCase` for JavaScript/TypeScript
- Boolean variables should be questions: `is_active`, `has_permission`
- Functions should be verbs: `calculate_total`, `send_email`

**Examples**:
```python
# ✅ GOOD
user_count = 10
is_authenticated = True
has_premium_subscription = False

def calculate_tax(amount):
    return amount * TAX_RATE

def send_welcome_email(user):
    ...

# ❌ BAD
uc = 10  # ❌ Unclear abbreviation
authenticated = True  # ❌ Not a question
premium = False  # ❌ Not a question

def tax(amount):  # ❌ Not a verb
    return amount * TAX_RATE

def email(user):  # ❌ Not descriptive
    ...
```

### Classes

**Rules**:
- Use `PascalCase`
- Nouns, not verbs
- Descriptive, not abbreviated

**Examples**:
```python
# ✅ GOOD
class User:
    pass

class OrderProcessor:
    pass

class EmailNotificationService:
    pass

# ❌ BAD
class user:  # ❌ Not PascalCase
    pass

class ProcessOrder:  # ❌ Verb, not noun
    pass

class EmailNotifSvc:  # ❌ Abbreviated
    pass
```

### Constants

**Rules**:
- Use `UPPER_SNAKE_CASE`
- Group related constants

**Examples**:
```python
# ✅ GOOD
MAX_LOGIN_ATTEMPTS = 3
SESSION_TIMEOUT_SECONDS = 3600
DEFAULT_PAGE_SIZE = 20

# Tax rates
TAX_RATE_CA = 0.0725
TAX_RATE_NY = 0.08875
TAX_RATE_TX = 0.0625

# ❌ BAD
maxLoginAttempts = 3  # ❌ Not UPPER_SNAKE_CASE
timeout = 3600  # ❌ Not descriptive
```

---

## Function Design

### Function Length

**Rule**: Functions should be <20 lines. If longer, extract.

### Function Parameters

**Rule**: Max 3-4 parameters. If more, use a data class or dict.

**Before**:
```python
# ❌ BAD - Too many parameters
def create_user(first_name, last_name, email, phone, address, city, state, zip_code, country):
    ...
```

**After**:
```python
# ✅ GOOD - Data class
@dataclass
class UserData:
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str

def create_user(user_data: UserData):
    ...
```

### Return Values

**Rule**: Return early, return often.

**Before**:
```python
# ❌ BAD
def get_user_role(user):
    role = None
    if user:
        if user.is_admin:
            role = "admin"
        else:
            if user.is_moderator:
                role = "moderator"
            else:
                role = "user"
    return role
```

**After**:
```python
# ✅ GOOD
def get_user_role(user):
    if not user:
        return None

    if user.is_admin:
        return "admin"

    if user.is_moderator:
        return "moderator"

    return "user"
```

---

## Comments and Documentation

### When to Comment

**DO Comment**:
- WHY code does something (not WHAT)
- Complex algorithms
- Business logic rationale
- Gotchas and edge cases
- TODO/FIXME with ticket numbers

**DON'T Comment**:
- Obvious code (self-documenting)
- What code does (name it better instead)
- Commented-out code (delete it)

**Examples**:
```python
# ❌ BAD - Obvious comment
# Increment counter by 1
counter += 1

# ❌ BAD - What instead of why
# Loop through users
for user in users:
    ...

# ✅ GOOD - Why, not what
# Use exponential backoff to avoid overwhelming API during high load
retry_delay = 2 ** attempt_count

# ✅ GOOD - Business logic rationale
# Orders over $50 ship free per 2024 Q1 marketing campaign
if order.total >= 50:
    shipping_cost = 0

# ✅ GOOD - Gotcha
# Note: Database cursor must be closed manually (context manager not available in this library version)
cursor = db.execute(query)
try:
    result = cursor.fetchall()
finally:
    cursor.close()

# ✅ GOOD - TODO with ticket
# TODO(PROJ-123): Replace with async implementation in v2.0
def fetch_user_sync(user_id):
    ...
```

### Docstrings

**Rule**: Every public function/class needs a docstring.

**Format**:
```python
def calculate_shipping(weight, distance, priority):
    """Calculate shipping cost based on weight, distance, and priority.

    Args:
        weight: Package weight in pounds
        distance: Shipping distance in miles
        priority: Priority level ("standard", "express", "overnight")

    Returns:
        Shipping cost in dollars

    Raises:
        ValueError: If weight is negative or priority is invalid

    Example:
        >>> calculate_shipping(5, 100, "standard")
        12.50
    """
    ...
```

---

## Static Analysis Tools

### Required Tools

**Black** - Code formatting:
```bash
black --check .
black .  # Auto-format
```

**isort** - Import sorting:
```bash
isort --check .
isort .  # Auto-sort
```

**Flake8** - Linting:
```bash
flake8 .
```

**mypy** - Type checking:
```bash
mypy .
```

### Configuration

**pyproject.toml**:
```toml
[tool.black]
line-length = 100
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.flake8]
max-line-length = 100
extend-ignore = E203, W503
```

---

## Quality Checklist

Before committing code:

- [ ] **DRY**: No duplication
- [ ] **SOLID**: Single responsibility, proper abstractions
- [ ] **Functions**: <20 lines, <4 parameters
- [ ] **Names**: Clear, descriptive, follow conventions
- [ ] **Nesting**: <3 levels deep
- [ ] **Comments**: Only WHY, not WHAT
- [ ] **Docstrings**: All public functions/classes
- [ ] **Magic numbers**: Replaced with constants
- [ ] **Code smells**: None detected
- [ ] **Black**: Formatting passes
- [ ] **isort**: Imports sorted
- [ ] **Flake8**: No linting errors
- [ ] **mypy**: No type errors

**If ANY box is unchecked, code is NOT ready for commit.**

---

## Constitutional Integration

Code quality standards enforce constitutional principles:

- **Evidence-Based**: Tests prove code works, static analysis proves code quality
- **Thoroughness**: Quality checks are comprehensive, not shortcuts
- **Transparency**: Clean code is self-documenting, shows intent
- **No Ambiguity**: Clear names, simple logic, obvious behavior

**Clean code is not optional. It is constitutional law for software development.**
