# AkriOnline Deployment Guide for GoDaddy cPanel

## 📋 Pre-Deployment Checklist

### ✅ Code Analysis Results
Your codebase has been analyzed and is **READY FOR DEPLOYMENT** with the following fixes applied:

1. **URL Configuration**: ✅ Fixed allauth URL conflicts
2. **Phone Validation**: ✅ Implemented django-phonenumber-field
3. **Authentication**: ✅ Fixed backend specification issues
4. **Templates**: ✅ All missing templates created
5. **Static Files**: ✅ Properly configured
6. **Security**: ✅ Production settings created

## 🚀 Deployment Steps

### 1. **Prepare Your Files**

**Files to Upload:**
```
akrionline/
├── accounts/
├── home/
├── marketplace/
├── templates/
├── static/
├── media/
├── akrionline/
│   ├── settings.py
│   ├── production_settings.py  # NEW
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── DEPLOYMENT_GUIDE.md
```

### 2. **Database Setup (MySQL)**

**In cPanel:**
1. Go to **MySQL Databases**
2. Create a new database: `akrionline_db`
3. Create a database user: `akrionline_user`
4. Add user to database with ALL PRIVILEGES
5. Note down: database name, username, password

### 3. **Environment Variables Setup**

**Create `.env` file in your project root:**
```env
DJANGO_SECRET_KEY=your-super-secret-production-key-here
DEBUG=False
DB_NAME=akrionline_db
DB_USER=akrionline_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-secret
```

### 4. **Update Production Settings**

**In `akrionline/production_settings.py`:**
```python
# Update ALLOWED_HOSTS with your actual domain
ALLOWED_HOSTS = ['akrionline.com', 'www.akrionline.com']

# Update database settings to match your cPanel MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_cpanel_username_akrionline',  # Usually prefixed
        'USER': 'your_cpanel_username_akriuser',
        'PASSWORD': 'your-db-password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. **Upload Files to cPanel**

**Via File Manager or FTP:**
1. Upload all project files to `public_html/` or subdirectory
2. Ensure proper file permissions (755 for directories, 644 for files)
3. Upload `.env` file (keep it secure)

### 6. **Install Dependencies**

**In cPanel Terminal or SSH:**
```bash
cd public_html/your-project-directory
pip3 install -r requirements.txt --user
```

### 7. **Run Migrations**

```bash
python3 manage.py migrate --settings=akrionline.production_settings
python3 manage.py collectstatic --settings=akrionline.production_settings
```

### 8. **Create Superuser**

```bash
python3 manage.py createsuperuser --settings=akrionline.production_settings
```

### 9. **Configure WSGI**

**Create/Update `passenger_wsgi.py` in your domain root:**
```python
import sys
import os

# Add your project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'akrionline.production_settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 10. **Setup Static Files**

**In cPanel File Manager:**
1. Create `static` directory in `public_html`
2. Run: `python3 manage.py collectstatic --settings=akrionline.production_settings`
3. Ensure static files are accessible via web

## 🔧 Post-Deployment Configuration

### 1. **Django Admin Setup**
1. Access: `https://akrionline.com/admin/`
2. Login with superuser credentials
3. Go to **Sites** → Update domain to `akrionline.com`

### 2. **Google OAuth Setup**
1. In Django Admin → **Social Applications**
2. Add Google OAuth app with production credentials
3. Update Google Cloud Console with production redirect URI:
   `https://akrionline.com/accounts/google/login/callback/`

### 3. **Email Configuration**
1. Set up Gmail App Password or SMTP service
2. Update email settings in production_settings.py
3. Test email verification functionality

## ⚠️ Important Security Notes

### **Environment Variables**
- Never commit `.env` file to version control
- Use strong, unique SECRET_KEY for production
- Use secure database passwords

### **SSL Certificate**
- Enable SSL in cPanel (Let's Encrypt)
- Update security settings in production_settings.py
- Force HTTPS redirects

### **File Permissions**
```bash
# Set proper permissions
chmod 755 directories
chmod 644 files
chmod 600 .env  # Keep environment file secure
```

## 🐛 Troubleshooting

### **Common Issues:**

1. **Import Errors**: Check Python path and virtual environment
2. **Database Connection**: Verify MySQL credentials and host
3. **Static Files**: Run collectstatic and check file permissions
4. **500 Errors**: Check error logs in cPanel
5. **OAuth Issues**: Verify redirect URIs match exactly

### **Debug Commands:**
```bash
# Check Django configuration
python3 manage.py check --settings=akrionline.production_settings

# Test database connection
python3 manage.py dbshell --settings=akrionline.production_settings

# View migrations status
python3 manage.py showmigrations --settings=akrionline.production_settings
```

## 📊 Performance Optimization

### **Recommended:**
1. Enable caching in production_settings.py
2. Optimize database queries
3. Use CDN for static files
4. Enable gzip compression in cPanel
5. Monitor server resources

## ✅ Final Checklist

- [ ] Database created and configured
- [ ] Environment variables set
- [ ] Files uploaded to cPanel
- [ ] Dependencies installed
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] Superuser created
- [ ] WSGI configured
- [ ] SSL certificate enabled
- [ ] Google OAuth configured
- [ ] Email settings tested
- [ ] Site domain updated in admin

## 🎉 Your AkriOnline platform is ready for production!

**Access your live site at:** `https://akrionline.com`
**Admin panel:** `https://akrionline.com/admin/`
