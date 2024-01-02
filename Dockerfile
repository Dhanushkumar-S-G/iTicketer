FROM python:3.12

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY Pipfile /usr/src/app/

RUN pip install pipenv

RUN pipenv install

COPY . /usr/src/app