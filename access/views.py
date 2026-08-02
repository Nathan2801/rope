from django.http import HttpResponse
from django.template import loader

def index(request):
    context = {'name': 'Robien'}
    template = loader.get_template('access/index.html')
    return HttpResponse(template.render(context, request))
