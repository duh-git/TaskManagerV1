# Generated by Django 5.2 on 2025-04-09 18:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("start_date", models.DateField()),
                ("due_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("N", "New"),
                            ("P", "In Progress"),
                            ("C", "Completed"),
                            ("X", "Cancelled"),
                        ],
                        default="N",
                        max_length=1,
                    ),
                ),
                (
                    "priority",
                    models.IntegerField(
                        choices=[
                            (1, "Low"),
                            (2, "Medium"),
                            (3, "High"),
                            (4, "Urgent"),
                            (5, "Critical"),
                        ],
                        default=2,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TaskHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                ("field", models.CharField(max_length=50)),
                ("old_value", models.CharField(blank=True, max_length=255, null=True)),
                ("new_value", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history",
                        to="tasks.task",
                    ),
                ),
            ],
        ),
    ]
