# Dockerfile
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set environment variables (if needed)
ENV PYTHONUNBUFFERED=1

# Define the command to run the script
CMD ["python", "main.py"]
