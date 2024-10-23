from django.shortcuts import render,redirect
from .models import user_collection
from django.http import HttpResponse
from . import views
from django.contrib import messages
from db_connection import db 
user_collection = db['user_data']
import gridfs
import base64
from .forms import ProductForm
from base64 import b64encode
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from db_connection import get_db 
from pymongo import MongoClient
from bson.objectid import ObjectId  
client = MongoClient('mongodb://localhost:27017/')
db = client['ecom_website']  
cart_collection = db['addtocart']
products_collection = db['product_details'] 
db = get_db()

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

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = user_collection.find_one({"name": username, "password": password})
        if user: 
            request.session['username'] = username  
            request.session['user_id'] = str(user['_id'])  
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
            'image_data': encoded_image,
            'product_id': str(product['_id'])
        })
    return render(request, 'product.html', {'products': product_list})

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        image_id = request.POST.get('image_id')
        if not product_id:
            print("NO product ID")
            return JsonResponse({'message': 'Product ID is required'}, status=400)
        user_id = request.session.get('user_id') 
        if not user_id:
            return JsonResponse({'message': 'You need to be logged in to add items to your cart.'}, status=401)
        cart_item = {
            'product_id': product_id,
            'quantity': quantity,
            'user_id': user_id,
        }
        cart_collection.insert_one(cart_item)
        print("Product added successfully")
        return redirect('checkout') 
    return JsonResponse({'message': 'Invalid request method'}, status=400)

@csrf_exempt
def remove_from_cart(request, product_id):
    user_id = request.user.id
    cart_collection.delete_one({'product_id': product_id, 'user_id': user_id})
    return JsonResponse({'message': 'Product removed from cart!'})

def view_cart(request):
    user_id = request.user.id
    cart_items = list(cart_collection.find({'user_id': user_id}))
    products_collection = db['product_details'] 
    for item in cart_items:
        product = products_collection.find_one({'_id': item['product_id']})
        if product:
            item['name'] = product['name']
            item['price'] = product['price']
            item['image_data'] = product['image_data']
    return render(request, 'cart.html', {'cart_items': cart_items})

def checkout(request):
    user_id = "67113ab2a42d802e3d319ae8"  
    cart_items_cursor = cart_collection.find({'user_id': user_id})
    cart_items = list(cart_items_cursor)
    total_price = 0
    for item in cart_items:
        try:
            product_id = ObjectId(item['product_id'])
            product = products_collection.find_one({'_id': product_id})  
            if product:
                image_data = b64encode(product['image_id']).decode('utf-8')
                item['name'] = product['name']
                item['price'] = product['price']
                item['total'] = product['price'] * item['quantity']  
                item['image_id'] = product['image_data']  
                total_price += item['total']
            else:
                print(f"Product not found for ID: {item['product_id']}")  
        except Exception as e:
            print(f"Error retrieving product for item {item}: {e}")  
    print("Final cart items:", cart_items)
    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})

@csrf_exempt
def complete_order(request):
    if request.method == 'POST':
        user_id = request.user.id
        cart_items = list(cart_collection.find({'user_id': user_id}))
        orders_collection = db['orders']
        order = {
            'user_id': user_id,
            'items': cart_items,
            'total_price': sum(item['quantity'] * item['price'] for item in cart_items),
            'status': 'Pending'
        }
        orders_collection.insert_one(order)
        cart_collection.delete_many({'user_id': user_id})
        return JsonResponse({'message': 'Order completed successfully!'})
    


