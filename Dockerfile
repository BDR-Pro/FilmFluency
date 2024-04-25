# Use an official Python runtime as a parent image
FROM python:3.13.0a6-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Git, necessary libraries, and system utilities
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    musl-dev \
    git

# Upgrade pip
RUN pip install --upgrade pip

RUN pip install gunicorn 

RUN pip install --upgrade setuptools

# Clone the specific Git repository
# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose port 8000 to the outside once the container has launched
EXPOSE 8000

# Define environment variable
ENV NAME World

# Define the command to run your Django application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "FilmFluency.wsgi:application"]
