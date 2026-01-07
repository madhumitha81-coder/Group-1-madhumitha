from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden

from .models import Profile, Project, Proposal, Contract, Message
from .forms import ProjectForm
from .decorators import client_required, freelancer_required

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import ProjectSerializer, ProposalSerializer

# ---------------- REGISTER ----------------
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")  # client / freelancer

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        # Create user
        user = User.objects.create_user(username=username, password=password)
        profile = user.profile
        profile.role = role if role in ['client', 'freelancer'] else 'client'
        profile.save()

        messages.success(request, "Registered successfully")
        return redirect("login")
    return render(request, "register.html")


# ---------------- LOGIN / LOGOUT ----------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('root')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------- ROOT REDIRECT ----------------
@login_required
def root_redirect(request):
    role = request.user.profile.role
    if role == 'client':
        return redirect('client_dashboard')
    return redirect('freelancer_dashboard')


# ---------------- DASHBOARDS ----------------
@client_required
def client_dashboard(request):
    profile = request.user.profile
    projects = request.user.project_set.all()  # all projects by this client
    contracts = profile.client_contracts.all()  # fetch contracts related to client

    context = {
        'projects': projects,
        'contracts': contracts
    }
    return render(request, 'client_dashboard.html', context)



from django.db.models import Q
from .models import Project, Contract

def freelancer_dashboard(request):
    q = request.GET.get('q', '').strip()

    projects = Project.objects.all()

    if q:
        projects = projects.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(client__username__icontains=q)
        )

    contracts = Contract.objects.filter(freelancer__user=request.user)

    return render(request, "freelancer_dashboard.html", {
        "projects": projects,
        "contracts": contracts
    })



# ---------------- PROJECT DETAIL ----------------
@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    profile = request.user.profile
    is_client = profile.role == "client"

    proposals = Proposal.objects.filter(project=project) if is_client else None
    user_proposal = None
    if not is_client:
        user_proposal = Proposal.objects.filter(project=project, freelancer=profile).first()

    context = {
        "project": project,
        "is_client": is_client,
        "proposals": proposals,
        "user_proposal": user_proposal
    }
    return render(request, "project_detail.html", context)


# ---------------- CREATE / UPDATE PROJECT ----------------
@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            project.save()
            form.save()  # saves M2M fields
            return redirect("client_dashboard")
    else:
        form = ProjectForm()
    return render(request, "create_project.html", {"form": form})


@login_required
def update_project(request, pk):
    project = get_object_or_404(Project, pk=pk, client=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("project_detail", project_id=project.pk)  # ✅ correct
    else:
        form = ProjectForm(instance=project)
    return render(request, "update_project.html", {"form": form, "project": project})


# ---------------- DELETE PROJECT ----------------
@login_required
@client_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Fix: Compare with profile, not user
    
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect('client_dashboard')

    # For GET request, just redirect back
    return redirect('client_dashboard')

# ---------------- PROPOSAL ----------------
@login_required
def submit_proposal(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    freelancer_profile = request.user.profile

    if freelancer_profile.role != "freelancer":
        return redirect('root')

    if request.method == "POST":
        cover_letter = request.POST.get("cover_letter")
        bid_amount = request.POST.get("bid_amount")

        existing = Proposal.objects.filter(project=project, freelancer=freelancer_profile).first()
        if existing:
            existing.cover_letter = cover_letter
            existing.bid_amount = bid_amount
            existing.status = "PENDING"
            existing.save()
        else:
            Proposal.objects.create(
                project=project,
                freelancer=freelancer_profile,
                cover_letter=cover_letter,
                bid_amount=bid_amount,
                status="PENDING"
            )
        return redirect("project_detail", project_id=project.id)

    return render(request, "submit_proposal.html", {"project": project})




def accept_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)

    if request.method == "POST" and request.user == proposal.project.client:
        # Update proposal status
        proposal.status = 'accepted'
        proposal.save()

        # Create a Contract
        Contract.objects.create(
            project=proposal.project,
            proposal=proposal,
            client=proposal.project.client.profile,
            freelancer=proposal.freelancer,
            status='PENDING'
        )

        return redirect('client_dashboard')  # or your dashboard URL

@login_required
def reject_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    if proposal.project.client != request.user:
        return redirect("client_dashboard")
    proposal.status = "REJECTED"
    proposal.save()
    return redirect("project_detail", project_id=proposal.project.pk)


@login_required


# ---------------- ACCEPT / REJECT PROPOSAL ----------------
@login_required
def update_proposal_status(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    project = proposal.project

    if request.user != project.client:
        return redirect('client_dashboard')  # Only client can accept/reject

    if request.method == "POST":
        status = request.POST.get("status").upper()
        proposal.status = status
        proposal.save()

        # If accepted → create contract
        if status == "ACCEPTED":
            Contract.objects.create(
                project=project,
                proposal=proposal,
                client=project.client.profile,
                freelancer=proposal.freelancer,
                status="PENDING"
            )
        return redirect('client_dashboard')


# ---------------- CONTRACT CHAT ----------------

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Contract, Message

@login_required
def contract_chat(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)

    # Use session to track cleared messages per user
    if 'cleared_messages' not in request.session:
        request.session['cleared_messages'] = {}

    cleared = request.session['cleared_messages'].get(str(contract.id), [])

    # Exclude cleared messages
    messages = contract.messages.exclude(id__in=cleared).order_by('timestamp')

    # Handle sending messages
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        uploaded_file = request.FILES.get('file')

        if content or uploaded_file:
            Message.objects.create(
                contract=contract,
                sender=request.user.profile,
                content=content if content else '',
                file=uploaded_file if uploaded_file else None
            )
        return redirect('contract_chat', contract_id=contract.id)

    # Prepare messages for template
    msg_list = []
    for msg in messages:
        # Detect if file is an image
        is_image = False
        if msg.file:
            if msg.file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                is_image = True

        msg_list.append({
            'id': msg.id,
            'sender': msg.sender.user.username,
            'sender_role': msg.sender.role,
            'content': msg.content,
            'timestamp': msg.timestamp,
            'file': msg.file,
            'is_image': is_image
        })

    context = {
        'contract': contract,
        'messages': msg_list
    }
    return render(request, 'contract_chat.html', context)


@login_required
def clear_contract_chat(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)

    # Mark all messages as cleared for this user in session
    if 'cleared_messages' not in request.session:
        request.session['cleared_messages'] = {}

    request.session['cleared_messages'][str(contract.id)] = list(
        contract.messages.values_list('id', flat=True)
    )
    request.session.modified = True

    return redirect('contract_chat', contract_id=contract.id)


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project
from .serializers import ProjectSerializer
from .filters import ProjectFilter

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = ProjectFilter      # ✅ Use custom filterset
    ordering_fields = ['created_at', 'budget', 'deadline']
    ordering = ['-created_at']
    search_fields = ['title', 'description']
