from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from users.models import UserProfile

class Payment(models.Model):
    # Assuming User model is the default auth user model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    invoice_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=100)
    is_recurring = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=1)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    isGift = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.username} - {self.invoice_uuid}"

    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(weeks=1)
    
    @property
    def is_paid(self):
        return self.is_completed
    
    @property
    def invoice_url(self):
        return self.invoice.url
    
    def is_still_valid(self):
        return not self.is_expired and self.is_completed
    
    def recurr_payment(self):
        if  self.is_time_to_renew():
            product = self.objects.get(name=self.product)
            #using profile.card_id to charge the user
            #charge the user
            #if the payment is successful
            card_id = UserProfile.objects.get(user=self.user).card_id
            charge_user(card_id,self.product.price)
            self.expires_at = timezone.now() + timezone.timedelta(weeks=product.days/7)
            self.save()
        else:
            return False
    
    def is_time_to_renew(self):
        return timezone.now() >= self.expires_at

def charge_user(card_id,amount):
    #charge the user using tap payment gateway
       pass
   
class Invoice(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    subscreibed_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.payment.user.username} - {self.amount} {self.currency}"
    
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2,help_text="Price in decimal format and USD")
    days = models.PositiveIntegerField(default=1)
    description = models.TextField()
    zid_url = models.URLField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.URLField(default="")
    featured = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    
class code(models.Model):
    code = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.code} - {self.user.username}"
    
    

class SubscriptionCode(models.Model):
    hex_code = models.CharField(max_length=16, unique=True)
    subscription_length = models.IntegerField(help_text="Subscription length in months")
    is_redeemed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hex_code} - {self.subscription_length} months"