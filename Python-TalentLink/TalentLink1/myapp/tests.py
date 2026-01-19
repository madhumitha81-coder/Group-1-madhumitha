from django.test import TestCase
from django.contrib.auth.models import User
from myapp.models import Project, Proposal, Contract, Profile

class ProjectTest(TestCase):
    def setUp(self):
        # Create user to assign as client
        self.user = User.objects.create_user(username="clientuser", password="pass")
        # Profile is auto-created via signals
        self.profile = self.user.profile

    def test_project_creation(self):
        project = Project.objects.create(title="Test", budget=100, client=self.user)
        self.assertEqual(project.budget, 100)
        self.assertEqual(project.client.username, "clientuser")


class ProposalContractTest(TestCase):

    def setUp(self):
        # Client
        self.client_user = User.objects.create_user(username="client1", password="pass123")
        self.client_profile = self.client_user.profile

        # Freelancer
        self.freelancer_user = User.objects.create_user(username="freelancer1", password="pass123")
        self.freelancer_profile = self.freelancer_user.profile

        # Project
        self.project = Project.objects.create(
            title="Test Project",
            description="Test Desc",
            budget=5000,
            client=self.client_user
        )

        # Proposal
        self.proposal = Proposal.objects.create(
            project=self.project,
            freelancer=self.freelancer_profile,
            bid_amount=4500,
            status="pending"
        )

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from myapp.models import Profile, Project, Proposal, Contract, Review, Notification

class TalentLinkFullTests(TestCase):
    def setUp(self):
        # Users
        self.client_user = User.objects.create_user(username="client", password="pass")
        self.freelancer_user = User.objects.create_user(username="freelancer", password="pass")
        self.client_profile = self.client_user.profile
        self.freelancer_profile = self.freelancer_user.profile

        # Project
        self.project = Project.objects.create(
            title="Test Project",
            description="Demo",
            budget=1000,
            client=self.client_user
        )

        # Proposal
        self.proposal = Proposal.objects.create(
            project=self.project,
            freelancer=self.freelancer_profile,
            bid_amount=900,
            status="PENDING"
        )

    # DASHBOARD ACCESS
    def test_client_dashboard_access(self):
        self.client.login(username="client", password="pass")
        response = self.client.get(reverse("client_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_freelancer_dashboard_access(self):
        self.client.login(username="freelancer", password="pass")
        response = self.client.get(reverse("freelancer_dashboard"))
        self.assertEqual(response.status_code, 200)

    # PROPOSAL WORKFLOW
    def test_accept_proposal_creates_contract_and_rejects_others(self):
        self.client.login(username="client", password="pass")
        url = reverse("accept_proposal", args=[self.proposal.id])
        self.client.post(url)
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, "ACCEPTED")
        contract = Contract.objects.get(proposal=self.proposal)
        self.assertEqual(contract.status, "ACTIVE")

    def test_reject_proposal(self):
        self.client.login(username="client", password="pass")
        url = reverse("reject_proposal", args=[self.proposal.id])
        self.client.post(url)
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, "REJECTED")

    # CONTRACT ACTIONS
    def test_complete_contract(self):
        contract = Contract.objects.create(
            proposal=self.proposal,
            project=self.project,
            client=self.client_profile,
            freelancer=self.freelancer_profile,
            status="ACTIVE"
        )
        self.client.login(username="client", password="pass")
        url = reverse("complete_contract", args=[contract.id])
        self.client.post(url)
        contract.refresh_from_db()
        self.assertEqual(contract.status, "COMPLETED")

    def test_cancel_contract(self):
        contract = Contract.objects.create(
            proposal=self.proposal,
            project=self.project,
            client=self.client_profile,
            freelancer=self.freelancer_profile,
            status="ACTIVE"
        )
        self.client.login(username="client", password="pass")
        url = reverse("cancel_contract", args=[contract.id])
        self.client.post(url)
        contract.refresh_from_db()
        self.assertEqual(contract.status, "CANCELLED")

    # REVIEWS
    def test_submit_review(self):
        contract = Contract.objects.create(
            proposal=self.proposal,
            project=self.project,
            client=self.client_profile,
            freelancer=self.freelancer_profile,
            status="COMPLETED"
        )
        self.client.login(username="client", password="pass")
        url = reverse("submit_review", args=[contract.id])
        self.client.post(url, {"rating": 5, "comment": "Excellent work!"})
        review = Review.objects.get(project=self.project)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Excellent work!")

    # NOTIFICATIONS
    def test_notification_created_on_accept(self):
        self.client.login(username="client", password="pass")
        self.client.post(reverse("accept_proposal", args=[self.proposal.id]))
        notif = Notification.objects.filter(user=self.freelancer_user).first()
        self.assertIsNotNone(notif)
        self.assertIn("ACCEPTED", notif.message)
