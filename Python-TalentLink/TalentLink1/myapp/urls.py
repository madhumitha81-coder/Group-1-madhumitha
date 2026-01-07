from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from . import views

# ------------------- DRF ROUTER -------------------

router = DefaultRouter()
router.register(r'api/projects', views.ProjectViewSet, basename='api-projects')
router.register(r'api/proposals', views.ProposalViewSet, basename='api-proposals')


urlpatterns = [

    # ---------------- AUTH ----------------
    path('', views.root_redirect, name='root'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ---------------- CLIENT ----------------
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('project/create/', views.create_project, name='create_project'),
    
    path('project/<int:pk>/update/', views.update_project, name='update_project'),
    path("project/<int:pk>/delete/", views.delete_project, name="delete_project"),

     path('proposal/<int:proposal_id>/update/', views.update_proposal_status, name='update_proposal_status'),
    path('contract/<int:contract_id>/chat/', views.contract_chat, name='contract_chat'),

    # ---------------- PROPOSALS (CLIENT ACTIONS) ----------------
    path('proposal/<int:pk>/accept/', views.accept_proposal, name='accept_proposal'),
    path('proposal/<int:pk>/reject/', views.reject_proposal, name='reject_proposal'),
     path('contract/<int:contract_id>/chat/', views.contract_chat, name='contract_chat'),
    path('contract/<int:contract_id>/chat/clear/', views.clear_contract_chat, name='clear_contract_chat'),

    # ---------------- FREELANCER ----------------
    
    path('freelancer/dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    
  # use project_id
    path('project/<int:project_id>/submit/', views.submit_proposal, name='submit_proposal'),
    path('project/<int:pk>/update/', views.update_project, name='update_project'),
    
    # other 
    # ---------------- CONTRACT CHAT ----------------
    
    # urls.py
    path('project/<int:project_id>/update/', views.update_project, name='update_project'),



    # ---------------- DRF API ----------------
    path('', include(router.urls)),
]
