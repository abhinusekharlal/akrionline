from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import ScrapCategory, ScrapMaterial
from PIL import Image
import uuid

User = get_user_model()

class ScrapListing(models.Model):
    """User listings for selling scrap materials"""
    LISTING_STATUS = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    QUALITY_GRADES = [
        ('A', 'Grade A (Excellent)'),
        ('B', 'Grade B (Good)'),
        ('C', 'Grade C (Fair)'),
        ('D', 'Grade D (Poor)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scrap_listings')
    material = models.ForeignKey(ScrapMaterial, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quality_grade = models.CharField(max_length=1, choices=QUALITY_GRADES, default='B')
    expected_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Expected price per unit")
    
    # Location
    pickup_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Images
    image1 = models.ImageField(upload_to='scrap_listings/', blank=True, null=True)
    image2 = models.ImageField(upload_to='scrap_listings/', blank=True, null=True)
    image3 = models.ImageField(upload_to='scrap_listings/', blank=True, null=True)
    
    # AI Assessment (will be populated by AI service)
    ai_quality_grade = models.CharField(max_length=1, choices=QUALITY_GRADES, blank=True)
    ai_material_type = models.CharField(max_length=100, blank=True)
    ai_confidence_score = models.FloatField(default=0.0)
    ai_suggested_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=LISTING_STATUS, default='active')
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.seller.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize images
        for field_name in ['image1', 'image2', 'image3']:
            image_field = getattr(self, field_name)
            if image_field:
                self._resize_image(image_field)
    
    def _resize_image(self, image_field):
        """Resize uploaded images"""
        try:
            img = Image.open(image_field.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(image_field.path)
        except Exception:
            pass

class ReusableItemCategory(models.Model):
    """Categories for reusable items"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Reusable Item Categories"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name

class ReusableItemListing(models.Model):
    """User listings for reusable items"""
    TRANSACTION_TYPES = [
        ('sale', 'For Sale'),
        ('free', 'Free Giveaway'),
        ('exchange', 'Exchange'),
    ]
    
    CONDITION_GRADES = [
        ('like_new', 'Like New'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    LISTING_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reusable_listings')
    category = models.ForeignKey(ReusableItemCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Item details
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_GRADES)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # For exchanges
    exchange_requirements = models.TextField(blank=True, help_text="What you're looking for in exchange")
    
    # Location
    pickup_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Images
    image1 = models.ImageField(upload_to='reusable_items/', blank=True, null=True)
    image2 = models.ImageField(upload_to='reusable_items/', blank=True, null=True)
    image3 = models.ImageField(upload_to='reusable_items/', blank=True, null=True)
    image4 = models.ImageField(upload_to='reusable_items/', blank=True, null=True)
    
    # AI Assessment
    ai_condition_grade = models.CharField(max_length=20, choices=CONDITION_GRADES, blank=True)
    ai_confidence_score = models.FloatField(default=0.0)
    ai_suggested_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=LISTING_STATUS, default='active')
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_transaction_type_display()}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize images
        for field_name in ['image1', 'image2', 'image3', 'image4']:
            image_field = getattr(self, field_name)
            if image_field:
                self._resize_image(image_field)
    
    def _resize_image(self, image_field):
        """Resize uploaded images"""
        try:
            img = Image.open(image_field.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(image_field.path)
        except Exception:
            pass

class ListingInquiry(models.Model):
    """Inquiries for both scrap and reusable item listings"""
    INQUIRY_STATUS = [
        ('pending', 'Pending'),
        ('responded', 'Responded'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_inquiries')
    
    # Generic foreign keys for different listing types
    scrap_listing = models.ForeignKey(ScrapListing, on_delete=models.CASCADE, blank=True, null=True, related_name='inquiries')
    reusable_listing = models.ForeignKey(ReusableItemListing, on_delete=models.CASCADE, blank=True, null=True, related_name='inquiries')
    
    message = models.TextField()
    offered_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    offered_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Seller response
    status = models.CharField(max_length=20, choices=INQUIRY_STATUS, default='pending')
    seller_response = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        listing = self.scrap_listing or self.reusable_listing
        return f"Inquiry from {self.buyer.username} for {listing.title}"
    
    @property
    def listing(self):
        return self.scrap_listing or self.reusable_listing
    
    @property
    def seller(self):
        return self.listing.seller if self.listing else None

class Transaction(models.Model):
    """Completed transactions"""
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('released', 'Released'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    
    # Related listing
    scrap_listing = models.ForeignKey(ScrapListing, on_delete=models.CASCADE, blank=True, null=True)
    reusable_listing = models.ForeignKey(ReusableItemListing, on_delete=models.CASCADE, blank=True, null=True)
    
    # Transaction details
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Eco points awarded
    seller_eco_points = models.PositiveIntegerField(default=0)
    buyer_eco_points = models.PositiveIntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        listing = self.scrap_listing or self.reusable_listing
        return f"Transaction: {self.buyer.username} ↔ {self.seller.username} - {listing.title}"
    
    @property
    def listing(self):
        return self.scrap_listing or self.reusable_listing

class EcoPointsHistory(models.Model):
    """Track eco points earning and spending history"""
    TRANSACTION_TYPES = [
        ('earned_sale', 'Earned from Sale'),
        ('earned_purchase', 'Earned from Purchase'),
        ('earned_review', 'Earned from Review'),
        ('earned_referral', 'Earned from Referral'),
        ('spent_discount', 'Spent on Discount'),
        ('spent_cashout', 'Cashed Out'),
        ('spent_donation', 'Donated to Charity'),
        ('bonus', 'Bonus Points'),
        ('penalty', 'Penalty Deduction'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eco_points_history')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()  # Positive for earned, negative for spent
    description = models.CharField(max_length=200)
    reference_id = models.CharField(max_length=100, blank=True, help_text="Reference to related transaction/listing")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Eco Points History"
    
    def __str__(self):
        action = "Earned" if self.points > 0 else "Spent"
        return f"{self.user.username} {action} {abs(self.points)} points - {self.get_transaction_type_display()}"