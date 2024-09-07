from django.db import models
from U_auth.models import UserPersonalDetails, costume_user
# Create your models here.


# ..............Target user profile flow model here.............................

class InterestRequest(models.Model):
    sender=models.ForeignKey(costume_user, related_name="sent_requests", on_delete=models.CASCADE)
    receiver=models.ForeignKey(costume_user, related_name="received_requests", on_delete=models.CASCADE)
    created_at=models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.status}"
    
    def get_sender_profile_pic(self):
        try:
            return self.sender.user_details.profile_pic
        except UserPersonalDetails.DoesNotExist:
            return None

    def get_receiver_profile_pic(self):
        try:
            return self.receiver.user_details.profile_pic
        except UserPersonalDetails.DoesNotExist:
            return None

