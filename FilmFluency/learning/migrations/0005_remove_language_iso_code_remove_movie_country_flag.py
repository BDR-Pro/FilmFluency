# Generated by Django 4.2.11 on 2024-04-23 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0004_alter_language_iso_code_alter_movie_country_flag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='iso_code',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='country_flag',
        ),
    ]