from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

HARDCODE_USERS = [
    ('foo', 'bar'),
    ('bar', 'baz'),
]

def access_error_description(errid):
    if errid == 'invalid':
        return 'Invalid username or password'
    return ''

def index(request):
    errid = request.GET.get('error', '')
    error = access_error_description(errid)

    context = {'error': error}
    return render(request, "access/index.html", context)

def enter(request):
    username = request.POST['username']
    password = request.POST['password']

    for (it_username, it_password) in HARDCODE_USERS:
        if it_username == username and it_password == password:
            return redirect('/')

    return redirect(f'/access?error=invalid')

def register(request):
    if request.method == "POST":
        email = request.POST.get('email', '')
        if email == '':
            return redirect('/access/register?error=invalid')

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if username == '' or password == '':
            return redirect('/access/register?error=invalid')

        # user = User.objects.create_user(username, email, password)
        return redirect('/')

    errid = request.GET.get('error', '')
    error = access_error_description(errid)

    context = {'error': error}
    return render(request, 'access/register.html', context)
