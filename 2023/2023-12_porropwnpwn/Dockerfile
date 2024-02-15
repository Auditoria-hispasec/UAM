FROM ubuntu:22.04

run apt-get update
run apt-get install -y bash

RUN mkdir /app
WORKDIR /app
RUN adduser appuser 
COPY ynetd /app/
COPY src/flag1.txt src/flag2.txt /app/
RUN chmod 755 /app -R
RUN chmod 777 /app/hof.txt

COPY src/main src/main.b64 /app
RUN chmod 755 /app/main* -R

