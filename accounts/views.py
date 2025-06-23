from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from .models import User, DealerProfile, ScrapCategory, ScrapMaterial, DealerPrice, DealerRating, DealerInquiry
from .forms import UserRegistrationForm, DealerRegistrationForm, DealerPriceFormSet, DealerInquiryForm

def login_view(request):
    """Login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home:home')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    """Registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            
            # Redirect to dealer registration if user selected dealer type
            if user.user_type == 'dealer':
                return redirect('accounts:dealer_register')
            return redirect('home:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def google_login_redirect(request):
    """Redirect to Google OAuth"""
    # Store user type in session for social account adapter
    user_type = request.GET.get('type', 'regular')
    request.session['signup_user_type'] = user_type
    return redirect('/accounts/auth/google/login/')

@login_required
def profile_view(request):
    """User profile view"""
    context = {
        'user': request.user,
        'is_dealer': hasattr(request.user, 'dealer_profile'),
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone_number = request.POST.get('phone_number', '')
        user.city = request.POST.get('city', '')
        user.address = request.POST.get('address', '')
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/edit_profile.html', {'user': request.user})

@login_required
def dealer_register_view(request):
    """Dealer profile registration"""
    if request.user.user_type != 'dealer':
        messages.error(request, 'Only dealer accounts can access this page.')
        return redirect('home:home')
    
    if hasattr(request.user, 'dealer_profile'):
        messages.info(request, 'You already have a dealer profile.')
        return redirect('accounts:dealer_dashboard')
    
    if request.method == 'POST':
        form = DealerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            dealer_profile = form.save(commit=False)
            dealer_profile.user = request.user
            dealer_profile.save()
            messages.success(request, 'Dealer profile created! Your account is pending verification.')
            return redirect('accounts:dealer_dashboard')
    else:
        form = DealerRegistrationForm()
    
    return render(request, 'accounts/dealer_register.html', {'form': form})

@login_required
def dealer_dashboard(request):
    """Dealer dashboard"""
    if request.user.user_type != 'dealer' or not hasattr(request.user, 'dealer_profile'):
        messages.error(request, 'Access denied.')
        return redirect('home:home')
    
    dealer = request.user.dealer_profile
    prices = dealer.prices.filter(is_active=True).select_related('material__category')
    recent_inquiries = dealer.inquiries.all()[:5]
    recent_ratings = dealer.ratings.all()[:5]
    
    context = {
        'dealer': dealer,
        'prices': prices,
        'recent_inquiries': recent_inquiries,
        'recent_ratings': recent_ratings,
        'total_materials': prices.count(),
        'avg_rating': dealer.average_rating,
    }
    return render(request, 'accounts/dealer_dashboard.html', context)

@login_required
def manage_prices(request):
    """Manage dealer prices"""
    if request.user.user_type != 'dealer' or not hasattr(request.user, 'dealer_profile'):
        messages.error(request, 'Access denied.')
        return redirect('home:home')
    
    dealer = request.user.dealer_profile
    if not dealer.is_verified:
        messages.warning(request, 'Your dealer account is not verified yet.')
        return redirect('accounts:dealer_dashboard')
    
    if request.method == 'POST':
        formset = DealerPriceFormSet(request.POST, instance=dealer)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Prices updated successfully!')
            return redirect('accounts:manage_prices')
    else:
        formset = DealerPriceFormSet(instance=dealer)
    
    categories = ScrapCategory.objects.filter(is_active=True).prefetch_related('materials')
    
    context = {
        'formset': formset,
        'dealer': dealer,
        'categories': categories,
    }
    return render(request, 'accounts/manage_prices.html', context)

def dealers_directory(request):
    """Public directory of verified dealers"""
    dealers = DealerProfile.objects.filter(verification_status='verified')
    
    # Search and filters
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    city = request.GET.get('city', '')
    
    if search:
        dealers = dealers.filter(
            Q(business_name__icontains=search) |
            Q(specialization__icontains=search) |
            Q(user__city__icontains=search)
        )
    
    if category:
        dealers = dealers.filter(prices__material__category__name=category).distinct()
    
    if city:
        dealers = dealers.filter(user__city__icontains=city)
    
    # Pagination
    paginator = Paginator(dealers, 12)
    page_number = request.GET.get('page')
    dealers = paginator.get_page(page_number)
    
    categories = ScrapCategory.objects.filter(is_active=True)
    cities = DealerProfile.objects.filter(
        verification_status='verified'
    ).values_list('user__city', flat=True).distinct()
    
    context = {
        'dealers': dealers,
        'categories': categories,
        'cities': [city for city in cities if city],
        'search': search,
        'selected_category': category,
        'selected_city': city,
    }
    return render(request, 'accounts/dealers_directory.html', context)

def dealer_detail(request, dealer_id):
    """Dealer detail page with prices and contact form"""
    dealer = get_object_or_404(DealerProfile, id=dealer_id, verification_status='verified')
    prices = dealer.prices.filter(is_active=True).select_related('material__category').order_by('material__category', 'material__name')
    ratings = dealer.ratings.all()[:10]
    
    # Group prices by category
    prices_by_category = {}
    for price in prices:
        category = price.material.category.name
        if category not in prices_by_category:
            prices_by_category[category] = []
        prices_by_category[category].append(price)
    
    context = {
        'dealer': dealer,
        'prices_by_category': prices_by_category,
        'ratings': ratings,
        'can_contact': request.user.is_authenticated and request.user != dealer.user,
    }
    return render(request, 'accounts/dealer_detail.html', context)

@login_required
@require_http_methods(["POST"])
def contact_dealer(request, dealer_id):
    """Handle dealer contact form"""
    dealer = get_object_or_404(DealerProfile, id=dealer_id, verification_status='verified')
    
    if request.user == dealer.user:
        return JsonResponse({'success': False, 'error': 'You cannot contact yourself.'})
    
    form = DealerInquiryForm(request.POST)
    if form.is_valid():
        inquiry = form.save(commit=False)
        inquiry.dealer = dealer
        inquiry.user = request.user
        inquiry.save()
        
        messages.success(request, 'Your inquiry has been sent to the dealer.')
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})

