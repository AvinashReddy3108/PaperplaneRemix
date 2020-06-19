FROM python:3.8-slim-buster

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
        atomicparsley \
        neofetch \
        && rm -rf /var/lib/apt/lists /var/cache/apt/archives /tmp

COPY . /usr/src/app/PaperplaneRemix/
WORKDIR /usr/src/app/PaperplaneRemix/

# "Dirty Fix" for Heroku Dynos to track updates via 'git'.
# Fork/Clone maintainers may change the clone URL to match
# the location of their repository. [#GodDamnItHeroku!]
RUN if [ ! -d /usr/src/app/PaperplaneRemix/.git ] ; then \
    git clone "https://github.com/AvinashReddy3108/PaperplaneRemix.git" /tmp/dirty/PaperplaneRemix/; \
    cp -a /tmp/dirty/PaperplaneRemix/. /usr/src/app/PaperplaneRemix/; \
    rm -rf /tmp/dirty/PaperplaneRemix/; \
    fi

RUN python3 -m pip install --no-warn-script-location --no-cache-dir --upgrade -r requirements.txt

ENTRYPOINT ["python", "-m", "userbot"]
