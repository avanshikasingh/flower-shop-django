from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Profile, Wishlist
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart
from django.contrib.auth.decorators import login_required

#My views
#-----------------------------------------------------------------------------------------------------------

#Home page
#------------------------------------------------------------------------------
def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products':products})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product
from .forms import ReviewForm

# Product view page
# ------------------------------------------------------------------------------
def product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get all reviews for this product
    reviews = product.reviews.all().order_by('-created_at')

    # Review form (only for logged in users)
    form = None
    if request.user.is_authenticated:
        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, "Your review has been submitted!")
                return redirect('product', product_id=product.id)
        else:
            form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
        'average_rating': product.average_rating(),  # method in Product model
    }

    return render(request, 'shop/product.html', context)

	
#Category page
#------------------------------------------------------------------------------
def category(request, foo):
    foo = foo.replace('-', ' ')   #Replace hyphens with spaces
    try: 
        #Look up the category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'shop/category.html', {'products':products, 'category':category})
    except:
        messages.success(request, ("That Category doesn't exists....."))
        return redirect('home')

#login page
#------------------------------------------------------------------------------
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)

            #Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            #get their saved art from database
            saved_cart = current_user.old_cart
            #convert database string to python dictionary
            if saved_cart:
                #convert to dictionary using json
                converted_cart = json.loads(saved_cart)
                #add the loaded cart dictionary and get the cart
                cart = Cart(request)
                #loop through the cart and items from DB
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, ("You have been logged in........"))
            return redirect('home')
        else:
            messages.success(request, ("There is an error....."))
            return redirect('home')
    
    else:
        return render(request, 'shop/login.html', )


#logout page
#------------------------------------------------------------------------------
def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out ............"))
    return redirect('home')


#register page
#------------------------------------------------------------------------------
def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            password_confirm = form.cleaned_data['password2']

            #log in user
            user = authenticate(username=username, password=password)
            login(request,user)
            messages.success(request, ("You have register successfully..."))
            return redirect('update_info')
        else:
            messages.success(request, ("Ooops!! There is an problem, Try again later..."))
            return redirect('register')
    else:
        return render(request, 'shop/register.html', {'form':form})


#Update_user page
#------------------------------------------------------------------------------
def update_user(request):
    if request.user.is_authenticated:
        current_users = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_users)

        if user_form.is_valid():
            user_form.save()

            login(request, current_users)
            messages.success(request, "User Has Been updated!!!")
            return redirect('home')
        return render(request, "shop/update_user.html",{'user_form':user_form})
    else:
        messages.success(request, "You must be logged in to access that page!")
        return redirect('home')
    
#Update password page
#------------------------------------------------------------------------------
def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user

        #did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            #Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password has been updated, please login again..... ")
                #login(request, current_user)
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')

        else:
            form = ChangePasswordForm(current_user)
            return render(request, "shop/update_password.html", {'form':form})
        
    else:
        messages.success(request, "You must be logged in to view that page!")
        return redirect('home')
    

#Update information
#------------------------------------------------------------------------------
def update_info(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access that page!")
        return redirect('home')

    #  Correct objects
    current_user = request.user
    current_profile = get_object_or_404(Profile, user=current_user)

    # Bind forms to the right instances
    user_form = UpdateUserForm(request.POST or None, instance=current_user)
    profile_form = UserInfoForm(request.POST or None, instance=current_profile)

    #  Validate BOTH forms together
    if request.method == 'POST':
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()       
            profile_form.save()
            messages.success(request, "Your info has been updated!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")

    return render(
        request,
        "shop/update_info.html",
        {"form": user_form, "shipping_form": profile_form}  # keep your template keys if used
    )

#product search
#------------------------------------------------------------------------------
def search_results(request):
    query = request.GET.get("q", "").strip()  # get query from URL
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        products = Product.objects.all()
    
    return render(
        request,
        "shop/search_results.html",
        {"products": products, "query": query},
    )


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related("product")
    return render(request, "shop/wishlist.html", {"wishlist_items": wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"❤️ {product.name} added to your wishlist.")
    return redirect("wishlist")

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"❌ {product.name} removed from your wishlist.")
    return redirect("wishlist")




