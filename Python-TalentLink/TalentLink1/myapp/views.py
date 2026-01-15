from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Profile, Project, Proposal, Contract, Message, Review, Notification
from .forms import ProjectForm, ReviewForm
from .decorators import client_required, freelancer_required
from .serializers import ProjectSerializer, ProposalSerializer
from .filters import ProjectFilter

# ===========================
# PUBLIC
# ===========================

def home_view(request):
    return render(request, "home.html")


# ===========================
# AUTH
# ===========================

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST["role"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.profile.role = role
        user.profile.save()

        messages.success(request, "Registered successfully")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )
        if user:
            login(request, user)
            return redirect("root_redirect")
        messages.error(request, "Invalid credentials")
    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def root_redirect(request):
    if request.user.profile.role == "client":
        return redirect("client_dashboard")
    return redirect("freelancer_dashboard")


# ===========================
# CLIENT DASHBOARD
# ===========================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Project, Proposal, Contract, Notification, Review
from .decorators import client_required

@login_required
@client_required
def client_dashboard(request):
    user = request.user
    profile = user.profile  # Profile instance

    # All projects created by this client
    projects = Project.objects.filter(client=user)

    # All proposals submitted to this client's projects
    proposals = Proposal.objects.filter(project__client=user)

    # All contracts where client is this profile
    contracts = Contract.objects.filter(client=profile).select_related('project', 'freelancer')

    # Notifications
    notifications = Notification.objects.filter(user=user).order_by("-created_at")
    unread_count = notifications.filter(is_read=False).count()

    # Prepare dict of reviews for each contract
    contract_reviews = {}
    for contract in contracts:
        # Filter reviews for this contract by this client
        review = Review.objects.filter(
            project=contract.project,
            reviewer_name=user.username  # Client's username as reviewer
        ).first()
        contract_reviews[contract.id] = review  # None if not reviewed

    context = {
        "projects": projects,
        "proposals": proposals,
        "contracts": contracts,
        "notifications": notifications,
        "unread_count": unread_count,
        "contract_reviews": contract_reviews,
    }

    return render(request, "client_dashboard.html", context)

# ===========================
# FREELANCER DASHBOARD
# ===========================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Project, Contract, Review, Notification

@login_required
def freelancer_dashboard(request):
    user = request.user
    profile = user.profile  # freelancer profile

    # Contracts for this freelancer
    contracts = Contract.objects.filter(freelancer=profile).select_related('project', 'client')

    # Prepare reviews dict
    reviews_by_contract = {}
    for contract in contracts:
        review = Review.objects.filter(
            project=contract.project,
            reviewer_name=contract.client.user.username
        ).first()
        reviews_by_contract[contract.id] = review

    # Fetch all projects
    projects = Project.objects.all()

    # Fetch notifications for this freelancer
    notifications = Notification.objects.filter(user=user).order_by('-created_at')

    # Calculate unread notifications count
    unread_count = notifications.filter(is_read=False).count()

    context = {
        "contracts": contracts,
        "reviews_by_contract": reviews_by_contract,
        "projects": projects,
        "notifications": notifications,
        "unread_count": unread_count,  # <--- Add this
    }

    return render(request, "freelancer_dashboard.html", context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm
from .models import Skill

@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            # 1️⃣ Create project explicitly
            project = Project(
                client=request.user,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                budget=form.cleaned_data.get("budget"),
                deadline=form.cleaned_data.get("deadline"),
                duration=form.cleaned_data.get("duration"),
            )
            project.save()  # 🔥 WILL raise error if DB blocks

            # 2️⃣ Handle skills explicitly
            skills_raw = form.cleaned_data.get("skills_text", "")
            skills_list = [s.strip() for s in skills_raw.split(",") if s.strip()]

            for skill_name in skills_list:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                project.skills_required.add(skill)

            return redirect("client_dashboard")

        else:
            print("FORM ERRORS:", form.errors)

    else:
        form = ProjectForm()

    return render(request, "create_project.html", {"form": form})


def update_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user.profile.role != "client" or project.client != request.user:
        return redirect("freelancer_dashboard" if request.user.profile.role != "client" else "client_dashboard")

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, "update_project.html", {"form": form})


