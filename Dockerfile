FROM python:3.11

# Install ffmpeg
RUN apt-get update && \
  apt-get install -y -q --no-install-recommends ffmpeg

# Ensures that the python and pip versions are up-to-date
RUN python -m ensurepip --upgrade

# Install Poetry
RUN pip install poetry

# Copy only requirements, to cache them in docker layer
WORKDIR /app

# Copy poetry lock files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies without creating the poetry toolchain
RUN poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-ansi

COPY . .

CMD ["uvicorn", "downloader.api:app", "--host", "0.0.0.0"]
