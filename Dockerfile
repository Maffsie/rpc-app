FROM python:3.11-alpine

# Is it psychopathic to use make for everything? probably
#  will that stop me? absolutely not.
RUN apk add -t runtime-deps make && \
    mkdir /app && \
    chown -R nobody:daemon /app \

RUN pip install -U pipenv

USER nobody:daemon

WORKDIR /app

COPY Pipfile /app/
COPY requirements /app/
COPY Makefile /app/

RUN mkdir /app/.venv && \
    make requirements

COPY resources /app/resources.default
COPY RPC /app/
COPY gunicorn_config.py /app/

VOLUME /app/resources

CMD [ "make", "gunicorn-run" ]
