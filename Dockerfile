FROM python:3.7-alpine as base

RUN apk --update add \
    libressl-dev \
    python3 python3-dev gcc \
    gfortran musl-dev \
    libffi-dev bash nano \
    build-base \
    jpeg-dev \
    zlib-dev \
    ffmpeg \
    imagemagick

# Install fonts
RUN apk --no-cache add font-noto && fc-cache -f

RUN pip install --upgrade pip
RUN pip install --upgrade google-api-python-client
RUN pip install --upgrade google-auth-oauthlib google-auth-httplib2

ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt --no-cache-dir

EXPOSE 80


