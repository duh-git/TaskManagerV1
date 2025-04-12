import django_filters
from django_filters import DateFromToRangeFilter
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskFilter(django_filters.FilterSet):
    due_date = django_filters.DateFilter(field_name="due_date")
    due_date_range = DateFromToRangeFilter(field_name="due_date")
    priority = django_filters.NumberFilter(field_name="priority")
    owner = django_filters.CharFilter(field_name='owner__username')
    
    class Meta:
        model = Task
        fields = ["status", "priority", "due_date", "owner"]
