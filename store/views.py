from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Sneaker, Category, Size, Review
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

    #parameters
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

    #recommendations
    if category_id:
        recommendations = Sneaker.objects.filter(subcategory__category_id=category_id).order_by('?')[:3]
    elif query:
        recommendations = Sneaker.objects.filter(Q(brand__icontains=query) | Q(name__icontains=query)).order_by('?')[:3]
    elif brand:
        recommendations = Sneaker.objects.filter(brand__icontains=brand).order_by('?')[:3]
    else:
        recommendations = Sneaker.objects.order_by('?')[:3]

    #reviews of the user
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


# profile view (only for users)
@login_required(login_url='/login/')
def profile_view(request):
    return render(request, 'profile.html')


#reviews saving
@login_required(login_url='/login/')
def add_review(request, sneaker_id):
    if request.method == "POST":
        comment = request.POST.get('comment')
        rating_str = request.POST.get('rating')

        try:
            rating = int(rating_str)
        except (ValueError, TypeError):
            rating = 5

        #checking if the user has already reviewed the product
        has_reviewed = Review.objects.filter(sneaker_id=sneaker_id, user=request.user).exists()

        if comment and not has_reviewed:
            Review.objects.create(
                sneaker_id=sneaker_id,
                user=request.user,
                comment=comment,
                rating=rating
            )
    return redirect('/')

#delete review
@login_required(login_url='/login/')
def delete_review(request, review_id):
    if request.method == "POST":
        review = get_object_or_404(Review, id=review_id)
        if request.user == review.user:
            review.delete()
    return redirect('/')