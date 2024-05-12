# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /

# Copy the current directory contents into the container at /code
COPY . /

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Add wait-for-it.sh script
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the application with wait-for-it.sh
CMD ["sh", "-c", "wait-for-it.sh db:5431 -- python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
