from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Profile, Project, Proposal
from .serializers import ProjectSerializer, ProposalSerializer
from .forms import ProjectForm, LoginForm

# ------------------- AUTHENTICATION ------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated

from .models import Profile, Project, Proposal
from .serializers import ProjectSerializer, ProposalSerializer
from .forms import LoginForm


# ------------------- AUTH -------------------

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile

def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')  # 'client' or 'freelancer'

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        # Create the user
        user = User.objects.create_user(username=username, password=password)

        # Only create Profile if it doesn't exist
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user, role=role)

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')  # Redirect to login page

    return render(request, 'register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('root')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('root')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------- ROOT -------------------

def root_redirect(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'client':
            return redirect('client_dashboard')
        return redirect('freelancer_dashboard')
    return redirect('login')


# ------------------- CLIENT -------------------


   


@login_required
def create_project(request):
    if request.method == 'POST':
        Project.objects.create(
            client=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            budget=request.POST['budget'],
            duration=request.POST['duration'],
            deadline=request.POST['deadline']
        )
        return redirect('client_dashboard')

    return render(request, 'create_project.html')




from django.contrib.auth.decorators import login_required
from .models import Project
from .forms import ProjectForm
from django.contrib import messages

@login_required
def update_project(request, pk):
    # Get the project, ensure only the owner can update
    project = get_object_or_404(Project, pk=pk, client=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            return redirect('client_dashboard')  # Redirect to client dashboard
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project
    }
    return render(request, 'update_project.html', context)


@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, id=pk)

    if request.method == 'POST':
        project.delete()
        return redirect('client_dashboard')

 


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Project, Proposal, Profile

# ---------------- Client Dashboard ----------------

# ---------------- Project Detail ----------------

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Proposal, Profile

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Check if current user is the client
    is_client = request.user == project.client  # <-- fixed

    # Get all proposals if client
    proposals = project.proposals.all() if is_client else None

    # Check if freelancer has already submitted
    has_submitted = False
    if not is_client:
        profile = get_object_or_404(Profile, user=request.user)
        has_submitted = Proposal.objects.filter(project=project, freelancer=profile).exists()

    context = {
        'project': project,
        'is_client': is_client,
        'proposals': proposals,
        'has_submitted': has_submitted,
    }
    return render(request, 'project_detail.html', context)


# ---------------- Accept Proposal ----------------



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Proposal


@login_required
def accept_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)

    # Only project owner can accept
    if proposal.project.client != request.user:
        return redirect('project_detail', proposal.project.pk)

    proposal.status = "ACCEPTED"
    proposal.save()

    return redirect('project_detail', proposal.project.pk)


@login_required
def reject_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)

    # Only project owner can reject
    if proposal.project.client != request.user:
        return redirect('project_detail', proposal.project.pk)

    proposal.status = "REJECTED"
    proposal.save()

    return redirect('project_detail', proposal.project.pk)


from django.utils import timezone

# ---------------- CLIENT DASHBOARD ----------------
@login_required
def client_dashboard(request):
    projects = Project.objects.filter(client=request.user)
    return render(request, "client_dashboard.html", {
        "projects": projects
    })

# ---------------- FREELANCER DASHBOARD ----------------

@login_required
def freelancer_dashboard(request):
    profile = Profile.objects.get(user=request.user)

    projects = Project.objects.all().select_related('client')

    # Attach freelancer's proposal directly to each project
    for project in projects:
        project.user_proposal = Proposal.objects.filter(
            project=project,
            freelancer=profile
        ).first()

    context = {
        'projects': projects
    }
    return render(request, 'freelancer_dashboard.html', context)

# ---------------- SUBMIT PROPOSAL ----------------
@login_required
def submit_proposal(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Ensure the user is a freelancer
    freelancer_profile = get_object_or_404(Profile, user=request.user, role='freelancer')

    # Check if a proposal already exists
    existing_proposal = Proposal.objects.filter(project=project, freelancer=freelancer_profile).first()
    if existing_proposal:
        messages.warning(request, "You have already submitted a proposal for this project.")
        return redirect('freelancer_dashboard')

    if request.method == 'POST':
        bid_amount = request.POST.get('bid_amount')
        cover_letter = request.POST.get('cover_letter', '')

        # Create proposal
        proposal = Proposal.objects.create(
            project=project,
            freelancer=freelancer_profile,
            bid_amount=bid_amount,
            cover_letter=cover_letter,
            status='pending',
            created_at=timezone.now()
        )
        messages.success(request, "Proposal submitted successfully!")
        return redirect('freelancer_dashboard')

    # fallback redirect
    return redirect('freelancer_dashboard')


from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Proposal, Profile

def submit_proposal(request, pk):  # pk from URL
    project = get_object_or_404(Project, id=pk)
    
    if request.method == "POST":
        cover_letter = request.POST.get("cover_letter")
        bid_amount = request.POST.get("bid_amount")

        freelancer_profile = Profile.objects.get(user=request.user)

        Proposal.objects.create(
            project=project,
            freelancer=freelancer_profile,
            cover_letter=cover_letter,
            bid_amount=bid_amount,  # <-- Correct field
            status="PENDING"
        )

        return redirect("freelancer_dashboard")  # Redirect after submission

    return render(request, "submit_proposal.html", {"project": project})


        


# ------------------- ROOT REDIRECT -------------------

def root_redirect(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            if request.user.profile.role == 'client':
                return redirect('client_dashboard')
            else:
                return redirect('freelancer_dashboard')
    return redirect('login')


# ------------------- DRF API VIEWS -------------------
class ProjectListAPIView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]


class ClientProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class ClientProjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(client=self.request.user)


class FreelancerProjectListAPIView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubmitProposalAPIView(generics.CreateAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(freelancer=self.request.user)


class ProposalUpdateAPIView(generics.UpdateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
