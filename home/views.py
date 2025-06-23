from django.shortcuts import render

def home(request):
    """
    Home page view with platform statistics and overview
    """
    context = {
        'total_users': 15000,
        'total_scrap_traded': 50000, # in kg
        'co2_saved': 25000, # in kg
        'active_listings': 1250,
        'successful_transactions': 8500,
    }
    return render(request, 'home/index.html', context)