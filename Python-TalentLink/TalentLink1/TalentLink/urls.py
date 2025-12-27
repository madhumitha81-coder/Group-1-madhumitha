from django.contrib import admin
from django.urls import path, include
from myapp.views import login_view, register_view, logout_view, root_redirect

urlpatterns = [
    path('', root_redirect, name='root'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),  # 👈 IMPORTANT
    path('api-auth/', include('rest_framework.urls')),  # ✅ ADD THIS


]
