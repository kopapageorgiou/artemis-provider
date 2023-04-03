FROM python:3.11

WORKDIR /root/service
COPY app/. .
COPY requirements.txt /root/service/
COPY app/X509Certificate.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

RUN pip install -r requirements.txt
# RUN git clone https://github.com/orbitdb/py-orbit-db-http-client.git
# WORKDIR /root/service/py-orbit-db-http-client
# RUN python setup.py install
# WORKDIR /root/service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]