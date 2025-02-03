# Use a minimal Python base image
FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["uv",  "run", "uvicorn", "snacks.main:app", "--port", "80", "--host", "0.0.0.0"]
