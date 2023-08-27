FROM python:3.7
ADD ./ work/
WORKDIR /work
ENV PYTHONPATH "${PYTHONPATH}:/work"

# Install MQTT Client lib
RUN pip3 install paho-mqtt flask
