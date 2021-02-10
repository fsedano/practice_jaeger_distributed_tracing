FROM ubuntu:18.04
RUN apt-get update && apt-get install -y python3.8 python3-pip
WORKDIR /app
COPY app/requirements.txt /app
RUN pip3 install -r requirements.txt
COPY app/app.py /app
COPY bootstrap.sh /

CMD ["/bootstrap.sh"]