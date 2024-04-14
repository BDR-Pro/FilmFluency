from django.db import models
from django.contrib.auth.models import User
from learning.models import Video, Movie

class UserProgress(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_level = models.IntegerField(default=1)
    points = models.IntegerField(default=0)
    paid_user = models.BooleanField(default=False)
    highest_score = models.IntegerField(default=0)
    joined_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    favourite_movies = models.ManyToManyField(Movie, related_name='favourite_of')
    known_languages = models.ManyToManyField('learning.Language', related_name='known_by')
    community = models.ManyToManyField('learning.Community', related_name='community_of')
    videos_watched = models.ManyToManyField(Video, related_name='watched_by')
    posts = models.ManyToManyField('learning.Post', related_name='posted_by')
    comments = models.ManyToManyField('learning.Comment', related_name='commented_by')
    likes = models.ManyToManyField('learning.Post', related_name='liked_by')
    dislikes = models.ManyToManyField('learning.Post', related_name='disliked_by')
    bookmarks = models.ManyToManyField('learning.Post', related_name='bookmarked_by')
    notifications = models.ManyToManyField('learning.Notification', related_name='notified_to')
    friends = models.ManyToManyField('self', symmetrical=True, related_name='friends_with')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    cover_picture = models.ImageField(upload_to='cover_pictures/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    def next_level_points(self):
        """ Calculate points needed for the next level dynamically. """
        return (self.points / 2) * self.user_level

    @property
    def completed_videos_count(self):
        return self.videos_watched.count()

    @property
    def percentage_movies_completed(self):
        total_movies = Movie.objects.count()
        watched_movies = self.videos_watched.values_list('movie', flat=True).distinct().count()
        return (watched_movies / total_movies) * 100 if total_movies > 0 else 0

    @property
    def average_complexity(self):
        if self.videos_watched.count() > 0:
            return self.videos_watched.aggregate(models.Avg('complexity'))['complexity__avg']
        return 0

class LeaderboardEntry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    class Meta:
        ordering = ['-score']
