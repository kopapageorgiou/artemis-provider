FROM python:3.11

#Add file watcher
RUN apt-get update && apt-get install -y entr
WORKDIR /root/mqtt_listener
COPY requirements.txt /root/mqtt_listener/

RUN pip install -r requirements.txt
COPY files/. .
CMD find . -name "*.py" | entr -r python -u mqtt_listener.py
#CMD ["python3", "-u", "./mqtt_listener.py"]