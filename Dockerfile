# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Git, necessary libraries, and system utilities
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    ffmpeg \
    python3-dev \
    musl-dev \
    git

# Upgrade pip
RUN pip install --upgrade pip

RUN git clone https://github.com/BDR-Pro/FilmFluency.git .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose port 8000 to the outside once the container has launched
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run clipsmaker.py if the RUN_CLIPMAKER variable is set to "yes",
# otherwise run the Django development server
CMD if [ "$RUN_CLIPMAKER" = "yes" ]; \
    then python FilmFluency/clipsmaker.py; \
    else python FilmFluency/manage.py runserver 0.0.0.0:8000; \
    fi
