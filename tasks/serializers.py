from rest_framework import serializers
from .models import Task, TaskHistory
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskHistory
        fields = ["changed_at", "field", "old_value", "new_value"]


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.username", read_only=True)
    status = serializers.CharField(source="get_status_display", read_only=True)
    priority = serializers.CharField(source="get_priority_display", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "start_date",
            "due_date",
            "owner",
        ]
        read_only_fields = ["owner"]

    def validate_priority(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Priority must be between 1 and 5.")
        return value

    def validate(self, data):
        if data.get("start_date") and data.get("due_date"):
            if data["start_date"] > data["due_date"]:
                raise serializers.ValidationError(
                    "Start date cannot be later than due date."
                )
        return data