@login_required
def rate_dealer(request, dealer_id):
    """Rate a dealer"""
    dealer = get_object_or_404(DealerProfile, id=dealer_id, verification_status='verified')
    
    if request.user == dealer.user:
        messages.error(request, 'You cannot rate yourself.')
        return redirect('accounts:dealer_detail', dealer_id=dealer_id)
    
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        review = request.POST.get('review', '')
        
        if rating_value and 1 <= int(rating_value) <= 5:
            rating, created = DealerRating.objects.update_or_create(
                dealer=dealer,
                user=request.user,
                defaults={'rating': rating_value, 'review': review}
            )
            
            # Update dealer's average rating
            avg_rating = dealer.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
            dealer.average_rating = round(avg_rating, 2)
            dealer.total_ratings = dealer.ratings.count()
            dealer.save()
            
            action = 'updated' if not created else 'submitted'
            messages.success(request, f'Your rating has been {action}!')
        else:
            messages.error(request, 'Invalid rating value.')
    
    return redirect('accounts:dealer_detail', dealer_id=dealer_id)

def logout_view(request):
    """Logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home:home')

def price_comparison(request):
    """Compare prices across dealers for specific materials"""
    material_id = request.GET.get('material')
    grade = request.GET.get('grade', 'A')
    
    context = {
        'categories': ScrapCategory.objects.filter(is_active=True).prefetch_related('materials'),
        'selected_material': material_id,
        'selected_grade': grade,
        'grades': ScrapMaterial.QUALITY_GRADES,
    }
    
    if material_id:
        material = get_object_or_404(ScrapMaterial, id=material_id)
        prices = DealerPrice.objects.filter(
            material=material,
            quality_grade=grade,
            is_active=True,
            dealer__verification_status='verified'
        ).select_related('dealer__user').order_by('-price_per_unit')
        
        context.update({
            'material': material,
            'prices': prices,
        })
    
    return render(request, 'accounts/price_comparison.html', context)