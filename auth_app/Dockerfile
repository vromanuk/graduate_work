FROM python:3.9-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN useradd -ms /bin/bash auth_user
WORKDIR /src

# Install Poetry
RUN apt-get update && apt-get install -y curl netcat && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | \
 POETRY_HOME=/opt/poetry python3.9 && \
 cd /usr/local/bin && \
 ln -s /opt/poetry/bin/poetry && \
 poetry config virtualenvs.create false && rm -rf /var/lib/apt/lists/*

# Copy using poetry.lock* in case it doesn't exist yet
COPY --chown=auth_user:auth_user ["./auth_app/pyproject.toml", "./auth_app/poetry.lock*", "./auth_app/patched.py", "/src/"]
EXPOSE 5000

RUN poetry install --no-root

COPY --chown=auth_user:auth_user ["./auth_app/", "/src"]

RUN chmod +x src/scripts/wait_to_start.sh
USER auth_user

ENTRYPOINT ["src/scripts/wait_to_start.sh"]
