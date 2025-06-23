from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Google auth placeholder (handled by allauth)
    path('google/login/', views.google_login_redirect, name='google_login'),
    
    # Dealer URLs
    path('dealer/register/', views.dealer_register_view, name='dealer_register'),
    path('dealer/dashboard/', views.dealer_dashboard, name='dealer_dashboard'),
    path('dealer/prices/', views.manage_prices, name='manage_prices'),
    
    # Public dealer directory
    path('dealers/', views.dealers_directory, name='dealers_directory'),
    path('dealers/<int:dealer_id>/', views.dealer_detail, name='dealer_detail'),
    path('dealers/<int:dealer_id>/contact/', views.contact_dealer, name='contact_dealer'),
    path('dealers/<int:dealer_id>/rate/', views.rate_dealer, name='rate_dealer'),
    
    # Price comparison
    path('prices/', views.price_comparison, name='price_comparison'),
    
    # Profile management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Allauth URLs
    path('auth/', include('allauth.urls')),
]