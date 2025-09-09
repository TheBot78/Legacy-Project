###############################################################################
#                                                      STAGE 1: Build Geneweb
###############################################################################

FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/opt/venv

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libssl-dev libffi-dev zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:$PATH"

# Copy project files and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

###############################################################################
#                                              STAGE 2: Assemble Docker image
###############################################################################

FROM python:3.11-slim AS container

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/opt/venv
ENV PATH="${VENV_PATH}/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl-dev libffi-dev zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment and application files from the builder stage
COPY --from=builder ${VENV_PATH} ${VENV_PATH}
COPY --from=builder /app /app

# Set the working directory
WORKDIR /app

# Expose ports and define the default command
EXPOSE 2316-2317
CMD ["uvicorn", "RPC.main:app", "--host", "0.0.0.0", "--port", "2316"]