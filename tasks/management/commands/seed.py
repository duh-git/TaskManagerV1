from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
import random
from ...models import (
    Task,
    TaskHistory,
)  # Замените your_app на имя вашего приложения

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with test data"

    def handle(self, *args, **options):
        fake = Faker()

        # Создаем тестового пользователя, если его нет
        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={
                "email": "test@example.com",
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
        )
        if created:
            user.set_password("testpass123")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created test user"))

        # Удаляем старые данные
        Task.objects.all().delete()
        TaskHistory.objects.all().delete()

        # Создаем задачи
        status_choices = ["N", "P", "C", "X"]
        priority_choices = [1, 2, 3, 4, 5]

        for i in range(20):
            start_date = fake.date_between(start_date="-30d", end_date="+30d")
            due_date = fake.date_between(start_date=start_date, end_date="+60d")

            task = Task.objects.create(
                title=fake.sentence(nb_words=3),
                description=fake.text(max_nb_chars=200),
                start_date=start_date,
                due_date=due_date,
                status=random.choice(status_choices),
                priority=random.choice(priority_choices),
                owner=user,
            )

            # Создаем историю изменений для каждой задачи
            changes_count = random.randint(1, 5)
            for _ in range(changes_count):
                field_changed = random.choice(
                    ["status", "priority", "title", "description"]
                )
                old_value = str(getattr(task, field_changed))

                # Изменяем значение поля
                if field_changed == "status":
                    new_value = random.choice(
                        [s for s in status_choices if s != old_value]
                    )
                elif field_changed == "priority":
                    new_value = random.choice(
                        [p for p in priority_choices if p != old_value]
                    )
                elif field_changed == "title":
                    new_value = fake.sentence(nb_words=3)
                else:  # description
                    new_value = fake.text(max_nb_chars=200)

                # Создаем запись в истории
                TaskHistory.objects.create(
                    task=task,
                    field=field_changed,
                    old_value=old_value,
                    new_value=new_value,
                    changed_at=fake.date_time_between(
                        start_date="-30d",
                        end_date="now",
                        tzinfo=timezone.get_current_timezone(),
                    ),
                )

                # Обновляем значение поля в задаче
                setattr(task, field_changed, new_value)

            task.save()

        self.stdout.write(self.style.SUCCESS("Successfully seeded database"))
