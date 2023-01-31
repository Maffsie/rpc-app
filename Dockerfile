FROM python:3.11-alpine AS build

# i686 (and possibly other uncommon architectures?) require
#  build-time dependencies.
# Since this is split into a two-stage build now, don't need
#  to check the architecture.
# For posterity, the architecture check was: sh -c '[ `uname -m` == "i686" ]' && ...
RUN apk add -t build-deps \
		alpine-sdk \
    	make && \
    apk add -t build-deps-py3-pillow \
		freetype-dev \
		jpeg-dev \
    	zlib-dev
RUN mkdir -p /app/resources && \
	pip install -U pipenv && \
	chown -R nobody:daemon /app

USER nobody:daemon
WORKDIR /app

COPY --chown=nobody:daemon Makefile /app/
COPY --chown=nobody:daemon resources.default /app/resources.default

COPY --chown=nobody:daemon Pipfile /app/
COPY --chown=nobody:daemon requirements /app/

RUN make requirements

FROM python:3.11-alpine as release
USER root:root
# Is it psychopathic to use make for everything? probably
#  will that stop me? absolutely not.
RUN apk add -t runtime-deps \
      freetype jpeg \
      make && \
    apk add -t healthcheck-deps \
      curl && \
    pip install -U pipenv && \
    mkdir /conf && \
    chown nobody:daemon /conf

USER nobody:daemon

COPY --from=build --chown=nobody:daemon /app /app
WORKDIR /app

COPY --chown=nobody:daemon RPC /app/RPC
COPY --chown=nobody:daemon gunicorn_config.py /app/

# you have encountered my trap card (killing myself as soon as something goes wrong)
RUN sh -c '[ `find /app ! \( -user nobody -o -group daemon \) | wc -l` -eq 0 ]'

VOLUME [ "/app/resources", "/conf" ]
EXPOSE 8080
HEALTHCHECK --interval=10s \
            --timeout=1s \
            --start-period=10s \
            --retries=3 \
            CMD [ "make", "healthcheck" ]

CMD [ "make", "gunicorn-run" ]

LABEL org.opencontainers.image.url="https://github.com/Maffsie/rpc-app" \
			org.opencontainers.image.source="https://github.com/Maffsie/rpc-app.git" \
			org.opencontainers.image.name="RPC-App" \
			org.opencontainers.image.description="an api server, but bad!"
