from django.contrib import admin
from django.urls import path, include
from myapp.views import login_view, register_view, logout_view, root_redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # root URL redirects to dashboard/login based on role
    path('', root_redirect, name='root_redirect'),

    # authentication
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # include your myapp URLs if you have app-level routing
    path('', include('myapp.urls')),  
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)








