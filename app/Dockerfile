# Start with a Python image.
FROM python:3.6

RUN apt-get update && apt-get install -y postgresql-client cron

# For debugging
RUN apt-get install -y vim

# Some stuff that everyone has been copy-pasting
# since the dawn of time.
ENV PYTHONUNBUFFERED 1

# Copy all our files into the image.
RUN mkdir /code
WORKDIR /code
COPY . /code/

# Install our requirements.

RUN mkdir media
RUN mkdir media/database
RUN mkdir media/unapproved
RUN mkdir media/bulk

WORKDIR make_folder

RUN python make_folder.py

RUN cp -r DATA/* ../media/database/
RUN cp -r DATA/* ../media/bulk/

WORKDIR /code

# RUN mkdir protected
# RUN cp -r media/* protected/

RUN pip install -U pip
RUN pip install -Ur requirements.txt
WORKDIR /code/bookShelf

