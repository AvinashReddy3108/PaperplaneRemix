# syntax=docker/dockerfile:1
##
## PaperplaneRemix - A modular Telegram selfbot script
## Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
##
## SPDX-License-Identifier: GPL-3.0-or-later
##
FROM python:3-slim

# Sane Environment variables
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

# APT Packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl g++ git libjpeg62-turbo-dev libwebp-dev ffmpeg neofetch zlib1g-dev && \
    apt-get clean

# Virtual Environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install PIP packages
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip wheel setuptools && \
    python -m pip install --no-cache-dir --upgrade -r requirements.txt && \
    rm -rf /tmp/*

WORKDIR /app/src

# Bundle sauce for obvious reasons
COPY . .

# "Dirty Fix" for some PaaS Runners to track updates via 'git'.
# Fork/Clone maintainers may change the clone URL to match the location of their repository.
RUN if [ ! -d .git ] ; then \
        git clone --no-checkout "https://github.com/AvinashReddy3108/PaperplaneRemix.git" /tmp/dirty/PaperplaneRemix/ && \
        mv -u /tmp/dirty/PaperplaneRemix/.git /PaperplaneRemix && rm -rf /tmp/*; \
    fi

ENTRYPOINT ["python", "-m", "userbot"]
