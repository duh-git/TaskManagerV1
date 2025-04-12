from django import forms
from .models import Task
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "start_date",
            "due_date",
            "status",
            "priority",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        due_date = cleaned_data.get("due_date")

        if start_date and due_date and start_date > due_date:
            raise ValidationError("Дата начала не может быть позже даты окончания!")

        return cleaned_data

    def clean_priority(self):
        priority = self.cleaned_data.get("priority")
        if priority < 1 or priority > 5:
            raise ValidationError("Приоритет должен быть от 1 до 5!")
        return priority
