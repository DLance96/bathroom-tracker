FROM python:3

RUN apt-get update && apt-get install libpq-dev

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

CMD /app/server.py
