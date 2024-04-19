from django.db import models
import string
import random
from django.utils.text import slugify
from django.db import models
from django.utils import timezone
from urllib.parse import quote
from django.contrib.auth.models import User 
import re
import sys


def format_transcript(text):
    """Formats the transcript text to add new lines after each '.', ',', or every 8 words."""
    
    # Insert a new line after each period or comma
    text = re.sub(r'([.,])', r'\1\n', text)
    
    # Further break down long sentences without punctuation into lines of approximately 8 words
    def insert_newlines(match):
        words = match.group(0).split()
        return '\n'.join(' '.join(words[i:i+8]) for i in range(0, len(words), 8))

    text = re.sub(r'[^\n]+', insert_newlines, text)
    
    return text

   
def random_slug_generator(size=12):  # Adjusted to default 12 characters
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=size))

class BaseMedia(models.Model):
    # Common fields that other models could inherit
    random_slug = models.CharField(max_length=12, unique=True, default=random_slug_generator)

    class Meta:
        abstract = True  # This makes it so Django doesn't try to create a table for this model

class Movie(models.Model):
    title = models.CharField(max_length=100, unique=True)
    genre = models.CharField(max_length=100, default="28")
    description = models.TextField(null=True)
    random_slug = models.SlugField(max_length=50, unique=True, blank=True)
    type = models.CharField(max_length=10, default='movie')
    date_added = models.DateTimeField(default=timezone.now)
    release_date = models.DateField(null=True)
    rating = models.FloatField(default=0)
    poster = models.TextField(default='no-image.jpg')
    backdrop_path = models.CharField(max_length=200, null=True, blank=True)
    tmdb_id = models.IntegerField(null=True, blank=True)
    original_title = models.CharField(max_length=100, null=True, blank=True)
    original_language = models.CharField(max_length=10, null=True, blank=True)
    popularity = models.FloatField(null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)

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
        
    def get_desc(self):
        return self.description[:50]

class TrendingMovies(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, primary_key=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.movie.title  # Use movie title for string representation


class Video(BaseMedia):
    video = models.FileField()
    date_added = models.DateTimeField(default=timezone.now)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='videos')
    complexity = models.FloatField()
    length = models.FloatField()
    random_slug = models.SlugField(max_length=50, unique=True, default=random_slug_generator)

    def __str__(self):
        # This function should only be defined once.
        return f"{self.movie.title} - Video"

    def video_path(self):
        return self.video.path

    def audio_url(self):
        # Ensures the method returns a URL path for the audio file
        return quote(self.video.url.replace(".mp4", ".wav"))

    def video_url(self):
        # Ensures the method returns a URL path for the video file
        return quote(self.video.url)
    
    def thumbnail_url(self):
        # Ensures the method returns a URL path for the thumbnail
        return quote(self.video.url.replace(".mp4", ".jpg"))

    def transcript(self):
        """Returns the contents of the transcript file as a formatted string with added newlines for readability."""
        transcript_path = self.video.path.replace(".mp4", ".txt")
        try:
            with open(transcript_path, 'r', encoding='utf-8') as file:
                content = "".join(file.readlines())
                return format_transcript(content)  # Format the transcript text
        except FileNotFoundError:
            return "No transcript available."
        except Exception as e:
            return f"An error occurred while reading the transcript: {str(e)}"
        
    def translation(self, language="ar"):
        """Returns the contents of the translation file as a formatted string with added newlines for readability."""
        translation_path = Translation.objects.get(video=self.title,tmdb_code=language).translated_text
        try:
            with open(translation_path, 'r', encoding='utf-8') as file:
                content = "".join(file.readlines())
            return format_transcript(content) 
        except FileNotFoundError:
            return "No translation available."
        
    def get_hardest_word(self, language="ar"):
        """Returns the contents of the translation file as a formatted string with added newlines for readability."""
        translation_path = Translation.objects.get(video=self.title,tmdb_code=language).translated_text
        try:
            with open(translation_path, 'r', encoding='utf-8') as file:
                content = "".join(file.readlines())
            return format_transcript(content) 
        except FileNotFoundError:
            return "No translation available."

class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tmdb_code = models.CharField(max_length=10, unique=True)
    is_src_lang = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Translation(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='translations')
    translated_text = models.TextField()
    hardest_word = models.TextField(null=True)
    
    

    def __str__(self):
        return f"{self.video.movie.title} - {self.language.name} Translation"

class Community(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name='communities')
    lang = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='communities',default=1)
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

