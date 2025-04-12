from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegisterForm
from django.utils import timezone
from .models import Task, TaskHistory
from datetime import datetime, timedelta
from .forms import TaskForm
from .serializers import TaskSerializer, TaskHistorySerializer
from .filters import TaskFilter
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .utils.mixins import TaskOwnerMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import PermissionDenied
from django.contrib import messages

# ===== Основные представления =====


class BaseTaskListView(LoginRequiredMixin, ListView):
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "status_choices": dict(Task.STATUS_CHOICES),
                "priority_choices": dict(Task.PRIORITY_CHOICES),
                "all_users": User.objects.all(),
                "current_filters": {
                    "status": self.request.GET.get("status", ""),
                    "priority": self.request.GET.get("priority", ""),
                    "owner": self.request.GET.get("owner", ""),
                },
            }
        )
        return context


class TaskListView(BaseTaskListView):
    def get_queryset(self):
        queryset = Task.objects.all().order_by("-created_at")

        if search_query := self.request.GET.get('search'):
            queryset = queryset.filter(description__icontains=search_query)
            
        # Применяем фильтры из URL-параметров
        filters = {
            "status": self.request.GET.get("status"),
            "priority": self.request.GET.get("priority"),
            "owner__username": self.request.GET.get("owner"),
            "due_date": self.request.GET.get("due_date"),
        }

        # Создаем условия для фильтрации
        filter_conditions = {
            key: value
            for key, value in filters.items()
            if value  # Исключаем пустые значения
        }

        if filter_conditions:
            queryset = queryset.filter(**filter_conditions)

        # Фильтр по диапазону дат (специальный случай)
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date and end_date:
            queryset = queryset.filter(due_date__range=[start_date, end_date])

        return queryset


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()  # Убираем .filter(owner=self.request.user)

        # Оставляем только фильтры
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        priority = self.request.GET.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        due_date = self.request.GET.get("due_date")
        if due_date:
            queryset = queryset.filter(due_date=due_date)

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date and end_date:
            queryset = queryset.filter(due_date__range=[start_date, end_date])

        return queryset.order_by("-due_date")  # Добавляем сортировку

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = dict(Task.STATUS_CHOICES)
        context["priority_choices"] = dict(Task.PRIORITY_CHOICES)

        # Добавляем информацию о владельце для отображения
        context["show_owner"] = True
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class TaskUpdateView(LoginRequiredMixin, TaskOwnerMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")

    def get_queryset(self):
        return super().get_queryset()

    def dispatch(self, request, *args, **kwargs):
        try:
            task = self.get_object()
            if task.owner != request.user:
                messages.error(request, "Вы можете редактировать только свои задачи")
                return redirect("task_list")
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            messages.error(
                request, "Доступ запрещен: вы не можете редактировать эту задачу"
            )
            return redirect("task_list")


class TaskDeleteView(LoginRequiredMixin, TaskOwnerMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("task_list")

    def get_queryset(self):
        return super().get_queryset()

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if task.owner != request.user:
            raise PermissionDenied("Вы можете редактировать только свои задачи")
        return super().dispatch(request, *args, **kwargs)


# ===== Дополнительные представления (фильтры и сложные запросы) =====


class DueSoonTasksView(BaseTaskListView):
    def get_queryset(self):
        next_week = timezone.now().date() + timedelta(days=7)
        return Task.objects.filter(
            owner=self.request.user, due_date__range=[timezone.now().date(), next_week]
        )


class HighPriorityIncompleteTasksView(BaseTaskListView):

    def get_queryset(self):
        return Task.objects.filter(
            priority__gte=3,  # Все задачи с высоким приоритетом
            status__in=["N", "P"],  # Незавершенные
        ).order_by("-created_at")


class ComplexQueryTasksView(BaseTaskListView):
    def get_queryset(self):
        tomorrow = datetime.now().date() + timedelta(days=1)
        return Task.objects.filter(
            owner=self.request.user,
        ).filter(Q(priority__gte=3, status__in=["N", "P"]) | Q(due_date=tomorrow))


class OthersTasksView(BaseTaskListView):
    def get_queryset(self):
        return Task.objects.exclude(owner=self.request.user).filter(
            status__in=["P", "X"]
        )


# ===== Действия (actions) =====


class ChangeTaskStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, owner=request.user)
        new_status = request.POST.get("status")

        if new_status in dict(Task.STATUS_CHOICES).keys():
            task.status = new_status
            task.save()

        return redirect("task_detail", pk=pk)

    def dispatch(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])
        if task.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class OverdueTasksView(BaseTaskListView):
    def get_queryset(self):
        return Task.objects.filter(
            owner=self.request.user,
            due_date__lt=timezone.now().date(),
            status__in=["N", "P"],
        )


User = get_user_model()


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-created_at")
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TaskFilter
    search_fields = ["description"]

    def get_queryset(self):
        queryset = super().get_queryset()  # Убираем фильтр по владельцу

        # Оставляем только фильтры
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        priority = self.request.GET.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        due_date = self.request.GET.get("due_date")
        if due_date:
            queryset = queryset.filter(due_date=due_date)

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date and end_date:
            queryset = queryset.filter(due_date__range=[start_date, end_date])

        return queryset

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return []

    def perform_create(self, serializer):
        # Автоматически назначаем текущего пользователя как владельца
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        # Проверяем, что пользователь - владелец задачи
        if serializer.instance.owner != self.request.user:
            raise PermissionDenied("Вы можете редактировать только свои задачи")
        serializer.save()

    def perform_destroy(self, instance):
        # Проверяем, что пользователь - владелец задачи
        if instance.owner != self.request.user:
            raise PermissionDenied("Вы можете удалять только свои задачи")
        instance.delete()

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get("status")

        if new_status not in dict(Task.STATUS_CHOICES).keys():
            return Response(
                {"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Сохраняем историю изменений
        TaskHistory.objects.create(
            task=task, field="status", old_value=task.status, new_value=new_status
        )

        task.status = new_status
        task.save()

        return Response({"status": "status changed"})

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        overdue_tasks = self.get_queryset().filter(
            due_date__lt=timezone.now().date(), status__in=["N", "P"]
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def task_history(self, request, pk=None):
        task = self.get_object()
        history = task.history.all()
        serializer = TaskHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def due_in_week(self, request):
        week_later = timezone.now().date() + timedelta(days=7)
        tasks = self.get_queryset().filter(
            due_date__range=[timezone.now().date(), week_later]
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def high_priority_incomplete(self, request):
        tasks = self.get_queryset().filter(priority__gte=3, status__in=["N", "P"])
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def complex_query(self, request):
        tomorrow = timezone.now().date() + timedelta(days=1)
        tasks = self.get_queryset().filter(
            Q(priority__gte=3, status__in=["N", "P"]) | Q(due_date=tomorrow)
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def others_in_progress_or_cancelled(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tasks = Task.objects.exclude(owner=request.user).filter(status__in=["P", "X"])
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")
