FROM python:3.12.1-alpine

WORKDIR /app
RUN apk add build-base curl
COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

COPY ./src ./

CMD python3 -u main.py
