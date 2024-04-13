# views.py
from django.shortcuts import render
import sqlite3

def getAllVideos():
    """ Return all videos in the database. """
    db = sqlite3.connect('english_learning.db')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM EnglishLearningVideos')
    videos = cursor.fetchall()
    return videos

def getVideoById(video_id):
    """ Return a specific video by its ID. """
    db = sqlite3.connect('english_learning.db')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM EnglishLearningVideos WHERE ID = ?', (video_id,))
    video = cursor.fetchone()
    #add counter in trending movies table
    cursor.execute('SELECT * FROM TrendingMovies WHERE ID = ?', (video_id,))
    trending = cursor.fetchone()
    if trending:
        cursor.execute('UPDATE TrendingMovies SET Views = Views + 1 WHERE ID = ?', (video_id,))
    else:
        cursor.execute('INSERT INTO TrendingMovies (ID, Title, Views) VALUES (?, ?, 1)', (video[0], video[1]))
    db.commit()
    
    return video

def getTrendingMovies():
    """ Return all trending movies in the database. """
    db = sqlite3.connect('english_learning.db')
    cursor = db.cursor()
    # make table if not exists
    cursor.execute('CREATE TABLE IF NOT EXISTS TrendingMovies (ID INTEGER PRIMARY KEY, Title TEXT, Views INTEGER)')
    cursor.execute('SELECT * FROM TrendingMovies')
    movies = cursor.fetchall()
    return movies

def home(request):
    """ Render the homepage with introductory information. """
    return render(request, 'index.html',{'movies':getTrendingMovies()})

def video_list(request):
    """ Show a list of all videos sorted by complexity. """
    videos = getAllVideos().order_by('Complexity')
    return render(request, 'video_list.html', {'videos': videos})

def video_detail(request, video_id):
    """ Show details for a specific video, including related transcript and options. """
    video = getVideoById(video_id)
    return render(request, 'video_detail.html', {'video': video})
