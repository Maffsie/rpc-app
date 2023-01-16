FROM python:3.11-alpine

RUN apk add -t build-deps alpine-sdk make && \
    mkdir /app

COPY . /app/
WORKDIR /app
RUN make novenv-requirements && \
    apk del build-deps

CMD [ "gunicorn", "--chdir", "/app", "--config", "gunicorn_config.py", "RPC:create_app()" ]
