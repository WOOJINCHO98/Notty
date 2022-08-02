"""Notty URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import NottyApp.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',NottyApp.views.home, name='home'),
    path('setting/',NottyApp.views.setting, name='setting'),
    path('detail/',NottyApp.views.detail, name='detail'),
    path('favorite/',NottyApp.views.favorite, name='favorite'),
    path('sht_path/' ,NottyApp.views.sht_path, name='sht_path'),
    path('min_path/' ,NottyApp.views.min_path, name='min_path'),

]
