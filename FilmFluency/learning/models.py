from django.db import models
import string
import random
from django.utils.text import slugify
from django.db import models
import uuid
from django.contrib.auth.models import User

def random_slug_generator(size=12):  # Adjusted to default 12 characters
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=size))

class BaseMedia(models.Model):
    # Common fields that other models could inherit
    random_slug = models.CharField(max_length=12, unique=True, default=random_slug_generator)

    class Meta:
        abstract = True  # This makes it so Django doesn't try to create a table for this model

class Movie(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True)
    release_date = models.DateField(null=True)
    rating = models.FloatField(default=0)
    poster = models.ImageField(upload_to="posters/")
    random_slug = models.SlugField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def poster_url(self):
        return self.poster.url



    def save(self, *args, **kwargs):
        if not self.random_slug:
            # Generate a slug based on the title
            self.random_slug = slugify(self.title)
        super(Movie, self).save(*args, **kwargs)


class TrendingMovies(models.Model):
    title = models.CharField(max_length=100, unique=True, primary_key=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title



from urllib.parse import quote


class Video(BaseMedia):
    video = models.FileField()
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='videos')
    complexity = models.FloatField()
    length = models.FloatField()

    def __str__(self):
        # This function should only be defined once.
        return f"{self.movie.title} - Video"

    def video_path(self):
        # Renamed from path to video_path for clarity
        return quote(self.video.path)

    def audio_url(self):
        # Ensures the method returns a URL path for the audio file
        return quote(self.video.url.replace(".mp4", ".wav"))

    def text(self):
        # Ensures the method returns a URL path for the audio file
        return quote(self.video.url.replace(".mp4", ".txt"))
    
    

class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    iso_code = models.CharField(max_length=10, unique=True)  # ISO language code

    def __str__(self):
        return self.name


class Community(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name='communities')

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}"


