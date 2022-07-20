from django.shortcuts import render, redirect
import requests
from bs4 import BeautifulSoup
from .forms import RouteForm
from .models import Route


# Create your views here.
def home(request):
    

    return render(request, 'home.html')

def setting(request):
    return render(request, 'setting.html')


def detail(request):
    
    if request.method == 'POST': # POST 요청
        rt = Route()
        rt.start = request.POST['start']
        rt.fin = request.POST['fin']
        rt.save()
            
        return render(request, 'detail.html')
    else: #GET 요청
        form = RouteForm()    
    
    return redirect('home')

def favorite(request):
    return render(request, 'favorite.html')