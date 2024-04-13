from django.db import models

class Video(models.Model):
    video = models.FileField(upload_to="cut_videos/")
    movie = models.CharField(max_length=100)
    complexity = models.FloatField()
    length = models.FloatField()

    def __str__(self):
        return self.video.name

class TrendingMovies(models.Model):
    title = models.CharField(max_length=100, unique=True, primary_key=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title
