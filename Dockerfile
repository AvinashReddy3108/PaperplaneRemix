FROM python:3.8-alpine

RUN apk add --no-cache --update \
    bash \
    curl \
    ffmpeg \
    gcc \
    git \
    libffi-dev \
    libjpeg \
    libjpeg-turbo-dev \
    libwebp-dev \
    linux-headers \
    musl \
    musl-dev \
    neofetch \
    rsync \
    zlib \
    zlib-dev

COPY . /tmp/userbot_local
WORKDIR /usr/src/app/PaperplaneRemix/

RUN git clone -b staging https://github.com/AvinashReddy3108/PaperplaneRemix.git /usr/src/app/PaperplaneRemix/
RUN rsync --ignore-existing --recursive /tmp/userbot_local/ /usr/src/app/PaperplaneRemix/

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-warn-script-location --no-cache-dir --upgrade -r requirements.txt

RUN rm -rf /var/cache/apk/* /tmp/*
CMD ["python", "-m", "userbot"]
