FROM python:3.11-alpine

# Is it psychopathic to use make for everything? probably
#  will that stop me? absolutely not.
RUN apk add -t runtime-deps make && \
    mkdir /app && \
    pip install -U pipenv

COPY . /app/
WORKDIR /app

RUN mkdir /app/.venv && \
    make requirements

CMD [ "make", "gunicorn-run" ]
