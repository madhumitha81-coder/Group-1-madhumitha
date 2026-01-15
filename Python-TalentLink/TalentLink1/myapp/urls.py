from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# ------------------- DRF ROUTER -------------------
router = DefaultRouter()
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="projects")


    # HTML views
    

router.register(r'api/projects', views.ProjectViewSet, basename='api-projects')
router.register(r'api/proposals', views.ProposalViewSet, basename='api-proposals')

# ------------------- URL PATTERNS -------------------
urlpatterns = [
    # ---------------- AUTH ----------------
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("redirect/", views.root_redirect, name="root_redirect"),
    


    # API
    path("api/", include(router.urls)),

    # ---------------- CLIENT ----------------
    path("client/dashboard/", views.client_dashboard, name="client_dashboard"),
    path("project/create/", views.create_project, name="create_project"),
    path("project/<int:project_id>/", views.project_detail, name="project_detail"),
    path("project/<int:pk>/update/", views.update_project, name="update_project"),
    path("project/<int:pk>/delete/", views.delete_project, name="delete_project"),
    path('notification/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('contract/<int:contract_id>/chat/', views.contract_chat, name='contract_chat'),
    
    path('contract/<int:contract_id>/clear/', views.clear_chat, name='clear_chat'),

    path("send_message/", views.send_message, name="send_message"),
    path("notifications/", views.get_notifications, name="get_notifications"),
    path("notification/read/<int:id>/", views.read_notification, name="read_notification"),
    path('proposal/<int:proposal_id>/accept/', views.accept_proposal, name='accept_proposal'),
    path('proposal/<int:proposal_id>/reject/', views.reject_proposal, name='reject_proposal'),


    path("contract/<int:contract_id>/complete/", views.complete_contract, name="complete_contract"),
    path("contract/<int:contract_id>/cancel/", views.cancel_contract, name="cancel_contract"),
    path("contract/<int:contract_id>/chat/", views.contract_chat, name="contract_chat"),
    
    path("contract/<int:contract_id>/submit_review/", views.submit_review, name="submit_review"),
    
    path("notifications/read/<int:notif_id>/", views.mark_notification_read, name="mark_notification_read"),

    # ---------------- PROPOSALS ----------------
    
    path("proposal/<int:proposal_id>/update/", views.update_proposal_status, name="update_proposal_status"),
    path("project/<int:project_id>/submit/", views.submit_proposal, name="submit_proposal"),

    # ---------------- FREELANCER ----------------
    path("freelancer/dashboard/", views.freelancer_dashboard, name="freelancer_dashboard"),
    path("project/<int:project_id>/", views.project_detail, name="project_detail"),
    path("review/<int:project_id>/<int:reviewee_id>/", views.leave_review, name="leave_review"),

    # ---------------- NOTIFICATIONS ----------------
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/read/<int:notif_id>/", views.mark_notification_read, name="mark_notification_read"),
    path("notification/read/<int:id>/", views.read_notification, name="read_notification"),
    # Delete all notifications for logged-in user
    path('notifications/clear_all/', views.clear_all_notifications, name='clear_all_notifications'),

    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('contract/<int:contract_id>/submit_review/', views.submit_review, name='submit_review'),


    # ---------------- DRF API ----------------
    path("api/", include(router.urls)),
]
