from django.db import models
from users.models import CustomUser
from subscriptions.models import Subscription

# Create your models here.
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



from decimal import Decimal

class Invoice(models.Model):
    INVOICE_TYPE = [
        ("sale", "Sale"),
        ("expense", "Expense"),
    ]
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("unpaid", "Unpaid"),
        ("overdue", "Overdue"),
    ]

    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_type = models.CharField(max_length=10, choices=INVOICE_TYPE)

    # (Sale হলে client থাকবে)
    client = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'client'},
        null=True, blank=True,
        related_name="invoices"
    )

    # (Expense হলে employee connected থাকবে)
    employee = models.ForeignKey(
        "CustomUser",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'user_type': 'employee'},
        related_name="expenses"
    )

    # subscription link for sale invoice
    subscription = models.ForeignKey(
        "Subscription", null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="invoices"
    )

    # expenses-এর জন্য আলাদা ক্যাটাগরি
    category = models.ForeignKey(
        ExpenseCategory, null=True, blank=True, on_delete=models.SET_NULL
    )

    # billing amounts
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unpaid")

    def save(self, *args, **kwargs):
        amount_after_discount = self.sub_total - self.discount
        tax_amount = (amount_after_discount * (self.tax / Decimal(100)))
        self.total_amount = amount_after_discount + tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.get_invoice_type_display()} - {self.total_amount}"