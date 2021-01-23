"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from raykomfi.sitemaps import PostSitemap, StaticViewSitemap
from raykomfi import views
from dotenv import load_dotenv
load_dotenv()
import os
from django.views.generic import RedirectView


import debug_toolbar

sitemaps = {
	"posts": PostSitemap,
    "static": StaticViewSitemap
}

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path(os.getenv("ADMIN_URL"), admin.site.urls),
    path('', include('raykomfi.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('api.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    url('^inbox/notifications/', include('notifications.urls', namespace='notifications')),
    path("robots.txt/", views.robots_txt),
    url(r'^favicon\.ico$',RedirectView.as_view(url='/static/img/favicon.ico')),
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps},
			name='django.contrib.sitemaps.views.sitemap'),
]


urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    
    
