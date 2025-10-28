###############################################################################
#                                                      STAGE 1: Build RPC App
###############################################################################

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/opt/venv
ENV PATH="${VENV_PATH}/bin:$PATH"
ENV PYTHONPATH=/app

# Installer dépendances système pour builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libssl-dev libffi-dev zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Créer le virtualenv
RUN python -m venv ${VENV_PATH}

# Copier le code RPC
WORKDIR /app
COPY rpc/ rpc/

# Installer dépendances spécifiques à rpc
RUN pip install --upgrade pip && pip install -r rpc/requirements.txt

###############################################################################
#                                              STAGE 2: Runtime container
###############################################################################

FROM python:3.11-slim AS container

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/opt/venv
ENV PATH="${VENV_PATH}/bin:$PATH"
ENV PYTHONPATH=/app

# Dépendances système runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl-dev libffi-dev zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copier venv + code depuis le builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

WORKDIR /app
EXPOSE 2316

CMD ["uvicorn", "rpc.server.main:app", "--host", "0.0.0.0", "--port", "2316"]
