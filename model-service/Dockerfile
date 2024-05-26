# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the model files and app script
COPY . .

# Expose the port for the Flask app
EXPOSE 8080

# Run the app
CMD ["python", "app.py"]
