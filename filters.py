import django_filters
from .models import Project

class ProjectFilter(django_filters.FilterSet):
    min_budget = django_filters.NumberFilter(field_name="budget", lookup_expr="gte")
    max_budget = django_filters.NumberFilter(field_name="budget", lookup_expr="lte")

    deadline_before = django_filters.DateFilter(field_name="deadline", lookup_expr="lte")
    deadline_after = django_filters.DateFilter(field_name="deadline", lookup_expr="gte")

    skills = django_filters.CharFilter(field_name="skills_required", lookup_expr="icontains")

    class Meta:
        model = Project
        fields = [
            'min_budget',
            'max_budget',
            'deadline_before',
            'deadline_after',
            'skills',
        ]
