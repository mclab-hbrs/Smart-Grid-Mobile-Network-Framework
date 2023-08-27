FROM python:3.7
ADD ./ work/
WORKDIR /work

# Install swig and update apt
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install build-essential python3 iputils-ping

RUN pip3 install websocket-client
