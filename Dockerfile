FROM python:3.9-slim-buster
USER root

RUN apt-get update ; apt-get install -y fonts-ipaexfont

RUN mkdir -p /root/src \
    && mkdir -p /root/resources \
    && mkdir -p /root/output

WORKDIR /root

RUN python3 -m pip install --upgrade pip  \
    && pip install numpy matplotlib

ARG mplrc=/usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/matplotlibrc
RUN sed -i 's/#font.family:  sans-serif/font.family:   IPAexGothic/g' "$mplrc"

