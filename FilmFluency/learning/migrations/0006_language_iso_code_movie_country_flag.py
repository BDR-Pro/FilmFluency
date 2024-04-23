# Generated by Django 4.2.11 on 2024-04-23 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0005_remove_language_iso_code_remove_movie_country_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='iso_code',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='country_flag',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]