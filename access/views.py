from django.http import HttpResponse
from django.shortcuts import redirect, render

HARDCODE_USERS = [
    ('foo', 'bar'),
    ('bar', 'baz'),
]

def access_error_description(error_name):
    if error_name == 'invalid':
        return 'Invalid username or password'
    return ''

def index(request):
    error_name = request.GET.get('error', '')
    error_desc = access_error_description(error_name)

    context = {'error': error_desc}
    return render(request, "access/index.html", context)

def enter(request):
    username = request.POST['username']
    password = request.POST['password']

    for (it_username, it_password) in HARDCODE_USERS:
        if it_username == username and it_password == password:
            return HttpResponse(200)

    return redirect(f'/access?error=invalid')
