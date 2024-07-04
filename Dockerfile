# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage caching
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose port 9111 for the Flask app
EXPOSE 9111

# Define environment variable
ENV FLASK_APP=run.py

# Run the command to start the Flask app
CMD ["python", "-u", "run.py"]

