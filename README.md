Установка

1. Установить зависимости через uv:

```bash
uv sync
```

2. Установить PaddlePaddle отдельно (не на PyPI):

```bash
uv pip install paddlepaddle-gpu==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu130/
uv pip install paddleocr==3.6.0
```

3. Запустить приложение:

```bash
uv run app/main.py
```

Временый запуск прод БД

```Shell
docker run -d --rm --name test_prod_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=1234 -e POSTGRES_DB=invoice_app_db --network test_db -p 8080:5432 -v postgres-data:/var/lib/postgresql/data postgres:17.10-alpine3.24

docker run -d --name invoice_app --network test_db --gpus all --env-file .env.docker -p 8000:8000 invoice_app:0.14
```

Запуск всего приложения

```Shell
docker compose up
```
