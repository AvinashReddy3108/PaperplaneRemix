FROM python:3.8-slim-buster

ENV PIP_NO_CACHE_DIR 1
RUN set -euo pipefail
ENV DEBIAN_FRONTEND noninteractive

RUN apt update; apt upgrade -y; \
    apt install --no-install-recommends -y \
        bash \
        curl \
        ffmpeg \
        git \
        libjpeg-dev \
        libjpeg62-turbo-dev \
        libwebp-dev \
        linux-headers-amd64 \
        musl-dev \
        neofetch \
        rsync; \
    rm -rf /var/lib/apt/lists /var/cache/apt/archives /tmp

COPY . /tmp/userbot_local
WORKDIR /usr/src/app/PaperplaneRemix/

RUN git clone https://github.com/AvinashReddy3108/PaperplaneRemix.git /usr/src/app/PaperplaneRemix/
RUN rsync --ignore-existing --recursive /tmp/userbot_local/ /usr/src/app/PaperplaneRemix/

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-warn-script-location --no-cache-dir --upgrade -r requirements.txt

CMD ["python", "-m", "userbot"]
