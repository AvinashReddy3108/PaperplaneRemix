##
## PaperplaneRemix - A modular Telegram selfbot script
## Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
##
## SPDX-License-Identifier: GPL-3.0-or-later
##
FROM python:3.9-slim

RUN apt update && \
    apt upgrade -y && \
    apt install -y bash curl git libjpeg62-turbo-dev libwebp-dev ffmpeg neofetch

COPY . /usr/src/app/PaperplaneRemix/
WORKDIR /usr/src/app/PaperplaneRemix/

# "Dirty Fix" for Heroku Dynos to track updates via 'git'.
# Fork/Clone maintainers may change the clone URL to match
# the location of their repository. [#ThatsHerokuForYa!]
#RUN if [ ! -d /usr/src/app/PaperplaneRemix/.git ] ; then \
#    git clone --no-checkout "https://github.com/AvinashReddy3108/PaperplaneRemix.git" /tmp/dirty/PaperplaneRemix/ && \
#    mv -vu /tmp/dirty/PaperplaneRemix/.git /usr/src/app/PaperplaneRemix; \
#    fi

# Install PIP packages
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade -r requirements.txt

# Cleanup
RUN rm -rfv /var/lib/apt/lists /var/cache/apt/archives "$(pip cache dir)" /tmp/*

ENTRYPOINT ["python", "-m", "userbot"]
