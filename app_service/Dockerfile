FROM python:3.11.2-slim

RUN mkdir ./app
WORKDIR ./app

COPY ./app_service/* .

RUN mkdir common
COPY ./common common

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app.py"]