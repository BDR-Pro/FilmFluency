# Generated by Django 4.2.7 on 2024-04-15 22:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0005_alter_video_random_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='lang',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='communities', to='learning.language'),
        ),
        migrations.AddField(
            model_name='trendingmovies',
            name='movie',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='trending_movie', to='learning.movie'),
        ),
    ]
