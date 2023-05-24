"""DjangoCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from my_app.views import home, signup, CustomLoginView, logout_view, submit_support_request, support_form,\
    support_request_submitted, ai_insights


urlpatterns = [
    path('', home, name='home'),  # add the URL for the home page
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('my_app/', include('my_app.urls')),
    path('signup/', signup, name='signup'),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('support/', support_form, name='support_form'),
    path('submit-support-request/', submit_support_request, name='submit_support_request'),
    path('support-request-submitted/<int:support_request_id>/', support_request_submitted, name='support_request_submitted'),
    path('ai_insights/', ai_insights, name='ai_insights'),
]

# Serve static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Set the login and logout redirects to the home page
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

