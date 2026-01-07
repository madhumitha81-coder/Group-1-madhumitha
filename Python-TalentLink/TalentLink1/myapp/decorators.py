from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def client_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.profile.role != 'client':
            return redirect('freelancer_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def freelancer_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.profile.role != 'freelancer':
            return redirect('client_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
