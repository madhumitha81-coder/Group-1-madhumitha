from django.contrib import admin
from django.urls import path, include
from myapp.views import login_view, register_view, logout_view, root_redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Role-based redirect after login
    path('redirect/', root_redirect, name='root_redirect'),

    # App URLs (catch-all)
    path('', include('myapp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
