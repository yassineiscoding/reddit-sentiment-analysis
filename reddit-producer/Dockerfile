# Use the official Python image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install netcat for network checking
RUN apt-get update && apt-get install -y netcat-openbsd

# Copy the rest of the application code into the container
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the startup script
COPY startup.sh /app/startup.sh

# Make the startup script executable
RUN chmod +x /app/startup.sh

# Set the entry point to the startup script
ENTRYPOINT ["/app/startup.sh"]
