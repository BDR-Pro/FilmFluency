from django.db import models
from django.contrib.auth.models import User
from learning.models import Video, Movie
import random
from django_countries.fields import CountryField
from api.upload_to_s3 import get_random_file

def default_profile_pic():
    return get_random_file('avatars')

def default_cover_pic():
    return get_random_file('covers')

def genrate_bio():
    #random bio generator from a list of bios
    bios = [
        "I am a language enthusiast and a movie buff!",
        "I love learning new languages and watching movies.",
        "I am a language learner and a movie lover.",
        "I enjoy learning new languages and watching movies.",
        "I am a polyglot and a cinephile."
    ]
    return random.choice(bios)

def upload_to(instance, filename):
    # This function generates a path like: 'profile_pictures/user_123/myphoto.jpg'
    return f'{instance._meta.app_label}/{instance._meta.model_name}/{instance.user.id}/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=255) 
    profile_picture = models.ImageField(upload_to='avatars/', default=default_profile_pic)
    cover_picture = models.ImageField(upload_to='covers/', default=default_cover_pic)
    bio = models.TextField(null=True, blank=True, default=genrate_bio)
    country = CountryField(blank_label='(select country)', null=True, blank=True, default='SA')
    language = models.ForeignKey('learning.Language', on_delete=models.SET_NULL, null=True, blank=True)
    favourite_languages = models.ManyToManyField('learning.Language', related_name='favourite_of', blank=True)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)
    posts = models.ManyToManyField('learning.Post', related_name='posted_by', blank=True)
    comments = models.ManyToManyField('learning.Comment', related_name='commented_by', blank=True)
    dislikes = models.ManyToManyField('learning.Post', related_name='disliked_by', blank=True)
    likes = models.ManyToManyField('learning.Post', related_name='liked_by', blank=True)
    bookmarks = models.ManyToManyField('learning.Post', related_name='bookmarked_by', blank=True)
    last_login = models.DateTimeField(auto_now=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    paid_user = models.BooleanField(default=False)
    reports = models.ManyToManyField('users.Report', related_name='reported_by', blank=True) 
   
    def __str__(self):
        return f"{self.nickname} - {self.user.username}"

    def get_friends(self):
        return self.friends.all()
    
    def get_avatar(self):
        return self.profile_picture.url.split('?')[0]
    
    def get_cover(self):
        return self.cover_picture.url.split('?')[0]

class UserProgress(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_level = models.IntegerField(default=1)
    points = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    watched_movies = models.ManyToManyField(Movie, related_name='watched_by',default=0)
    favourite_movies = models.ManyToManyField(Movie, related_name='favourite_of',default=0)
    known_languages = models.ManyToManyField('learning.Language', related_name='known_by',default=0)
    community = models.ManyToManyField('learning.Community', related_name='community_of',default=0)
    videos_watched = models.ManyToManyField(Video, related_name='watched_by',default=0)

    def next_level_points(self):
        """Calculate points needed for the next level, with a difficulty multiplier."""
        next_level = self.user_level + 1
        multiplier = 10  # Adjust the multiplier to set the difficulty curve
        points_required = (next_level ** 2) * multiplier
        return points_required


    @property
    def completed_videos_count(self):
        return self.videos_watched.count()

    @property
    def percentage_movies_completed(self):
        total_movies = Movie.objects.count()
        watched_movies = self.videos_watched.values_list('movie', flat=True).distinct().count()
        return (watched_movies / total_movies) * 100 if total_movies > 0 else 0
    
    @property
    def average_score(self):
        if self.videos_watched.count() > 0:
            return self.videos_watched.aggregate(models.Avg('complexity'))['complexity__avg']
        return 0
    
    @property
    def percentage_movies_watched(self):
        total_movies = Movie.objects.count()
        watched_movies = self.watched_movies.count()
        return (total_movies/watched_movies) * 100 if watched_movies > 0 else 0
    
    @property
    def check_and_update_level(self):
        if self.points >= self.next_level_points():
            self.user_level += 1
            self.save()
            return True
        return False

    @property
    def average_complexity(self):
        if self.videos_watched.count() > 0:
            return self.videos_watched.aggregate(models.Avg('complexity'))['complexity__avg']
        return 0
    
    @property
    def latest_movies(self):
        return self.watched_movies[:5]
    
    @property
    def latest_watched_videos(self):
        return self.videos_watched[:5]
    
    def __str__(self):
        return self.user.userProfile.nickname

class LeaderboardEntry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['-score']

    def __str__(self):
        return self.user.userProfile.nickname
    
    def update_score(self, points):
        self.score += points
        self.save()
        return self.score
    
    def update_level(self):
        if self.score >= (self.level * 100):
            self.level += 1
            self.save()
            return self.level
        return self.level
    
    def getTopUsers():
        return LeaderboardEntry.objects.all()[:10]
    
    def getTopUserRank(user):
        return LeaderboardEntry.objects.filter(score__gt=user.score).count() + 1  




from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,default=1)
    object_id = models.PositiveIntegerField(default=1)
    content_object = GenericForeignKey('content_type', 'object_id')
    report = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.report
