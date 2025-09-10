FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

COPY ./app ./app

FROM python:3.13-slim
WORKDIR /app
RUN groupadd -r appuser && useradd --no-create-home -r -g appuser appuser
COPY --from=builder /app /app
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "-b", "0.0.0.0:8000"]
