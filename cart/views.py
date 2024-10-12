from django.shortcuts import render,redirect
# from .forms import RegistrationForm
# from .models import user_collection
from .models import user_collection
from django.http import HttpResponse

from . import views
# Create your views here.
def home(request):
    return render(request,'home.html')
def login(request):
    # if request.method == 'POST':
    #     form = AuthenticationForm(request, data=request.POST)
    #     if form.is_valid():
    #         username = form.cleaned_data.get('username')
    #         password = form.cleaned_data.get('password')
    #         user = authenticate(username=username, password=password)
    #         if user is not None:
    #             login(request, user)
    #             return redirect('home')  # Redirect to homepage or another page
    # else:
    #     form = AuthenticationForm()
    # return render(request, 'login.html', {'form': form})
    return render(request,'login.html')

# from django.shortcuts import render, redirect
# from .forms import RegistrationForm
# from .models import User
# from django.contrib.auth.hashers import make_password

# def register(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.password = make_password(user.password)  # Hash the password
#             user.save()  # Save the user to MongoDB
#             return redirect('login')  # Redirect to the login page after saving
#     else:
#         form = RegistrationForm()
    
#     return render(request, 'register.html', {'form': form})
def add_person(request):
    records={
        "firstname":"Talib",
        "lastname":"Mir"
    }
    user_collection.insert_one(records)
    return HttpResponse("New Person is added")


def register(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Save the user data in MongoDB
        user_data = {
            'username': username,
            'email': email,
            'password': password  # Save as plain text for now; use hashing for security later
        }
        user_collection.insert_one(user_data)

        return render(request, 'register.html', {'message': 'User registered successfully!'})

    return render(request, 'register.html')