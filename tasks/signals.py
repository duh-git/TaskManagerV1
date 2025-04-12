from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Task, TaskHistory


@receiver(pre_save, sender=Task)
def track_task_changes(sender, instance, **kwargs):
    if instance.pk:
        original = Task.objects.get(pk=instance.pk)
        for field in ["title", "description", "status", "priority", "due_date"]:
            original_value = getattr(original, field)
            new_value = getattr(instance, field)
            if original_value != new_value:
                TaskHistory.objects.create(
                    task=instance,
                    field=field,
                    old_value=str(original_value),
                    new_value=str(new_value),
                )
