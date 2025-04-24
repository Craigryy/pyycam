# Use an official Python runtime based on Debian 10 "buster" as a parent image.
ARG PYTHON_VERSION=3.10-slim-buster
FROM python:$PYTHON_VERSION

# Port used by this container to serve HTTP.
EXPOSE 8000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

ARG BUILD_ENV=dev
ARG POETRY_VERSION=1.6.1

ENV BUILD_ENV="$BUILD_ENV"
ENV PYTHON_VERSION="$PYTHON_VERSION"

LABEL pycam.distro.name=linux
LABEL pycam.distro.release=debian
LABEL pycam.image.name=pycam-web
LABEL pycam.build.env="$BUILD_ENV"
LABEL pycam.python.version="$PYTHON_VERSION"

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadbclient-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    graphviz \
 && rm -rf /var/lib/apt/lists/*

# Install the application server.
RUN pip install "gunicorn==20.0.4"

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Install flake8 for linting
RUN pip install flake8

# setting locales
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Copy poetry configuration files
COPY ./pycam/poetry.lock ./pycam/pyproject.toml /app/

# Install dependencies as root
RUN poetry config virtualenvs.create false && \
    if [ "$BUILD_ENV" = "dev" ]; then \
        poetry install --no-interaction --no-ansi; \
    else \
        poetry install --only main --no-interaction --no-ansi; \
    fi

# Copy scripts first (they need to be available before copying other code)
COPY ./scripts /scripts
RUN chmod -R +x /scripts

# Copy application code
COPY . /app

# Now create user and group after all installations are complete
RUN adduser --disabled-password --gecos '' pycam && \
    groupadd docker && \
    usermod -aG docker pycam && \
    # grant newly created user permissions on app directory
    chown -R pycam:pycam /app/ && \
    chown -R pycam:pycam /scripts

# Add scripts directory to PATH
ENV PATH="/scripts:$PATH"

# Change user to pycam only after all installations are complete
USER pycam

# Set working directory to where manage.py is located
WORKDIR /app/pycam

# Default command - use run.sh script
CMD ["/scripts/run.sh"]
