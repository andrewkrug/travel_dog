# syntax=docker/dockerfile:1
FROM python:3.10.7 AS stage1

RUN mkdir -p /app/travel_dog
RUN apt update && apt install nmap wget inetutils-ping wkhtmltopdf git -y
RUN pip3 install poetry --timeout 60 # because I built this on a plane

FROM stage1 AS stage2

WORKDIR /app
RUN touch /app/travel_dog/.empty
ADD pyproject.toml poetry.lock README.md /app/
RUN poetry install --no-root

FROM stage2
ADD . /app/
WORKDIR /app/travel_dog

CMD poetry run ddtrace-run gunicorn --bind 0.0.0.0:80 wsgi:app --reload 