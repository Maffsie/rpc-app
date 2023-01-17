FROM python:3.11-alpine

# Is it psychopathic to use make for everything? probably
#  will that stop me? absolutely not.
RUN apk add -t runtime-deps make && \
    mkdir /app

RUN pip install -U pipenv

RUN chown -R nobody:daemon /app
USER nobody:daemon

WORKDIR /app

COPY --chown=nobody:daemon Pipfile /app/
COPY --chown=nobody:daemon requirements /app/
COPY --chown=nobody:daemon Makefile /app/

RUN mkdir /app/.venv && \
    make requirements

COPY --chown=nobody:daemon resources /app/resources.default
COPY --chown=nobody:daemon RPC /app/RPC
COPY --chown=nobody:daemon gunicorn_config.py /app/

# you have encountered my trap card (killing myself as soon as something goes wrong)
RUN find /app -not -user nobody -or -not -group daemon || exit 0 && exit 1

VOLUME /app/resources

CMD [ "make", "gunicorn-run" ]
