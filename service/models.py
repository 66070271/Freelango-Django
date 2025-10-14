from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

# -------------------------
# User / Freelancer / Client
# -------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    email = models.EmailField()
    address = models.TextField()
    phone_number =models.CharField(max_length=10)
    birthday = models.DateField(null = True,blank=True)
    image = models.FileField(upload_to='profile_images/',null=True,blank=True)

# -------------------------
# Category
# -------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null = True)

    def __str__(self):
        return self.name


# -------------------------
# Service
# -------------------------
class Service(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")

    freelancer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="services"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time = models.PositiveIntegerField(help_text="Delivery time in days")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    categories = models.ManyToManyField(Category, related_name="services")  # M:N
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='service_images/')

    def __str__(self):
        return f"Image for {self.service.title}"
# -------------------------
# Order
# -------------------------
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        IN_PROGRESS = "in_progress", _("In Progress")
        COMPLETED = "completed", _("Completed")
        CONFIRMED =  "confirmed",_("confirmed")
        CANCELLED = "cancelled", _("Cancelled")
    class Meta:
        permissions = [
            ("manage_order", "Can manage order"),
        ]
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=False)
    def __str__(self):
        return f"Order #{self.id} - {self.client}"


# -------------------------
# Review
# -------------------------
class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reviews")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.client} for {self.freelancer}"


# -------------------------
# Payment
# -------------------------
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed",_("confirmed")
        PAID = "paid", _("Paid")
        CANCELLED = "cancelled", _("Cancelled")
        REFUNDED = "refunded", _("Refunded")
    class Meta:
        permissions = [
            ("approve_payment", "Can approve payment"),
            ("approve_refund", "Can approve refund")
        ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=50,default="QR")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_ref = models.FileField(upload_to='transaction_ref/',null=True,blank=True)

    def __str__(self):
        return f"Payment #{self.id} for Order #{self.order.id}"

class PlatformAccount(models.Model):
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    qr_image = models.FileField(upload_to='bank_qr/', null=True, blank=True)  # QR พร้อมโอน

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"