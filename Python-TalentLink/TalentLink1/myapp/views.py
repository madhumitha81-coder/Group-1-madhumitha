from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions



# Import models
from .models import Project, Proposal, Contract, Message, Review, Profile, Skill

# Import serializers
from .serializers import ProjectSerializer, ProposalSerializer, ContractSerializer, MessageSerializer, ReviewSerializer

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User
from django.contrib import messages
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import viewsets, permissions
from .models import Project
from .serializers import ProjectSerializer
from .permissions import IsClientOwner
# Root redirect
def root_redirect(request):
    return redirect('login')

# Login
# myapp/views.py


# ---------------- REGISTER ----------------
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # 🔑 MAKE USER ADMIN
        user.is_staff = True
        user.is_superuser = True   # FULL ADMIN
        user.save()

        return redirect('login')

    return render(request, 'register.html')



# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("/admin/")  # ✅ Django admin
        else:
            messages.error(request, "Invalid credentials")
            return redirect("login")

    return render(request, "login.html")


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect("login")





# ---------------- API Viewsets ----------------




class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Project.objects.all()

    filter_backends = [DjangoFilterBackend, SearchFilter]

    # Filter fields
    filterset_fields = ['budget', 'duration']

    # Search by skill
    search_fields = ['skills_required', 'title']

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
