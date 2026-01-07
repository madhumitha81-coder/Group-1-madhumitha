import django_filters
from .models import Project

class ProjectFilter(django_filters.FilterSet):
    client_username = django_filters.CharFilter(field_name="client__user__username", lookup_expr='icontains')
    min_budget = django_filters.NumberFilter(field_name="budget", lookup_expr='gte')
    max_budget = django_filters.NumberFilter(field_name="budget", lookup_expr='lte')
    deadline_after = django_filters.DateFilter(field_name="deadline", lookup_expr='gte')
    deadline_before = django_filters.DateFilter(field_name="deadline", lookup_expr='lte')

    class Meta:
        model = Project
        fields = []  # we define filters explicitly
