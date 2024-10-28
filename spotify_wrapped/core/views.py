from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib.auth.views import LoginView  # Import LoginView
from . import views

def index(request):
    return render(request, 'core/index.html')

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful registration
    else:
        form = UserCreationForm()

    return render(request, 'core/register.html', {'form': form})

