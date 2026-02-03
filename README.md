# ai-mcp-agent

Небольшой сервис на FastAPI, который отвечает на запросы “агента” и использует MCP-серверы (stdio) для работы с товарами и заказами.  
Данные хранятся в JSON-файлах.

## Возможности

- HTTP API: `POST /api/v1/agent/query`
- MCP Products Server (stdio): товары, статистика
- MCP Orders Server (stdio): заказы, статистика
- Хранение данных в `data/products.json` и `data/orders.json`
- Тесты: `pytest`


## Требования

- Python 3.12+
- Docker Desktop (для запуска через Docker)
- (локально) `pip`, `venv`


## Быстрый запуск через Docker

### Убедитесь, что Docker работает:
```bash
docker info
```

### Запустите проект:
```
docker compose up --build

```

### Проверка API:
```
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Какая средняя цена продуктов?"}'
```

### Добавить продукт:
```
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Добавь новый продукт: Мышка, цена 1500, категория Электроника"}'
```

### Остановить:
```
docker compose down
```

Данные сохраняются в папке data/.

## Локальный запуск без Docker

### Создайте окружение и поставь зависимости:
```
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### Подготовьте файлы данных:
```
mkdir -p data
echo "[]" > data/products.json
echo "[]" > data/orders.json
```

### Выставьте переменные окружения:
```
export PYTHONPATH="$(pwd)"
export PRODUCTS_JSON_PATH="$(pwd)/data/products.json"
export ORDERS_JSON_PATH="$(pwd)/data/orders.json"
```

### Запустите API:
```
uvicorn src.entrypoints.api.main:app --reload --port 8000
```

### Проверка:
```
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Какая средняя цена продуктов?"}'
```

### Запуск тестов
```
source .venv/bin/activate
pytest -q
```

## Структура проекта
```
src/entrypoints/api/ — FastAPI приложение и роуты

src/entrypoints/mcp_products_server/ — MCP сервер товаров (stdio)

src/entrypoints/mcp_orders_server/ — MCP сервер заказов (stdio)

src/adapters/mcp_stdio/ — клиентские репозитории, которые дергают MCP сервера

src/adapters/storage/ — JSON-хранилище

tests/ — unit/integration тесты

Переменные окружения

PRODUCTS_JSON_PATH — путь к products.json

ORDERS_JSON_PATH — путь к orders.json

PYTHONPATH - должен указывать на корень проекта (нужно для import src...)

```

## Примеры запросов

### Средняя цена:
```
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Какая средняя цена продуктов?"}'
```

### Добавить продукт:
```
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Добавь новый продукт: Клавиатура, цена 12000, категория Электроника"}'
```

### Создать заказ:
```
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Создай заказ: продукт 1, количество 2"}'
```

### JSON режим (по умолчанию):
```
mkdir -p data
echo "[]" > data/products.json
echo "[]" > data/orders.json
export PRODUCTS_JSON_PATH="$(pwd)/data/products.json"
export ORDERS_JSON_PATH="$(pwd)/data/orders.json"
uvicorn src.entrypoints.api.main:app --port 8000
```

### SQLite режим:
```
mkdir -p data
export DB_PATH="$(pwd)/data/app.db"
uvicorn src.entrypoints.api.main:app --port 8000
```

### Автор проекта

- Салемкан Акнур