from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Sneaker, Category, Size, Review, Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.db.models import Q

#registration view
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

#login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def home(request):
    all_sneakers = Sneaker.objects.all()
    categories = Category.objects.all()
    all_sizes = Size.objects.all()

    query = request.GET.get('q')
    category_id = request.GET.get('category')
    brand = request.GET.get('brand')
    size_id = request.GET.get('size')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

#filters
    if query:
        all_sneakers = all_sneakers.filter(Q(brand__icontains=query) | Q(name__icontains=query))
    if category_id:
        all_sneakers = all_sneakers.filter(subcategory__category_id=category_id)
    if brand:
        all_sneakers = all_sneakers.filter(brand__icontains=brand)
    if size_id:
        all_sneakers = all_sneakers.filter(sizes__id=size_id)
    if min_price:
        all_sneakers = all_sneakers.filter(price__gte=min_price)
    if max_price:
        all_sneakers = all_sneakers.filter(price__lte=max_price)

    if category_id:
        recommendations = Sneaker.objects.filter(subcategory__category_id=category_id).order_by('?')[:3]
    elif query:
        recommendations = Sneaker.objects.filter(Q(brand__icontains=query) | Q(name__icontains=query)).order_by('?')[:3]
    elif brand:
        recommendations = Sneaker.objects.filter(brand__icontains=brand).order_by('?')[:3]
    else:
        recommendations = Sneaker.objects.order_by('?')[:3]

    user_reviewed_sneakers = []
    if request.user.is_authenticated:
        user_reviewed_sneakers = Review.objects.filter(user=request.user).values_list('sneaker_id', flat=True)

    context = {
        'sneakers': all_sneakers.distinct(),
        'categories': categories,
        'all_sizes': all_sizes,
        'recommendations': recommendations,
        'user_reviewed_sneakers': user_reviewed_sneakers
    }
    return render(request, 'store/home.html', context)

def logout_view(request):
    logout(request)
    return redirect('/')

#profile view
@login_required(login_url='/login/')
def profile_view(request):
    return render(request, 'profile.html')

#product details page
def product_detail(request, sneaker_id):
    sneaker = get_object_or_404(Sneaker, id=sneaker_id)
    has_reviewed = False
    if request.user.is_authenticated:
        has_reviewed = Review.objects.filter(sneaker=sneaker, user=request.user).exists()

    context = {
        'sneaker': sneaker,
        'has_reviewed': has_reviewed
    }
    return render(request, 'store/product_detail.html', context)

#review management
@login_required(login_url='/login/')
def add_review(request, sneaker_id):
    if request.method == "POST":
        comment = request.POST.get('comment')
        rating_str = request.POST.get('rating')

        try:
            rating = int(rating_str)
        except (ValueError, TypeError):
            rating = 5

        has_reviewed = Review.objects.filter(sneaker_id=sneaker_id, user=request.user).exists()
        if comment and not has_reviewed:
            Review.objects.create(
                sneaker_id=sneaker_id,
                user=request.user,
                comment=comment,
                rating=rating
            )
    return redirect('product_detail', sneaker_id=sneaker_id)

@login_required(login_url='/login/')
def delete_review(request, review_id):
    if request.method == "POST":
        review = get_object_or_404(Review, id=review_id)
        sneaker_id = review.sneaker.id
        if request.user == review.user:
            review.delete()
    return redirect('product_detail', sneaker_id=sneaker_id)

#cart
@login_required(login_url='/login/')
def add_to_cart(request, sneaker_id):
    if request.method == "POST":
        sneaker = get_object_or_404(Sneaker, id=sneaker_id)
        selected_size = request.POST.get('size') #get size

        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        #max quantity 10
        if quantity > 10:
            quantity = 10
        elif quantity < 1:
            quantity = 1

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            sneaker=sneaker,
            selected_size=selected_size,
            defaults={'quantity': quantity}
        )

        if not item_created:
            cart_item.quantity += quantity
            if cart_item.quantity > 10:
                cart_item.quantity = 10
            cart_item.save()

    return redirect('cart_view')

@login_required(login_url='/login/')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    total_cart_price = sum(item.total_price for item in cart.items.all())

    context = {
        'cart': cart,
        'total_cart_price': total_cart_price
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='/login/')
def update_cart(request, item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        try:
            new_quantity = int(request.POST.get('quantity'))
        except ValueError:
            new_quantity = 1

        if new_quantity > 10:
            new_quantity = 10
        elif new_quantity < 1:
            new_quantity = 1

        cart_item.quantity = new_quantity
        cart_item.save()
    return redirect('cart_view')

@login_required(login_url='/login/')
def remove_from_cart(request, item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
    return redirect('cart_view')

#checkout simulation
@login_required(login_url='/login/')
def checkout_view(request):
    if request.method == "POST":
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return render(request, 'store/checkout_success.html')
    return redirect('cart_view')