FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (e.g., libpq-dev for PostgreSQL support) and curl (to install Poetry)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry using the official installer.
# Here we set a specific version (1.2.2 or higher is recommended so the export command works)
ENV POETRY_VERSION=1.8.4
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

# Make Poetry available on the PATH. The installer puts it in /root/.local/bin
ENV PATH="/root/.local/bin:${PATH}"

# Copy dependency specification files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Configure Poetry to install dependencies to the system (not in a virtualenv)
RUN poetry config virtualenvs.create false

# Install dependencies defined in pyproject.toml (and poetry.lock)
# Using --no-interaction and --no-ansi for non-interactive Docker builds
RUN poetry install 
# Copy the rest of the application code
COPY . .

# Expose the port your FastAPI app will run on
EXPOSE 8000

# Command to run the FastAPI application with uvicorn
CMD ["uvicorn", "main:backend_server", "--host", "0.0.0.0", "--port", "8000"]
