"""
URL configuration for boilerplate project.

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
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path

from learning.frontend_views import serve_frontend_config, serve_frontend_page

urlpatterns = [
    # Frontend runtime config (reads API_BASE_URL etc. from .env).
    path('config.js', serve_frontend_config, name='frontend-config'),
    # Frontend web app (session-cookie client for the JSON API).
    path('', serve_frontend_page, {'page': ''}, name='frontend-home'),
    path('login/', serve_frontend_page, {'page': 'login'}, name='frontend-login'),
    path('notes/', serve_frontend_page, {'page': 'notes'}, name='frontend-notes'),
    path('panel/', serve_frontend_page, {'page': 'panel'}, name='frontend-panel'),
    path('account/', serve_frontend_page, {'page': 'account'}, name='frontend-account'),
    path('logout/', serve_frontend_page, {'page': 'logout'}, name='frontend-logout'),
    # Django admin site routes.
    path('admin/', admin.site.urls),
    path('schema-viewer/', include('schema_viewer.urls')),
    # Learning app API endpoints.
    path('api/', include('learning.urls')),
] + debug_toolbar_urls()
