FROM python:3.12

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

RUN apt-get update

COPY requirements.txt /usr/src/app/

RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

COPY . /usr/src/app