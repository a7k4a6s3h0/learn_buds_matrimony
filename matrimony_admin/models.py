from datetime import timedelta
from django.db import models
from django.shortcuts import render
from U_auth.models import costume_user
from django.utils.text import slugify
from django.views.generic import ListView
# Create your models here.


class Subscription(models.Model):

    PLAN_CHOICES = [
        ('free', 'Free'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('premium', 'Premium'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    slug = models.SlugField(unique=True, blank=True, null=True)  # New slug field
    plan_type = models.CharField(max_length=100, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=True)  # Manually set the end date based on the plan duration
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return self.plan_type

    # Optional method to calculate end date based on the subscription duration
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.plan_type)

        if not self.end_date:
            # Example: Set end_date to 30 days from start_date for premium plans
            self.end_date = self.start_date + timedelta(days=30 if self.plan_type == 'premium' else 0)
        super().save(*args, **kwargs)


class SubscriptionINFO(models.Model):

    sub = models.ForeignKey(Subscription, related_name="sub_info", on_delete=models.CASCADE)
    info = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SubscriptionINFO"
        verbose_name_plural = "SubscriptionINFOS"

    def __str__(self):
        return f"{self.sub.plan_type}_info"


class BlockedUserInfo(models.Model):
    user = models.OneToOneField(costume_user, related_name="blocked_user", on_delete=models.CASCADE)
    reason = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    times = models.IntegerField(default=0)


#arjun

#ARJUN 
class Add_expense(models.Model):
    # Auto-incrementing field for serial number (sl_no)
    sl_no = models.AutoField(primary_key=True)
    
    # Date field to store the date of the expense
    date = models.DateField()

    # Invoice number for the expense
    invoice_number = models.CharField(max_length=100, unique=True)

    # Choices for the category field
    CATEGORY_CHOICES = [
        ('OTHER', 'Other'),
        ('OFFICE', 'Office'),
        ('DARING', 'Daring'),
        ('MISCELLANEOUS', 'Miscellaneous'),
    ]

    # Category field with predefined options
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    # Description of the expense
    description = models.CharField(max_length=15)

    # Remark with a max length of 15 characters
    remark = models.CharField(max_length=15)

    # DR (debit) - an integer field
    dr = models.IntegerField()

    # CR (credit) - another integer field
    cr = models.IntegerField()

    # Image field to store an invoice image
    invoice = models.FileField(upload_to='invoices/', blank=True, null=True)

    class Meta:
        verbose_name = "Add Expense"
        verbose_name_plural = "Add Expenses"

    def __str__(self):
        return f"{self.invoice_number} - {self.category}"