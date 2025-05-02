FROM python:3.11.2-slim

RUN mkdir ./ranking_service
WORKDIR ./ranking_service

RUN pip install --upgrade pip

COPY ./ranking_service/* .

RUN mkdir common
COPY ./common common


RUN pip install -r requirements.txt

CMD ["python", "app.py"]

