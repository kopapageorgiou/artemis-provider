FROM python:3.11

WORKDIR /root/service
COPY requirements.txt /root/service/
#RUN pip install --cert /etc/ssl/certs/X509Certificate.pem
#RUN bash -c "echo export \"REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates\" >> ~/.bashrc ; source ~/.bashrc"

RUN pip install -r requirements.txt
COPY app/. .
# RUN git clone https://github.com/orbitdb/py-orbit-db-http-client.git
# WORKDIR /root/service/py-orbit-db-http-client
# RUN python setup.py install
# WORKDIR /root/service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]