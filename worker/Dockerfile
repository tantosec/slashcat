ARG WORKER_BASE=dizcza/docker-hashcat:cuda
FROM ${WORKER_BASE}


# Install python3.12
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3.12 python3.12-dev
RUN wget -O - https://bootstrap.pypa.io/get-pip.py | python3.12

RUN apt-get install -y curl

# Worker application
WORKDIR /app
COPY ./requirements.txt ./
RUN python3.12 -m pip install -r requirements.txt

COPY ./src ./

RUN mkdir /storage

CMD python3.12 -u main.py
