FROM python:3.11-alpine

RUN apk add alpine-sdk make && \
    mkdir /app

WORKDIR /app

COPY . /app/
RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    cd /app && \
    make requirements.txt

CMD [ ".", "/app/venv/bin/activate", "&&", "gunicorn", "--chdir", "/app", "--worker-tmp-dir", "/dev/shm", "--config", "gunicorn_config.py", "RPC" ]
