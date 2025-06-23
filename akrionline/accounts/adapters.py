from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_field, user_username
from .models import User

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In case of auto-signup,
        the signup form is not available.
        """
        user = sociallogin.user
        user.set_unusable_password()
        
        # Set user type based on request or default to regular
        user_type = request.session.get('signup_user_type', 'regular')
        user.user_type = user_type
        
        if form:
            user_email(user, form.cleaned_data.get('email'))
            user_username(user, form.cleaned_data.get('username'))
            user_field(user, 'first_name', form.cleaned_data.get('first_name'))
            user_field(user, 'last_name', form.cleaned_data.get('last_name'))
        else:
            # Extract from social account data
            extra_data = sociallogin.account.extra_data
            user_email(user, extra_data.get('email'))
            
            # Try to extract name from Google data
            if 'given_name' in extra_data:
                user_field(user, 'first_name', extra_data.get('given_name'))
            if 'family_name' in extra_data:
                user_field(user, 'last_name', extra_data.get('family_name'))
                
            # Generate username if not set
            if not user.username:
                base_username = extra_data.get('email', '').split('@')[0]
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                user_username(user, username)
        
        user.save()
        return user

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed.
        """
        # If user is already connected to the social account, just continue
        if sociallogin.is_existing:
            return

        # Try to connect social account to existing user account
        try:
            email = sociallogin.account.extra_data.get('email')
            if email:
                existing_user = User.objects.get(email=email)
                sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass