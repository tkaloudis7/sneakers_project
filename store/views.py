from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Sneaker
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
    #if the user clicked submit
    if request.method == 'POST':
        #authenticationForm
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user) #login of the user
            return redirect('/') #homepage redirection

    #visitors only
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})



def home(request):
    query = request.GET.get('q')

    #checking if keyword exists
    if query:
        all_sneakers = Sneaker.objects.filter(
            Q(brand__icontains=query) | Q(name__icontains=query)
        )
    else:
        all_sneakers = Sneaker.objects.all()

    context = {'sneakers': all_sneakers}
    return render(request, 'store/home.html', context)

def logout_view(request):
    logout(request)
    return redirect('/')


# profile view (only for users)
@login_required(login_url='/login/')
def profile_view(request):
    return render(request, 'profile.html')