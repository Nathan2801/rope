from django.http import HttpResponse
from django.shortcuts import redirect, render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

HARDCODE_USERS = [
    ('foo', 'bar'),
    ('bar', 'baz'),
]

def access_error_description(errid):
    if errid == 'empty-field':
        return 'There is a empty field'
    if errid == 'unknown-user':
        return 'User not registered'
    return ''

def index(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if username == '' or password == '':
            return redirect('/access?error=empty-field')

        user = authenticate(request, username=username, password=password)
        if user is None:
            return redirect('/access?error=unknown-user')
        else:
            login(request, user)
            return redirect('/')

    errid = request.GET.get('error', '')
    error = access_error_description(errid)

    context = {'error': error}
    return render(request, "access/index.html", context)

def register(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        email = request.POST.get('email', '')
        if email == '':
            return redirect('/access/register?error=empty-field')

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if username == '' or password == '':
            return redirect('/access/register?error=empty-field')

        user = User.objects.create_user(username, email, password)
        return redirect('/')

    errid = request.GET.get('error', '')
    error = access_error_description(errid)

    context = {'error': error}
    return render(request, 'access/register.html', context)

def logoutuser(request):
    logout(request)
    return redirect('/')
