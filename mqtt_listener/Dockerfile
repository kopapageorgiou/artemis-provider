FROM python:3.11

#Add file watcher
RUN apt-get update && apt-get install -y entr
WORKDIR /root/mqtt_listener
COPY requirements.txt /root/mqtt_listener/

RUN pip install -r requirements.txt
COPY files/. .

# Set environment variable to run non-interactively
ENV TERM xterm


CMD find -name "*.py" | entr -rn python -u mqtt_listener.py
#CMD ["python3", "-u", "./mqtt_listener.py"]