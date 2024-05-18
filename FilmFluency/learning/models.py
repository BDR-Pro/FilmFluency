from django.db import models
import string
import random
from django.utils.text import slugify
from django.db import models
from django.utils import timezone
from urllib.parse import quote
from django.contrib.auth.models import User 
import re
from  django.urls import reverse
from learning.func import language_to_country
import subprocess
import os
from api.upload_to_s3 import upload_to_s3
from time import sleep

def get_biggest_file(directory):
    """Return the path to the biggest file in the given directory."""
    files = os.listdir(directory)
    for i in range(len(files)):
        if os.path.isdir(files[i]):
            os.chdir(files[i])
    subdirectory = os.getcwd()         
    biggest_file = max(files, key=lambda x: os.path.getsize(os.path.join(subdirectory, x)))
    return os.path.join(directory,subdirectory,biggest_file)

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




class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    iso_code = models.CharField(unique=True)

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tmdb_code = models.CharField(unique=True)
    is_src_lang = models.BooleanField(default=False)
    iso_code = models.CharField(max_length=2, blank=True, null=True)
    
    
    def save(self, *args, **kwargs):
        self.iso_code = self.lang_to_iso_code()
        super(Language, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def lang_to_iso_code(self):
    # Return the country code corresponding to the language code, or a default if not found
        return language_to_country(self.tmdb_code).lower() if language_to_country(self.tmdb_code) else 'us'   



class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    rating = models.FloatField(default=0)
    poster = models.URLField(blank=True, null=True)
    tmdb_id = models.IntegerField(default='1')
    random_slug = models.SlugField(max_length=50, unique=True, default=random_slug_generator)
    original_title = models.CharField(max_length=255, blank=True, null=True)
    original_language = models.CharField(blank=True, null=True)
    popularity = models.FloatField(default=0)
    vote_count = models.IntegerField(default=0)
    budget = models.BigIntegerField(default=0)
    revenue = models.BigIntegerField(default=0)
    runtime = models.IntegerField(default=0)
    homepage = models.URLField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    country_flag = models.CharField(max_length=2, blank=True, null=True)  
    transcript_path = models.CharField(max_length=255, blank=True, null=True)
    subtitle_path = models.CharField(max_length=255, blank=True, null=True)
    movie_path = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['date_added']
        
    def __str__(self):
        """String representation of the Movie object json compatible"""
        return self.title

    def save(self, *args, **kwargs):
        if not self.random_slug:
            # Generate a slug based on the title
            self.random_slug = slugify(self.title)
        super(Movie, self).save(*args, **kwargs)
        
    
    def save(self, *args, **kwargs):
        self.country_flag = self.Lang_to_country_flag()
        super(Movie, self).save(*args, **kwargs)
        
    def get_desc(self):
        return self.description[:50]
    
    def get_bookmarked_videos(self):
        return self.videos.filter(bookmarked_users__isnull=False)

    
    def get_videos(self):
        return self.videos.all()
    
    def get_videos_count(self):
        return self.videos.count()
    
    def get_videos_duration(self):
        return sum([video.length for video in self.videos.all()])
    
    def get_videos_complexity(self):
        
        return ([video.complexity for video in self.videos.all()])/self.get_videos_count()

    
    def vote_average(self):
        return self.rating / self.vote_count
    
    def Lang_to_country_flag(self):
        # Return the country code corresponding to the language code, or a default if not found
        return language_to_country(self.original_language).lower() if language_to_country(self.original_language) else 'us'   


    def get_absolute_url(self):
        return reverse("web:movie_detail", kwargs={"random_slug": self.random_slug})
    
    
    def last_updated(self):
        """Return the most recent date either the instance was added or the most recent video was added."""
        latest_video = self.videos.latest('date_added') if self.videos.exists() else None
        return latest_video.date_added if latest_video else self.date_added
    
    def download_movie(self):
        """Download the movie file to the S3 bucket and return the URL path."""
        try:
            title = self.title.translate(str.maketrans('', '', string.punctuation)).replace(" ","_")
            title = title[:20]
            os.chdir(os.path.dirname(os.path.realpath(__file__)))
            Dir = os.path.join(os.getcwd(), "MovieToClips", "movies", title)
            os.makedirs(Dir, exist_ok=True)
            subprocess.run(["pirate-get", title,"-0","-S",Dir],capture_output=True, text=True)
            sleep(5)
            file = get_biggest_file(Dir)
            key = file.split("\\")[-1]
            key = 'movies/'+key
            self.movie_path = upload_to_s3(file,key)
        except Exception as e:
            print(f"An error occurred while downloading the movie: {str(e)}")
    
    def set_slug(self):
        self.random_slug = slugify(self.title)[:50]
        
    def get_poster(self):
        if not self.poster:
            return "https://filmfluency.fra1.cdn.digitaloceanspaces.com/posters/placeholder.webp"
        return "https://filmfluency.fra1.cdn.digitaloceanspaces.com"+self.poster if not self.poster.startswith("https") else self.poster
    
    def download_transcript(self):
        try:
            """Download the transcript file to the S3 bucket and return the URL path."""
            title = self.title.translate(str.maketrans('', '', string.punctuation)).replace(" ","_")
            title = title[:20]
            # change dirctory to the script directory
            os.chdir(os.path.dirname(os.path.realpath(__file__)))
            Dir = os.path.join(os.getcwd(), "MovieToClips", "transcripts", title)
            os.makedirs(Dir, exist_ok=True)
            os.chdir(Dir)
            #subliminal download -l en "The Matrix"
            title = self.title.translate(str.maketrans('', '', string.punctuation)).replace(" ","_")
            subprocess.run(["subliminal","download","-l","en",title])
            sleep(5)
            file = get_biggest_file(Dir)
            key = file.split("\\")[-1]
            key = 'transcripts/'+key
            print(f"Transcript path: {file}")
            print(f"Transcript key: {key}")
            self.transcript_path = upload_to_s3(file,key)
        except Exception as e:
            print(f"An error occurred while downloading the transcript: {str(e)}")
            
        
    def download_translation(self):
        try:
            """Download the translation file to the S3 bucket and return the URL path."""
            title = self.title.translate(str.maketrans('', '', string.punctuation)).replace(" ","_")
            title = title[:20]
            os.chdir(os.path.dirname(os.path.realpath(__file__)))
            Dir = os.path.join(os.getcwd(), "MovieToClips", "translations", title)
            os.makedirs(Dir, exist_ok=True)
            os.chdir(Dir)
            #subliminal download -l en "The Matrix.avi"
    
            if not self.original_language == "en":
                title = self.title.translate(str.maketrans('', '', string.punctuation)).replace(" ","_")
                title = title[:20]
                subprocess.run(["subliminal","download","-l","en",title])
                file = get_biggest_file(Dir)
                key = file.split("\\")[-1]
                key = 'translations/'+key
                self.transcript_path = upload_to_s3(file,key)
            else:
                self.transcript_path = self.transcript_path
        except Exception as e:
            print(f"An error occurred while downloading the translation: {str(e)}")
        
    
    def get_transcript(self):
        if not self.transcript_path:
            return False
        title = self.title
        title=title.translate(str.maketrans('', '', string.punctuation)).replace(" ","_")
        title = title + "." + self.original_language + ".srt"
        
        return "transcripts/"+f"{title}"
    
    
    def get_translation(self):
        if not self.transcript_path:
            return False
        title=title.translate(str.maketrans('', '', string.punctuation)).replace(" ","_")
        title = title + ".en" + ".srt"
        
        return "translations/"+f"{title}"
#################################################################


class TrendingMovies(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, primary_key=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.movie.title  # Use movie title for string representation

    
class Video(models.Model):
    video = models.URLField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='videos')
    complexity = models.FloatField()
    length = models.FloatField()
    random_slug = models.SlugField(max_length=50, unique=True, default=random_slug_generator)
    bookmarked_users = models.ManyToManyField(User, related_name='bookmarked_videos', blank=True)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)
    audio = models.URLField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    
    def __str__(self):
        # This function should only be defined once.
        return f"{self.movie.title} - Video"

    def audio_url(self):
        # Ensures the method returns a URL path for the audio file
        s3_url = "https://filmfluency.fra1.cdn.digitaloceanspaces.com/"
        return s3_url + quote(self.audio)

    def video_url(self):
        # Ensures the method returns a URL path for the video file
        s3_url = "https://filmfluency.fra1.cdn.digitaloceanspaces.com/"

        return s3_url + quote(self.video)
     
    def thumbnail_url(self):
        # Ensures the method returns a URL path for the thumbnail
        s3_url = "https://filmfluency.fra1.cdn.digitaloceanspaces.com/"
        
        return s3_url + quote(self.thumbnail.url)

    def transcript(self):
        """Read from postgress database"""
        return self.text
        
    def translation(self, language="ar"):
        """Read from postgress database"""
        # TODO: Implement the translation method
        pass
        
        
    def getAllbookmarks(self):
        return self.bookmarked_users.all()


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
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}"


