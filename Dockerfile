FROM python:3.11

RUN apt-get update && \
  apt-get install -y -q --no-install-recommends ffmpeg curl unzip

# Install Deno
RUN curl -fsSL https://deno.land/install.sh | sh
ENV PATH="/root/.deno/bin:$PATH"

RUN python -m ensurepip --upgrade

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-ansi --no-root

COPY . .

CMD ["uvicorn", "downloader.api:app", "--host", "0.0.0.0"]
