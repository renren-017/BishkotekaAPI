FROM python:3.8.16-slim

ENV PYTHONUNBUFFERED 1

RUN mkdir /afisha
WORKDIR /afisha

# Update package lists, install build dependencies, and libpq
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        python3-dev \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Upgrade pip and install requirements
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Clean up unnecessary packages and cache to reduce image size
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
        gcc \
        libffi-dev \
        python3-dev \
        build-essential
