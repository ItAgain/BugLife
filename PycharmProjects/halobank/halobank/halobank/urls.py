"""
URL configuration for halobank project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name='index'),
    path('key_rate/', views.key_rate_view, name='key_rate'),
    path('metals_rate/', views.metals_rate_view, name='metals_rate'),
    path('currency_rate/', views.currency_rate_view, name='currency_rate'),
    path('card/<int:id>', views.SingleCardOperation.as_view()),
    path('card/', views.CardOperation.as_view()),
]
