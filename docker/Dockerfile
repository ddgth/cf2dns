# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

LABEL maintainer="tongdongdong@outlook.com"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /cf2dns

COPY . /cf2dns

# Install pip requirements
RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt



# Creates a non-root user with an explicit UID and adds permission to access the /app folder
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

CMD ["python3", "src/main.py"]
