FROM python:latest
COPY arbeiten/ /usr/pril/src/
WORKDIR /usr/pril/src/
RUN apt-get update && apt-get install -y python3-pip && pip3 install matplotlib influxdb loguru \
    && apt-get install -y python3-tk