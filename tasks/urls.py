from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("api/", include(router.urls)),
    path("", TaskListView.as_view(), name="task_list"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path("create/", TaskCreateView.as_view(), name="task_create"),
    path("<int:pk>/update/", TaskUpdateView.as_view(), name="task_update"),
    path("<int:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("due_soon/", DueSoonTasksView.as_view(), name="due_soon_tasks"),
    path(
        "high_priority/",
        HighPriorityIncompleteTasksView.as_view(),
        name="high_priority_tasks",
    ),
    path("complex_query/", ComplexQueryTasksView.as_view(), name="complex_query_tasks"),
    path("others_tasks/", OthersTasksView.as_view(), name="others_tasks"),
    # Действия
    path(
        "<int:pk>/change_status/",
        ChangeTaskStatusView.as_view(),
        name="change_task_status",
    ),
    path("overdue/", OverdueTasksView.as_view(), name="overdue_tasks"),
    path("accounts/register/", RegisterView.as_view(), name="register"),
    # path("export/excel/", ExportTasksExcel.as_view(), name="export_excel"),
]
