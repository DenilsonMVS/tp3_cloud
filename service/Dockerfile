# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir redis

# Expose the port the app runs on
# EXPOSE 8050

# Command to run the application
CMD ["python", "app.py"]
