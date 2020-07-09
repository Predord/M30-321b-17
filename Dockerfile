FROM python:latest
COPY task1/ /usr/pril/src
WORKDIR /usr/pril/src/task1
RUN apt-get update && apt-get install -y python3-pip && pip3 install matplotlib influxdb loguru flask paho-mqtt
CMD ["python3", "server.py"]