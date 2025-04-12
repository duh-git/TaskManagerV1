from import_export import resources
from .models import Task


class TaskResource(resources.ModelResource):
    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "status",
            "priority",
            "start_date",
            "due_date",
        )

    def dehydrate_status(self, task):
        return task.get_status_display()

    def dehydrate_priority(self, task):
        return task.get_priority_display()

# tasks/resources.py
from import_export import resources, fields
from import_export.widgets import DateWidget
from .models import Task
from datetime import datetime


class ExportTasksExcel(resources.ModelResource):
    # Кастомизированное поле для даты
    due_date = fields.Field(
        column_name="Due Date",
        attribute="due_date",
        widget=DateWidget(format="%d-%m-%Y"),
    )

    # Кастомизированное поле для статуса
    status = fields.Field(
        column_name="Status",
        attribute="get_status_display",  # Используем стандартный метод модели
    )

    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "status",
            "priority",
            "start_date",
            "due_date",
        )
        export_order = fields
        widgets = {
            "start_date": {"format": "%d-%m-%Y"}  # Форматирование для start_date
        }

    def get_export_queryset(self):
        """Фильтрация - только задачи с высоким приоритетом (>=3)"""
        return super().get_export_queryset().filter(priority__gte=3)

    def dehydrate_due_date(self, task):
        """Кастомное форматирование даты (альтернативный способ)"""
        return task.due_date.strftime("%d-%m-%Y")

    def get_status(self, task):
        """Дополнительное форматирование статуса (если нужно переопределить)"""
        status_map = {
            "N": "New",
            "P": "In Progress",
            "C": "Completed",
            "X": "Cancelled",
        }
        return status_map.get(task.status, task.status)

    def dehydrate_priority(self, task):
        """Преобразование приоритета в читаемый формат"""
        return dict(Task.PRIORITY_CHOICES).get(task.priority, task.priority)
