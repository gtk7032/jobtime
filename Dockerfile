FROM python:3.9-slim-buster

ARG USERNAME=jobtime
ARG GROUPNAME=jobtime
ARG UID
ARG GID
ARG APP_DIR=/usr/local/jobtime
ARG mplrc=/usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/matplotlibrc

RUN groupadd -g "$GID" "$GROUPNAME" \
    && useradd -m -s /bin/bash -u "$UID" -g"$GID" "$USERNAME" \
    && mkdir -p "$APP_DIR" \
    && chown -R "$USERNAME" "$APP_DIR" \
    && apt-get update && apt-get install -y --no-install-recommends \
    fonts-ipaexfont \
    tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir numpy matplotlib  \
    && sed -i 's/#font.family:  sans-serif/font.family:   IPAexGothic/g' "$mplrc"

ENV TZ Asia/Tokyo
USER "$USERNAME"
WORKDIR "$APP_DIR"

