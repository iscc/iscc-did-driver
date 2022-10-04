FROM python:3.9 AS builder

ARG POETRY_VERSION=1.2.1

# Disable stdout/stderr buffering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

# Disable some obvious pip functionality
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1

# Configure poetry
ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_PATH=/venvs


# Install Poetry
RUN pip install -U pip wheel setuptools && \
  pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

#
# prod-build
#

FROM builder AS prod-build

# Create virtualenv and install dependencies
RUN python -m venv /venv && . /venv/bin/activate && poetry install --only=main --no-root

COPY . /app/


#
# prod-runtime
#

FROM python:3.9-slim AS prod-runtime

LABEL org.opencontainers.image.source=https://github.com/iscc/iscc-did-driver

# Disable stdout/stderr buggering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV=/venv

ENV PORT=8080

COPY --from=prod-build /app /app
COPY --from=prod-build /venv /venv

WORKDIR /app

EXPOSE 8080

CMD ["gunicorn", "iscc_did_driver.main:app", "-k", "uvicorn.workers.UvicornWorker"]
