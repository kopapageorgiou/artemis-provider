FROM python:3.11

WORKDIR /root/service
COPY app/. .
COPY requirements.txt /root/service/
COPY app/rootKeySSL.crt /usr/local/share/ca-certificates/extra/
COPY app/orbitdb.crt /usr/local/share/ca-certificates/extra/
COPY app/chained.crt /usr/local/share/ca-certificates/extra/
RUN update-ca-certificates
#RUN pip install --cert /etc/ssl/certs/X509Certificate.pem
#RUN bash -c "echo export \"REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates\" >> ~/.bashrc ; source ~/.bashrc"

RUN pip install -r requirements.txt
# RUN git clone https://github.com/orbitdb/py-orbit-db-http-client.git
# WORKDIR /root/service/py-orbit-db-http-client
# RUN python setup.py install
# WORKDIR /root/service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]