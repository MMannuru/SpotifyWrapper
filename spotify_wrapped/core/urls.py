from django.urls import path
from . import views
from django.urls import path
from django.contrib.auth.views import LoginView  # Import LoginView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('register/', views.register, name='register'),  # custom registration view
    # You can add other app-specific routes here
]