@login_required
@client_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk, client=request.user)
    if request.method == "POST":
        project.delete()
    return redirect("client_dashboard")


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    is_client = request.user.is_authenticated and request.user == project.client
    proposals = project.proposals.all() if is_client else None
    user_proposal = None if is_client else project.proposals.filter(freelancer__user=request.user).first()

    return render(request, "project_detail.html", {
        "project": project,
        "proposals": proposals,
        "is_client": is_client,
        "user_proposal": user_proposal,
    })


# ===========================
# PROPOSALS
# ===========================

@login_required
@freelancer_required
def submit_proposal(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        Proposal.objects.update_or_create(
            project=project,
            freelancer=request.user.profile,
            defaults={
                "cover_letter": request.POST["cover_letter"],
                "bid_amount": request.POST["bid_amount"],
                "status": "PENDING"
            }
        )
        return redirect("project_detail", project_id=project.id)
    return render(request, "submit_proposal.html", {"project": project})


@login_required
def update_proposal_status(request, proposal_id):
    if request.method == "POST":
        proposal = get_object_or_404(Proposal, id=proposal_id)
        new_status = request.POST.get("status")
        if new_status in ["accepted", "rejected"]:
            proposal.status = new_status.upper()
            proposal.save()
            messages.success(request, f"Proposal {new_status} successfully.")
    return redirect("client_dashboard")


@login_required
def accept_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    project = proposal.project
    client_profile = request.user.profile

    if project.client != request.user:
        messages.error(request, "Unauthorized.")
        return redirect('client_dashboard')

    if request.method == 'POST':
        if proposal.status != 'accepted':
            proposal.status = 'accepted'
            proposal.save()
            Proposal.objects.filter(project=project).exclude(id=proposal.id).update(status='rejected')

        Contract.objects.get_or_create(
            proposal=proposal,
            defaults={
                'project': project,
                'client': client_profile,
                'freelancer': proposal.freelancer,
                'status': 'ACTIVE',
            }
        )

        messages.success(request, f"Proposal ACCEPTED. Contract CREATED/EXISTS.")

    return redirect('client_dashboard')


@login_required
def reject_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    project = proposal.project
    if project.client != request.user:
        messages.error(request, "Unauthorized.")
        return redirect('client_dashboard')

    if request.method == 'POST':
        proposal.status = 'rejected'
        proposal.save()
        Notification.objects.create(
            user=proposal.freelancer.user,
            message=f"Your proposal for '{project.title}' has been rejected."
        )
        messages.info(request, "Proposal rejected.")
    return redirect('client_dashboard')


# ===========================
# CONTRACTS
# ===========================

@login_required
@require_POST
def cancel_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.user.profile not in [contract.client, contract.freelancer]:
        return HttpResponseForbidden()
    contract.status = 'CANCELLED'
    contract.save()
    return redirect('client_dashboard')


@login_required
@require_POST
def complete_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.user.profile not in [contract.client, contract.freelancer]:
        return HttpResponseForbidden()
    contract.status = 'COMPLETED'
    contract.save()
    return redirect('client_dashboard')


# ===========================
# CONTRACT CHAT
# ===========================

@login_required
def contract_chat(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    messages = contract.messages.order_by('timestamp')
    return render(request, "contract_chat.html", {"contract": contract, "messages": messages})


@login_required
def clear_chat(request, contract_id):
    if request.method == "POST":
        contract = get_object_or_404(Contract, id=contract_id)
        profile = get_object_or_404(Profile, user=request.user)
        if profile in [contract.client, contract.freelancer]:
            contract.messages.all().delete()
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})


