FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN apt-get update && apt-get install -y build-essential \
    && python -m pip install --upgrade pip

# Install poetry and dependencies
RUN pip install poetry && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi || true

# Copy code
COPY . /app

ENTRYPOINT ["python", "research/experiment.py"]
