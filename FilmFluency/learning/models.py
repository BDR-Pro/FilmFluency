from django.db import models
import string
import random
from django.utils.text import slugify

def random_slug_generator(size=12):  # Adjusted to default 12 characters
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=size))

class BaseMedia(models.Model):
    # Common fields that other models could inherit
    random_slug = models.CharField(max_length=12, unique=True, default=random_slug_generator)

    class Meta:
        abstract = True  # This makes it so Django doesn't try to create a table for this model

class Movie(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    release_date = models.DateField()
    rating = models.FloatField()
    poster = models.ImageField(upload_to="posters/")
    random_slug = models.SlugField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def poster_url(self):
        return self.poster.url

    @property
    def trailer_url(self):
        return self.trailer.url

    def save(self, *args, **kwargs):
        if not self.random_slug:
            # Generate a slug based on the title
            self.random_slug = slugify(self.title)
        super(Movie, self).save(*args, **kwargs)

class Video(BaseMedia):
    video = models.FileField(upload_to="videos/")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='videos')
    complexity = models.FloatField()
    length = models.FloatField()
    
    def __str__(self):
        return f"{self.movie.title} - Video"

    @property
    def video_url(self):
        return self.video.url

    @property
    def audio_url(self):
        # This method should correctly point to where the audio file is stored.
        return self.video.url.replace('.mp4', '.wav')

    @property
    def transcript_url(self):
        # This method should correctly point to where the transcript is stored.
        return self.video.url.replace('.mp4', '.txt')

class TrendingMovies(models.Model):
    title = models.CharField(max_length=100, unique=True, primary_key=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title
