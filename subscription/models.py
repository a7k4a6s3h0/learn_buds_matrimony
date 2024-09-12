# models.py
from django.db import models
from U_auth.models import costume_user

class Payment(models.Model):
    user = models.ForeignKey(costume_user, on_delete=models.CASCADE, related_name="userpayment_details")
    razorpay_order_id = models.CharField(max_length=100,null=True)
    razorpay_payment_id = models.CharField(max_length=100,null=True)
    razorpay_signature = models.CharField(max_length=255,null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.razorpay_payment_id)
    
