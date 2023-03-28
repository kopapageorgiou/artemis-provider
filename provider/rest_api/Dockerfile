FROM python:3.11

WORKDIR /root/service

COPY app/. .
COPY requirements.txt /root/service/

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]