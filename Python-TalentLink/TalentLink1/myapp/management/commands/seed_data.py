from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import Profile, Project, Proposal, Contract, Review, Skill, Notification
from django.utils import timezone
import random

class Command(BaseCommand):
    help = "Seed database with 1 client and 1 freelancer, plus sample projects, proposals, contracts, reviews"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # =========================
        # 1️⃣ PICK EXISTING USERS OR CREATE IF MISSING
        # =========================
        client_user, _ = User.objects.get_or_create(username="client1", defaults={"email": "client1@test.com"})
        client_user.set_password("password123")
        client_user.save()
        client_profile, _ = Profile.objects.get_or_create(user=client_user, defaults={"role": "client"})

        freelancer_user, _ = User.objects.get_or_create(username="freelancer1", defaults={"email": "freelancer1@test.com"})
        freelancer_user.set_password("password123")
        freelancer_user.save()
        freelancer_profile, _ = Profile.objects.get_or_create(user=freelancer_user, defaults={"role": "freelancer"})

        # =========================
        # 2️⃣ CREATE SKILLS
        # =========================
        skill_names = ["Python", "Django", "React"]
        skills = []
        for s in skill_names:
            skill, _ = Skill.objects.get_or_create(name=s)
            skills.append(skill)

        # =========================
        # 3️⃣ CREATE A SINGLE PROJECT
        # =========================
        project, _ = Project.objects.get_or_create(
            title="Sample Project",
            client=client_user,
            defaults={
                "description": "This is a sample project description",
                "budget": 1000,
                "deadline": timezone.now() + timezone.timedelta(days=15),
            }
        )
        project.skills_required.set(skills[:2])

        # =========================
        # 4️⃣ CREATE PROPOSAL FROM FREELANCER
        # =========================
        proposal, _ = Proposal.objects.get_or_create(
            project=project,
            freelancer=freelancer_profile,
            defaults={
                "cover_letter": "I would like to work on this project.",
                "bid_amount": 900,
                "status": "PENDING",
            }
        )

        # =========================
        # 5️⃣ ACCEPT PROPOSAL → CREATE CONTRACT
        # =========================
        proposal.status = "ACCEPTED"
        proposal.save()

        contract, _ = Contract.objects.get_or_create(
            project=project,
            freelancer=freelancer_profile,
            proposal=proposal,
            client=client_profile,
            defaults={"status": "ACTIVE"}
        )

        Notification.objects.get_or_create(
            user=freelancer_user,
            message=f"Your proposal for '{project.title}' was ACCEPTED."
        )

        # =========================
        # 6️⃣ CREATE REVIEW
        # =========================
        Review.objects.get_or_create(
            project=project,
            reviewer_name=client_user.username,
            defaults={
                "rating": 5,
                "comment": f"Excellent work by {freelancer_user.username}!"
            }
        )

        self.stdout.write(self.style.SUCCESS("Database seeded: 1 client, 1 freelancer, 1 project, 1 proposal, 1 contract, 1 review"))
