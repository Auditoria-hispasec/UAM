FROM alpine:latest

RUN apk update && \
    apk add --no-cache python3 py3-pip bash

COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app
CMD ["bash -c sleep 100000"]
