from django.db import models
import string
import random
from django.utils.text import slugify
from django.db import models
import uuid

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


class TrendingMovies(models.Model):
    title = models.CharField(max_length=100, unique=True, primary_key=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title





class OneTimeLink(models.Model):
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    content_type = models.CharField(max_length=10, choices=(('video', 'Video'), ('audio', 'Audio'), ('transcript', 'Transcript')))
    file_path = models.CharField(max_length=255)  # Path to the file
    accessed = models.BooleanField(default=False)

    def generate_link(self):
        if not self.accessed:
            self.accessed = True
            self.save()
            return f'https://yourdomain.com/media/{self.content_type}/{self.key}'
        else:
            return None

class Video(BaseMedia):
    video = models.FileField(upload_to="videos/")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='videos')
    complexity = models.FloatField()
    length = models.FloatField()

    def __str__(self):
        return f"{self.movie.title} - Video"

    def create_one_time_link(self, content_type):
        file_path_map = {
            'video': self.video.path,
            'audio': self.video.path.replace('.mp4', '.wav'),
            'transcript': self.video.path.replace('.mp4', '.txt')
        }
        file_path = file_path_map[content_type]
        link = OneTimeLink(content_type=content_type, file_path=file_path)
        link.save()
        return link.generate_link()

    @property
    def video_url(self):
        return self.create_one_time_link('video')

    @property
    def audio_url(self):
        return self.create_one_time_link('audio')

    @property
    def transcript_url(self):
        return self.create_one_time_link('transcript')