from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Payment(models.Model):
    # Assuming User model is the default auth user model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    invoice_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=100)
    is_recurring = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

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
            self.expires_at = timezone.now() + timezone.timedelta(weeks=1)
            self.save()
        else:
            return False
    
    def is_time_to_renew(self):
        return timezone.now() >= self.expires_at
    
class Invoice(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment.user.username} - {self.amount} {self.currency}"
    
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2,help_text="Price in decimal format and USD")
    weeks = models.DateTimeField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    featured = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"