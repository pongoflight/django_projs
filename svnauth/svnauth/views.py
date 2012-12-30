from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse

def homepage(request):
    d = '2012-12-30'
    t = get_template('main.html')
    html = t.render(Context({'the_date': d}))
    return HttpResponse(html)

def hello(request):
    return HttpResponse("Hello world~")
