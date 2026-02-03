FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml /app/pyproject.toml

RUN pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir .

COPY src /app/src
COPY tests /app/tests
COPY README.md /app/README.md

EXPOSE 8000

CMD ["uvicorn", "src.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
