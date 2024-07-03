# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Install the Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 9111 for the Flask app
EXPOSE 9111

# Define environment variable
ENV FLASK_APP=run.py

# Run the command to start the Flask app
CMD ["python", "-u", "run.py"]
