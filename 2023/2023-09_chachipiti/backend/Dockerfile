FROM ubuntu:20.04

WORKDIR /app
CMD [ "bash" ]

RUN groupadd -g 1200 appuser && useradd -m -u 1200 -g appuser appuser

ENV DEBIAN_FRONTEND=noninteractive
RUN ln -sf /usr/share/zoneinfo/Europe/Madrid /etc/localtime


RUN apt-get update && \
    apt-get install -y gnupg wget curl unzip --no-install-recommends && \
    wget --no-check-certificate -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update -y && \
    apt-get install -y google-chrome-stable 

RUN apt-get update && apt-get install -y python3 python3-pip libnss3
# firefox-geckodriver

# COPY chromedriver /app/

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
RUN pip3 install selenium

COPY *.py /app/

RUN chown appuser:appuser /app -R && chmod 755 /app -R
