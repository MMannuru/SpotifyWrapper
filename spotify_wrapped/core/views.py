from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

def login_view(request):
    return render(request, 'login.html')


