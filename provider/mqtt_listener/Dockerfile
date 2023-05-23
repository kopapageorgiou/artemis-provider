FROM python:3.11

WORKDIR /root/mqtt_listener
COPY requirements.txt /root/mqtt_listener/

RUN pip install -r requirements.txt
COPY files/. .

CMD ["python3", "-u", "./mqtt_listener.py"]