## Установка

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

## Подправить .env
