FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add \
    python3 python3-dev gcc \
    gfortran musl-dev \
    libffi-dev openssl-dev bash nano \
    build-base \
    jpeg-dev \
    zlib-dev \
    ffmpeg \
    imagemagick

# Install fonts
RUN apk --no-cache add font-noto && \
    fc-cache -f

RUN pip install --upgrade pip
RUN pip install --upgrade google-api-python-client
RUN pip install --upgrade google-auth-oauthlib google-auth-httplib2

ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt
