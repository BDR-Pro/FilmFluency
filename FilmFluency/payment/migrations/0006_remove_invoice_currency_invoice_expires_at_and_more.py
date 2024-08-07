# Generated by Django 4.2.11 on 2024-05-18 19:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0005_payment_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='currency',
        ),
        migrations.AddField(
            model_name='invoice',
            name='expires_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='subscreibed_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='payment',
            name='isGift',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='payment',
            name='is_recurring',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_used', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