@login_required
def send_message(request):
    if request.method == "POST":
        contract_id = request.POST.get("contract_id")
        contract = get_object_or_404(Contract, id=contract_id)
        sender_profile, _ = Profile.objects.get_or_create(user=request.user)

        content = request.POST.get("content", "").strip()
        file = request.FILES.get("file")

        if not content and not file:
            return JsonResponse({"status": "error", "error": "Empty message"})

        message = Message.objects.create(
            contract=contract,
            sender=sender_profile,
            content=content,
            file=file
        )

        receiver = contract.freelancer.user if request.user == contract.client.user else contract.client.user
        Notification.objects.create(
            user=receiver,
            message=f"New message from {request.user.username} in contract {contract.id}"
        )

        response_data = {
            "status": "success",
            "sender": request.user.username,
            "content": content,
            "timestamp": timezone.localtime(message.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        }

        if file:
            response_data.update({
                "file_url": message.file.url,
                "file_name": message.file.name,
                "is_image": message.is_image,
            })

        return JsonResponse(response_data)

    return JsonResponse({"status": "error", "error": "Invalid request method"})


# ===========================
# NOTIFICATIONS
# ===========================

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "notifications.html", {"notifications": notifications})



from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Notification

@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()

    # Return updated unread count
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"status": "success", "unread_count": unread_count})
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def clear_all_notifications(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user).delete()
        return JsonResponse({"success": True, "unread_count": 0})
    return JsonResponse({"success": False, "error": "Invalid request"})


def get_notifications(request):
    notifs = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by("-created_at")

    data = []
    for n in notifs:
        data.append({
            "id": n.id,
            "message": n.message
        })

    return JsonResponse({"notifications": data})

def get_notifications(request):
    notifs = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by("-created_at")

    data = []
    for n in notifs:
        data.append({
            "id": n.id,
            "message": n.message
        })

    return JsonResponse({"notifications": data})

def read_notification(request, id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Not POST"}, status=400)

    notif = get_object_or_404(Notification, id=id, user=request.user)
    notif.is_read = True
    notif.save()

    return JsonResponse({"success": True, "id": notif.id})
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({"status": "success"})
# ===========================
# REVIEWS
# ===========================

@login_required
@client_required
def submit_review(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id, client=request.user.profile)

    # Check if review already exists for this contract
    existing_review = Review.objects.filter(
        project=contract.project,
        reviewer=request.user,
        reviewee=contract.freelancer.user
    ).first()

    if existing_review:
        messages.error(request, "You have already reviewed this freelancer for this contract.")
        return redirect("client_dashboard")

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        Review.objects.create(
            project=contract.project,
            reviewer=request.user,
            reviewee=contract.freelancer.user,
            rating=rating,
            comment=comment
        )

        messages.success(request, f"Review submitted for {contract.freelancer.user.username}.")

    return redirect("client_dashboard")

@login_required
def leave_review(request, project_id, reviewee_id):
    project = get_object_or_404(Project, id=project_id)
    reviewee = get_object_or_404(User, id=reviewee_id)
    if request.method == "POST":
        Review.objects.create(
            project=project,
            reviewer=request.user,
            reviewee=reviewee,
            rating=request.POST["rating"],
            comment=request.POST["comment"]
        )
        messages.success(request, "Review submitted.")
    return redirect("freelancer_dashboard")


# ===========================
# DRF VIEWSETS
# ===========================

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = ProjectFilter
    ordering_fields = ['created_at', 'budget', 'deadline']
    ordering = ['-created_at']
    search_fields = ['title', 'description']


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]
@login_required
@client_required
def submit_review(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id, client=request.user.profile)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        # Check if a review by this client already exists
        existing_review = Review.objects.filter(
            project=contract.project,
            reviewer_name=request.user.username
        ).first()

        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
        else:
            Review.objects.create(
                project=contract.project,
                rating=rating,
                comment=comment,
                reviewer_name=request.user.username
            )

        return redirect("client_dashboard")

    context = {"contract": contract}
    return render(request, "submit_review.html", context)
