FROM --platform=linux/amd64 ubuntu:latest as builder

##### BEGIN SAT INSTALLATION ####

RUN apt-get update && apt-get -y upgrade && \
    apt-get -y install apt-utils gcc automake zlib1g-dev make g++ git curl unzip cmake software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get -y install python3.8 python3-pip

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install build-essential software-properties-common

RUN rm -r /var/lib/apt/lists/*

USER root

RUN git clone -b glucose-reboot https://github.com/audemard/glucose.git

RUN rm -rf /glucose/pfactory

RUN curl -L https://github.com/crillab/pfactory/releases/download/v2.0.0/pfactory-2.0.0.zip --output /tmp/pfactory.zip && cd /tmp && unzip pfactory.zip && mv pfactory-2.0.0 /glucose/pfactory && rm -r /tmp/pf*

RUN cd /glucose/pfactory && autoreconf --install && ./configure && make -j

RUN cd /glucose/simp && make rs -j

RUN apt-get update && apt-get install -y linux-tools-generic

# Add glucose to the path
ENV PATH="/glucose/simp:${PATH}"

#### END SAT INSTALLATION ####

#### BEGIN ASP INSTALLATION ####

# Set the working directory in the container to /learner_strips
WORKDIR /learner_strips

# Copy the current directory contents into the container at /learner_strips
COPY . /learner_strips

# Install any python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Build the strips program
WORKDIR /learner_strips/sat/src
RUN make






