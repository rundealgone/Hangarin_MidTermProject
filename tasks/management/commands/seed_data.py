from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from tasks.models import Category, Priority, Task, SubTask, Note

fake = Faker()


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # ── Priorities ──────────────────────────────────────────────────────
        priority_data = [
            ('Critical', 'critical'),
            ('High', 'high'),
            ('Medium', 'medium'),
            ('Low', 'low'),
            ('Optional', 'optional'),
        ]
        priorities = {}
        for name, level in priority_data:
            obj, created = Priority.objects.get_or_create(name=name, defaults={'level': level})
            priorities[name] = obj
            if created:
                self.stdout.write(f'  Created priority: {name}')

        # ── Categories ──────────────────────────────────────────────────────
        category_names = ['Work', 'School', 'Personal', 'Finance', 'Projects']
        categories = []
        for name in category_names:
            obj, created = Category.objects.get_or_create(name=name)
            categories.append(obj)
            if created:
                self.stdout.write(f'  Created category: {name}')

        # ── Tasks ───────────────────────────────────────────────────────────
        self.stdout.write('  Generating 30 fake tasks...')
        priority_list = list(priorities.values())
        for _ in range(30):
            task = Task.objects.create(
                title=fake.sentence(nb_words=5).rstrip('.'),
                description=fake.paragraph(nb_sentences=3),
                status=fake.random_element(elements=["Pending", "In Progress", "Completed"]),
                deadline=timezone.make_aware(fake.date_time_this_month()),
                category=fake.random_element(elements=categories),
                priority=fake.random_element(elements=priority_list),
            )

            # ── SubTasks ────────────────────────────────────────────────────
            for _ in range(fake.random_int(min=1, max=4)):
                SubTask.objects.create(
                    parent_task=task,
                    title=fake.sentence(nb_words=4).rstrip('.'),
                    status=fake.random_element(elements=["Pending", "In Progress", "Completed"]),
                )

            # ── Notes ───────────────────────────────────────────────────────
            for _ in range(fake.random_int(min=0, max=3)):
                Note.objects.create(
                    task=task,
                    content=fake.paragraph(nb_sentences=2),
                )

        self.stdout.write(self.style.SUCCESS('✔ Seeding complete!'))
