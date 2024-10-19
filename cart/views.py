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

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from db_connection import get_db  # Import the database connection

# Access the MongoDB collection
db = get_db()
cart_collection = db['addtocart']

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart_item = {
            'product_id': product_id,
            'quantity': quantity,
            'user_id': request.user.id  # Assuming you have user authentication
        }
        
        cart_collection.insert_one(cart_item)
        
        return JsonResponse({'message': 'Product added to cart!'})

def view_cart(request):
    user_id = request.user.id
    cart_items = list(cart_collection.find({'user_id': user_id}))
    
    return render(request, 'cart.html', {'cart_items': cart_items})

@csrf_exempt
def remove_from_cart(request, product_id):
    user_id = request.user.id
    cart_collection.delete_one({'product_id': product_id, 'user_id': user_id})
    
    return JsonResponse({'message': 'Product removed from cart!'})

from django.shortcuts import render
from django.http import JsonResponse
from db_connection import get_db  # Import the database connection

# Access the MongoDB collection
db = get_db()
cart_collection = db['addtocart']

def view_cart(request):
    # Assuming you have user authentication set up
    user_id = request.user.id
    cart_items = list(cart_collection.find({'user_id': user_id}))

    # If you have a products collection, fetch product details for each item in the cart
    products_collection = db['products']  # Ensure this matches your collection name
    for item in cart_items:
        product = products_collection.find_one({'_id': item['product_id']})
        if product:
            item['name'] = product['name']
            item['price'] = product['price']
            item['image_data'] = product['image_data']

    return render(request, 'cart.html', {'cart_items': cart_items})

def checkout(request):
    user_id = request.user.id
    cart_items = list(cart_collection.find({'user_id': user_id}))

    # If you have a products collection, fetch product details for each item in the cart
    products_collection = db['products']  # Make sure this matches your collection name
    total_price = 0
    for item in cart_items:
        product = products_collection.find_one({'_id': item['product_id']})
        if product:
            item['name'] = product['name']
            item['price'] = product['price']
            item['image_data'] = product['image_data']
            item['total'] = item['price'] * item['quantity']
            total_price += item['total']

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})

@csrf_exempt
def complete_order(request):
    if request.method == 'POST':
        user_id = request.user.id
        cart_items = list(cart_collection.find({'user_id': user_id}))
        
        # Process the order (e.g., save to orders collection, clear the cart)
        orders_collection = db['orders']
        order = {
            'user_id': user_id,
            'items': cart_items,
            'total_price': sum(item['quantity'] * item['price'] for item in cart_items),
            'status': 'Pending'
        }
        orders_collection.insert_one(order)

        # Clear the user's cart after completing the order
        cart_collection.delete_many({'user_id': user_id})

        return JsonResponse({'message': 'Order completed successfully!'})
    
def view_cart(request):
    user_id = request.user.id
    cart_items = list(cart_collection.find({'user_id': user_id}))
    return render(request, 'cart.html', {'cart_items': cart_items})


