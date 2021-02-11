FROM ubuntu:18.04
RUN apt-get update && apt-get install -y python3.8 python3-pip
RUN apt-get install -y inetutils-ping telnet wget
WORKDIR /app
COPY app/requirements.txt /app
RUN pip3 install -r requirements.txt
COPY app/app.py /app
COPY bootstrap.sh /

#CMD ["/bootstrap.sh"]
CMD ["/bin/bash", "-c", "sleep 9999999"]