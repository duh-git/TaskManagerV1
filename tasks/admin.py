from django.contrib import admin
from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field
from .models import Task, TaskHistory


class TaskResource(resources.ModelResource):
    formatted_due_date = Field()
    formatted_status = Field()

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "formatted_status",
            "priority",
            "formatted_due_date",
            "owner__username",
        )
        export_order = fields

    def get_export_queryset(self, request):
        """Фильтруем задачи с высоким приоритетом для экспорта"""
        return super().get_export_queryset(request).filter(priority__gte=3)

    def dehydrate_formatted_due_date(self, task):
        """Форматируем дату в DD-MM-YYYY"""
        return task.due_date.strftime("%d-%m-%Y")

    def dehydrate_formatted_status(self, task):
        """Преобразуем статус в читаемый формат"""
        return dict(Task.STATUS_CHOICES).get(task.status, task.status)


@admin.register(Task)
class TaskAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = TaskResource
    list_display = ("title", "status", "priority", "due_date", "owner")
    list_filter = ("status", "priority", "owner")
    search_fields = ("title", "description")


# @admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ("task", "field", "old_value", "new_value", "changed_at")
    list_filter = ("field", "changed_at")
    search_fields = ("task__title",)
