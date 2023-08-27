FROM python:3.7
ADD ./ work/
WORKDIR /work
COPY ./libiec61850 /work/libiec61850
ENV PYTHONPATH "${PYTHONPATH}:/work"

# Install swig and update apt
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install cmake build-essential python3 swig

# Make dir and make lib
RUN cd /work/libiec61850 && \
    mkdir build && \
    cd build && \
    cmake -DBUILD_PYTHON_BINDINGS=ON .. && \
    make && \
    cp /work/libiec61850/build/pyiec61850/_iec61850.so /work && \
    cp /work/libiec61850/build/pyiec61850/iec61850.py /work && \
    chmod 0777 /work

RUN chmod +x /work/_iec61850.so

RUN pip3 install flask
