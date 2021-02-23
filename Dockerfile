## STILL IN THE TESTING STAGE
FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7 as base

#FROM python:3.7-alpine as base

RUN apk --update add \
    python3 python3-dev gcc \
    gfortran musl-dev \
    libffi-dev bash nano \
    build-base \
    jpeg-dev \
    zlib-dev \
    ffmpeg \
    imagemagick

#Install postgres dependencies
#RUN apk add --no-cache postgresql-libs && \
#    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

# Install fonts
RUN apk --no-cache add font-noto && \
    fc-cache -f

RUN pip install --upgrade pip
RUN pip install --upgrade google-api-python-client
RUN pip install --upgrade google-auth-oauthlib google-auth-httplib2

ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt --no-cache-dir
#RUN apk --purge del .build-deps


################# DEBUG IMAGE      ##################
FROM base as debug
EXPOSE 80
RUN pip install ptvsd
WORKDIR /usr/src/

#RUN python manage.py db init && \
#    python manage.py db migrate && \
#    python manage.py db upgrade 

#CMD python -m ptvsd --host 0.0.0.0 -port 5678 --wait --multiprocess -m flask run --host=0.0.0.0 -p 5000

################# PRODUCTION IMAGE ##################
#FROM base as prod

#CMD flask run -h=0.0.0 -p 5000
