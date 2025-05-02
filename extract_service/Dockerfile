FROM python:3.11.2-slim

RUN mkdir ./extract_service
WORKDIR ./extract_service

RUN pip install --upgrade pip

COPY ./extract_service/* .

RUN mkdir common
COPY ./common common

RUN pip install -r requirements.txt

CMD ["python", "app.py"]

