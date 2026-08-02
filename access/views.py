from django.http import HttpResponse
from django.template import loader

HARDCODE_USERS = [
    ('foo', 'bar'),
    ('bar', 'baz'),
]

def index(request):
    context = {'name': 'Robien'}
    template = loader.get_template('access/index.html')
    return HttpResponse(template.render(context, request))

def enter(request):
    username = request.POST['username']
    password = request.POST['password']

    for (it_username, it_password) in HARDCODE_USERS:
        if it_username == username and it_password == password:
            return HttpResponse(200)
    return HttpResponse(400)
