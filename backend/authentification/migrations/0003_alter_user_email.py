"""
Миграция 0003: исправление типа поля email.

В модели User указано EmailField, но в 0001_initial было CharField.
Эта миграция приводит БД к соответствию с моделью.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentification", "0002_listing"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=255,
                unique=True,
                verbose_name="Email",
                help_text="Уникальный email-адрес.",
            ),
        ),
    ]
