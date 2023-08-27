FROM python:3.6.9
ADD ./ work/
WORKDIR /work
ENV PYTHONPATH "${PYTHONPATH}:/work"

# Install swig and update apt
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install make cmake build-essential python3 python3-contextlib2 iputils-ping

# Make dir and make lib
RUN cd /work/lib60870/lib60870-C && \
    cmake . && \
    make && \
    make install && \
    ldconfig

RUN cd /work/lib60870/lib60870-Python && \
    pip3 install -e .

RUN cd /work && \
    chmod 777 *

RUN pip3 install flask