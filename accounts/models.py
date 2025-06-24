from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image
import os

# TODO: ARCHITECTURAL IMPROVEMENT NEEDED
# ScrapCategory and ScrapMaterial models should logically belong in the marketplace app
# rather than accounts app. However, moving them requires careful database migration
# to avoid breaking existing data and relationships.
#
# Current circular import issue:
# - marketplace.models imports from accounts.models (ScrapCategory, ScrapMaterial)
# - This creates tight coupling between apps
#
# Recommended solution:
# 1. Create a new 'core' app for shared models like ScrapCategory and ScrapMaterial
# 2. Or move these models to marketplace app with proper migration
# 3. Update all imports and references accordingly

class User(AbstractUser):
    """Extended User Model with dealer support"""
    USER_TYPES = [
        ('regular', 'Regular User'),
        ('dealer', 'Scrap Dealer'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='regular')
    phone_number = PhoneNumberField(
        blank=True,
        region='IN',  # Default to India
        help_text="Phone number with country code (e.g., +91 9876543210)"
    )
    eco_points = models.PositiveIntegerField(default=0)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize profile picture
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)

class DealerProfile(models.Model):
    """Extended profile for verified dealers"""
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dealer_profile')
    business_name = models.CharField(max_length=200)
    business_registration_number = models.CharField(max_length=50, unique=True)
    gst_number = models.CharField(max_length=15, blank=True)
    business_license = models.ImageField(upload_to='dealer_documents/', blank=True)
    business_address = models.TextField()
    business_phone = PhoneNumberField(
        region='IN',  # Default to India
        help_text="Business phone number with country code (e.g., +91 9876543210)"
    )
    business_email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verification_date = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_dealers')
    
    # Business Details
    years_in_business = models.PositiveIntegerField(blank=True, null=True)
    specialization = models.TextField(help_text="Types of scrap materials you specialize in")
    minimum_quantity = models.CharField(max_length=100, help_text="Minimum quantity for pickup", blank=True)
    pickup_available = models.BooleanField(default=True)
    delivery_available = models.BooleanField(default=False)
    operating_hours = models.CharField(max_length=200, blank=True, help_text="e.g., Mon-Sat 9AM-6PM")
    
    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)
    total_transactions = models.PositiveIntegerField(default=0)
    
    # Location for nearby dealer search
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-verification_date', '-created_at']

    def __str__(self):
        return f"{self.business_name} ({self.get_verification_status_display()})"

    @property
    def is_verified(self):
        return self.verification_status == 'verified'

class ScrapCategory(models.Model):
    """Scrap material categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class or emoji")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Scrap Categories"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

class ScrapMaterial(models.Model):
    """Specific scrap materials within categories"""
    QUALITY_GRADES = [
        ('A', 'Grade A (Excellent)'),
        ('B', 'Grade B (Good)'),
        ('C', 'Grade C (Fair)'),
        ('D', 'Grade D (Poor)'),
    ]

    category = models.ForeignKey(ScrapCategory, on_delete=models.CASCADE, related_name='materials')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, default='kg', help_text="Unit of measurement (kg, ton, piece, etc.)")
    quality_grades = models.JSONField(default=list, help_text="List of applicable quality grades")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']
        unique_together = ['category', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"



class DealerPrice(models.Model):
    """Dealer prices for different scrap materials"""
    dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, related_name='prices')
    material = models.ForeignKey(ScrapMaterial, on_delete=models.CASCADE)
    quality_grade = models.CharField(max_length=1, choices=ScrapMaterial.QUALITY_GRADES)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['dealer', 'material', 'quality_grade']
        ordering = ['-price_per_unit']
    
    def __str__(self):
        return f"{self.dealer.business_name} - {self.material.name} ({self.quality_grade}) - ₹{self.price_per_unit}/{self.material.unit}"

class DealerRating(models.Model):
    """User ratings for dealers"""
    dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, help_text="Related transaction ID if any")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['dealer', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} rated {self.dealer.business_name} - {self.rating} stars"

class DealerInquiry(models.Model):
    """User inquiries to dealers"""
    INQUIRY_STATUS = [
        ('pending', 'Pending'),
        ('responded', 'Responded'),
        ('closed', 'Closed'),
    ]
    
    dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, related_name='inquiries')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    material = models.ForeignKey(ScrapMaterial, on_delete=models.CASCADE, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    quantity = models.CharField(max_length=100, blank=True, help_text="Estimated quantity")
    contact_preference = models.CharField(max_length=20, choices=[('email', 'Email'), ('phone', 'Phone')], default='email')
    status = models.CharField(max_length=20, choices=INQUIRY_STATUS, default='pending')
    dealer_response = models.TextField(blank=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Dealer Inquiries"
    
    def __str__(self):
        return f"Inquiry from {self.user.username} to {self.dealer.business_name}"