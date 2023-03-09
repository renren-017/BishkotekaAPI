FROM python:3.8.16-slim

ENV PYTHONUNBUFFERED 1

RUN mkdir /afisha

WORKDIR /afisha

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt