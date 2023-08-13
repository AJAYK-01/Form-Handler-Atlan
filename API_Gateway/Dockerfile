# Use an official Python runtime as a parent image
FROM python:3.10.8-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Set environment variables from .env file
RUN set -a; source .env; set +a

# Make wait for db script executable
RUN chmod +x ./wait-for-db.sh

# Run main.py when the container launches but wait for database to launch
CMD ["./wait-for-db.sh", "database:5432", "--", "python", "main.py"]
