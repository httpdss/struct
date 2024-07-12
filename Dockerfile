# Use an official Python runtime as a parent image
FROM python:3.12.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Run your script when the container launches
ENTRYPOINT ["python", "struct_module/main.py"]
