FROM debian:buster

RUN mkdir /app

RUN apt-get update
RUN apt-get install -y nano htop bmon ncdu net-tools
RUN apt-get install -y python3 python3-pip nginx

RUN pip3 install requests

RUN mkdir /app/logs
ADD src /app

WORKDIR /app

CMD ["python3", "."]
