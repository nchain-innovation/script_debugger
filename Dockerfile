FROM python:3.9-slim-buster  as base
ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/London
ENV DEBIAN_FRONTEND="noninteractive"
RUN  apt-get update && \
    apt-get install -y \
    python3-pip \
    docker.io\
    antlr4 \
    binutils \
    vim 

WORKDIR /app/src
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM base as release

WORKDIR /app/src

# Environment variable to detect we are in a docker instance
ENV APP_ENV=docker
CMD [ "python3", "debugger.py"]
