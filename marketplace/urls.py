from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Marketplace URLs will be added here
    path('', views.marketplace_home, name='home'),
]