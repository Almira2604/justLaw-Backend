"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from justlaw.views import (
    login, 
    signup, 
    book_list_create, 
    book_detail, 
    cart_list_create, 
    cart_detail
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', login),
    path('api/signup/', signup),
    path('api/books/', book_list_create),
    path('api/books/<int:id>/', book_detail),
    path('api/cart/', cart_list_create),
    path('api/cart/<int:id>/', cart_detail),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)