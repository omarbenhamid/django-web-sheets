"""demo_websheets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from tests.demo.views import BookResource, MySheetView
from websheets.views import WebSheetView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test1/', MySheetView.as_view()),
    path('test2/', WebSheetView.as_view(resource_class=BookResource)),
]
