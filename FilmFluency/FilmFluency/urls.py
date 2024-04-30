"""
URL configuration for FilmFluency project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls.conf import include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.sitemaps.views import sitemap
from .sitemaps import MovieSitemap

fav_url=staticfiles_storage.url('favicon.ico').split('?')[0]
robots_url=staticfiles_storage.url('robots.txt').split('?')[0]

sitemaps = {
    'mymodel': MovieSitemap,
}

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('media/', include('learning.urls')),
    path('',include('web.urls')),
    path('users/', include('users.urls')),
    path('api/', include('api.urls')),
    path('payment/', include('payment.urls')),
    path('contact/', include('contact.urls')),
    path('robots.txt', RedirectView.as_view(url=robots_url, permanent=False)),
    path('favicon.ico', RedirectView.as_view(url=fav_url, permanent=False)),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
    
    
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
