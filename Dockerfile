FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main

COPY . .

CMD ["poetry", "run", "python3", "-m", "src"]