FROM python:3.13-slim

ARG BUILD_NO_CACHE=dev
ENV BUILD_NO_CACHE=${BUILD_NO_CACHE}

WORKDIR /usr/src/app

COPY pyproject.toml .
COPY alembic.ini .
COPY alembic ./alembic
COPY src ./src
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN pip install --no-cache-dir "./"

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
