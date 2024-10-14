from django.shortcuts import render,redirect
from .models import user_collection
from django.http import HttpResponse
from . import views
from django.contrib import messages
from db_connection import db 

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = user_collection.find_one({"username": username, "password": password})
        
        if user: 
            return redirect('profile', username=username)
        else:
            messages.error(request, "Invalid username or password") 

    return render(request, 'login.html')

def logout(request):

    request.session.flush()
    return redirect('home')  

def profile(request, username=None):
    username = request.session.get('username', 'Guest')
    return render(request, 'profile.html', {'username': username})

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
    
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user_data = {
            'username': username,
            'email': email,
            'password': password  
        }
        user_collection.insert_one(user_data)

        return render(request, 'login.html')

    return render(request, 'register.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def services(request):
    return render(request, 'services.html')

def ecom(request):
    
    return render(request, 'ecom.html')
