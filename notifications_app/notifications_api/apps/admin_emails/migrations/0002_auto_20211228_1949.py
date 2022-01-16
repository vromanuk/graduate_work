# Generated by Django 3.2.10 on 2021-12-28 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_emails", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="email",
            name="from_email",
        ),
        migrations.RemoveField(
            model_name="email",
            name="status",
        ),
        migrations.AddField(
            model_name="emailtemplate",
            name="scheduled_at",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name="Дата и время отправки",
            ),
        ),
        migrations.AlterField(
            model_name="email",
            name="bcc",
            field=models.TextField(
                blank=True,
                help_text="список получателей через запятую",
                verbose_name="Скрытая копия",
            ),
        ),
        migrations.AlterField(
            model_name="email",
            name="cc",
            field=models.TextField(
                blank=True,
                help_text="список получателей через запятую",
                verbose_name="Копия",
            ),
        ),
        migrations.AlterField(
            model_name="email",
            name="subject",
            field=models.CharField(blank=True, max_length=989, verbose_name="Тема"),
        ),
    ]
