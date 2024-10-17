from django.shortcuts import render,redirect
from .models import user_collection
from django.http import HttpResponse
from . import views
from django.contrib import messages
from db_connection import db 
user_collection = db['cred']
import gridfs
import base64
from .forms import ProductForm

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = user_collection.find_one({"name": username, "password": password})
        
        if user: 
            request.session['username'] = username
            return redirect('profile', username=username)
        else:
            messages.error(request, "Invalid username or password") 

    return render(request, 'login.html')

def logout(request):
    if request.method == 'POST':
        
        request.session.flush()

        messages.success(request, "You have been logged out successfully.")

        return redirect('home')  

    return redirect('home')

def profile(request, username):
    if 'username' not in request.session or request.session['username'] != username:
        return redirect('login')

    return render(request, 'profile.html', {'username': username})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_collection.insert_one({
            "name": username,
            "password": password
        })

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'register.html')

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            quantity = form.cleaned_data['quantity']
            product_image = form.cleaned_data['product_image']

            fs = gridfs.GridFS(db)

            image_id = fs.put(product_image, filename=product_image.name)

            product_data = {
                'name': name,
                'price': float(price),
                'quantity': int(quantity),
                'image_id': image_id
            }
            db.product_details.insert_one(product_data)

            return redirect('home')
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})

def home_new(request):
    fs = gridfs.GridFS(db)

    products = db.product_details.find()
    product_list = []

    for product in products:
        image_id = product['image_id']
        image_data = fs.get(image_id).read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')

        product_list.append({
            'name': product['name'],
            'price': product['price'],
            'quantity': product['quantity'],
            'image_data': encoded_image
        })

    return render(request, 'product.html', {'products': product_list})

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def services(request):
    return render(request, 'services.html')

def ecom(request):
    return render(request, 'ecom.html')
