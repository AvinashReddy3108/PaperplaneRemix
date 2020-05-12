FROM python:3.8-slim-buster

ENV PIP_NO_CACHE_DIR 1

RUN apt update && apt upgrade -y && \
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
    && rm -rf /var/lib/apt/lists /var/cache/apt/archives /tmp

COPY . /usr/src/app/PaperplaneRemix
WORKDIR /usr/src/app/PaperplaneRemix/

RUN python3 -m pip install --no-warn-script-location --no-cache-dir --upgrade -r requirements.txt

ENTRYPOINT ["python", "-m", "userbot"]
