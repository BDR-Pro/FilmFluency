# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    ffmpeg\
    python3-dev \
    musl-dev



# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

RUN python FilmFluency/manage.py makemigrations && \
    python FilmFluency/manage.py migrate && \
    python FilmFluency/manage.py check

# Define environment variable
ENV NAME World

# Run clipsmaker.py if the RUN_CLIPMAKER variable is set to "yes",
# otherwise run the Django development server
CMD if [ "$RUN_CLIPMAKER" = "yes" ]; \
    then python FilmFluency/clipsmaker.py; \
    else python FilmFluency/manage.py runserver 0.0.0.0:8000; \
    fi
