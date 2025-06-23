from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
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
]