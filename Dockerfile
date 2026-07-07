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

# Change owner, to allow nonroot_user create .venv
RUN chown nonroot_user:nonroot_group /invoice_ai

# Settings for nonuser_root to use uv
USER nonroot_user

ENV PYTHONUNBUFFERED=1

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_TOOL_BIN_DIR=/usr/local/bin

# Install all depencies without tests
RUN --mount=type=cache,target=/home/nonroot_user/.cache/uv,uid=999,gid=999 \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copying the code, with nonroot_user
COPY --chown=nonroot_user:nonroot_group . /invoice_ai

# Copyying only entrypoint.sh and adding executable property
COPY --chown=nonroot_user:nonroot_group --chmod=755 entrypoint.sh /invoice_ai/entrypoint.sh

# Installing project
RUN --mount=type=cache,target=/home/nonroot_user/.cache/uv,uid=999,gid=999 \
    uv sync --locked

    RUN --mount=type=cache,target=/home/nonroot_user/.cache/uv,uid=999,gid=999 \
    uv pip install --python /invoice_ai/.venv paddlepaddle-gpu==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu130/ && \
    uv pip install --python /invoice_ai/.venv paddleocr==3.6.0

ENV PATH="/invoice_ai/.venv/bin:$PATH"
ENTRYPOINT ["/invoice_ai/entrypoint.sh"]