FROM python:3.9-slim-buster

ARG USERNAME=jobtime
ARG GROUPNAME=jobtime
ARG UID=1000
ARG GID=1000
ARG APP_DIR=/usr/local/jobtime
ARG MPLRC=/usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/matplotlibrc
ARG TIMEZONE=Asia/Tokyo

RUN groupadd -g "$GID" "$GROUPNAME" \
    && useradd -m -s /bin/bash -u "$UID" -g"$GID" "$USERNAME" \
    && mkdir -p "$APP_DIR" \
    && chown -R "$USERNAME" "$APP_DIR" \
    && apt-get update && apt-get install -y --no-install-recommends \
    fonts-ipaexfont \
    tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir \
    matplotlib==3.6.1 \
    chardet==5.2.0 \
    && sed -i 's/#font.family:  sans-serif/font.family:   IPAexGothic/g' "$MPLRC"

ENV TZ "$TIMEZONE"
USER "$USERNAME"
WORKDIR "$APP_DIR"

