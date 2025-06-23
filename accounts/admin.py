from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, DealerProfile, ScrapCategory, ScrapMaterial, DealerPrice, DealerRating, DealerInquiry

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'user_type', 'eco_points', 'is_verified', 'date_joined']
    list_filter = ['user_type', 'is_verified', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'eco_points', 'profile_picture', 
                      'address', 'city', 'state', 'pincode', 'is_verified')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'eco_points')
        }),
    )

@admin.register(DealerProfile)
class DealerProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'verification_status', 'average_rating', 'total_transactions', 'created_at']
    list_filter = ['verification_status', 'pickup_available', 'delivery_available', 'created_at']
    search_fields = ['business_name', 'user__username', 'user__email', 'business_registration_number']
    readonly_fields = ['average_rating', 'total_ratings', 'total_transactions', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'business_name', 'business_registration_number', 'gst_number')
        }),
        ('Contact Details', {
            'fields': ('business_address', 'business_phone', 'business_email', 'website')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verification_date', 'verified_by', 'business_license')
        }),
        ('Business Details', {
            'fields': ('years_in_business', 'specialization', 'minimum_quantity', 
                      'pickup_available', 'delivery_available', 'operating_hours')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_ratings', 'total_transactions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['verify_dealers', 'reject_dealers']
    
    def verify_dealers(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            verification_status='verified', 
            verification_date=timezone.now(),
            verified_by=request.user
        )
        self.message_user(request, f'{updated} dealers verified successfully.')
    verify_dealers.short_description = "Verify selected dealers"
    
    def reject_dealers(self, request, queryset):
        updated = queryset.update(verification_status='rejected')
        self.message_user(request, f'{updated} dealers rejected.')
    reject_dealers.short_description = "Reject selected dealers"

@admin.register(ScrapCategory)
class ScrapCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'sort_order', 'material_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'sort_order']
    
    def material_count(self, obj):
        return obj.materials.count()
    material_count.short_description = 'Materials Count'

@admin.register(ScrapMaterial)
class ScrapMaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'is_active', 'dealer_count']
    list_filter = ['category', 'is_active', 'unit']
    search_fields = ['name', 'description', 'category__name']
    list_editable = ['is_active']
    
    def dealer_count(self, obj):
        return obj.dealerprice_set.filter(is_active=True).values('dealer').distinct().count()
    dealer_count.short_description = 'Active Dealers'

@admin.register(DealerPrice)
class DealerPriceAdmin(admin.ModelAdmin):
    list_display = ['dealer', 'material', 'quality_grade', 'price_display', 'minimum_quantity', 'is_active', 'last_updated']
    list_filter = ['quality_grade', 'is_active', 'material__category', 'last_updated']
    search_fields = ['dealer__business_name', 'material__name', 'material__category__name']
    list_editable = ['is_active']
    
    def price_display(self, obj):
        return format_html('₹{}/{unit}', obj.price_per_unit, unit=obj.material.unit)
    price_display.short_description = 'Price'

@admin.register(DealerRating)
class DealerRatingAdmin(admin.ModelAdmin):
    list_display = ['dealer', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['dealer__business_name', 'user__username', 'review']
    readonly_fields = ['created_at']

@admin.register(DealerInquiry)
class DealerInquiryAdmin(admin.ModelAdmin):
    list_display = ['dealer', 'user', 'subject', 'status', 'created_at']
    list_filter = ['status', 'contact_preference', 'created_at']
    search_fields = ['dealer__business_name', 'user__username', 'subject', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Inquiry Details', {
            'fields': ('dealer', 'user', 'material', 'subject', 'message', 'quantity', 'contact_preference')
        }),
        ('Status', {
            'fields': ('status', 'dealer_response', 'responded_at')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )