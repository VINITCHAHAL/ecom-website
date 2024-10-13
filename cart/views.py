from django.shortcuts import render,redirect
from .models import user_collection
from django.http import HttpResponse
from . import views
from bson.objectid import ObjectId 

def home(request):
    return render(request,'home.html')
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = user_collection.find_one({"username": username, "password": password})
        
        if user: 
            return redirect('profile', username=username)  
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})

    return render(request, 'login.html')

def add_person(request):
    records={
        "firstname":"Talib",
        "lastname":"Mir"
    }
    user_collection.insert_one(records)
    return HttpResponse("New Person is added")


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

        return render(request, 'register.html', {'message': 'User registered successfully!'})

    return render(request, 'register.html')
def profile(request, username):
    user = user_collection.find_one({"username": username})
    if user:
        return render(request, 'profile.html', {'username': user['username']})
    else:
        return HttpResponse("User not found.")
def logout(request):
    request.session.flush()  
    return redirect('login')  