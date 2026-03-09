from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Product, Staff
from .serializers import ProductSerializer

# ==========================================
# 🌐 WEB ADMIN BROWSER VIEWS (HTML + CSS UI)
# ==========================================

def admin_login(request):
    """Admin/Staff Login Page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    error = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        if user is not None and (user.is_superuser or user.is_staff):  # Admins and Staff can access
            auth_login(request, user)
            return redirect('dashboard')
        else:
            error = "Invalid Credentials or no Admin/Staff access!"
            
    return render(request, 'login.html', {'error': error})

def admin_logout(request):
    """Logs out the super admin"""
    auth_logout(request)
    return redirect('admin_login')

@login_required(login_url='admin_login')
def dashboard(request):
    """Admin Dashboard showing all products"""
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'dashboard.html', {'products': products})

@login_required(login_url='admin_login')
def add_product(request):
    """Add a new product from the web UI"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        
        Product.objects.create(name=name, description=description, price=price, image=image)
        messages.success(request, 'Product added successfully!')
        return redirect('dashboard')
        
    return render(request, 'product_form.html', {'title': 'Add Product'})

@login_required(login_url='admin_login')
def edit_product(request, id):
    """Edit an existing product from the web UI"""
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        
        if 'image' in request.FILES:
            product.image = request.FILES.get('image')
            
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('dashboard')
        
    return render(request, 'product_form.html', {'title': 'Edit Product', 'product': product})

@login_required(login_url='admin_login')
def delete_product(request, id):
    """Delete a product from the web UI"""
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
    return redirect('dashboard')


# ==========================================
# � STAFF MANAGEMENT VIEWS (SUPER ADMIN ONLY)
# ==========================================

@login_required(login_url='admin_login')
def staff_list(request):
    """List all staffs (Super Admin only)"""
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Super Admin only!")
        return redirect('dashboard')
        
    staffs = Staff.objects.all().order_by('-id')
    return render(request, 'staff_list.html', {'staffs': staffs})

@login_required(login_url='admin_login')
def add_staff(request):
    """Add a new staff (Super Admin only)"""
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Super Admin only!")
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('add_staff')
            
        # Create User
        user = User.objects.create_user(username=username, password=password)
        
        if role == 'Admin':
            user.is_superuser = True
            user.is_staff = True
        else:
            user.is_superuser = False
            user.is_staff = True
        user.save()
        
        # Create Staff
        Staff.objects.create(user=user, role=role)
        
        messages.success(request, 'Staff added successfully!')
        return redirect('staff_list')
        
    return render(request, 'staff_form.html', {'title': 'Add Staff'})

@login_required(login_url='admin_login')
def delete_staff(request, id):
    """Delete a staff (Super Admin only)"""
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Super Admin only!")
        return redirect('dashboard')
        
    staff = get_object_or_404(Staff, id=id)
    if request.method == 'POST':
        user = staff.user
        staff.delete()
        user.delete() # Also delete the Django User
        messages.success(request, 'Staff deleted successfully!')
    return redirect('staff_list')


# ==========================================
# �📱 API VIEWS FOR FLUTTER APP (JSON)
# ==========================================

@api_view(['GET', 'POST'])
def api_products(request):
    """Get all products or create a new one (Flutter API)"""
    if request.method == 'GET':
        products = Product.objects.all().order_by('-created_at')
        serializer = ProductSerializer(products, context={'request': request}, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def api_product_detail(request, id):
    """Get, update, or delete a specific product (Flutter API)"""
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET':
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
