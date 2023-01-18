FROM python:3.11-alpine

# Is it psychopathic to use make for everything? probably
#  will that stop me? absolutely not.
RUN apk add -t runtime-deps make && \
    mkdir -p /app/resources

RUN pip install -U pipenv

RUN chown -R nobody:daemon /app
USER nobody:daemon

WORKDIR /app

COPY --chown=nobody:daemon Makefile /app/
COPY --chown=nobody:daemon resources.default /app/resources.default

COPY --chown=nobody:daemon Pipfile /app/
COPY --chown=nobody:daemon requirements /app/
RUN make requirements

COPY --chown=nobody:daemon RPC /app/RPC
COPY --chown=nobody:daemon gunicorn_config.py /app/

# you have encountered my trap card (killing myself as soon as something goes wrong)
RUN sh -c '[ `find /app ! \( -user nobody -o -group daemon \) | wc -l` -eq 0 ]'

VOLUME [ "/app/resources" ]
EXPOSE 8080
HEALTHCHECK --interval=10s \
            --timeout=1s \
            --start-period=10s \
            --retries=3 \
            CMD [ "make", "healthcheck" ]

CMD [ "make", "gunicorn-run" ]
