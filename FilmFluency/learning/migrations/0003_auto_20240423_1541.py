# Generated by Django 4.2.11 on 2024-04-23 12:41

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0002_movie_genre'),
    ]

    operations = [
        
    
        migrations.AddField(
            model_name='movie',
            name='genre',
            field=models.CharField(blank=True, max_length=100, null=True),
        )
    ]