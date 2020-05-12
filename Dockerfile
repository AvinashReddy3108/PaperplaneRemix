FROM python:3.8-slim-buster

RUN apt update; apt upgrade -y; \
    apt install -y \
    bash \
    curl \
    ffmpeg \
    gcc \
    git \
    libffi-dev \
    libjpeg-dev \
    libjpeg62-turbo-dev \
    libwebp-dev \
    linux-headers-amd64 \
    musl \
    musl-dev \
    neofetch \
    rsync \
    zlib1g \
    zlib1g-dev

COPY . /tmp/userbot_local
WORKDIR /usr/src/app/PaperplaneRemix/

RUN git clone https://github.com/AvinashReddy3108/PaperplaneRemix.git /usr/src/app/PaperplaneRemix/
RUN rsync --ignore-existing --recursive /tmp/userbot_local/ /usr/src/app/PaperplaneRemix/

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-warn-script-location --no-cache-dir --upgrade -r requirements.txt

RUN apt clean; apt autoclean
RUN rm -rf /tmp/* /var/lib/apt/lists/* /var/cache/apt/archives/*
CMD ["python", "-m", "userbot"]
