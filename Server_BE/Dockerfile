FROM python:3.12.3-alpine

# Install only essential build dependencies, and remove them after building
RUN apk add --no-cache \
    make \
    gcc \
    curl \
    net-tools \
    libpq-dev \
    python3-dev \
    build-base \
    && rm -rf /var/lib/apt/lists/*

# Create required folders
RUN mkdir -p /app/statics /app/log/{uwsgi,gunicorn,uvicorn}

# Install uv globally
RUN pip3 install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy only pyproject files before full source for better layer caching
COPY pyproject.toml uv.lock* /app/

# Create venv and sync dependencies with cache
RUN --mount=type=cache,target=/root/.cache

# Copy project files
COPY . /app/

# Create venv and sync dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv && uv sync --frozen

# Set working directory to your app
WORKDIR /app/src

# Healthcheck
# HEALTHCHECK --interval=15s --timeout=3s --retries=5 CMD curl --fail http://localhost:5000/health/ || exit 1

EXPOSE 3000

# Start the app using Makefile target
ENTRYPOINT ["make"]
CMD ["run-server"]