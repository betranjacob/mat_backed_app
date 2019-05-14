FROM ubuntu:18.04
MAINTAINER Betran Jacob "betran@gmail.com"
RUN apt-get update -y && \  
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y mosquitto
COPY . /
WORKDIR /
RUN pip3 install -r requirements.txt
EXPOSE 8084
CMD mosquitto -d -v -p 8084 && python3 ./backend_server_app.py