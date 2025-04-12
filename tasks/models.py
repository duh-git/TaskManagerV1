from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


class Task(models.Model):
    STATUS_CHOICES = [
        ("N", "New"),
        ("P", "In Progress"),
        ("C", "Completed"),
        ("X", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        (1, "Low"),
        (2, "Medium"),
        (3, "High"),
        (4, "Urgent"),
        (5, "Critical"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="N")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

    def clean(self):
        # Проверка дат
        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValidationError("Start date cannot be later than due date.")

        # Проверка приоритета
        if self.priority not in [choice[0] for choice in self.PRIORITY_CHOICES]:
            raise ValidationError("Priority must be between 1 and 5.")

        # Проверка уникальности названия (только если owner уже установлен)
        if hasattr(self, "owner") and self.owner:
            if (
                Task.objects.filter(title=self.title, owner=self.owner)
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError("You already have a task with this title.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="history")
    changed_at = models.DateTimeField(auto_now_add=True)
    field = models.CharField(max_length=50)
    old_value = models.CharField(max_length=255, blank=True, null=True)
    new_value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.task.title} - {self.field} changed at {self.changed_at}"
