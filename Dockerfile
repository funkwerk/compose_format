FROM alpine:3.11
MAINTAINER think@hotmail.de

ENV PYTHONUNBUFFERED=1

RUN \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

RUN pip install --no-cache-dir ruamel.yaml

COPY bin /bin
COPY compose_format /usr/lib/python3.8/site-packages/compose_format

RUN chmod +x /bin/compose_format

ENTRYPOINT ["python3", "/bin/compose_format"]
