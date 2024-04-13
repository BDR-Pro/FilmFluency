import sqlite3

def get_videos_by_complexity(max_complexity):
    conn = sqlite3.connect('english_learning.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM EnglishLearningVideos WHERE Complexity > ?', (max_complexity,))
    videos = cur.fetchall()
    conn.close()
    return videos

def get_videos_by_movie(movie_name):
    conn = sqlite3.connect('english_learning.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM EnglishLearningVideos WHERE Movie = ?', (movie_name,))
    videos = cur.fetchall()
    conn.close()
    return videos

def get_videos_by_length(max_length):
    conn = sqlite3.connect('english_learning.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM EnglishLearningVideos WHERE Length < ?', (max_length,))
    videos = cur.fetchall()
    conn.close()
    return videos

def get_unique_movies():
    conn = sqlite3.connect('english_learning.db')  
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT Movie FROM EnglishLearningVideos')
    movies = cur.fetchall()  
    conn.close()
    return [movie[0] for movie in movies]  


