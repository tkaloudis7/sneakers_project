from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from .models import Sneaker

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
    #fetch all sneakers from the database
    all_sneakers = Sneaker.objects.all()

    #pass the data to the template context
    context = {'sneakers': all_sneakers}
    return render(request, 'store/home.html', context)