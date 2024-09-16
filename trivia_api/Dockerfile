# Base image with Python 3.10
FROM python:3.10-slim

# Set the Current Working Directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python scripts and configuration files into the container
COPY trivia_generator_api.py trivia_generator.py config.yaml ./

# Expose the port that the FastAPI app will be using
EXPOSE 9000

# Command to start the FastAPI application
CMD ["uvicorn", "trivia_generator_api:app", "--host", "0.0.0.0", "--port", "9000"]
