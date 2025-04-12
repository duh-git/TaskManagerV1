# utils/mixins.py
from django.core.exceptions import PermissionDenied


class TaskOwnerMixin:
    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if task.owner != request.user:
            raise PermissionDenied("У вас нет прав на редактирование этой задачи!")
        return super().dispatch(request, *args, **kwargs)
