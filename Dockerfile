FROM nvidia/cuda:13.0.3-cudnn-runtime-ubuntu24.04

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot_group && useradd --system --gid 999 --uid 999 --create-home nonroot_user

RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Installing uv by copying the binaries
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

WORKDIR /invoice_ai

ENV PYTHONUNBUFFERED=1

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_TOOL_BIN_DIR=/usr/local/bin

# Install all depencies without tests
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

RUN --mount=type=cache, target=/root/.cache/uv \
    uv pip install paddlepaddle-gpu==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu130/ && \
    uv pip install paddleocr==3.6.0

# Copying the code
COPY . /invoice_ai

# Installing project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/invoice_ai/.venv/bin:$PATH"

COPY entrypoint.sh /invoice_ai/entrypoint.sh
RUN chmod +x /invoice_ai/entrypoint.sh

USER nonroot_user
ENTRYPOINT ["/invoice_ai/entrypoint.sh"]