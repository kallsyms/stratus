FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip gunicorn \
    libeccodes-dev gdal-bin libgdal-dev

RUN mkdir /opt/wx_explore
WORKDIR /opt/wx_explore

COPY requirements.txt setup.py /opt/wx_explore

RUN pip3 install -r requirements.txt

COPY wx_explore /opt/wx_explore/wx_explore

RUN chmod +x /opt/wx_explore/wx_explore/common/seed.py
RUN pip3 install -e .

COPY data /opt/wx_explore/data

EXPOSE 8080

CMD ["gunicorn3", "-b:8080", "--preload", "--workers=4", "wx_explore.web.app:app"]
