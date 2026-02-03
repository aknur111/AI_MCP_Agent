FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir -e .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "src.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
