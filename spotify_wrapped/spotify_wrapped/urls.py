"""
URL configuration for spotify_wrapped project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from core import views  # Import views from core



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Your app's URLs
    path('', include('django.contrib.auth.urls')),  # Django's built-in auth URLs
    path('callback/', views.spotify_callback, name='callback'),  # Add this route for the callback
    path('summary/', views.show_summary, name='show_summary'),  # Add this for the summary page
    path('', include('core.urls')),  # Correct path to core.urls
]
