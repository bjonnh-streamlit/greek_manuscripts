FROM docker.io/library/python:3.11-slim
RUN apt update && apt install -y antiword git
RUN mkdir /app /data
RUN useradd -m nonroot
RUN chown nonroot /data
USER nonroot
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN pip install poetry
ENV PATH="${PATH}:/home/nonroot/.local/bin"
ENV SHELL="/usr/bin/bash"
RUN poetry config virtualenvs.create true \
    && poetry install --no-interaction --no-ansi
