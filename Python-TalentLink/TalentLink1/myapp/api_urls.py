from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProjectViewSet, ProposalViewSet, ContractViewSet, MessageViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'proposals', ProposalViewSet, basename='proposals')
router.register(r'contracts', ContractViewSet, basename='contracts')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),  # Now /api/... works correctly
]
